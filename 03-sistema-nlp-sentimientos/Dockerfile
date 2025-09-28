# Dockerfile para Sistema NLP
# Multi-stage build para optimizar imagen

# Etapa 1: Build
FROM python:3.11-slim as builder

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa 2: Runtime
FROM python:3.11-slim

# Instalar dependencias del sistema para runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /home/appuser/.local

# Crear directorios necesarios
RUN mkdir -p /app/modelos /app/datos /app/logs
RUN chown -R appuser:appuser /app

# Copiar código de la aplicación
COPY . .

# Cambiar ownership al usuario appuser
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Agregar directorio de dependencias al PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=Agg

# Descargar modelos de spaCy (opcional)
RUN python -m spacy download es_core_news_sm || echo "Modelo español no disponible, continuando..."
RUN python -m spacy download en_core_web_sm || echo "Modelo inglés no disponible, continuando..."
RUN python -m spacy download fr_core_news_sm || echo "Modelo francés no disponible, continuando..."
RUN python -m spacy download de_core_news_sm || echo "Modelo alemán no disponible, continuando..."

# Comando por defecto
CMD ["python", "-m", "presentacion.api.aplicacion"]
