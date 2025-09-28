#!/bin/bash

# Script de inicialización del Portfolio Completo
# Inicializa todos los servicios de manera ordenada y verifica su estado

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Función para verificar si Docker está corriendo
verificar_docker() {
    if ! docker info >/dev/null 2>&1; then
        error "Docker no está corriendo. Por favor inicia Docker Desktop."
        exit 1
    fi
    success "Docker está corriendo"
}

# Función para limpiar contenedores existentes
limpiar_contenedores() {
    log "Limpiando contenedores existentes..."
    docker-compose down --remove-orphans || true
    success "Contenedores limpiados"
}

# Función para construir imágenes
construir_imagenes() {
    log "Construyendo imágenes Docker..."
    docker-compose build --no-cache
    success "Imágenes construidas"
}

# Función para iniciar servicios base
iniciar_servicios_base() {
    log "Iniciando servicios base (bases de datos)..."
    docker-compose up -d postgres-proyecto1 postgres-proyecto3 postgres-proyecto5 postgres-airflow redis-proyecto1 redis-proyecto3 redis-proyecto5
    success "Servicios base iniciados"
}

# Función para esperar que las bases de datos estén listas
esperar_bases_datos() {
    log "Esperando que las bases de datos estén listas..."
    sleep 30
    success "Bases de datos listas"
}

# Función para iniciar servicios de aplicación
iniciar_servicios_aplicacion() {
    log "Iniciando servicios de aplicación..."
    docker-compose up -d api-proyecto1 api-nlp-proyecto3 api-recomendaciones-proyecto5
    success "Servicios de aplicación iniciados"
}

# Función para iniciar servicios de monitoreo
iniciar_servicios_monitoreo() {
    log "Iniciando servicios de monitoreo..."
    docker-compose up -d prometheus grafana mlflow
    success "Servicios de monitoreo iniciados"
}

# Función para iniciar Airflow
iniciar_airflow() {
    log "Iniciando Airflow..."
    docker-compose up -d airflow-webserver airflow-scheduler
    success "Airflow iniciado"
}

# Función para iniciar Nginx
iniciar_nginx() {
    log "Iniciando Nginx..."
    docker-compose up -d nginx
    success "Nginx iniciado"
}

# Función para verificar estado de servicios
verificar_servicios() {
    log "Verificando estado de servicios..."
    
    # Esperar un poco para que los servicios se estabilicen
    sleep 60
    
    # Verificar servicios principales
    servicios=(
        "api-proyecto1:8001"
        "api-nlp-proyecto3:8003"
        "api-recomendaciones-proyecto5:8005"
        "airflow-webserver:8080"
        "mlflow:5000"
        "grafana:3000"
        "prometheus:9090"
        "nginx:80"
    )
    
    for servicio in "${servicios[@]}"; do
        nombre=$(echo $servicio | cut -d: -f1)
        puerto=$(echo $servicio | cut -d: -f2)
        
        if docker-compose ps | grep -q "$nombre.*Up"; then
            success "$nombre está corriendo"
        else
            warning "$nombre no está corriendo correctamente"
        fi
    done
}

# Función para mostrar URLs de acceso
mostrar_urls() {
    echo ""
    echo "=========================================="
    echo "🚀 PORTFOLIO INICIADO EXITOSAMENTE"
    echo "=========================================="
    echo ""
    echo "📊 Servicios disponibles:"
    echo "  • Portfolio Principal: http://localhost"
    echo "  • Proyecto 1 (API): http://localhost/proyecto1/"
    echo "  • Proyecto 3 (NLP): http://localhost/proyecto3/"
    echo "  • Proyecto 5 (ML): http://localhost/proyecto5/"
    echo "  • Airflow: http://localhost/airflow/"
    echo "  • MLflow: http://localhost/mlflow/"
    echo "  • Grafana: http://localhost/grafana/"
    echo "  • Prometheus: http://localhost/prometheus/"
    echo ""
    echo "🔑 Credenciales:"
    echo "  • Airflow: admin / admin"
    echo "  • Grafana: admin / admin123"
    echo ""
    echo "📝 Para ver logs: docker-compose logs -f [servicio]"
    echo "🛑 Para detener: docker-compose down"
    echo ""
}

# Función principal
main() {
    echo "🚀 Iniciando Portfolio Completo de Gabriel"
    echo "=========================================="
    echo ""
    
    # Verificar Docker
    verificar_docker
    
    # Limpiar contenedores existentes
    limpiar_contenedores
    
    # Construir imágenes
    construir_imagenes
    
    # Iniciar servicios en orden
    iniciar_servicios_base
    esperar_bases_datos
    iniciar_servicios_aplicacion
    iniciar_servicios_monitoreo
    iniciar_airflow
    iniciar_nginx
    
    # Verificar servicios
    verificar_servicios
    
    # Mostrar URLs
    mostrar_urls
    
    success "¡Portfolio iniciado exitosamente!"
}

# Manejo de señales
trap 'echo ""; error "Script interrumpido"; exit 1' SIGINT SIGTERM

# Ejecutar función principal
main "$@"
