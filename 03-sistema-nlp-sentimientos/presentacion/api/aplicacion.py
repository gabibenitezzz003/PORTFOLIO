"""
Aplicación FastAPI - Sistema NLP
Aplicación principal con API REST para análisis de sentimientos y entidades
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

from aplicacion.servicios.servicio_sentimientos import ServicioSentimientos
from aplicacion.servicios.servicio_entidades import ServicioEntidades
from infraestructura.algoritmos.spacy_sentimientos import AlgoritmoSpacySentimientos
from infraestructura.algoritmos.spacy_entidades import AlgoritmoSpacyEntidades
from .dto.analisis_dto import (
    AnalisisSentimientoRequest, AnalisisSentimientoResponse,
    ExtraccionEntidadesRequest, ExtraccionEntidadesResponse,
    AnalisisCompletoRequest, AnalisisCompletoResponse,
    ComparacionAlgoritmosRequest, ComparacionAlgoritmosResponse
)
from .dto.respuesta_api_dto import RespuestaAPI, ErrorAPI
from .middleware.middleware_logging import LoggingMiddleware
from .middleware.middleware_errores import ErrorHandlingMiddleware
from .dependencias.dependencias import obtener_servicio_sentimientos, obtener_servicio_entidades


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
    logger.info("Iniciando aplicación NLP")
    
    try:
        # Inicializar servicios
        servicio_sentimientos = ServicioSentimientos()
        servicio_entidades = ServicioEntidades()
        
        # Registrar algoritmos
        algoritmo_spacy_sentimientos = AlgoritmoSpacySentimientos()
        algoritmo_spacy_entidades = AlgoritmoSpacyEntidades()
        
        servicio_sentimientos.registrar_algoritmo("spacy", algoritmo_spacy_sentimientos)
        servicio_entidades.registrar_algoritmo("spacy", algoritmo_spacy_entidades)
        
        # Almacenar en el estado de la aplicación
        app.state.servicio_sentimientos = servicio_sentimientos
        app.state.servicio_entidades = servicio_entidades
        
        logger.info("Servicios inicializados correctamente")
        
        yield
        
    except Exception as e:
        logger.error(f"Error inicializando aplicación: {str(e)}")
        raise
    finally:
        logger.info("Cerrando aplicación NLP")


# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema NLP - Análisis de Sentimientos y Entidades",
    description="API REST para análisis de sentimientos, extracción de entidades y procesamiento de lenguaje natural",
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
        mensaje="Sistema NLP - Análisis de Sentimientos y Entidades",
        datos={
            "version": "1.0.0",
            "endpoints": {
                "sentimientos": "/api/v1/sentimientos",
                "entidades": "/api/v1/entidades",
                "analisis_completo": "/api/v1/analisis/completo",
                "comparacion": "/api/v1/analisis/comparacion",
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


@app.post("/api/v1/sentimientos/analizar", response_model=RespuestaAPI)
async def analizar_sentimiento(
    request: AnalisisSentimientoRequest,
    background_tasks: BackgroundTasks,
    servicio: ServicioSentimientos = Depends(obtener_servicio_sentimientos)
):
    """
    Analizar sentimientos de un texto
    """
    try:
        logger.info("Iniciando análisis de sentimientos", texto_preview=request.texto[:100])
        
        resultado = await servicio.analizar_sentimiento(
            texto=request.texto,
            idioma=request.idioma,
            algoritmo=request.algoritmo,
            incluir_emociones=request.incluir_emociones,
            incluir_palabras_clave=request.incluir_palabras_clave
        )
        
        # Convertir a DTO de respuesta
        respuesta = AnalisisSentimientoResponse.from_entidad(resultado)
        
        logger.info("Análisis de sentimientos completado", categoria=resultado.categoria.value)
        
        return RespuestaAPI(
            exito=True,
            mensaje="Análisis de sentimientos completado",
            datos=respuesta.dict()
        )
        
    except Exception as e:
        logger.error(f"Error en análisis de sentimientos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sentimientos/analizar-lote", response_model=RespuestaAPI)
async def analizar_sentimientos_lote(
    textos: List[str],
    idioma: str = "es",
    algoritmo: Optional[str] = None,
    servicio: ServicioSentimientos = Depends(obtener_servicio_sentimientos)
):
    """
    Analizar sentimientos de múltiples textos
    """
    try:
        logger.info(f"Iniciando análisis de lote: {len(textos)} textos")
        
        resultados = await servicio.analizar_sentimientos_lote(
            textos=textos,
            idioma=idioma,
            algoritmo=algoritmo
        )
        
        # Convertir a DTOs de respuesta
        respuestas = [AnalisisSentimientoResponse.from_entidad(r) for r in resultados]
        
        logger.info(f"Análisis de lote completado: {len(respuestas)} resultados")
        
        return RespuestaAPI(
            exito=True,
            mensaje=f"Análisis de lote completado: {len(respuestas)} textos procesados",
            datos=[r.dict() for r in respuestas]
        )
        
    except Exception as e:
        logger.error(f"Error en análisis de lote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/entidades/extraer", response_model=RespuestaAPI)
async def extraer_entidades(
    request: ExtraccionEntidadesRequest,
    servicio: ServicioEntidades = Depends(obtener_servicio_entidades)
):
    """
    Extraer entidades de un texto
    """
    try:
        logger.info("Iniciando extracción de entidades", texto_preview=request.texto[:100])
        
        entidades = await servicio.extraer_entidades(
            texto=request.texto,
            idioma=request.idioma,
            algoritmo=request.algoritmo,
            tipos_entidades=request.tipos_entidades,
            umbral_confianza=request.umbral_confianza
        )
        
        # Convertir a DTO de respuesta
        respuesta = ExtraccionEntidadesResponse.from_entidades(entidades)
        
        logger.info(f"Extracción de entidades completada: {len(entidades)} entidades")
        
        return RespuestaAPI(
            exito=True,
            mensaje=f"Extracción de entidades completada: {len(entidades)} entidades encontradas",
            datos=respuesta.dict()
        )
        
    except Exception as e:
        logger.error(f"Error en extracción de entidades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/entidades/extraer-lote", response_model=RespuestaAPI)
async def extraer_entidades_lote(
    textos: List[str],
    idioma: str = "es",
    algoritmo: Optional[str] = None,
    tipos_entidades: Optional[List[str]] = None,
    servicio: ServicioEntidades = Depends(obtener_servicio_entidades)
):
    """
    Extraer entidades de múltiples textos
    """
    try:
        logger.info(f"Iniciando extracción de lote: {len(textos)} textos")
        
        resultados = await servicio.extraer_entidades_lote(
            textos=textos,
            idioma=idioma,
            algoritmo=algoritmo,
            tipos_entidades=tipos_entidades
        )
        
        # Convertir a DTOs de respuesta
        respuestas = [ExtraccionEntidadesResponse.from_entidades(ents) for ents in resultados]
        
        logger.info(f"Extracción de lote completada: {len(respuestas)} resultados")
        
        return RespuestaAPI(
            exito=True,
            mensaje=f"Extracción de lote completada: {len(respuestas)} textos procesados",
            datos=[r.dict() for r in respuestas]
        )
        
    except Exception as e:
        logger.error(f"Error en extracción de lote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analisis/completo", response_model=RespuestaAPI)
async def analisis_completo(
    request: AnalisisCompletoRequest,
    servicio_sentimientos: ServicioSentimientos = Depends(obtener_servicio_sentimientos),
    servicio_entidades: ServicioEntidades = Depends(obtener_servicio_entidades)
):
    """
    Realizar análisis completo de un texto (sentimientos + entidades)
    """
    try:
        logger.info("Iniciando análisis completo", texto_preview=request.texto[:100])
        
        # Ejecutar análisis en paralelo
        tarea_sentimientos = servicio_sentimientos.analizar_sentimiento(
            texto=request.texto,
            idioma=request.idioma,
            algoritmo=request.algoritmo_sentimientos
        )
        
        tarea_entidades = servicio_entidades.extraer_entidades(
            texto=request.texto,
            idioma=request.idioma,
            algoritmo=request.algoritmo_entidades,
            tipos_entidades=request.tipos_entidades
        )
        
        # Esperar resultados
        resultado_sentimientos, entidades = await asyncio.gather(
            tarea_sentimientos, tarea_entidades
        )
        
        # Crear respuesta
        respuesta = AnalisisCompletoResponse(
            texto=request.texto,
            idioma=request.idioma,
            analisis_sentimiento=AnalisisSentimientoResponse.from_entidad(resultado_sentimientos),
            entidades=ExtraccionEntidadesResponse.from_entidades(entidades),
            estadisticas={
                "total_entidades": len(entidades),
                "categoria_sentimiento": resultado_sentimientos.categoria.value,
                "polaridad": resultado_sentimientos.polaridad,
                "confianza_sentimiento": resultado_sentimientos.confianza
            }
        )
        
        logger.info("Análisis completo finalizado")
        
        return RespuestaAPI(
            exito=True,
            mensaje="Análisis completo finalizado",
            datos=respuesta.dict()
        )
        
    except Exception as e:
        logger.error(f"Error en análisis completo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analisis/comparacion", response_model=RespuestaAPI)
async def comparar_algoritmos(
    request: ComparacionAlgoritmosRequest,
    servicio: ServicioSentimientos = Depends(obtener_servicio_sentimientos)
):
    """
    Comparar diferentes algoritmos de análisis
    """
    try:
        logger.info("Iniciando comparación de algoritmos", texto_preview=request.texto[:100])
        
        resultados = await servicio.comparar_algoritmos(
            texto=request.texto,
            idioma=request.idioma,
            algoritmos=request.algoritmos
        )
        
        # Convertir a DTOs de respuesta
        respuestas = {}
        for algoritmo, resultado in resultados.items():
            if resultado:
                respuestas[algoritmo] = AnalisisSentimientoResponse.from_entidad(resultado).dict()
            else:
                respuestas[algoritmo] = None
        
        logger.info("Comparación de algoritmos completada")
        
        return RespuestaAPI(
            exito=True,
            mensaje="Comparación de algoritmos completada",
            datos=respuestas
        )
        
    except Exception as e:
        logger.error(f"Error en comparación de algoritmos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/estadisticas/sentimientos", response_model=RespuestaAPI)
async def obtener_estadisticas_sentimientos(
    servicio: ServicioSentimientos = Depends(obtener_servicio_sentimientos)
):
    """
    Obtener estadísticas del servicio de sentimientos
    """
    try:
        configuracion = servicio.obtener_configuracion()
        algoritmos = servicio.listar_algoritmos_disponibles()
        
        return RespuestaAPI(
            exito=True,
            mensaje="Estadísticas de sentimientos obtenidas",
            datos={
                "configuracion": configuracion,
                "algoritmos_disponibles": algoritmos
            }
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/estadisticas/entidades", response_model=RespuestaAPI)
async def obtener_estadisticas_entidades(
    servicio: ServicioEntidades = Depends(obtener_servicio_entidades)
):
    """
    Obtener estadísticas del servicio de entidades
    """
    try:
        configuracion = servicio.obtener_configuracion()
        algoritmos = servicio.listar_algoritmos_disponibles()
        
        return RespuestaAPI(
            exito=True,
            mensaje="Estadísticas de entidades obtenidas",
            datos={
                "configuracion": configuracion,
                "algoritmos_disponibles": algoritmos
            }
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
