# Dockerfile para Pipeline de Procesamiento de Datos
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
RUN mkdir -p /app/datos/entrada /app/datos/procesados /app/datos/reportes /app/graficos /app/logs
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

# Comando por defecto
CMD ["python", "-m", "pipeline.ejecutor"]
