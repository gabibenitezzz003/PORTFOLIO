#!/bin/bash

# Script para iniciar el Portfolio Completo
# Portfolio de Gabriel para GreenCode Software

echo "🚀 Iniciando Portfolio Completo - Gabriel"
echo "=========================================="

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar que Docker Compose esté instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p monitoring/prometheus/rules
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources
mkdir -p nginx/ssl
mkdir -p logs

# Dar permisos de ejecución
chmod +x scripts/*.sh

echo "🐳 Iniciando servicios con Docker Compose..."

# Iniciar servicios
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 30

# Verificar estado de los servicios
echo "🔍 Verificando estado de los servicios..."

# Función para verificar servicio
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name está funcionando"
            return 0
        fi
        echo "⏳ Esperando $service_name... (intento $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    echo "❌ $service_name no está respondiendo después de $max_attempts intentos"
    return 1
}

# Verificar servicios principales
check_service "API Proyecto 1" "http://localhost:8001/health"
check_service "API NLP Proyecto 3" "http://localhost:8003/health"
check_service "Airflow" "http://localhost:8080/health"
check_service "API Recomendaciones Proyecto 5" "http://localhost:8005/health"
check_service "MLflow" "http://localhost:5000/health"
check_service "Grafana" "http://localhost:3000/api/health"
check_service "Prometheus" "http://localhost:9090/-/healthy"

echo ""
echo "🎉 Portfolio iniciado exitosamente!"
echo ""
echo "📊 Servicios disponibles:"
echo "  • Página Principal: http://localhost"
echo "  • Proyecto 1 (API Gestión): http://localhost:8001"
echo "  • Proyecto 3 (API NLP): http://localhost:8003"
echo "  • Proyecto 4 (Airflow): http://localhost:8080"
echo "  • Proyecto 5 (Recomendaciones): http://localhost:8005"
echo "  • MLflow: http://localhost:5000"
echo "  • Grafana: http://localhost:3000 (admin/admin123)"
echo "  • Prometheus: http://localhost:9090"
echo ""
echo "🔧 Comandos útiles:"
echo "  • Ver logs: docker-compose logs -f [servicio]"
echo "  • Parar servicios: docker-compose down"
echo "  • Reiniciar: docker-compose restart [servicio]"
echo "  • Estado: docker-compose ps"
echo ""
echo "📚 Documentación:"
echo "  • Proyecto 1: http://localhost:8001/docs"
echo "  • Proyecto 3: http://localhost:8003/docs"
echo "  • Proyecto 5: http://localhost:8005/docs"
echo ""
echo "¡Portfolio listo para presentar en GreenCode Software! 🚀"
