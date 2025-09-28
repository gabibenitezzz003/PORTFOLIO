# Guía de Instalación - Portfolio Gabriel

## 📋 Requisitos Previos

### Software Necesario
- **Docker** (versión 20.10 o superior)
- **Docker Compose** (versión 2.0 o superior)
- **Git** (para clonar el repositorio)
- **Curl** (para health checks)

### Recursos del Sistema
- **RAM:** Mínimo 8GB, recomendado 16GB
- **CPU:** Mínimo 4 cores, recomendado 8 cores
- **Disco:** Mínimo 20GB de espacio libre
- **Sistema Operativo:** Linux, macOS, o Windows con WSL2

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd PORTFOLIO
```

### 2. Ejecutar Script de Inicio
```bash
# Dar permisos de ejecución
chmod +x scripts/*.sh

# Iniciar todo el portfolio
./scripts/start-portfolio.sh
```

### 3. Verificar Instalación
```bash
# Health check completo
./scripts/health-check.sh

# Ver estado de servicios
docker-compose ps
```

## 🔧 Instalación Manual

### 1. Preparar Entorno
```bash
# Crear directorios necesarios
mkdir -p monitoring/prometheus/rules
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources
mkdir -p nginx/ssl
mkdir -p logs

# Dar permisos
chmod +x scripts/*.sh
```

### 2. Iniciar Servicios
```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f api-proyecto1
```

### 3. Verificar Servicios
```bash
# Verificar APIs
curl http://localhost:8001/health  # Proyecto 1
curl http://localhost:8003/health  # Proyecto 3
curl http://localhost:8080/health  # Airflow
curl http://localhost:8005/health  # Proyecto 5

# Verificar servicios de soporte
curl http://localhost:5000/health  # MLflow
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:9090/-/healthy  # Prometheus
```

## 📊 Acceso a Servicios

### URLs Principales
- **Página Principal:** http://localhost
- **Proyecto 1 (API Gestión):** http://localhost:8001
- **Proyecto 3 (API NLP):** http://localhost:8003
- **Proyecto 4 (Airflow):** http://localhost:8080
- **Proyecto 5 (Recomendaciones):** http://localhost:8005

### Servicios de Soporte
- **MLflow:** http://localhost:5000
- **Grafana:** http://localhost:3000 (admin/admin123)
- **Prometheus:** http://localhost:9090

### Documentación API
- **Proyecto 1:** http://localhost:8001/docs
- **Proyecto 3:** http://localhost:8003/docs
- **Proyecto 5:** http://localhost:8005/docs

## 🛠️ Comandos Útiles

### Gestión de Servicios
```bash
# Iniciar servicios
docker-compose up -d

# Parar servicios
docker-compose down

# Reiniciar un servicio
docker-compose restart api-proyecto1

# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f [servicio]

# Ejecutar comando en contenedor
docker-compose exec api-proyecto1 bash
```

### Limpieza
```bash
# Parar y eliminar contenedores
docker-compose down

# Eliminar volúmenes (¡CUIDADO! Elimina datos)
docker-compose down -v

# Limpiar imágenes no utilizadas
docker system prune -a

# Limpiar todo (contenedores, imágenes, volúmenes)
docker system prune -a --volumes
```

### Monitoreo
```bash
# Health check completo
./scripts/health-check.sh

# Ver uso de recursos
docker stats

# Ver logs de todos los servicios
docker-compose logs --tail=100
```

## 🔍 Solución de Problemas

### Problemas Comunes

#### 1. Puerto ya en uso
```bash
# Ver qué proceso usa el puerto
lsof -i :8001

# Matar proceso
kill -9 <PID>

# O cambiar puerto en docker-compose.yml
```

#### 2. Servicio no inicia
```bash
# Ver logs del servicio
docker-compose logs api-proyecto1

# Reiniciar servicio
docker-compose restart api-proyecto1

# Reconstruir imagen
docker-compose build api-proyecto1
```

#### 3. Base de datos no conecta
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres-proyecto1

# Ver logs de PostgreSQL
docker-compose logs postgres-proyecto1

# Reiniciar base de datos
docker-compose restart postgres-proyecto1
```

#### 4. Memoria insuficiente
```bash
# Ver uso de memoria
docker stats

# Limpiar contenedores no utilizados
docker system prune

# Aumentar memoria en Docker Desktop
```

### Logs Importantes
```bash
# Logs de aplicación
docker-compose logs api-proyecto1
docker-compose logs api-nlp-proyecto3
docker-compose logs api-recomendaciones-proyecto5

# Logs de base de datos
docker-compose logs postgres-proyecto1
docker-compose logs postgres-proyecto3

# Logs de Airflow
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler

# Logs de Nginx
docker-compose logs nginx
```

## 📈 Monitoreo y Métricas

### Prometheus
- **URL:** http://localhost:9090
- **Métricas:** CPU, memoria, requests, latencia
- **Alertas:** Configuradas automáticamente

### Grafana
- **URL:** http://localhost:3000
- **Usuario:** admin
- **Contraseña:** admin123
- **Dashboards:** Portfolio Overview, APIs, Bases de Datos

### MLflow
- **URL:** http://localhost:5000
- **Experimentos:** Modelos de ML, métricas, artefactos
- **Tracking:** Experimentos de recomendaciones

## 🔒 Seguridad

### Configuración de Producción
1. **Cambiar contraseñas por defecto**
2. **Configurar SSL/TLS**
3. **Restringir acceso a puertos**
4. **Configurar firewall**
5. **Usar secrets de Docker**

### Variables de Entorno
```bash
# Crear archivo .env
cat > .env << EOF
POSTGRES_PASSWORD=tu_password_seguro
REDIS_PASSWORD=tu_redis_password
API_SECRET_KEY=tu_secret_key_muy_largo
EOF
```

## 📚 Documentación Adicional

### Proyectos Individuales
- **Proyecto 1:** Ver `01-sistema-gestion-datos/README.md`
- **Proyecto 2:** Ver `02-pipeline-procesamiento-datos/README.md`
- **Proyecto 3:** Ver `03-sistema-nlp-sentimientos/README.md`
- **Proyecto 4:** Ver `04-orquestacion-airflow/README.md`
- **Proyecto 5:** Ver `05-sistema-recomendaciones-ml/README.md`

### Arquitectura
- **Hexagonal Architecture:** Implementada en todos los proyectos
- **Clean Code:** Principios SOLID aplicados
- **Docker:** Containerización completa
- **Microservicios:** Servicios independientes

## 🆘 Soporte

### Contacto
- **Desarrollador:** Gabriel
- **Email:** [tu-email@ejemplo.com]
- **LinkedIn:** [tu-linkedin]

### Recursos
- **Repositorio:** [url-del-repo]
- **Documentación:** [url-docs]
- **Issues:** [url-issues]

---
