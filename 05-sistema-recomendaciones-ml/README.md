# Sistema de Recomendaciones con Machine Learning

## 📋 Descripción

Sistema completo de recomendaciones desarrollado con **scikit-learn**, **TensorFlow**, **Pandas** y **FastAPI**. Implementa múltiples algoritmos de recomendación (colaborativo, contenido, híbrido), análisis de comportamiento de usuarios, evaluación de modelos y APIs REST para integración en tiempo real.

## 🏗️ Arquitectura del Sistema

### Arquitectura de Sistema de Recomendaciones
```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   API REST      │  │   Dashboard     │  │   Web App   │  │
│  │   (FastAPI)     │  │   (Streamlit)   │  │   (React)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Servicios     │  │   Casos de Uso  │  │   DTOs      │  │
│  │   de ML         │  │   de Recomend.  │  │   (Pydantic)│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DOMINIO                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Algoritmos    │  │   Modelos       │  │   Métricas  │  │
│  │   de ML         │  │   de Datos      │  │   de Eval.  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE INFRAESTRUCTURA                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Base de Datos │  │   Almacenamiento│  │   Caché     │  │
│  │   (PostgreSQL)  │  │   (S3/MinIO)    │  │   (Redis)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Características

- **Múltiples Algoritmos** de recomendación (colaborativo, contenido, híbrido)
- **Análisis de Comportamiento** de usuarios en tiempo real
- **Evaluación Automática** de modelos con métricas avanzadas
- **APIs REST** para integración en tiempo real
- **Dashboard Interactivo** para análisis y monitoreo
- **Escalabilidad Horizontal** con microservicios
- **Caché Inteligente** para optimización de rendimiento
- **A/B Testing** para comparación de algoritmos
- **Personalización** basada en perfil de usuario
- **Recomendaciones Explicables** con justificación

## 🛠️ Tecnologías Utilizadas

- **scikit-learn** - Algoritmos de machine learning
- **TensorFlow/Keras** - Redes neuronales profundas
- **Pandas/NumPy** - Procesamiento de datos
- **FastAPI** - API REST de alto rendimiento
- **PostgreSQL** - Base de datos principal
- **Redis** - Caché y sesiones
- **MLflow** - Gestión de experimentos
- **Streamlit** - Dashboard interactivo
- **Docker** - Containerización
- **Prometheus** - Métricas y monitoreo

## 📁 Estructura del Proyecto

```
05-sistema-recomendaciones-ml/
├── aplicacion/                    # Capa de Aplicación
│   ├── servicios/                # Servicios de recomendaciones
│   ├── casos_uso/                # Casos de uso de ML
│   └── dto/                      # Data Transfer Objects
├── dominio/                       # Capa de Dominio
│   ├── algoritmos/               # Algoritmos de recomendación
│   ├── modelos/                  # Modelos de datos
│   └── metricas/                 # Métricas de evaluación
├── infraestructura/              # Capa de Infraestructura
│   ├── base_datos/               # Configuración de BD
│   ├── almacenamiento/           # Almacenamiento de modelos
│   └── caché/                    # Configuración de Redis
├── presentacion/                 # Capa de Presentación
│   ├── api/                      # API REST
│   ├── dashboard/                # Dashboard Streamlit
│   └── web/                      # Aplicación web
├── modelos/                      # Modelos entrenados
│   ├── colaborativo/             # Modelos colaborativos
│   ├── contenido/                # Modelos de contenido
│   └── hibrido/                  # Modelos híbridos
├── datos/                        # Datos de entrenamiento
│   ├── raw/                      # Datos crudos
│   ├── processed/                # Datos procesados
│   └── features/                 # Características extraídas
├── tests/                        # Tests automatizados
├── scripts/                      # Scripts de utilidad
├── requirements.txt              # Dependencias
├── Dockerfile                    # Imagen Docker
├── docker-compose.yml            # Orquestación
└── README.md                     # Documentación
```

## 🚀 Instalación y Uso

### Opción 1: Con Docker (Recomendado)

```bash
# Clonar el repositorio
git clone <repo-url>
cd 05-sistema-recomendaciones-ml

# Levantar servicios con Docker Compose
docker-compose up -d

# La API estará disponible en http://localhost:8000
# Dashboard en http://localhost:8501
```

### Opción 2: Instalación Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
python scripts/init-db.py

# Iniciar servicios
python -m presentacion.api.aplicacion
```

## 📊 Funcionalidades del Sistema

### 1. Algoritmos de Recomendación

#### Filtrado Colaborativo
- **User-Based:** Recomendaciones basadas en usuarios similares
- **Item-Based:** Recomendaciones basadas en items similares
- **Matrix Factorization:** Descomposición de matrices (SVD, NMF)
- **Deep Learning:** Redes neuronales para embeddings

#### Filtrado por Contenido
- **TF-IDF:** Análisis de contenido textual
- **Word2Vec:** Embeddings de palabras
- **Categorización:** Recomendaciones por categorías
- **Características:** Recomendaciones por atributos

#### Filtrado Híbrido
- **Weighted Hybrid:** Combinación ponderada de algoritmos
- **Switching Hybrid:** Selección dinámica de algoritmos
- **Mixed Hybrid:** Combinación de resultados
- **Feature Combination:** Fusión de características

### 2. Análisis de Comportamiento
- **Sesiones de Usuario:** Análisis de patrones de navegación
- **Interacciones:** Clicks, vistas, compras, ratings
- **Temporal:** Análisis de tendencias temporales
- **Contextual:** Recomendaciones basadas en contexto

### 3. Evaluación de Modelos
- **Métricas Offline:** RMSE, MAE, Precision@K, Recall@K
- **Métricas Online:** CTR, Conversion Rate, Engagement
- **A/B Testing:** Comparación de algoritmos
- **Cross-Validation:** Validación cruzada temporal

### 4. Personalización
- **Perfil de Usuario:** Características demográficas y de comportamiento
- **Preferencias:** Aprendizaje de preferencias implícitas
- **Contexto:** Recomendaciones contextuales
- **Feedback:** Aprendizaje de feedback explícito

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=aplicacion --cov=dominio --cov=infraestructura

# Tests específicos
pytest tests/test_algoritmos.py
pytest tests/test_servicios.py
pytest tests/test_api.py
```

## 📈 Métricas de Calidad

- **Precisión Offline:** >85%
- **Recall Offline:** >80%
- **Tiempo de Respuesta:** <100ms promedio
- **Throughput:** >1000 req/s
- **Disponibilidad:** >99.9%
- **Cobertura de Items:** >90%

## 🔧 Configuración

### Variables de Entorno

```env
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/recomendaciones

# Redis
REDIS_URL=redis://localhost:6379/0

# Almacenamiento
STORAGE_TYPE=s3
S3_BUCKET=recomendaciones-models
S3_REGION=us-east-1

# Modelos
DEFAULT_ALGORITHM=hybrid
COLLABORATIVE_WEIGHT=0.6
CONTENT_WEIGHT=0.4

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Caché
CACHE_TTL=3600
CACHE_MAX_ITEMS=10000
```

## 📝 Ejemplos de Uso

### API REST
```bash
# Obtener recomendaciones para un usuario
curl -X POST "http://localhost:8000/api/v1/recomendaciones/usuario/123" \
  -H "Content-Type: application/json" \
  -d '{"limit": 10, "algoritmo": "hybrid"}'

# Obtener recomendaciones para un item
curl -X POST "http://localhost:8000/api/v1/recomendaciones/item/456" \
  -H "Content-Type: application/json" \
  -d '{"limit": 5, "algoritmo": "content"}'

# Evaluar modelo
curl -X POST "http://localhost:8000/api/v1/modelos/evaluar" \
  -H "Content-Type: application/json" \
  -d '{"algoritmo": "collaborative", "metricas": ["rmse", "mae", "precision@10"]}'
```

### Python SDK
```python
from sistema_recomendaciones import RecomendacionesClient

# Inicializar cliente
client = RecomendacionesClient(api_url="http://localhost:8000")

# Obtener recomendaciones
recomendaciones = client.obtener_recomendaciones_usuario(
    usuario_id=123,
    limit=10,
    algoritmo="hybrid"
)

# Evaluar modelo
metricas = client.evaluar_modelo(
    algoritmo="collaborative",
    metricas=["rmse", "mae", "precision@10"]
)
```

## 🚀 Despliegue

### Docker Hub
```bash
# Construir imagen
docker build -t sistema-recomendaciones-ml .

# Subir a Docker Hub
docker tag sistema-recomendaciones-ml username/sistema-recomendaciones-ml
docker push username/sistema-recomendaciones-ml
```

### Kubernetes
```bash
# Aplicar configuración
kubectl apply -f k8s/

# Escalar servicios
kubectl scale deployment recomendaciones-api --replicas=5
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/RecomendacionIncreible`)
3. Commit cambios (`git commit -m 'Agregar RecomendacionIncreible'`)
4. Push a la rama (`git push origin feature/RecomendacionIncreible`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---
