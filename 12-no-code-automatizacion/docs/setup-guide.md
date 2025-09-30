# 🚀 Guía de Configuración - No-Code Automation

## 📋 Prerrequisitos

### **Software Requerido**
- Docker Desktop 4.0+
- Docker Compose 2.0+
- Git
- Navegador web moderno

### **Cuentas Necesarias**
- **N8N:** Cuenta gratuita en n8n.io
- **Zapier:** Cuenta gratuita en zapier.com
- **Make.com:** Cuenta gratuita en make.com
- **APIs:** Keys de servicios a integrar

## 🔧 Instalación Paso a Paso

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/gabibenitezzz003/PORTFOLIO.git
cd PORTFOLIO/12-no-code-automatizacion
```

### **2. Configurar Variables de Entorno**
```bash
# Crear archivo .env
cp .env.example .env

# Editar variables
nano .env
```

### **3. Iniciar Servicios**
```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar estado
docker-compose ps
```

### **4. Acceder a las Interfaces**

#### **N8N (Principal)**
- **URL:** http://localhost:5678
- **Usuario:** admin
- **Contraseña:** admin123

#### **Webhook Testing**
- **URL:** http://localhost:8080
- **Uso:** Testing de webhooks

#### **Grafana (Monitoreo)**
- **URL:** http://localhost:3000
- **Usuario:** admin
- **Contraseña:** admin123

#### **Prometheus (Métricas)**
- **URL:** http://localhost:9090

## 🔑 Configuración de APIs

### **N8N Credentials**
1. Acceder a N8N
2. Ir a Settings > Credentials
3. Agregar credenciales para:
   - **HTTP Basic Auth**
   - **OAuth2**
   - **API Keys**
   - **Webhooks**

### **Zapier Integration**
1. Crear cuenta en Zapier
2. Obtener API key
3. Configurar webhook URLs
4. Importar workflows desde `workflows/zapier/`

### **Make.com Integration**
1. Crear cuenta en Make.com
2. Configurar conexiones
3. Importar scenarios desde `workflows/make/`

## 📊 Monitoreo y Métricas

### **Dashboard de Grafana**
1. Acceder a http://localhost:3000
2. Importar dashboards desde `monitoring/grafana/dashboards/`
3. Configurar datasources

### **Métricas de Prometheus**
1. Acceder a http://localhost:9090
2. Verificar targets
3. Explorar métricas

## 🚨 Troubleshooting

### **Problemas Comunes**

#### **N8N no inicia**
```bash
# Verificar logs
docker-compose logs n8n

# Reiniciar servicio
docker-compose restart n8n
```

#### **Base de datos no conecta**
```bash
# Verificar PostgreSQL
docker-compose logs postgres-n8n

# Reiniciar base de datos
docker-compose restart postgres-n8n
```

#### **Redis no responde**
```bash
# Verificar Redis
docker-compose logs redis-n8n

# Reiniciar Redis
docker-compose restart redis-n8n
```

### **Logs Útiles**
```bash
# Todos los servicios
docker-compose logs

# Servicio específico
docker-compose logs n8n

# Seguir logs en tiempo real
docker-compose logs -f n8n
```

## 🔄 Workflows de Ejemplo

### **1. E-commerce Automation**
- **Archivo:** `workflows/n8n/ecommerce-automation.json`
- **Descripción:** Automatización de tienda online
- **Funcionalidades:**
  - Sincronización de inventario
  - Notificaciones de pedidos
  - Actualización de precios

### **2. Social Media Scheduler**
- **Archivo:** `workflows/n8n/social-media-scheduler.json`
- **Descripción:** Programación de contenido
- **Funcionalidades:**
  - Publicación automática
  - Análisis de engagement
  - Programación inteligente

### **3. Data Collection Pipeline**
- **Archivo:** `workflows/n8n/data-collection-pipeline.json`
- **Descripción:** Recolección de datos
- **Funcionalidades:**
  - Scraping web
  - Procesamiento de APIs
  - Almacenamiento en BD

## 📈 Optimización

### **Performance**
- **Recursos:** Ajustar memoria y CPU
- **Caching:** Configurar Redis
- **Queue:** Optimizar colas de trabajo

### **Seguridad**
- **HTTPS:** Configurar SSL
- **Auth:** Implementar autenticación
- **Logs:** Configurar auditoría

### **Escalabilidad**
- **Load Balancing:** Distribuir carga
- **Clustering:** Múltiples instancias
- **Monitoring:** Alertas automáticas

## 🆘 Soporte

### **Documentación**
- [N8N Docs](https://docs.n8n.io/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Grafana Docs](https://grafana.com/docs/)

### **Comunidad**
- [N8N Community](https://community.n8n.io/)
- [GitHub Issues](https://github.com/gabibenitezzz003/PORTFOLIO/issues)

### **Contacto**
- **Email:** gabriel@example.com
- **GitHub:** @gabibenitezzz003
- **LinkedIn:** Gabriel Benitez

---

**Desarrollado para GreenCode Software - Portfolio de Gabriel**  
*No-Code Automation | Workflow Design | System Integration*
