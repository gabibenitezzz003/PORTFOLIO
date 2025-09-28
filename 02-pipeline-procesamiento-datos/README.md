# Pipeline de Procesamiento de Datos con Pandas

## 📋 Descripción

Sistema completo de procesamiento y análisis de datos empresariales desarrollado con **Pandas**, **NumPy** y **Matplotlib**. Implementa un pipeline ETL robusto con análisis estadístico avanzado, visualizaciones interactivas y reportes automatizados.

## 🏗️ Arquitectura del Pipeline

### Patrón Pipeline ETL
```
┌─────────────────────────────────────────────────────────────┐
│                    EXTRACT (Extracción)                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Fuentes CSV   │  │   APIs REST     │  │   Bases de  │  │
│  │   Excel, JSON   │  │   Web Scraping  │  │   Datos     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   TRANSFORM (Transformación)               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Limpieza de   │  │   Análisis      │  │   Feature   │  │
│  │   Datos         │  │   Estadístico   │  │   Engineering│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     LOAD (Carga)                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Base de Datos │  │   Archivos      │  │   Reportes  │  │
│  │   PostgreSQL    │  │   CSV, Excel    │  │   PDF, HTML │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Características

- **Pipeline ETL** modular y escalable
- **Análisis estadístico** avanzado con Pandas y NumPy
- **Visualizaciones interactivas** con Matplotlib y Seaborn
- **Limpieza de datos** automatizada
- **Feature Engineering** inteligente
- **Reportes automatizados** en PDF y HTML
- **Métricas de calidad** de datos
- **Validación de datos** robusta
- **Logging estructurado** del pipeline

## 🛠️ Tecnologías Utilizadas

- **Pandas** - Manipulación y análisis de datos
- **NumPy** - Cálculos numéricos y arrays
- **Matplotlib** - Visualizaciones básicas
- **Seaborn** - Visualizaciones estadísticas
- **Plotly** - Visualizaciones interactivas
- **Scikit-learn** - Machine learning y métricas
- **SQLAlchemy** - Conexión a base de datos
- **Jinja2** - Templates para reportes
- **Docker** - Containerización

## 📁 Estructura del Proyecto

```
02-pipeline-procesamiento-datos/
├── datos/                        # Datos de entrada y salida
│   ├── entrada/                  # Datos de entrada
│   ├── procesados/               # Datos procesados
│   └── reportes/                 # Reportes generados
├── pipeline/                     # Código del pipeline
│   ├── extractores/              # Extractores de datos
│   ├── transformadores/          # Transformadores de datos
│   ├── cargadores/               # Cargadores de datos
│   └── validadores/              # Validadores de datos
├── analisis/                     # Análisis de datos
│   ├── estadistico/              # Análisis estadístico
│   ├── visualizaciones/          # Generación de gráficos
│   └── reportes/                 # Generación de reportes
├── utilidades/                   # Utilidades compartidas
│   ├── decoradores/              # Decoradores personalizados
│   ├── helpers/                  # Funciones auxiliares
│   └── configuracion/            # Configuración
├── tests/                        # Tests automatizados
├── notebooks/                    # Jupyter notebooks
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
cd 02-pipeline-procesamiento-datos

# Levantar servicios con Docker Compose
docker-compose up -d

# Ejecutar pipeline
docker-compose exec pipeline python -m pipeline.ejecutor
```

### Opción 2: Instalación Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pipeline
python -m pipeline.ejecutor
```

## 📊 Funcionalidades del Pipeline

### 1. Extracción de Datos
- **CSV/Excel:** Lectura de archivos planos
- **APIs REST:** Extracción de datos de APIs
- **Base de Datos:** Consultas SQL complejas
- **Web Scraping:** Extracción de datos web

### 2. Transformación de Datos
- **Limpieza:** Manejo de valores nulos y outliers
- **Normalización:** Estandarización de formatos
- **Feature Engineering:** Creación de nuevas variables
- **Agregaciones:** Cálculos estadísticos

### 3. Análisis Estadístico
- **Estadísticas Descriptivas:** Media, mediana, desviación
- **Análisis de Correlación:** Matrices de correlación
- **Análisis de Tendencias:** Series temporales
- **Análisis de Distribución:** Histogramas y boxplots

### 4. Visualizaciones
- **Gráficos de Barras:** Comparaciones categóricas
- **Gráficos de Líneas:** Tendencias temporales
- **Scatter Plots:** Relaciones entre variables
- **Heatmaps:** Matrices de correlación
- **Dashboards Interactivos:** Visualizaciones dinámicas

### 5. Reportes Automatizados
- **Reportes PDF:** Documentos profesionales
- **Reportes HTML:** Visualizaciones web
- **Dashboards:** Paneles interactivos
- **Métricas de Calidad:** Indicadores de datos

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=pipeline --cov=analisis

# Ejecutar tests específicos
pytest tests/test_pipeline.py
```

## 📈 Métricas de Calidad

- **Cobertura de tests:** >90%
- **Tiempo de procesamiento:** <5 minutos para 1M registros
- **Precisión de datos:** >99.5%
- **Completitud de datos:** >95%
- **Consistencia de datos:** >98%

## 🔧 Configuración

### Variables de Entorno

```env
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/datos_empresa

# Configuración del pipeline
PIPELINE_BATCH_SIZE=10000
PIPELINE_MAX_WORKERS=4
PIPELINE_LOG_LEVEL=INFO

# Configuración de reportes
REPORT_OUTPUT_DIR=./datos/reportes
REPORT_FORMAT=pdf,html
```

## 📝 Ejemplos de Uso

### Análisis de Ventas
```python
from pipeline.ejecutor import EjecutorPipeline
from analisis.estadistico import AnalizadorVentas

# Crear ejecutor
ejecutor = EjecutorPipeline()

# Ejecutar análisis de ventas
resultado = ejecutor.ejecutar_analisis_ventas(
    archivo_datos="ventas_2024.csv",
    generar_reporte=True
)
```

### Análisis de Texto
```python
from analisis.texto import AnalizadorTexto

# Crear analizador
analizador = AnalizadorTexto()

# Analizar sentimientos
resultado = analizador.analizar_sentimientos(
    texto="Este producto es excelente",
    idioma="es"
)
```

## 🚀 Despliegue

### Docker Hub
```bash
# Construir imagen
docker build -t pipeline-procesamiento-datos .

# Subir a Docker Hub
docker tag pipeline-procesamiento-datos username/pipeline-procesamiento-datos
docker push username/pipeline-procesamiento-datos
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
