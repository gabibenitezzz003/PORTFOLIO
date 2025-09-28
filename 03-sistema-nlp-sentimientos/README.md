# Sistema de NLP con spaCy para Análisis de Sentimientos

## 📋 Descripción

Sistema completo de procesamiento de lenguaje natural (NLP) desarrollado con **spaCy**, **NLTK** y **scikit-learn**. Implementa análisis de sentimientos multilingüe, extracción de entidades, análisis de texto en tiempo real y APIs REST para integración.

## 🏗️ Arquitectura del Sistema

### Arquitectura de Microservicios NLP
```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   API REST      │  │   WebSocket     │  │   Dashboard  │  │
│  │   (FastAPI)     │  │   (Tiempo Real) │  │   (Streamlit)│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Servicios     │  │   Casos de Uso  │  │   DTOs      │  │
│  │   de NLP        │  │   de Análisis   │  │   (Pydantic)│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DOMINIO                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Modelos       │  │   Algoritmos    │  │   Entidades │  │
│  │   de Texto      │  │   de NLP        │  │   de Dominio│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE INFRAESTRUCTURA                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Modelos       │  │   Base de Datos │  │   Caché     │  │
│  │   Pre-entrenados│  │   (PostgreSQL)  │  │   (Redis)   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Características

- **Análisis de Sentimientos** multilingüe (español, inglés, francés, alemán)
- **Extracción de Entidades** (personas, organizaciones, lugares, fechas)
- **Análisis de Texto** en tiempo real con WebSockets
- **Clasificación de Texto** automática por categorías
- **Resumen Automático** de documentos largos
- **Detección de Lenguaje** automática
- **API REST** completa con documentación automática
- **Dashboard Interactivo** con Streamlit
- **Caché Inteligente** para optimización de rendimiento
- **Métricas de Calidad** del análisis

## 🛠️ Tecnologías Utilizadas

- **spaCy** - Procesamiento de lenguaje natural
- **NLTK** - Herramientas de texto y corpus
- **scikit-learn** - Machine learning y clasificación
- **TextBlob** - Análisis de sentimientos simple
- **Transformers** - Modelos pre-entrenados (BERT, RoBERTa)
- **FastAPI** - API REST de alto rendimiento
- **WebSockets** - Comunicación en tiempo real
- **Streamlit** - Dashboard interactivo
- **PostgreSQL** - Base de datos para almacenamiento
- **Redis** - Caché y sesiones
- **Docker** - Containerización

## 📁 Estructura del Proyecto

```
03-sistema-nlp-sentimientos/
├── aplicacion/                    # Capa de Aplicación
│   ├── servicios/                # Servicios de NLP
│   ├── casos_uso/                # Casos de uso de análisis
│   └── dto/                      # Data Transfer Objects
├── dominio/                       # Capa de Dominio
│   ├── modelos/                  # Modelos de texto
│   ├── algoritmos/               # Algoritmos de NLP
│   └── entidades/                # Entidades de dominio
├── infraestructura/              # Capa de Infraestructura
│   ├── modelos/                  # Modelos pre-entrenados
│   ├── base_datos/               # Configuración de BD
│   └── caché/                    # Configuración de Redis
├── presentacion/                 # Capa de Presentación
│   ├── api/                      # API REST
│   ├── websocket/                # WebSocket handlers
│   └── dashboard/                # Dashboard Streamlit
├── utilidades/                   # Utilidades compartidas
│   ├── decoradores/              # Decoradores personalizados
│   ├── helpers/                  # Funciones auxiliares
│   └── configuracion/            # Configuración
├── tests/                        # Tests automatizados
├── modelos/                      # Modelos de ML entrenados
├── datos/                        # Datos de entrenamiento
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
cd 03-sistema-nlp-sentimientos

# Descargar modelos de spaCy
python -m spacy download es_core_news_sm
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
python -m spacy download de_core_news_sm

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

# Descargar modelos de spaCy
python -m spacy download es_core_news_sm
python -m spacy download en_core_web_sm

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Iniciar servicios
python -m presentacion.api.aplicacion
```

## 📊 Funcionalidades del Sistema

### 1. Análisis de Sentimientos
- **Multilingüe:** Español, inglés, francés, alemán
- **Modelos:** VADER, TextBlob, BERT, RoBERTa
- **Escalas:** Polaridad (-1 a 1), Subjetividad (0 a 1)
- **Categorías:** Positivo, Negativo, Neutral

### 2. Extracción de Entidades
- **Personas:** Nombres de personas
- **Organizaciones:** Empresas, instituciones
- **Lugares:** Ciudades, países, direcciones
- **Fechas:** Fechas absolutas y relativas
- **Dinero:** Cantidades monetarias
- **Porcentajes:** Valores porcentuales

### 3. Análisis de Texto
- **Tokenización:** División en palabras y oraciones
- **Lematización:** Formas canónicas de palabras
- **Etiquetado POS:** Partes del discurso
- **Análisis de Dependencias:** Relaciones sintácticas
- **Detección de Lenguaje:** Identificación automática

### 4. Clasificación de Texto
- **Categorías:** Noticias, opiniones, spam, etc.
- **Modelos:** Naive Bayes, SVM, Random Forest
- **Entrenamiento:** Datos personalizados
- **Evaluación:** Métricas de precisión y recall

### 5. Resumen Automático
- **Extractivo:** Selección de oraciones importantes
- **Abstractivo:** Generación de resúmenes nuevos
- **Longitud:** Configurable (1-10 oraciones)
- **Idiomas:** Múltiples idiomas soportados

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=aplicacion --cov=dominio --cov=infraestructura

# Ejecutar tests específicos
pytest tests/test_analisis_sentimientos.py
```

## 📈 Métricas de Calidad

- **Precisión de Sentimientos:** >85%
- **Precisión de Entidades:** >90%
- **Tiempo de Respuesta:** <500ms promedio
- **Disponibilidad:** >99.5%
- **Cobertura de Tests:** >90%

## 🔧 Configuración

### Variables de Entorno

```env
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/nlp_sentimientos

# Redis
REDIS_URL=redis://localhost:6379/0

# Modelos de spaCy
SPACY_MODELS=es_core_news_sm,en_core_web_sm

# Configuración de análisis
SENTIMENT_MODEL=bert
ENTITY_MODEL=spacy
CACHE_TTL=3600

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
```

## 📝 Ejemplos de Uso

### Análisis de Sentimientos
```python
from aplicacion.servicios.servicio_sentimientos import ServicioSentimientos

servicio = ServicioSentimientos()

# Análisis simple
resultado = await servicio.analizar_sentimiento(
    texto="Este producto es excelente, lo recomiendo totalmente",
    idioma="es"
)

print(f"Polaridad: {resultado.polaridad}")
print(f"Subjetividad: {resultado.subjetividad}")
print(f"Categoría: {resultado.categoria}")
```

### Extracción de Entidades
```python
from aplicacion.servicios.servicio_entidades import ServicioEntidades

servicio = ServicioEntidades()

# Extraer entidades
entidades = await servicio.extraer_entidades(
    texto="Apple Inc. fue fundada por Steve Jobs en Cupertino, California en 1976",
    idioma="es"
)

for entidad in entidades:
    print(f"{entidad.texto} - {entidad.tipo} - {entidad.confianza}")
```

### API REST
```bash
# Análisis de sentimientos
curl -X POST "http://localhost:8000/api/v1/sentimientos/analizar" \
  -H "Content-Type: application/json" \
  -d '{"texto": "Me encanta este producto", "idioma": "es"}'

# Extracción de entidades
curl -X POST "http://localhost:8000/api/v1/entidades/extraer" \
  -H "Content-Type: application/json" \
  -d '{"texto": "Microsoft fue fundada por Bill Gates", "idioma": "es"}'
```

## 🚀 Despliegue

### Docker Hub
```bash
# Construir imagen
docker build -t sistema-nlp-sentimientos .

# Subir a Docker Hub
docker tag sistema-nlp-sentimientos username/sistema-nlp-sentimientos
docker push username/sistema-nlp-sentimientos
```

### Producción
```bash
# Usar docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AnalisisIncreible`)
3. Commit cambios (`git commit -m 'Agregar AnalisisIncreible'`)
4. Push a la rama (`git push origin feature/AnalisisIncreible`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---
