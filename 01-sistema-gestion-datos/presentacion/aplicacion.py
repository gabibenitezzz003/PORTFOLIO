"""
Aplicación FastAPI - Capa de Presentación
Configuración principal de la aplicación FastAPI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
from typing import Dict, Any

from infraestructura.base_datos.configuracion_bd import crear_tablas
from aplicacion.excepciones.excepciones_aplicacion import ExcepcionAplicacion
from .controladores.usuario_controlador import router as usuario_router
from .middleware.middleware_logging import MiddlewareLogging
from .middleware.middleware_errores import MiddlewareErrores


# Configurar logging estructurado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    """
    # Startup
    logger.info("Iniciando aplicación FastAPI")
    crear_tablas()
    logger.info("Tablas de base de datos creadas")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación FastAPI")


# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Gestión de Datos",
    description="API REST para gestión de datos empresariales con Arquitectura Hexagonal",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar middleware personalizado
app.add_middleware(MiddlewareLogging)
app.add_middleware(MiddlewareErrores)

# Incluir routers
app.include_router(usuario_router, prefix="/api/v1", tags=["usuarios"])


@app.get("/")
async def raiz() -> Dict[str, Any]:
    """
    Endpoint raíz de la API
    """
    return {
        "mensaje": "Sistema de Gestión de Datos API",
        "version": "1.0.0",
        "documentacion": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Endpoint de health check
    """
    return {
        "estado": "saludable",
        "timestamp": "2024-01-01T00:00:00Z"
    }


# Manejador global de excepciones
@app.exception_handler(ExcepcionAplicacion)
async def manejar_excepcion_aplicacion(request, exc: ExcepcionAplicacion):
    """
    Manejador global para excepciones de aplicación
    """
    logger.error("Excepción de aplicación", excepcion=str(exc), tipo=type(exc).__name__)
    
    return JSONResponse(
        status_code=400,
        content={
            "error": True,
            "mensaje": str(exc),
            "tipo": type(exc).__name__
        }
    )


@app.exception_handler(HTTPException)
async def manejar_http_exception(request, exc: HTTPException):
    """
    Manejador global para excepciones HTTP
    """
    logger.error("Excepción HTTP", status_code=exc.status_code, detalle=exc.detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "mensaje": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def manejar_excepcion_general(request, exc: Exception):
    """
    Manejador global para excepciones no controladas
    """
    logger.error("Excepción no controlada", excepcion=str(exc), tipo=type(exc).__name__)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "mensaje": "Error interno del servidor",
            "tipo": "ErrorInterno"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
