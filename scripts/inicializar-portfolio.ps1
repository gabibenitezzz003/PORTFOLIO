# Script de inicialización del Portfolio Completo para Windows
# Inicializa todos los servicios de manera ordenada y verifica su estado

param(
    [switch]$Limpiar,
    [switch]$SoloVerificar
)

# Función para logging
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    switch ($Level) {
        "ERROR" { Write-Host "[$timestamp] [ERROR] $Message" -ForegroundColor Red }
        "SUCCESS" { Write-Host "[$timestamp] [SUCCESS] $Message" -ForegroundColor Green }
        "WARNING" { Write-Host "[$timestamp] [WARNING] $Message" -ForegroundColor Yellow }
        default { Write-Host "[$timestamp] [INFO] $Message" -ForegroundColor Blue }
    }
}

# Función para verificar si Docker está corriendo
function Test-Docker {
    try {
        docker info | Out-Null
        Write-Log "Docker está corriendo" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Docker no está corriendo. Por favor inicia Docker Desktop." "ERROR"
        return $false
    }
}

# Función para limpiar contenedores existentes
function Clear-Containers {
    Write-Log "Limpiando contenedores existentes..."
    try {
        docker-compose down --remove-orphans
        Write-Log "Contenedores limpiados" "SUCCESS"
    }
    catch {
        Write-Log "Error limpiando contenedores: $($_.Exception.Message)" "WARNING"
    }
}

# Función para construir imágenes
function Build-Images {
    Write-Log "Construyendo imágenes Docker..."
    try {
        docker-compose build --no-cache
        Write-Log "Imágenes construidas" "SUCCESS"
    }
    catch {
        Write-Log "Error construyendo imágenes: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Función para iniciar servicios base
function Start-BaseServices {
    Write-Log "Iniciando servicios base (bases de datos)..."
    try {
        docker-compose up -d postgres-proyecto1 postgres-proyecto3 postgres-proyecto5 postgres-airflow redis-proyecto1 redis-proyecto3 redis-proyecto5
        Write-Log "Servicios base iniciados" "SUCCESS"
    }
    catch {
        Write-Log "Error iniciando servicios base: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Función para esperar que las bases de datos estén listas
function Wait-ForDatabases {
    Write-Log "Esperando que las bases de datos estén listas..."
    Start-Sleep -Seconds 30
    Write-Log "Bases de datos listas" "SUCCESS"
}

# Función para iniciar servicios de aplicación
function Start-ApplicationServices {
    Write-Log "Iniciando servicios de aplicación..."
    try {
        docker-compose up -d api-proyecto1 api-nlp-proyecto3 api-recomendaciones-proyecto5
        Write-Log "Servicios de aplicación iniciados" "SUCCESS"
    }
    catch {
        Write-Log "Error iniciando servicios de aplicación: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Función para iniciar servicios de monitoreo
function Start-MonitoringServices {
    Write-Log "Iniciando servicios de monitoreo..."
    try {
        docker-compose up -d prometheus grafana mlflow
        Write-Log "Servicios de monitoreo iniciados" "SUCCESS"
    }
    catch {
        Write-Log "Error iniciando servicios de monitoreo: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Función para iniciar Airflow
function Start-Airflow {
    Write-Log "Iniciando Airflow..."
    try {
        docker-compose up -d airflow-webserver airflow-scheduler
        Write-Log "Airflow iniciado" "SUCCESS"
    }
    catch {
        Write-Log "Error iniciando Airflow: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Función para iniciar Nginx
function Start-Nginx {
    Write-Log "Iniciando Nginx..."
    try {
        docker-compose up -d nginx
        Write-Log "Nginx iniciado" "SUCCESS"
    }
    catch {
        Write-Log "Error iniciando Nginx: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Función para verificar estado de servicios
function Test-Services {
    Write-Log "Verificando estado de servicios..."
    
    # Esperar un poco para que los servicios se estabilicen
    Start-Sleep -Seconds 60
    
    # Verificar servicios principales
    $servicios = @(
        "api-proyecto1",
        "api-nlp-proyecto3", 
        "api-recomendaciones-proyecto5",
        "airflow-webserver",
        "mlflow",
        "grafana",
        "prometheus",
        "nginx"
    )
    
    foreach ($servicio in $servicios) {
        try {
            $status = docker-compose ps --services --filter "status=running" | Select-String $servicio
            if ($status) {
                Write-Log "$servicio está corriendo" "SUCCESS"
            } else {
                Write-Log "$servicio no está corriendo correctamente" "WARNING"
            }
        }
        catch {
            Write-Log "Error verificando $servicio" "WARNING"
        }
    }
}

# Función para mostrar URLs de acceso
function Show-URLs {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "🚀 PORTFOLIO INICIADO EXITOSAMENTE" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 Servicios disponibles:" -ForegroundColor Yellow
    Write-Host "  • Portfolio Principal: http://localhost" -ForegroundColor White
    Write-Host ""
    Write-Host "🐍 Proyectos Python Backend:" -ForegroundColor Cyan
    Write-Host "  • Proyecto 1 (API): http://localhost/proyecto1/" -ForegroundColor White
    Write-Host "  • Proyecto 3 (NLP): http://localhost/proyecto3/" -ForegroundColor White
    Write-Host "  • Proyecto 5 (ML): http://localhost/proyecto5/" -ForegroundColor White
    Write-Host ""
    Write-Host "🏗️ Proyectos Arquitectura de Software:" -ForegroundColor Cyan
    Write-Host "  • Proyecto 6 (Java): http://localhost:8081/" -ForegroundColor White
    Write-Host "  • Proyecto 7 (Observabilidad): http://localhost:3000/" -ForegroundColor White
    Write-Host "  • Proyecto 8 (CI/CD): http://localhost:8080/" -ForegroundColor White
    Write-Host "  • Proyecto 9 (React): http://localhost:3001/" -ForegroundColor White
    Write-Host "  • Proyecto 10 (Kafka): http://localhost:8080/" -ForegroundColor White
    Write-Host "  • Proyecto 11 (Go): http://localhost:8082/" -ForegroundColor White
    Write-Host "  • Proyecto 12 (No-Code): http://localhost:5678/" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Servicios de Monitoreo:" -ForegroundColor Cyan
    Write-Host "  • Airflow: http://localhost/airflow/" -ForegroundColor White
    Write-Host "  • MLflow: http://localhost/mlflow/" -ForegroundColor White
    Write-Host "  • Grafana: http://localhost/grafana/" -ForegroundColor White
    Write-Host "  • Prometheus: http://localhost/prometheus/" -ForegroundColor White
    Write-Host ""
    Write-Host "🔑 Credenciales:" -ForegroundColor Yellow
    Write-Host "  • Airflow: admin / admin" -ForegroundColor White
    Write-Host "  • Grafana: admin / admin123" -ForegroundColor White
    Write-Host ""
    Write-Host "📝 Para ver logs: docker-compose logs -f [servicio]" -ForegroundColor Cyan
    Write-Host "🛑 Para detener: docker-compose down" -ForegroundColor Cyan
    Write-Host ""
}

# Función principal
function Main {
    Write-Host "🚀 Iniciando Portfolio Completo de Gabriel" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    
    # Verificar Docker
    if (-not (Test-Docker)) {
        exit 1
    }
    
    # Solo verificar si se especifica
    if ($SoloVerificar) {
        Test-Services
        return
    }
    
    # Limpiar contenedores si se especifica
    if ($Limpiar) {
        Clear-Containers
    }
    
    # Construir imágenes
    Build-Images
    
    # Iniciar servicios en orden
    Start-BaseServices
    Wait-ForDatabases
    Start-ApplicationServices
    Start-MonitoringServices
    Start-Airflow
    Start-Nginx
    
    # Verificar servicios
    Test-Services
    
    # Mostrar URLs
    Show-URLs
    
    Write-Log "¡Portfolio iniciado exitosamente!" "SUCCESS"
}

# Ejecutar función principal
try {
    Main
}
catch {
    Write-Log "Error ejecutando script: $($_.Exception.Message)" "ERROR"
    exit 1
}
