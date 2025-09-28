# Orquestación de Workflows con Apache Airflow

## 📋 Descripción

Sistema completo de orquestación de workflows desarrollado con **Apache Airflow** para automatizar procesos de datos, ETL, análisis y machine learning. Implementa DAGs (Directed Acyclic Graphs) complejos, monitoreo en tiempo real, alertas inteligentes y escalabilidad horizontal.

## 🏗️ Arquitectura del Sistema

### Arquitectura de Orquestación Airflow
```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Web UI        │  │   API REST      │  │   CLI       │  │
│  │   (Monitoreo)   │  │   (Integración) │  │   (Admin)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE ORQUESTACIÓN                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Scheduler     │  │   Executor      │  │   DAGs      │  │
│  │   (Planificación)│  │   (Ejecución)   │  │   (Workflows)│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE TAREAS                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   ETL Tasks     │  │   ML Tasks      │  │   API Tasks │  │
│  │   (Datos)       │  │   (Modelos)     │  │   (Servicios)│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE INFRAESTRUCTURA                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Base de Datos │  │   Almacenamiento│  │   Servicios │  │
│  │   (PostgreSQL)  │  │   (S3/MinIO)    │  │   (Redis)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Características

- **DAGs Complejos** con dependencias y paralelización
- **Monitoreo en Tiempo Real** con métricas y alertas
- **Escalabilidad Horizontal** con múltiples workers
- **Integración Completa** con APIs, bases de datos y servicios
- **Retry Inteligente** con backoff exponencial
- **Alertas Automáticas** por email, Slack y webhooks
- **Scheduling Avanzado** con cron y triggers
- **Logging Centralizado** con análisis de logs
- **Seguridad** con autenticación y autorización
- **Backup y Recovery** automático

## 🛠️ Tecnologías Utilizadas

- **Apache Airflow** - Orquestación de workflows
- **PostgreSQL** - Base de datos de metadatos
- **Redis** - Broker de mensajes y caché
- **Celery** - Ejecutor distribuido
- **Docker** - Containerización
- **Kubernetes** - Orquestación de contenedores (opcional)
- **Prometheus** - Métricas y monitoreo
- **Grafana** - Dashboards de visualización
- **Python** - Lenguaje principal
- **SQLAlchemy** - ORM para base de datos

## 📁 Estructura del Proyecto

```
04-orquestacion-airflow/
├── dags/                        # DAGs de Airflow
│   ├── etl/                    # DAGs de ETL
│   ├── ml/                     # DAGs de Machine Learning
│   ├── monitoreo/              # DAGs de monitoreo
│   └── utilidades/             # DAGs de utilidades
├── plugins/                     # Plugins personalizados
│   ├── operators/              # Operadores personalizados
│   ├── sensors/                # Sensores personalizados
│   ├── hooks/                  # Hooks personalizados
│   └── executors/              # Ejecutores personalizados
├── config/                     # Configuración
│   ├── airflow.cfg            # Configuración principal
│   ├── logging.conf           # Configuración de logs
│   └── webserver_config.py    # Configuración web
├── scripts/                    # Scripts de utilidad
│   ├── init-db.py             # Inicialización de BD
│   ├── backup.py              # Backup de datos
│   └── monitoring.py          # Scripts de monitoreo
├── tests/                      # Tests automatizados
│   ├── unit/                  # Tests unitarios
│   ├── integration/           # Tests de integración
│   └── e2e/                   # Tests end-to-end
├── monitoring/                 # Configuración de monitoreo
│   ├── prometheus/            # Configuración Prometheus
│   ├── grafana/               # Dashboards Grafana
│   └── alerts/                # Reglas de alertas
├── docker/                     # Configuración Docker
│   ├── Dockerfile.airflow     # Imagen Airflow
│   ├── Dockerfile.worker      # Imagen Worker
│   └── docker-compose.yml     # Orquestación
├── k8s/                       # Configuración Kubernetes
│   ├── namespace.yaml         # Namespace
│   ├── configmap.yaml         # ConfigMap
│   ├── secrets.yaml           # Secrets
│   └── deployments/           # Deployments
├── requirements.txt            # Dependencias
├── airflow.cfg                # Configuración Airflow
└── README.md                  # Documentación
```

## 🚀 Instalación y Uso

### Opción 1: Con Docker Compose (Recomendado)

```bash
# Clonar el repositorio
git clone <repo-url>
cd 04-orquestacion-airflow

# Levantar servicios con Docker Compose
docker-compose up -d

# Verificar estado
docker-compose ps

# Acceder a la interfaz web
# http://localhost:8080 (admin/admin)
```

### Opción 2: Instalación Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos
airflow db init

# Crear usuario administrador
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Iniciar servicios
airflow webserver --port 8080 &
airflow scheduler &
```

### Opción 3: Con Kubernetes

```bash
# Aplicar configuración de Kubernetes
kubectl apply -f k8s/

# Verificar pods
kubectl get pods -n airflow

# Acceder a la interfaz web
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow
```

## 📊 Funcionalidades del Sistema

### 1. DAGs de ETL
- **Extracción de Datos** de múltiples fuentes
- **Transformación** con Pandas y SQL
- **Carga** a data warehouse
- **Validación** de calidad de datos
- **Monitoreo** de rendimiento

### 2. DAGs de Machine Learning
- **Entrenamiento** de modelos
- **Validación** y testing
- **Despliegue** de modelos
- **Monitoreo** de drift
- **Retraining** automático

### 3. DAGs de Monitoreo
- **Health Checks** de servicios
- **Métricas** de rendimiento
- **Alertas** automáticas
- **Reportes** de estado
- **Dashboards** en tiempo real

### 4. DAGs de Utilidades
- **Backup** de datos
- **Limpieza** de logs
- **Mantenimiento** de BD
- **Sincronización** de configuraciones
- **Auditoría** de seguridad

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests específicos
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Tests con cobertura
pytest --cov=dags --cov=plugins

# Tests de DAGs
python -m pytest tests/dag_tests.py
```

## 📈 Monitoreo y Alertas

### Métricas Disponibles
- **DAGs ejecutados** por día/hora
- **Tiempo de ejecución** promedio
- **Tasa de éxito/fallo** de tareas
- **Uso de recursos** (CPU, memoria)
- **Latencia** de tareas
- **Throughput** del sistema

### Alertas Configuradas
- **DAGs fallidos** por más de 1 hora
- **Tareas con error** repetido
- **Uso de recursos** alto
- **Conexiones** de BD perdidas
- **Espacio en disco** bajo

## 🔧 Configuración

### Variables de Entorno

```env
# Airflow
AIRFLOW_HOME=/opt/airflow
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://user:pass@localhost:5432/airflow
AIRFLOW__CELERY__BROKER_URL=redis://localhost:6379/0
AIRFLOW__CELERY__RESULT_BACKEND=redis://localhost:6379/0

# Base de datos
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow123
POSTGRES_DB=airflow

# Redis
REDIS_PASSWORD=redis123

# Monitoreo
PROMETHEUS_ENDPOINT=http://prometheus:9090
GRAFANA_ENDPOINT=http://grafana:3000
```

## 📝 Ejemplos de DAGs

### DAG de ETL Diario
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'etl_diario',
    default_args=default_args,
    description='ETL diario de datos de ventas',
    schedule_interval='0 2 * * *',  # Diario a las 2 AM
    catchup=False
)

def extraer_datos():
    # Lógica de extracción
    pass

def transformar_datos():
    # Lógica de transformación
    pass

def cargar_datos():
    # Lógica de carga
    pass

# Definir tareas
extraer = PythonOperator(
    task_id='extraer_datos',
    python_callable=extraer_datos,
    dag=dag
)

transformar = PythonOperator(
    task_id='transformar_datos',
    python_callable=transformar_datos,
    dag=dag
)

cargar = PythonOperator(
    task_id='cargar_datos',
    python_callable=cargar_datos,
    dag=dag
)

# Definir dependencias
extraer >> transformar >> cargar
```

### DAG de Machine Learning
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

dag = DAG(
    'ml_pipeline',
    default_args=default_args,
    description='Pipeline de Machine Learning',
    schedule_interval='0 3 * * 0',  # Semanal los domingos
    catchup=False
)

def entrenar_modelo():
    # Lógica de entrenamiento
    pass

def validar_modelo():
    # Lógica de validación
    pass

def desplegar_modelo():
    # Lógica de despliegue
    pass

# Tareas paralelas
entrenar = PythonOperator(
    task_id='entrenar_modelo',
    python_callable=entrenar_modelo,
    dag=dag
)

validar = PythonOperator(
    task_id='validar_modelo',
    python_callable=validar_modelo,
    dag=dag
)

desplegar = PythonOperator(
    task_id='desplegar_modelo',
    python_callable=desplegar_modelo,
    dag=dag
)

# Dependencias
entrenar >> validar >> desplegar
```

## 🚀 Despliegue

### Docker Hub
```bash
# Construir imagen
docker build -f docker/Dockerfile.airflow -t airflow-custom .

# Subir a Docker Hub
docker tag airflow-custom username/airflow-custom
docker push username/airflow-custom
```

### Kubernetes
```bash
# Aplicar configuración
kubectl apply -f k8s/

# Escalar workers
kubectl scale deployment airflow-worker --replicas=5 -n airflow

# Verificar estado
kubectl get all -n airflow
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/DAGIncreible`)
3. Commit cambios (`git commit -m 'Agregar DAGIncreible'`)
4. Push a la rama (`git push origin feature/DAGIncreible`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

