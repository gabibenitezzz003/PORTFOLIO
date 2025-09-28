"""
Aplicación FastAPI - Sistema de Recomendaciones ML
Aplicación principal con API REST para recomendaciones
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
import asyncio

from ...aplicacion.servicios.servicio_recomendaciones import ServicioRecomendaciones
from ...infraestructura.algoritmos.algoritmo_colaborativo import AlgoritmoColaborativo
from .dto.recomendacion_dto import (
    RecomendacionRequest, RecomendacionResponse,
    RecomendacionSimilarRequest, RecomendacionSimilarResponse,
    ComparacionAlgoritmosRequest, ComparacionAlgoritmosResponse
)
from .dto.respuesta_api_dto import RespuestaAPI, ErrorAPI
from .middleware.middleware_logging import LoggingMiddleware
from .middleware.middleware_errores import ErrorHandlingMiddleware
from .dependencias.dependencias import obtener_servicio_recomendaciones


# Configurar logging
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
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    Inicializa servicios y modelos al arrancar
    """
    logger.info("Iniciando aplicación de Recomendaciones ML")
    
    try:
        # Inicializar servicios
        servicio_recomendaciones = ServicioRecomendaciones()
        
        # Registrar algoritmos
        algoritmo_colaborativo = AlgoritmoColaborativo()
        
        servicio_recomendaciones.registrar_algoritmo("colaborativo", algoritmo_colaborativo)
        
        # Almacenar en el estado de la aplicación
        app.state.servicio_recomendaciones = servicio_recomendaciones
        
        logger.info("Servicios inicializados correctamente")
        
        yield
        
    except Exception as e:
        logger.error(f"Error inicializando aplicación: {str(e)}")
        raise
    finally:
        logger.info("Cerrando aplicación de Recomendaciones ML")


# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Recomendaciones ML",
    description="API REST para sistema de recomendaciones con machine learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar middleware personalizado
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)


@app.get("/", response_model=RespuestaAPI)
async def raiz():
    """
    Endpoint raíz con información de la API
    """
    return RespuestaAPI(
        exito=True,
        mensaje="Sistema de Recomendaciones ML",
        datos={
            "version": "1.0.0",
            "endpoints": {
                "recomendaciones_usuario": "/api/v1/recomendaciones/usuario/{usuario_id}",
                "recomendaciones_similares": "/api/v1/recomendaciones/similares/{item_id}",
                "comparar_algoritmos": "/api/v1/recomendaciones/comparar",
                "entrenar_modelo": "/api/v1/modelos/entrenar",
                "evaluar_modelo": "/api/v1/modelos/evaluar",
                "documentacion": "/docs"
            }
        }
    )


@app.get("/health", response_model=RespuestaAPI)
async def health_check():
    """
    Endpoint de verificación de salud
    """
    return RespuestaAPI(
        exito=True,
        mensaje="Sistema funcionando correctamente",
        datos={
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )


@app.post("/api/v1/recomendaciones/usuario/{usuario_id}", response_model=RespuestaAPI)
async def recomendar_para_usuario(
    usuario_id: str,
    request: RecomendacionRequest,
    background_tasks: BackgroundTasks,
    servicio: ServicioRecomendaciones = Depends(obtener_servicio_recomendaciones)
):
    """
    Generar recomendaciones para un usuario
    """
    try:
        logger.info("Generando recomendaciones para usuario", usuario_id=usuario_id)
        
        recomendaciones = await servicio.recomendar_para_usuario(
            usuario_id=usuario_id,
            limit=request.limit,
            algoritmo=request.algoritmo,
            contexto=request.contexto,
            filtros=request.filtros
        )
        
        # Convertir a DTOs de respuesta
        respuestas = [RecomendacionResponse.from_entidad(r) for r in recomendaciones]
        
        logger.info("Recomendaciones generadas exitosamente", total=len(recomendaciones))
        
        return RespuestaAPI(
            exito=True,
            mensaje=f"Recomendaciones generadas: {len(recomendaciones)} items",
            datos=[r.dict() for r in respuestas]
        )
        
    except Exception as e:
        logger.error(f"Error generando recomendaciones: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/recomendaciones/similares/{item_id}", response_model=RespuestaAPI)
async def recomendar_similares(
    item_id: str,
    request: RecomendacionSimilarRequest,
    servicio: ServicioRecomendaciones = Depends(obtener_servicio_recomendaciones)
):
    """
    Generar recomendaciones de items similares
    """
    try:
        logger.info("Generando recomendaciones similares", item_id=item_id)
        
        recomendaciones = await servicio.recomendar_similares(
            item_id=item_id,
            limit=request.limit,
            algoritmo=request.algoritmo
        )
        
        # Convertir a DTOs de respuesta
        respuestas = [RecomendacionSimilarResponse.from_entidad(r) for r in recomendaciones]
        
        logger.info("Recomendaciones similares generadas exitosamente", total=len(recomendaciones))
        
        return RespuestaAPI(
            exito=True,
            mensaje=f"Recomendaciones similares generadas: {len(recomendaciones)} items",
            datos=[r.dict() for r in respuestas]
        )
        
    except Exception as e:
        logger.error(f"Error generando recomendaciones similares: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/recomendaciones/comparar", response_model=RespuestaAPI)
async def comparar_algoritmos(
    request: ComparacionAlgoritmosRequest,
    servicio: ServicioRecomendaciones = Depends(obtener_servicio_recomendaciones)
):
    """
    Comparar diferentes algoritmos de recomendación
    """
    try:
        logger.info("Comparando algoritmos de recomendación", usuario_id=request.usuario_id)
        
        resultados = await servicio.comparar_algoritmos(
            usuario_id=request.usuario_id,
            limit=request.limit,
            algoritmos=request.algoritmos,
            contexto=request.contexto
        )
        
        # Convertir a DTOs de respuesta
        respuestas = {}
        for algoritmo, recomendaciones in resultados.items():
            if recomendaciones:
                respuestas[algoritmo] = [RecomendacionResponse.from_entidad(r).dict() for r in recomendaciones]
            else:
                respuestas[algoritmo] = []
        
        logger.info("Comparación de algoritmos completada")
        
        return RespuestaAPI(
            exito=True,
            mensaje="Comparación de algoritmos completada",
            datos=respuestas
        )
        
    except Exception as e:
        logger.error(f"Error comparando algoritmos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/modelos/entrenar", response_model=RespuestaAPI)
async def entrenar_modelo(
    algoritmo: str,
    datos_entrenamiento: Dict[str, Any],
    servicio: ServicioRecomendaciones = Depends(obtener_servicio_recomendaciones)
):
    """
    Entrenar un modelo de recomendación
    """
    try:
        logger.info("Iniciando entrenamiento de modelo", algoritmo=algoritmo)
        
        metricas = await servicio.entrenar_algoritmo(
            algoritmo=algoritmo,
            datos_entrenamiento=datos_entrenamiento
        )
        
        logger.info("Entrenamiento de modelo completado", metricas=metricas)
        
        return RespuestaAPI(
            exito=True,
            mensaje="Modelo entrenado exitosamente",
            datos=metricas
        )
        
    except Exception as e:
        logger.error(f"Error entrenando modelo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/modelos/evaluar", response_model=RespuestaAPI)
async def evaluar_modelo(
    algoritmo: str,
    datos_test: Dict[str, Any],
    metricas: Optional[List[str]] = None,
    servicio: ServicioRecomendaciones = Depends(obtener_servicio_recomendaciones)
):
    """
    Evaluar un modelo de recomendación
    """
    try:
        logger.info("Iniciando evaluación de modelo", algoritmo=algoritmo)
        
        metricas_evaluacion = await servicio.evaluar_algoritmo(
            algoritmo=algoritmo,
            datos_test=datos_test,
            metricas=metricas
        )
        
        logger.info("Evaluación de modelo completada", metricas=metricas_evaluacion)
        
        return RespuestaAPI(
            exito=True,
            mensaje="Modelo evaluado exitosamente",
            datos=metricas_evaluacion
        )
        
    except Exception as e:
        logger.error(f"Error evaluando modelo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/estadisticas", response_model=RespuestaAPI)
async def obtener_estadisticas(
    usuario_id: Optional[str] = None,
    servicio: ServicioRecomendaciones = Depends(obtener_servicio_recomendaciones)
):
    """
    Obtener estadísticas del sistema de recomendaciones
    """
    try:
        estadisticas = await servicio.obtener_estadisticas(usuario_id=usuario_id)
        
        return RespuestaAPI(
            exito=True,
            mensaje="Estadísticas obtenidas exitosamente",
            datos=estadisticas
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "presentacion.api.aplicacion:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
