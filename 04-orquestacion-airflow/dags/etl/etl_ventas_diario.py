"""
DAG de ETL Diario de Ventas
Extrae, transforma y carga datos de ventas diariamente
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.operators.dummy import DummyOperator
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.sql import SqlSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.task_group import TaskGroup
from airflow.utils.dates import days_ago
import pandas as pd
import structlog

# Configurar logging
logger = structlog.get_logger()

# Argumentos por defecto
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['admin@empresa.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30)
}

# Configuración del DAG
dag = DAG(
    'etl_ventas_diario',
    default_args=default_args,
    description='ETL diario de datos de ventas',
    schedule_interval='0 2 * * *',  # Diario a las 2:00 AM
    catchup=False,
    max_active_runs=1,
    tags=['etl', 'ventas', 'diario']
)

def extraer_datos_ventas(**context):
    """
    Extraer datos de ventas del día anterior
    """
    logger.info("Iniciando extracción de datos de ventas")
    
    # Obtener fecha de ejecución
    fecha_ejecucion = context['ds']
    fecha_anterior = (datetime.strptime(fecha_ejecucion, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Conectar a la base de datos
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # Query de extracción
    query = f"""
    SELECT 
        id_venta,
        fecha_venta,
        id_cliente,
        id_producto,
        cantidad,
        precio_unitario,
        total_venta,
        descuento,
        id_vendedor,
        region,
        canal_venta
    FROM ventas 
    WHERE DATE(fecha_venta) = '{fecha_anterior}'
    """
    
    # Ejecutar query y obtener datos
    df = postgres_hook.get_pandas_df(query)
    
    # Guardar datos en archivo temporal
    archivo_temp = f'/tmp/ventas_{fecha_anterior}.csv'
    df.to_csv(archivo_temp, index=False)
    
    # Almacenar en XCom para siguiente tarea
    context['task_instance'].xcom_push(key='archivo_ventas', value=archivo_temp)
    context['task_instance'].xcom_push(key='total_registros', value=len(df))
    
    logger.info(f"Extracción completada: {len(df)} registros")
    return archivo_temp

def transformar_datos_ventas(**context):
    """
    Transformar y limpiar datos de ventas
    """
    logger.info("Iniciando transformación de datos de ventas")
    
    # Obtener archivo de la tarea anterior
    archivo_ventas = context['task_instance'].xcom_pull(task_ids='extraer_datos', key='archivo_ventas')
    
    # Leer datos
    df = pd.read_csv(archivo_ventas)
    
    # Transformaciones
    logger.info("Aplicando transformaciones de datos")
    
    # 1. Limpiar datos nulos
    df = df.dropna(subset=['id_venta', 'fecha_venta', 'total_venta'])
    
    # 2. Convertir tipos de datos
    df['fecha_venta'] = pd.to_datetime(df['fecha_venta'])
    df['total_venta'] = pd.to_numeric(df['total_venta'], errors='coerce')
    df['descuento'] = df['descuento'].fillna(0)
    
    # 3. Calcular métricas adicionales
    df['margen_bruto'] = df['total_venta'] - (df['cantidad'] * df['precio_unitario'])
    df['porcentaje_descuento'] = (df['descuento'] / df['total_venta']) * 100
    df['dia_semana'] = df['fecha_venta'].dt.day_name()
    df['mes'] = df['fecha_venta'].dt.month
    df['trimestre'] = df['fecha_venta'].dt.quarter
    
    # 4. Categorizar ventas por valor
    df['categoria_venta'] = pd.cut(
        df['total_venta'],
        bins=[0, 100, 500, 1000, float('inf')],
        labels=['Baja', 'Media', 'Alta', 'Premium']
    )
    
    # 5. Validar datos
    registros_invalidos = df[df['total_venta'] <= 0].shape[0]
    if registros_invalidos > 0:
        logger.warning(f"Encontrados {registros_invalidos} registros con total_venta <= 0")
        df = df[df['total_venta'] > 0]
    
    # Guardar datos transformados
    archivo_transformado = f'/tmp/ventas_transformadas_{context["ds"]}.csv'
    df.to_csv(archivo_transformado, index=False)
    
    # Almacenar métricas
    context['task_instance'].xcom_push(key='archivo_transformado', value=archivo_transformado)
    context['task_instance'].xcom_push(key='registros_transformados', value=len(df))
    context['task_instance'].xcom_push(key='ventas_totales', value=df['total_venta'].sum())
    context['task_instance'].xcom_push(key='promedio_venta', value=df['total_venta'].mean())
    
    logger.info(f"Transformación completada: {len(df)} registros")
    return archivo_transformado

def cargar_datos_ventas(**context):
    """
    Cargar datos transformados a la base de datos de destino
    """
    logger.info("Iniciando carga de datos de ventas")
    
    # Obtener archivo transformado
    archivo_transformado = context['task_instance'].xcom_pull(task_ids='transformar_datos', key='archivo_transformado')
    
    # Leer datos transformados
    df = pd.read_csv(archivo_transformado)
    
    # Conectar a la base de datos de destino
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # Crear tabla si no existe
    crear_tabla_query = """
    CREATE TABLE IF NOT EXISTS ventas_procesadas (
        id_venta INTEGER,
        fecha_venta TIMESTAMP,
        id_cliente INTEGER,
        id_producto INTEGER,
        cantidad INTEGER,
        precio_unitario DECIMAL(10,2),
        total_venta DECIMAL(10,2),
        descuento DECIMAL(10,2),
        id_vendedor INTEGER,
        region VARCHAR(50),
        canal_venta VARCHAR(50),
        margen_bruto DECIMAL(10,2),
        porcentaje_descuento DECIMAL(5,2),
        dia_semana VARCHAR(20),
        mes INTEGER,
        trimestre INTEGER,
        categoria_venta VARCHAR(20),
        fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    postgres_hook.run(crear_tabla_query)
    
    # Insertar datos
    logger.info("Insertando datos en la base de datos")
    
    # Convertir DataFrame a lista de tuplas para inserción
    datos_para_insertar = df.to_records(index=False).tolist()
    
    # Query de inserción
    insert_query = """
    INSERT INTO ventas_procesadas (
        id_venta, fecha_venta, id_cliente, id_producto, cantidad,
        precio_unitario, total_venta, descuento, id_vendedor, region,
        canal_venta, margen_bruto, porcentaje_descuento, dia_semana,
        mes, trimestre, categoria_venta
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Ejecutar inserción
    postgres_hook.insert_rows(
        table='ventas_procesadas',
        rows=datos_para_insertar,
        target_fields=[
            'id_venta', 'fecha_venta', 'id_cliente', 'id_producto', 'cantidad',
            'precio_unitario', 'total_venta', 'descuento', 'id_vendedor', 'region',
            'canal_venta', 'margen_bruto', 'porcentaje_descuento', 'dia_semana',
            'mes', 'trimestre', 'categoria_venta'
        ]
    )
    
    logger.info("Carga de datos completada")
    return len(datos_para_insertar)

def validar_calidad_datos(**context):
    """
    Validar calidad de los datos procesados
    """
    logger.info("Iniciando validación de calidad de datos")
    
    # Obtener métricas de las tareas anteriores
    registros_originales = context['task_instance'].xcom_pull(task_ids='extraer_datos', key='total_registros')
    registros_transformados = context['task_instance'].xcom_pull(task_ids='transformar_datos', key='registros_transformados')
    ventas_totales = context['task_instance'].xcom_pull(task_ids='transformar_datos', key='ventas_totales')
    
    # Calcular métricas de calidad
    tasa_completitud = (registros_transformados / registros_originales) * 100 if registros_originales > 0 else 0
    
    # Validaciones
    validaciones = {
        'tasa_completitud': tasa_completitud,
        'registros_originales': registros_originales,
        'registros_transformados': registros_transformados,
        'ventas_totales': ventas_totales,
        'validacion_exitosa': True
    }
    
    # Verificar umbrales de calidad
    if tasa_completitud < 95:
        logger.error(f"Tasa de completitud muy baja: {tasa_completitud:.2f}%")
        validaciones['validacion_exitosa'] = False
    
    if ventas_totales <= 0:
        logger.error("Total de ventas inválido")
        validaciones['validacion_exitosa'] = False
    
    # Almacenar resultados
    context['task_instance'].xcom_push(key='validaciones', value=validaciones)
    
    logger.info(f"Validación completada: {validaciones}")
    return validaciones

def generar_reporte_diario(**context):
    """
    Generar reporte diario de ventas
    """
    logger.info("Generando reporte diario de ventas")
    
    # Obtener métricas
    validaciones = context['task_instance'].xcom_pull(task_ids='validar_calidad', key='validaciones')
    
    # Crear reporte
    reporte = f"""
    REPORTE DIARIO DE VENTAS - {context['ds']}
    ==========================================
    
    Métricas de Procesamiento:
    - Registros originales: {validaciones['registros_originales']:,}
    - Registros procesados: {validaciones['registros_transformados']:,}
    - Tasa de completitud: {validaciones['tasa_completitud']:.2f}%
    - Total de ventas: ${validaciones['ventas_totales']:,.2f}
    
    Estado de Validación: {'✅ EXITOSO' if validaciones['validacion_exitosa'] else '❌ FALLIDO'}
    
    Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    # Guardar reporte
    archivo_reporte = f'/tmp/reporte_ventas_{context["ds"]}.txt'
    with open(archivo_reporte, 'w') as f:
        f.write(reporte)
    
    context['task_instance'].xcom_push(key='archivo_reporte', value=archivo_reporte)
    
    logger.info("Reporte generado exitosamente")
    return archivo_reporte

# Definir tareas
with TaskGroup("extraccion", tooltip="Extracción de datos") as grupo_extraccion:
    # Sensor para verificar que hay datos disponibles
    sensor_datos = SqlSensor(
        task_id='verificar_datos_disponibles',
        conn_id='postgres_default',
        sql="SELECT COUNT(*) FROM ventas WHERE DATE(fecha_venta) = '{{ ds }}'::date - interval '1 day'",
        timeout=300,
        poke_interval=60
    )
    
    # Tarea de extracción
    extraer_datos = PythonOperator(
        task_id='extraer_datos',
        python_callable=extraer_datos_ventas,
        provide_context=True
    )
    
    sensor_datos >> extraer_datos

with TaskGroup("transformacion", tooltip="Transformación de datos") as grupo_transformacion:
    # Tarea de transformación
    transformar_datos = PythonOperator(
        task_id='transformar_datos',
        python_callable=transformar_datos_ventas,
        provide_context=True
    )

with TaskGroup("carga", tooltip="Carga de datos") as grupo_carga:
    # Tarea de carga
    cargar_datos = PythonOperator(
        task_id='cargar_datos',
        python_callable=cargar_datos_ventas,
        provide_context=True
    )
    
    # Tarea de validación
    validar_calidad = PythonOperator(
        task_id='validar_calidad',
        python_callable=validar_calidad_datos,
        provide_context=True
    )
    
    cargar_datos >> validar_calidad

with TaskGroup("reportes", tooltip="Generación de reportes") as grupo_reportes:
    # Tarea de reporte
    generar_reporte = PythonOperator(
        task_id='generar_reporte',
        python_callable=generar_reporte_diario,
        provide_context=True
    )
    
    # Tarea de limpieza de archivos temporales
    limpiar_archivos = BashOperator(
        task_id='limpiar_archivos',
        bash_command="""
        rm -f /tmp/ventas_*.csv
        rm -f /tmp/reporte_ventas_*.txt
        echo "Archivos temporales eliminados"
        """
    )
    
    generar_reporte >> limpiar_archivos

# Tarea de notificación por email
notificar_exito = EmailOperator(
    task_id='notificar_exito',
    to=['admin@empresa.com', 'data-team@empresa.com'],
    subject='ETL Ventas Diario - Ejecución Exitosa',
    html_content="""
    <h2>ETL de Ventas Diario Completado</h2>
    <p>El proceso ETL de ventas se ejecutó exitosamente.</p>
    <p>Fecha: {{ ds }}</p>
    <p>Para más detalles, revisar la interfaz de Airflow.</p>
    """,
    trigger_rule='all_success'
)

notificar_fallo = EmailOperator(
    task_id='notificar_fallo',
    to=['admin@empresa.com', 'data-team@empresa.com'],
    subject='ETL Ventas Diario - Error en Ejecución',
    html_content="""
    <h2>ETL de Ventas Diario - Error</h2>
    <p>El proceso ETL de ventas falló durante la ejecución.</p>
    <p>Fecha: {{ ds }}</p>
    <p>Por favor, revisar los logs para más información.</p>
    """,
    trigger_rule='one_failed'
)

# Definir dependencias
grupo_extraccion >> grupo_transformacion >> grupo_carga >> grupo_reportes
grupo_carga >> [notificar_exito, notificar_fallo]
