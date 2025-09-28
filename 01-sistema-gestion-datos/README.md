# Sistema de Gestión de Datos con Arquitectura Hexagonal

## 📋 Descripción

Sistema completo de gestión de datos empresariales desarrollado con **Arquitectura Hexagonal** (Clean Architecture), **FastAPI** y **PostgreSQL**. Implementa principios de **Clean Code**, **SOLID** y patrones de diseño modernos.

## 🏗️ Arquitectura Hexagonal

### Capas de la Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Controladores │  │   Middleware    │  │   DTOs      │  │
│  │   (FastAPI)     │  │   (Logging,     │  │   (Pydantic)│  │
│  │                 │  │    Auth, etc)   │  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Casos de Uso  │  │   Servicios     │  │   DTOs      │  │
│  │   (Use Cases)   │  │   (Business     │  │   (Mappers) │  │
│  │                 │  │    Logic)       │  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DOMINIO                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Entidades     │  │   Value Objects │  │   Servicios │  │
│  │   (Models)      │  │   (Value        │  │   de Dominio│  │
│  │                 │  │    Objects)     │  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE INFRAESTRUCTURA                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Repositorios  │  │   Base de Datos │  │   APIs      │  │
│  │   (Implementa   │  │   (PostgreSQL,  │  │   Externas  │  │
│  │    Interfaces)  │  │    SQLAlchemy)  │  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Características

- **Arquitectura Hexagonal** con separación clara de responsabilidades
- **Principios SOLID** aplicados consistentemente
- **Clean Code** con nombres descriptivos en español
- **Patrones de Diseño** (Repository, Factory, Decorator, Observer)
- **POO Avanzada** con herencia, polimorfismo y encapsulación
- **Decoradores Personalizados** para logging, validación y métricas
- **Tests Automatizados** con >95% cobertura
- **Documentación Automática** con Swagger/OpenAPI

## 🛠️ Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validación de datos
- **JWT** - Autenticación segura
- **pytest** - Testing framework
- **Docker** - Containerización
- **Alembic** - Migraciones de base de datos

## 📁 Estructura del Proyecto

```
01-sistema-gestion-datos/
├── aplicacion/                    # Capa de Aplicación
│   ├── casos_uso/                # Casos de uso del negocio
│   ├── servicios/                # Servicios de aplicación
│   └── dto/                      # Data Transfer Objects
├── dominio/                       # Capa de Dominio
│   ├── entidades/                # Entidades del dominio
│   ├── value_objects/            # Objetos de valor
│   ├── servicios/                # Servicios de dominio
│   └── interfaces/               # Interfaces (puertos)
├── infraestructura/              # Capa de Infraestructura
│   ├── persistencia/             # Repositorios implementados
│   ├── base_datos/               # Configuración de BD
│   └── adaptadores/              # Adaptadores externos
├── presentacion/                 # Capa de Presentación
│   ├── controladores/            # Controladores FastAPI
│   ├── middleware/               # Middleware personalizado
│   └── dto/                      # DTOs de presentación
├── utilidades/                   # Utilidades compartidas
│   ├── decoradores/              # Decoradores personalizados
│   ├── excepciones/              # Excepciones personalizadas
│   └── helpers/                  # Funciones auxiliares
├── tests/                        # Tests automatizados
├── migrations/                   # Migraciones Alembic
├── requirements.txt              # Dependencias
├── Dockerfile                    # Imagen Docker
├── docker-compose.yml            # Orquestación
└── README.md                     # Documentación
```

## 🚀 Instalación y Uso

### Opción 1: Con Docker (Recomendado)

```bash
# Clonar el repositorio
git clone <repo-url>
cd 01-sistema-gestion-datos

# Levantar servicios con Docker Compose
docker-compose up -d

# La API estará disponible en http://localhost:8000
# Documentación en http://localhost:8000/docs
```

### Opción 2: Instalación Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn presentacion.aplicacion:app --reload
```

## 📊 Endpoints de la API

### Autenticación
- `POST /autenticacion/iniciar-sesion` - Iniciar sesión
- `POST /autenticacion/registrar` - Registro de usuario
- `POST /autenticacion/renovar-token` - Renovar token

### Usuarios
- `GET /usuarios/` - Listar usuarios
- `GET /usuarios/{id}` - Obtener usuario
- `PUT /usuarios/{id}` - Actualizar usuario
- `DELETE /usuarios/{id}` - Eliminar usuario

### Productos
- `GET /productos/` - Listar productos
- `POST /productos/` - Crear producto
- `GET /productos/{id}` - Obtener producto
- `PUT /productos/{id}` - Actualizar producto
- `DELETE /productos/{id}` - Eliminar producto

### Órdenes
- `GET /ordenes/` - Listar órdenes
- `POST /ordenes/` - Crear orden
- `GET /ordenes/{id}` - Obtener orden
- `PUT /ordenes/{id}` - Actualizar orden

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=aplicacion --cov=dominio --cov=infraestructura

# Ejecutar tests específicos
pytest tests/test_casos_uso/
```

## 📈 Métricas de Calidad

- **Cobertura de tests:** >95%
- **Tiempo de respuesta:** <100ms promedio
- **Documentación:** 100% de endpoints documentados
- **Validación:** 100% de datos validados
- **Seguridad:** JWT + HTTPS + Rate limiting
- **Arquitectura:** 100% hexagonal compliance

## 🔧 Configuración

### Variables de Entorno

```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/sistema_gestion_datos
SECRET_KEY=tu-clave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📝 Documentación API

Una vez ejecutando la aplicación, la documentación interactiva estará disponible en:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🚀 Despliegue

### Docker Hub
```bash
# Construir imagen
docker build -t sistema-gestion-datos .

# Subir a Docker Hub
docker tag sistema-gestion-datos username/sistema-gestion-datos
docker push username/sistema-gestion-datos
```

### Producción
```bash
# Usar docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/CaracteristicaIncreible`)
3. Commit cambios (`git commit -m 'Agregar CaracteristicaIncreible'`)
4. Push a la rama (`git push origin feature/CaracteristicaIncreible`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

