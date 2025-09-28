"""
DAG de Pipeline de Machine Learning para Recomendaciones
Entrena, valida y despliega modelos de recomendación
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.task_group import TaskGroup
from airflow.utils.dates import days_ago
import pandas as pd
import numpy as np
import structlog
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import mlflow
import mlflow.sklearn

# Configurar logging
logger = structlog.get_logger()

# Configurar MLflow
mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("recomendaciones")

# Argumentos por defecto
default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['ml-team@empresa.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=60)
}

# Configuración del DAG
dag = DAG(
    'pipeline_ml_recomendaciones',
    default_args=default_args,
    description='Pipeline de ML para sistema de recomendaciones',
    schedule_interval='0 3 * * 0',  # Semanal los domingos a las 3 AM
    catchup=False,
    max_active_runs=1,
    tags=['ml', 'recomendaciones', 'semanal']
)

def extraer_datos_entrenamiento(**context):
    """
    Extraer datos para entrenamiento del modelo
    """
    logger.info("Iniciando extracción de datos de entrenamiento")
    
    # Conectar a la base de datos
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # Query para obtener datos de interacciones de usuarios
    query_interacciones = """
    SELECT 
        u.id_usuario,
        u.edad,
        u.genero,
        u.ciudad,
        u.fecha_registro,
        p.id_producto,
        p.categoria,
        p.precio,
        p.rating_promedio,
        i.tipo_interaccion,
        i.fecha_interaccion,
        i.duracion_segundos,
        CASE 
            WHEN i.tipo_interaccion = 'compra' THEN 1
            WHEN i.tipo_interaccion = 'vista' AND i.duracion_segundos > 30 THEN 1
            ELSE 0
        END as interes
    FROM usuarios u
    JOIN interacciones i ON u.id_usuario = i.id_usuario
    JOIN productos p ON i.id_producto = p.id_producto
    WHERE i.fecha_interaccion >= CURRENT_DATE - INTERVAL '90 days'
    """
    
    # Ejecutar query
    df = postgres_hook.get_pandas_df(query_interacciones)
    
    # Guardar datos
    archivo_datos = f'/tmp/datos_entrenamiento_{context["ds"]}.csv'
    df.to_csv(archivo_datos, index=False)
    
    # Almacenar en XCom
    context['task_instance'].xcom_push(key='archivo_datos', value=archivo_datos)
    context['task_instance'].xcom_push(key='total_registros', value=len(df))
    
    logger.info(f"Extracción completada: {len(df)} registros")
    return archivo_datos

def preparar_datos(**context):
    """
    Preparar y preprocesar datos para entrenamiento
    """
    logger.info("Iniciando preparación de datos")
    
    # Obtener archivo de datos
    archivo_datos = context['task_instance'].xcom_pull(task_ids='extraer_datos', key='archivo_datos')
    
    # Leer datos
    df = pd.read_csv(archivo_datos)
    
    # Preprocesamiento
    logger.info("Aplicando preprocesamiento de datos")
    
    # 1. Limpiar datos nulos
    df = df.dropna()
    
    # 2. Crear características adicionales
    df['dias_registro'] = (pd.to_datetime('now') - pd.to_datetime(df['fecha_registro'])).dt.days
    df['precio_categoria'] = pd.cut(df['precio'], bins=5, labels=['Muy Bajo', 'Bajo', 'Medio', 'Alto', 'Muy Alto'])
    df['rating_categoria'] = pd.cut(df['rating_promedio'], bins=3, labels=['Bajo', 'Medio', 'Alto'])
    
    # 3. Codificar variables categóricas
    df_encoded = pd.get_dummies(df, columns=['genero', 'ciudad', 'categoria', 'precio_categoria', 'rating_categoria'])
    
    # 4. Seleccionar características
    caracteristicas = [
        'edad', 'dias_registro', 'precio', 'rating_promedio', 'duracion_segundos',
        'genero_F', 'genero_M', 'categoria_electronica', 'categoria_ropa', 'categoria_hogar',
        'precio_categoria_Alto', 'precio_categoria_Medio', 'rating_categoria_Alto', 'rating_categoria_Medio'
    ]
    
    # Filtrar características disponibles
    caracteristicas_disponibles = [col for col in caracteristicas if col in df_encoded.columns]
    
    X = df_encoded[caracteristicas_disponibles]
    y = df_encoded['interes']
    
    # 5. Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 6. Normalizar características
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Guardar datos procesados
    datos_procesados = {
        'X_train': X_train_scaled,
        'X_test': X_test_scaled,
        'y_train': y_train.values,
        'y_test': y_test.values,
        'caracteristicas': caracteristicas_disponibles,
        'scaler': scaler
    }
    
    archivo_procesado = f'/tmp/datos_procesados_{context["ds"]}.joblib'
    joblib.dump(datos_procesados, archivo_procesado)
    
    # Almacenar métricas
    context['task_instance'].xcom_push(key='archivo_procesado', value=archivo_procesado)
    context['task_instance'].xcom_push(key='tamaño_entrenamiento', value=len(X_train))
    context['task_instance'].xcom_push(key='tamaño_test', value=len(X_test))
    context['task_instance'].xcom_push(key='caracteristicas', value=caracteristicas_disponibles)
    
    logger.info(f"Preparación completada: {len(X_train)} muestras de entrenamiento, {len(X_test)} de test")
    return archivo_procesado

def entrenar_modelo(**context):
    """
    Entrenar modelo de recomendación
    """
    logger.info("Iniciando entrenamiento del modelo")
    
    # Obtener datos procesados
    archivo_procesado = context['task_instance'].xcom_pull(task_ids='preparar_datos', key='archivo_procesado')
    datos = joblib.load(archivo_procesado)
    
    # Iniciar run de MLflow
    with mlflow.start_run(run_name=f"entrenamiento_{context['ds']}"):
        # Configurar parámetros del modelo
        params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42
        }
        
        # Log parámetros
        mlflow.log_params(params)
        
        # Crear y entrenar modelo
        modelo = RandomForestClassifier(**params)
        modelo.fit(datos['X_train'], datos['y_train'])
        
        # Hacer predicciones
        y_pred = modelo.predict(datos['X_test'])
        y_pred_proba = modelo.predict_proba(datos['X_test'])[:, 1]
        
        # Calcular métricas
        accuracy = accuracy_score(datos['y_test'], y_pred)
        precision = precision_score(datos['y_test'], y_pred)
        recall = recall_score(datos['y_test'], y_pred)
        f1 = f1_score(datos['y_test'], y_pred)
        
        # Log métricas
        mlflow.log_metrics({
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        })
        
        # Log modelo
        mlflow.sklearn.log_model(
            modelo, 
            "modelo_recomendaciones",
            registered_model_name="RecomendacionesRF"
        )
        
        # Guardar modelo localmente
        archivo_modelo = f'/tmp/modelo_recomendaciones_{context["ds"]}.joblib'
        joblib.dump(modelo, archivo_modelo)
        
        # Almacenar métricas
        context['task_instance'].xcom_push(key='archivo_modelo', value=archivo_modelo)
        context['task_instance'].xcom_push(key='accuracy', value=accuracy)
        context['task_instance'].xcom_push(key='precision', value=precision)
        context['task_instance'].xcom_push(key='recall', value=recall)
        context['task_instance'].xcom_push(key='f1_score', value=f1)
        
        logger.info(f"Entrenamiento completado - Accuracy: {accuracy:.3f}, F1: {f1:.3f}")
        return archivo_modelo

def validar_modelo(**context):
    """
    Validar modelo entrenado
    """
    logger.info("Iniciando validación del modelo")
    
    # Obtener métricas del entrenamiento
    accuracy = context['task_instance'].xcom_pull(task_ids='entrenar_modelo', key='accuracy')
    precision = context['task_instance'].xcom_pull(task_ids='entrenar_modelo', key='precision')
    recall = context['task_instance'].xcom_pull(task_ids='entrenar_modelo', key='recall')
    f1_score = context['task_instance'].xcom_pull(task_ids='entrenar_modelo', key='f1_score')
    
    # Criterios de validación
    umbrales = {
        'accuracy_min': 0.75,
        'precision_min': 0.70,
        'recall_min': 0.65,
        'f1_min': 0.70
    }
    
    # Validar métricas
    validaciones = {
        'accuracy_ok': accuracy >= umbrales['accuracy_min'],
        'precision_ok': precision >= umbrales['precision_min'],
        'recall_ok': recall >= umbrales['recall_min'],
        'f1_ok': f1_score >= umbrales['f1_min']
    }
    
    # Determinar si el modelo es válido
    modelo_valido = all(validaciones.values())
    
    # Almacenar resultados
    context['task_instance'].xcom_push(key='modelo_valido', value=modelo_valido)
    context['task_instance'].xcom_push(key='validaciones', value=validaciones)
    context['task_instance'].xcom_push(key='metricas', value={
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    })
    
    logger.info(f"Validación completada - Modelo válido: {modelo_valido}")
    return modelo_valido

def desplegar_modelo(**context):
    """
    Desplegar modelo validado a producción
    """
    logger.info("Iniciando despliegue del modelo")
    
    # Verificar que el modelo es válido
    modelo_valido = context['task_instance'].xcom_pull(task_ids='validar_modelo', key='modelo_valido')
    
    if not modelo_valido:
        raise ValueError("El modelo no pasó la validación, no se puede desplegar")
    
    # Obtener archivo del modelo
    archivo_modelo = context['task_instance'].xcom_pull(task_ids='entrenar_modelo', key='archivo_modelo')
    
    # Cargar modelo
    modelo = joblib.load(archivo_modelo)
    
    # Crear directorio de producción
    directorio_produccion = '/opt/models/produccion'
    
    # Guardar modelo en producción
    archivo_produccion = f'{directorio_produccion}/modelo_recomendaciones_latest.joblib'
    joblib.dump(modelo, archivo_produccion)
    
    # Crear archivo de metadatos
    metricas = context['task_instance'].xcom_pull(task_ids='validar_modelo', key='metricas')
    metadatos = {
        'fecha_entrenamiento': context['ds'],
        'version': '1.0.0',
        'metricas': metricas,
        'archivo_modelo': archivo_produccion
    }
    
    archivo_metadatos = f'{directorio_produccion}/metadatos_latest.json'
    with open(archivo_metadatos, 'w') as f:
        json.dump(metadatos, f, indent=2)
    
    # Almacenar información de despliegue
    context['task_instance'].xcom_push(key='archivo_produccion', value=archivo_produccion)
    context['task_instance'].xcom_push(key='archivo_metadatos', value=archivo_metadatos)
    
    logger.info("Despliegue completado exitosamente")
    return archivo_produccion

def probar_modelo_desplegado(**context):
    """
    Probar modelo desplegado con datos de prueba
    """
    logger.info("Iniciando pruebas del modelo desplegado")
    
    # Obtener archivo del modelo
    archivo_produccion = context['task_instance'].xcom_pull(task_ids='desplegar_modelo', key='archivo_produccion')
    
    # Cargar modelo
    modelo = joblib.load(archivo_produccion)
    
    # Crear datos de prueba
    datos_prueba = np.random.rand(10, 14)  # 10 muestras, 14 características
    
    # Hacer predicciones
    predicciones = modelo.predict(datos_prueba)
    probabilidades = modelo.predict_proba(datos_prueba)
    
    # Verificar que las predicciones son válidas
    predicciones_validas = all(pred in [0, 1] for pred in predicciones)
    probabilidades_validas = all(0 <= prob <= 1 for prob in probabilidades.flatten())
    
    # Almacenar resultados de prueba
    context['task_instance'].xcom_push(key='predicciones_validas', value=predicciones_validas)
    context['task_instance'].xcom_push(key='probabilidades_validas', value=probabilidades_validas)
    context['task_instance'].xcom_push(key='total_predicciones', value=len(predicciones))
    
    logger.info(f"Pruebas completadas - Predicciones válidas: {predicciones_validas}")
    return predicciones_validas

def generar_reporte_ml(**context):
    """
    Generar reporte del pipeline de ML
    """
    logger.info("Generando reporte del pipeline de ML")
    
    # Obtener métricas
    metricas = context['task_instance'].xcom_pull(task_ids='validar_modelo', key='metricas')
    modelo_valido = context['task_instance'].xcom_pull(task_ids='validar_modelo', key='modelo_valido')
    predicciones_validas = context['task_instance'].xcom_pull(task_ids='probar_modelo', key='predicciones_validas')
    
    # Crear reporte
    reporte = f"""
    REPORTE DE PIPELINE DE MACHINE LEARNING - {context['ds']}
    ========================================================
    
    Métricas del Modelo:
    - Accuracy: {metricas['accuracy']:.3f}
    - Precision: {metricas['precision']:.3f}
    - Recall: {metricas['recall']:.3f}
    - F1-Score: {metricas['f1_score']:.3f}
    
    Estado de Validación: {'✅ VÁLIDO' if modelo_valido else '❌ INVÁLIDO'}
    Estado de Despliegue: {'✅ EXITOSO' if predicciones_validas else '❌ FALLIDO'}
    
    Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    # Guardar reporte
    archivo_reporte = f'/tmp/reporte_ml_{context["ds"]}.txt'
    with open(archivo_reporte, 'w') as f:
        f.write(reporte)
    
    context['task_instance'].xcom_push(key='archivo_reporte', value=archivo_reporte)
    
    logger.info("Reporte generado exitosamente")
    return archivo_reporte

# Definir tareas
with TaskGroup("preparacion", tooltip="Preparación de datos") as grupo_preparacion:
    # Extraer datos
    extraer_datos = PythonOperator(
        task_id='extraer_datos',
        python_callable=extraer_datos_entrenamiento,
        provide_context=True
    )
    
    # Preparar datos
    preparar_datos = PythonOperator(
        task_id='preparar_datos',
        python_callable=preparar_datos,
        provide_context=True
    )
    
    extraer_datos >> preparar_datos

with TaskGroup("entrenamiento", tooltip="Entrenamiento del modelo") as grupo_entrenamiento:
    # Entrenar modelo
    entrenar_modelo = PythonOperator(
        task_id='entrenar_modelo',
        python_callable=entrenar_modelo,
        provide_context=True
    )
    
    # Validar modelo
    validar_modelo = PythonOperator(
        task_id='validar_modelo',
        python_callable=validar_modelo,
        provide_context=True
    )
    
    entrenar_modelo >> validar_modelo

with TaskGroup("despliegue", tooltip="Despliegue del modelo") as grupo_despliegue:
    # Desplegar modelo
    desplegar_modelo = PythonOperator(
        task_id='desplegar_modelo',
        python_callable=desplegar_modelo,
        provide_context=True
    )
    
    # Probar modelo
    probar_modelo = PythonOperator(
        task_id='probar_modelo',
        python_callable=probar_modelo_desplegado,
        provide_context=True
    )
    
    desplegar_modelo >> probar_modelo

with TaskGroup("reportes", tooltip="Generación de reportes") as grupo_reportes:
    # Generar reporte
    generar_reporte = PythonOperator(
        task_id='generar_reporte',
        python_callable=generar_reporte_ml,
        provide_context=True
    )
    
    # Limpiar archivos temporales
    limpiar_archivos = BashOperator(
        task_id='limpiar_archivos',
        bash_command="""
        rm -f /tmp/datos_entrenamiento_*.csv
        rm -f /tmp/datos_procesados_*.joblib
        rm -f /tmp/modelo_recomendaciones_*.joblib
        rm -f /tmp/reporte_ml_*.txt
        echo "Archivos temporales eliminados"
        """
    )
    
    generar_reporte >> limpiar_archivos

# Definir dependencias
grupo_preparacion >> grupo_entrenamiento >> grupo_despliegue >> grupo_reportes
