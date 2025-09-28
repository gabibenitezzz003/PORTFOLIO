#!/bin/bash

# Script de despliegue Blue-Green para Kubernetes
# Implementa estrategia de despliegue sin downtime

set -e

# Configuración
NAMESPACE="produccion"
APP_NAME="portfolio-app"
NEW_VERSION="$1"
CURRENT_VERSION=$(kubectl get deployment $APP_NAME -n $NAMESPACE -o jsonpath='{.spec.template.metadata.labels.version}' 2>/dev/null || echo "v1.0.0")

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

# Función para verificar si un deployment está listo
check_deployment_ready() {
    local deployment_name=$1
    local namespace=$2
    local timeout=${3:-300}
    
    log "Verificando que $deployment_name esté listo en namespace $namespace..."
    
    kubectl wait --for=condition=available --timeout=${timeout}s deployment/$deployment_name -n $namespace
}

# Función para verificar health check
check_health() {
    local service_name=$1
    local namespace=$2
    local port=${3:-80}
    local max_attempts=${4:-30}
    
    log "Verificando health check de $service_name..."
    
    for i in $(seq 1 $max_attempts); do
        if kubectl get service $service_name -n $namespace >/dev/null 2>&1; then
            local service_ip=$(kubectl get service $service_name -n $namespace -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
            if [ -n "$service_ip" ]; then
                if curl -f http://$service_ip:$port/health >/dev/null 2>&1; then
                    success "Health check exitoso para $service_name"
                    return 0
                fi
            fi
        fi
        log "Intento $i/$max_attempts - Esperando health check..."
        sleep 10
    done
    
    error "Health check falló para $service_name después de $max_attempts intentos"
    return 1
}

# Función para crear deployment verde
create_green_deployment() {
    local version=$1
    
    log "Creando deployment verde con versión $version..."
    
    # Aplicar deployment verde
    envsubst < k8s/produccion/deployment-green.yaml | kubectl apply -f -
    
    # Esperar a que esté listo
    check_deployment_ready "$APP_NAME-green" $NAMESPACE
    
    success "Deployment verde creado exitosamente"
}

# Función para cambiar tráfico a deployment verde
switch_traffic_to_green() {
    log "Cambiando tráfico a deployment verde..."
    
    # Actualizar service para apuntar a deployment verde
    kubectl patch service $APP_NAME -n $NAMESPACE -p '{"spec":{"selector":{"version":"'$NEW_VERSION'"}}}'
    
    # Verificar que el tráfico esté funcionando
    check_health $APP_NAME $NAMESPACE
    
    success "Tráfico cambiado exitosamente a deployment verde"
}

# Función para limpiar deployment azul
cleanup_blue_deployment() {
    log "Limpiando deployment azul..."
    
    # Eliminar deployment azul
    kubectl delete deployment $APP_NAME-blue -n $NAMESPACE --ignore-not-found=true
    
    success "Deployment azul eliminado"
}

# Función para rollback
rollback() {
    error "Iniciando rollback..."
    
    # Cambiar tráfico de vuelta a deployment azul
    kubectl patch service $APP_NAME -n $NAMESPACE -p '{"spec":{"selector":{"version":"'$CURRENT_VERSION'"}}}'
    
    # Verificar que el rollback funcione
    check_health $APP_NAME $NAMESPACE
    
    # Eliminar deployment verde
    kubectl delete deployment $APP_NAME-green -n $NAMESPACE --ignore-not-found=true
    
    success "Rollback completado"
    exit 1
}

# Función principal
main() {
    log "Iniciando despliegue Blue-Green para $APP_NAME"
    log "Versión actual: $CURRENT_VERSION"
    log "Nueva versión: $NEW_VERSION"
    
    # Verificar que kubectl esté configurado
    if ! kubectl cluster-info >/dev/null 2>&1; then
        error "kubectl no está configurado o no puede conectarse al cluster"
        exit 1
    fi
    
    # Verificar que el namespace existe
    if ! kubectl get namespace $NAMESPACE >/dev/null 2>&1; then
        error "Namespace $NAMESPACE no existe"
        exit 1
    fi
    
    # Crear deployment verde
    create_green_deployment $NEW_VERSION
    
    # Cambiar tráfico a deployment verde
    if switch_traffic_to_green; then
        # Esperar un poco para verificar estabilidad
        log "Esperando 60 segundos para verificar estabilidad..."
        sleep 60
        
        # Verificar que todo esté funcionando correctamente
        if check_health $APP_NAME $NAMESPACE; then
            success "Despliegue Blue-Green completado exitosamente"
            
            # Limpiar deployment azul
            cleanup_blue_deployment
            
            # Actualizar etiquetas del deployment principal
            kubectl label deployment $APP_NAME-green version=$NEW_VERSION -n $NAMESPACE
            kubectl patch deployment $APP_NAME-green -n $NAMESPACE -p '{"metadata":{"name":"'$APP_NAME'"}}'
            
            success "Despliegue completado. Nueva versión: $NEW_VERSION"
        else
            error "Health check falló después del switch de tráfico"
            rollback
        fi
    else
        error "No se pudo cambiar el tráfico a deployment verde"
        rollback
    fi
}

# Manejo de señales para rollback automático
trap rollback SIGINT SIGTERM

# Ejecutar función principal
main "$@"
