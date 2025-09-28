# Portfolio - Desarrollador Python Backend
Este portfolio reúne una colección de proyectos que demuestran mi experiencia en el desarrollo backend con Python, aplicando arquitectura hexagonal, principios SOLID, patrones de diseño modernos y metodologías de testing.
Incluye soluciones que abarcan APIs REST con FastAPI, procesamiento y análisis de datos con Pandas, NLP con spaCy/NLTK, orquestación de workflows con Airflow, integración con bases de datos SQL y despliegue con Docker.
El objetivo es mostrar mi capacidad para diseñar, implementar y mantener aplicaciones backend escalables, limpias y bien documentadas, siguiendo las mejores prácticas de la industria.

## 🏗️ Arquitectura y Principios

### Arquitectura Hexagonal (Clean Architecture)
- **Separación de responsabilidades** clara entre capas
- **Inversión de dependencias** con interfaces
- **Testabilidad** mejorada con mocks y stubs
- **Escalabilidad** y mantenibilidad del código

### Clean Code y Principios SOLID
- **Single Responsibility Principle** - Cada clase tiene una responsabilidad
- **Open/Closed Principle** - Abierto para extensión, cerrado para modificación
- **Liskov Substitution Principle** - Subtipos reemplazables
- **Interface Segregation Principle** - Interfaces específicas
- **Dependency Inversion Principle** - Dependencias hacia abstracciones

### Patrones de Diseño Implementados
- **Repository Pattern** - Abstracción de acceso a datos
- **Service Layer Pattern** - Lógica de negocio encapsulada
- **Factory Pattern** - Creación de objetos complejos
- **Decorator Pattern** - Funcionalidad adicional sin modificar clases
- **Observer Pattern** - Comunicación desacoplada

## 🚀 Tecnologías Demostradas

### Imprescindibles
- ✅ **Python** - 4+ años de experiencia con POO avanzada
- ✅ **FastAPI** - APIs REST con arquitectura hexagonal
- ✅ **Pandas** - Manipulación y procesamiento de datos
- ✅ **NLP/PLN** - Procesamiento de lenguaje natural con spaCy
- ✅ **Apache Airflow** - Orquestación de workflows
- ✅ **PostgreSQL** - Base de datos relacional avanzada
- ✅ **Docker** - Containerización de aplicaciones

### Valoradas
- ✅ **Machine Learning** - Modelos de recomendación y clasificación
- ✅ **Testing** - Pruebas automatizadas con pytest y TDD
- ✅ **Cloud Computing** - Preparado para AWS/GCP/Azure
- ✅ **Metodologías Ágiles** - Desarrollo iterativo y colaborativo

## 📁 Proyectos Incluidos

### 1. [Sistema de Gestión de Datos con Arquitectura Hexagonal](./01-sistema-gestion-datos/)
**Tecnologías:** FastAPI, PostgreSQL, SQLAlchemy, Pydantic, Docker
- Arquitectura hexagonal con separación de capas
- Patrones Repository y Service Layer
- Decoradores personalizados para logging y validación
- Tests unitarios e integración con >95% cobertura

### 2. [Pipeline de Procesamiento de Datos](./02-pipeline-procesamiento-datos/)
**Tecnologías:** Pandas, NumPy, Matplotlib, Seaborn
- ETL pipeline con arquitectura modular
- Análisis estadístico avanzado con POO
- Visualizaciones interactivas
- Reportes automatizados con decoradores

### 3. [Sistema de Análisis de Sentimientos con NLP](./03-sistema-analisis-sentimientos/)
**Tecnologías:** spaCy, NLTK, scikit-learn, FastAPI
- Procesamiento de texto en tiempo real
- Análisis de sentimientos multilingüe
- Patrón Strategy para diferentes algoritmos
- API REST con arquitectura hexagonal

### 4. [Orquestación de Workflows con Airflow](./04-orquestacion-workflows/)
**Tecnologías:** Apache Airflow, Python, Docker
- DAGs modulares con POO
- Patrón Factory para creación de tareas
- Monitoreo y alertas con decoradores
- Integración con APIs externas

### 5. [Sistema de Recomendaciones ML](./05-sistema-recomendaciones-ml/)
**Tecnologías:** scikit-learn, pandas, FastAPI, PostgreSQL
- Algoritmos de recomendación con patrón Strategy
- Sistema de filtrado de contenido
- API REST con arquitectura hexagonal
- Métricas de evaluación automatizadas

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)
```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd PORTFOLIO

# Dar permisos de ejecución
chmod +x scripts/*.sh

# Iniciar todo el portfolio
./scripts/start-portfolio.sh
```

### Opción 2: Docker Compose Manual
```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd PORTFOLIO

# Iniciar servicios
docker-compose up -d

# Verificar estado
./scripts/health-check.sh
```

### Opción 3: Instalación Local
```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd PORTFOLIO

# Instalar dependencias por proyecto
cd 01-sistema-gestion-datos && pip install -r requirements.txt
cd ../02-pipeline-procesamiento-datos && pip install -r requirements.txt
cd ../03-sistema-nlp-sentimientos && pip install -r requirements.txt
cd ../04-orquestacion-airflow && pip install -r requirements.txt
cd ../05-sistema-recomendaciones-ml && pip install -r requirements.txt
```

## 🌐 Servicios Disponibles

### APIs REST
- **Proyecto 1:** http://localhost:8001 (docs: /docs)
- **Proyecto 3:** http://localhost:8003 (docs: /docs)
- **Proyecto 5:** http://localhost:8005 (docs: /docs)

### Servicios de Soporte
- **Página Principal:** http://localhost
- **Airflow UI:** http://localhost:8080 (admin/admin)
- **MLflow:** http://localhost:5000
- **Grafana:** http://localhost:3000 (admin/admin123)
- **Prometheus:** http://localhost:9090

## 🔧 Comandos Útiles

```bash
# Iniciar portfolio completo
./scripts/start-portfolio.sh

# Verificar estado de servicios
./scripts/health-check.sh

# Parar todos los servicios
./scripts/stop-portfolio.sh

# Ver logs de un servicio
docker-compose logs -f api-proyecto1

# Reiniciar un servicio
docker-compose restart api-proyecto1

# Ver estado de contenedores
docker-compose ps
```

## 📚 Documentación Adicional

- **[Guía de Instalación](GUIA_INSTALACION.md)** - Instrucciones detalladas
- **[Tecnologías Demostradas](TECNOLOGIAS_DEMOSTRADAS.md)** - Stack técnico completo
- **README individual** por proyecto con documentación específica

## 📊 Métricas del Portfolio

- **5 proyectos** completos y funcionales
- **100% de cobertura** de tecnologías requeridas
- **Arquitectura hexagonal** en todos los proyectos
- **Clean Code** aplicado consistentemente
- **POO avanzada** con patrones de diseño
- **Tests automatizados** con >90% cobertura
- **Documentación** completa en español
- **Docker** en todos los proyectos

## 🎯 Experiencia Demostrada

- **Arquitectura hexagonal** y clean architecture
- **Patrones de diseño** modernos y efectivos
- **Clean Code** y principios SOLID
- **POO avanzada** con decoradores y metaclasses
- **Testing** con TDD y BDD
- **DevOps** con Docker y orquestación
- **Documentación** técnica profesional

## 📞 Contacto

- **Email:** gabibenitezzz003@gmail.com
- **LinkedIn:**https://linkedin.com/in/gabibenitezzz003
- **GitHub:** [@gabibenitezzz003](https://github.com/gabibenitezzz003/PORTFOLIO

---
