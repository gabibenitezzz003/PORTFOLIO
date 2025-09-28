#!/bin/bash

# Script de Health Check para Portfolio Completo
# Portfolio de Gabriel para GreenCode Software

echo "🔍 Health Check - Portfolio Completo"
echo "===================================="

# Función para verificar servicio
check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Verificando $service_name... "
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" = "$expected_status" ]; then
            echo "✅ OK ($response)"
            return 0
        else
            echo "❌ ERROR (HTTP $response)"
            return 1
        fi
    else
        echo "❌ ERROR (No disponible)"
        return 1
    fi
}

# Función para verificar base de datos
check_database() {
    local service_name=$1
    local host=$2
    local port=$3
    local database=$4
    
    echo -n "Verificando $service_name... "
    
    if nc -z "$host" "$port" 2>/dev/null; then
        echo "✅ OK (Puerto $port abierto)"
        return 0
    else
        echo "❌ ERROR (Puerto $port cerrado)"
        return 1
    fi
}

echo ""
echo "🌐 Verificando APIs REST..."

# Verificar APIs
check_service "API Proyecto 1" "http://localhost:8001/health"
check_service "API NLP Proyecto 3" "http://localhost:8003/health"
check_service "Airflow Web UI" "http://localhost:8080/health"
check_service "API Recomendaciones Proyecto 5" "http://localhost:8005/health"

echo ""
echo "🔧 Verificando servicios de soporte..."

# Verificar servicios de soporte
check_service "MLflow" "http://localhost:5000/health"
check_service "Grafana" "http://localhost:3000/api/health"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Nginx" "http://localhost/health"

echo ""
echo "🗄️ Verificando bases de datos..."

# Verificar bases de datos
check_database "PostgreSQL Proyecto 1" "localhost" "5432" "sistema_gestion_datos"
check_database "PostgreSQL Proyecto 3" "localhost" "5433" "sistema_nlp"
check_database "PostgreSQL Airflow" "localhost" "5434" "airflow"
check_database "PostgreSQL Proyecto 5" "localhost" "5435" "recomendaciones"

echo ""
echo "🔄 Verificando Redis..."

# Verificar Redis
check_database "Redis Proyecto 3" "localhost" "6380" ""
check_database "Redis Airflow" "localhost" "6381" ""
check_database "Redis Proyecto 5" "localhost" "6382" ""

echo ""
echo "🐳 Verificando contenedores Docker..."

# Verificar contenedores
echo "Contenedores en ejecución:"
docker-compose ps

echo ""
echo "📊 Resumen del Health Check:"
echo "============================"

# Contar servicios funcionando
total_services=0
working_services=0

# APIs
for url in "http://localhost:8001/health" "http://localhost:8003/health" "http://localhost:8080/health" "http://localhost:8005/health"; do
    ((total_services++))
    if curl -s -f "$url" > /dev/null 2>&1; then
        ((working_services++))
    fi
done

# Servicios de soporte
for url in "http://localhost:5000/health" "http://localhost:3000/api/health" "http://localhost:9090/-/healthy" "http://localhost/health"; do
    ((total_services++))
    if curl -s -f "$url" > /dev/null 2>&1; then
        ((working_services++))
    fi
done

# Bases de datos
for port in "5432" "5433" "5434" "5435"; do
    ((total_services++))
    if nc -z localhost "$port" 2>/dev/null; then
        ((working_services++))
    fi
done

# Redis
for port in "6380" "6381" "6382"; do
    ((total_services++))
    if nc -z localhost "$port" 2>/dev/null; then
        ((working_services++))
    fi
done

echo "Servicios funcionando: $working_services/$total_services"

if [ $working_services -eq $total_services ]; then
    echo "🎉 ¡Todos los servicios están funcionando correctamente!"
    exit 0
elif [ $working_services -gt $((total_services / 2)) ]; then
    echo "⚠️  La mayoría de servicios están funcionando, pero algunos tienen problemas."
    exit 1
else
    echo "❌ Muchos servicios no están funcionando. Revisa la configuración."
    exit 2
fi
