"""
DAG de Health Check del Sistema
Monitorea la salud de todos los servicios y componentes
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.operators.dummy import DummyOperator
from airflow.sensors.http_sensor import HttpSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.task_group import TaskGroup
from airflow.utils.dates import days_ago
import requests
import psutil
import structlog
import json

# Configurar logging
logger = structlog.get_logger()

# Argumentos por defecto
default_args = {
    'owner': 'ops-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['ops-team@empresa.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=10)
}

# Configuración del DAG
dag = DAG(
    'health_check_sistema',
    default_args=default_args,
    description='Health check completo del sistema',
    schedule_interval='*/15 * * * *',  # Cada 15 minutos
    catchup=False,
    max_active_runs=1,
    tags=['monitoreo', 'health-check', 'sistema']
)

def verificar_base_datos(**context):
    """
    Verificar salud de la base de datos
    """
    logger.info("Verificando salud de la base de datos")
    
    try:
        # Conectar a la base de datos
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Ejecutar query de salud
        query_salud = """
        SELECT 
            'postgres' as servicio,
            version() as version,
            pg_database_size(current_database()) as tamaño_bd,
            (SELECT count(*) FROM pg_stat_activity) as conexiones_activas,
            (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as consultas_activas
        """
        
        resultado = postgres_hook.get_first(query_salud)
        
        # Verificar métricas
        salud_bd = {
            'servicio': 'postgres',
            'estado': 'healthy',
            'version': resultado[1],
            'tamaño_mb': round(resultado[2] / 1024 / 1024, 2),
            'conexiones_activas': resultado[3],
            'consultas_activas': resultado[4],
            'timestamp': datetime.now().isoformat()
        }
        
        # Verificar umbrales
        if resultado[3] > 100:  # Más de 100 conexiones
            salud_bd['estado'] = 'warning'
            salud_bd['alerta'] = 'Demasiadas conexiones activas'
        
        if resultado[4] > 50:  # Más de 50 consultas activas
            salud_bd['estado'] = 'warning'
            salud_bd['alerta'] = 'Demasiadas consultas activas'
        
        # Almacenar resultado
        context['task_instance'].xcom_push(key='salud_bd', value=salud_bd)
        
        logger.info(f"Base de datos: {salud_bd['estado']}")
        return salud_bd
        
    except Exception as e:
        logger.error(f"Error verificando base de datos: {str(e)}")
        salud_bd = {
            'servicio': 'postgres',
            'estado': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        context['task_instance'].xcom_push(key='salud_bd', value=salud_bd)
        return salud_bd

def verificar_redis(**context):
    """
    Verificar salud de Redis
    """
    logger.info("Verificando salud de Redis")
    
    try:
        # Conectar a Redis
        import redis
        r = redis.Redis(host='redis', port=6379, decode_responses=True)
        
        # Ejecutar comando PING
        respuesta_ping = r.ping()
        
        # Obtener información del servidor
        info = r.info()
        
        # Verificar métricas
        salud_redis = {
            'servicio': 'redis',
            'estado': 'healthy' if respuesta_ping else 'unhealthy',
            'version': info.get('redis_version'),
            'memoria_usada_mb': round(info.get('used_memory', 0) / 1024 / 1024, 2),
            'memoria_maxima_mb': round(info.get('maxmemory', 0) / 1024 / 1024, 2),
            'conexiones_cliente': info.get('connected_clients', 0),
            'comandos_por_segundo': info.get('instantaneous_ops_per_sec', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        # Verificar umbrales
        if salud_redis['memoria_usada_mb'] > 1000:  # Más de 1GB
            salud_redis['estado'] = 'warning'
            salud_redis['alerta'] = 'Uso de memoria alto'
        
        if salud_redis['conexiones_cliente'] > 200:  # Más de 200 conexiones
            salud_redis['estado'] = 'warning'
            salud_redis['alerta'] = 'Demasiadas conexiones de cliente'
        
        # Almacenar resultado
        context['task_instance'].xcom_push(key='salud_redis', value=salud_redis)
        
        logger.info(f"Redis: {salud_redis['estado']}")
        return salud_redis
        
    except Exception as e:
        logger.error(f"Error verificando Redis: {str(e)}")
        salud_redis = {
            'servicio': 'redis',
            'estado': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        context['task_instance'].xcom_push(key='salud_redis', value=salud_redis)
        return salud_redis

def verificar_apis_externas(**context):
    """
    Verificar salud de APIs externas
    """
    logger.info("Verificando salud de APIs externas")
    
    apis_a_verificar = [
        {
            'nombre': 'API Principal',
            'url': 'http://api:8000/health',
            'timeout': 5
        },
        {
            'nombre': 'API NLP',
            'url': 'http://nlp-api:8000/health',
            'timeout': 5
        },
        {
            'nombre': 'MLflow',
            'url': 'http://mlflow:5000/health',
            'timeout': 5
        }
    ]
    
    resultados_apis = []
    
    for api in apis_a_verificar:
        try:
            # Hacer request a la API
            response = requests.get(
                api['url'], 
                timeout=api['timeout'],
                headers={'User-Agent': 'Airflow-HealthCheck/1.0'}
            )
            
            # Verificar respuesta
            if response.status_code == 200:
                estado = 'healthy'
                try:
                    data = response.json()
                    mensaje = data.get('mensaje', 'OK')
                except:
                    mensaje = 'OK'
            else:
                estado = 'unhealthy'
                mensaje = f'HTTP {response.status_code}'
            
            salud_api = {
                'servicio': api['nombre'],
                'estado': estado,
                'url': api['url'],
                'status_code': response.status_code,
                'tiempo_respuesta_ms': round(response.elapsed.total_seconds() * 1000, 2),
                'mensaje': mensaje,
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.Timeout:
            salud_api = {
                'servicio': api['nombre'],
                'estado': 'unhealthy',
                'url': api['url'],
                'error': 'Timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            salud_api = {
                'servicio': api['nombre'],
                'estado': 'unhealthy',
                'url': api['url'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
        resultados_apis.append(salud_api)
        logger.info(f"{api['nombre']}: {salud_api['estado']}")
    
    # Almacenar resultados
    context['task_instance'].xcom_push(key='salud_apis', value=resultados_apis)
    
    return resultados_apis

def verificar_recursos_sistema(**context):
    """
    Verificar recursos del sistema (CPU, memoria, disco)
    """
    logger.info("Verificando recursos del sistema")
    
    try:
        # Obtener métricas del sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memoria = psutil.virtual_memory()
        disco = psutil.disk_usage('/')
        
        # Verificar métricas
        salud_sistema = {
            'servicio': 'sistema',
            'estado': 'healthy',
            'cpu_percent': cpu_percent,
            'memoria_total_gb': round(memoria.total / 1024 / 1024 / 1024, 2),
            'memoria_usada_gb': round(memoria.used / 1024 / 1024 / 1024, 2),
            'memoria_percent': memoria.percent,
            'disco_total_gb': round(disco.total / 1024 / 1024 / 1024, 2),
            'disco_usado_gb': round(disco.used / 1024 / 1024 / 1024, 2),
            'disco_percent': round((disco.used / disco.total) * 100, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        # Verificar umbrales
        if cpu_percent > 80:
            salud_sistema['estado'] = 'warning'
            salud_sistema['alerta'] = 'Uso de CPU alto'
        
        if memoria.percent > 85:
            salud_sistema['estado'] = 'warning'
            salud_sistema['alerta'] = 'Uso de memoria alto'
        
        if salud_sistema['disco_percent'] > 90:
            salud_sistema['estado'] = 'critical'
            salud_sistema['alerta'] = 'Espacio en disco crítico'
        
        # Almacenar resultado
        context['task_instance'].xcom_push(key='salud_sistema', value=salud_sistema)
        
        logger.info(f"Sistema: {salud_sistema['estado']}")
        return salud_sistema
        
    except Exception as e:
        logger.error(f"Error verificando recursos del sistema: {str(e)}")
        salud_sistema = {
            'servicio': 'sistema',
            'estado': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        context['task_instance'].xcom_push(key='salud_sistema', value=salud_sistema)
        return salud_sistema

def consolidar_health_check(**context):
    """
    Consolidar todos los health checks
    """
    logger.info("Consolidando health checks")
    
    # Obtener resultados de todas las verificaciones
    salud_bd = context['task_instance'].xcom_pull(task_ids='verificar_bd', key='salud_bd')
    salud_redis = context['task_instance'].xcom_pull(task_ids='verificar_redis', key='salud_redis')
    salud_apis = context['task_instance'].xcom_pull(task_ids='verificar_apis', key='salud_apis')
    salud_sistema = context['task_instance'].xcom_pull(task_ids='verificar_sistema', key='salud_sistema')
    
    # Consolidar resultados
    health_check_completo = {
        'timestamp': datetime.now().isoformat(),
        'servicios': {
            'base_datos': salud_bd,
            'redis': salud_redis,
            'apis': salud_apis,
            'sistema': salud_sistema
        }
    }
    
    # Determinar estado general
    estados = [
        salud_bd.get('estado', 'unknown'),
        salud_redis.get('estado', 'unknown'),
        salud_sistema.get('estado', 'unknown')
    ]
    
    # Agregar estados de APIs
    for api in salud_apis:
        estados.append(api.get('estado', 'unknown'))
    
    # Determinar estado general
    if 'critical' in estados:
        estado_general = 'critical'
    elif 'unhealthy' in estados:
        estado_general = 'unhealthy'
    elif 'warning' in estados:
        estado_general = 'warning'
    else:
        estado_general = 'healthy'
    
    health_check_completo['estado_general'] = estado_general
    
    # Contar servicios por estado
    conteo_estados = {}
    for estado in estados:
        conteo_estados[estado] = conteo_estados.get(estado, 0) + 1
    
    health_check_completo['resumen'] = {
        'total_servicios': len(estados),
        'conteo_estados': conteo_estados,
        'estado_general': estado_general
    }
    
    # Almacenar resultado
    context['task_instance'].xcom_push(key='health_check_completo', value=health_check_completo)
    
    logger.info(f"Health check consolidado - Estado general: {estado_general}")
    return health_check_completo

def generar_reporte_health_check(**context):
    """
    Generar reporte de health check
    """
    logger.info("Generando reporte de health check")
    
    # Obtener health check consolidado
    health_check = context['task_instance'].xcom_pull(task_ids='consolidar_health_check', key='health_check_completo')
    
    # Crear reporte
    reporte = f"""
    REPORTE DE HEALTH CHECK - {context['ds']} {context['ts']}
    ========================================================
    
    Estado General: {health_check['estado_general'].upper()}
    
    Resumen:
    - Total de servicios: {health_check['resumen']['total_servicios']}
    - Estados: {health_check['resumen']['conteo_estados']}
    
    Detalles por Servicio:
    """
    
    # Agregar detalles de cada servicio
    for servicio, datos in health_check['servicios'].items():
        if isinstance(datos, list):
            for item in datos:
                reporte += f"\n  {item['servicio']}: {item['estado']}"
                if 'alerta' in item:
                    reporte += f" - {item['alerta']}"
                if 'error' in item:
                    reporte += f" - Error: {item['error']}"
        else:
            reporte += f"\n  {datos['servicio']}: {datos['estado']}"
            if 'alerta' in datos:
                reporte += f" - {datos['alerta']}"
            if 'error' in datos:
                reporte += f" - Error: {datos['error']}"
    
    reporte += f"\n\nFecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Guardar reporte
    archivo_reporte = f'/tmp/health_check_{context["ds"]}_{context["ts"].replace(":", "-")}.txt'
    with open(archivo_reporte, 'w') as f:
        f.write(reporte)
    
    context['task_instance'].xcom_push(key='archivo_reporte', value=archivo_reporte)
    
    logger.info("Reporte de health check generado")
    return archivo_reporte

# Definir tareas
with TaskGroup("verificaciones", tooltip="Verificaciones de salud") as grupo_verificaciones:
    # Verificar base de datos
    verificar_bd = PythonOperator(
        task_id='verificar_bd',
        python_callable=verificar_base_datos,
        provide_context=True
    )
    
    # Verificar Redis
    verificar_redis = PythonOperator(
        task_id='verificar_redis',
        python_callable=verificar_redis,
        provide_context=True
    )
    
    # Verificar APIs externas
    verificar_apis = PythonOperator(
        task_id='verificar_apis',
        python_callable=verificar_apis_externas,
        provide_context=True
    )
    
    # Verificar recursos del sistema
    verificar_sistema = PythonOperator(
        task_id='verificar_sistema',
        python_callable=verificar_recursos_sistema,
        provide_context=True
    )

# Tarea de consolidación
consolidar_health_check = PythonOperator(
    task_id='consolidar_health_check',
    python_callable=consolidar_health_check,
    provide_context=True
)

# Tarea de reporte
generar_reporte = PythonOperator(
    task_id='generar_reporte',
    python_callable=generar_reporte_health_check,
    provide_context=True
)

# Tarea de notificación por email
notificar_critical = EmailOperator(
    task_id='notificar_critical',
    to=['ops-team@empresa.com', 'admin@empresa.com'],
    subject='ALERTA CRÍTICA - Health Check del Sistema',
    html_content="""
    <h2>🚨 ALERTA CRÍTICA - Health Check del Sistema</h2>
    <p>Se han detectado problemas críticos en el sistema.</p>
    <p>Fecha: {{ ds }} {{ ts }}</p>
    <p>Por favor, revisar inmediatamente el estado de los servicios.</p>
    """,
    trigger_rule='one_failed'
)

# Definir dependencias
grupo_verificaciones >> consolidar_health_check >> generar_reporte
consolidar_health_check >> notificar_critical
