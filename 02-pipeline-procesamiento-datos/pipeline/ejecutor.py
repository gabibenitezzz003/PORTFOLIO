"""
Ejecutor del Pipeline - Pipeline ETL
Orquestador principal del pipeline de procesamiento de datos
"""
import asyncio
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .extractores.extractor_base import ExtractorBase
from .transformadores.transformador_base import TransformadorBase
from .cargadores.cargador_base import CargadorBase
from .validadores.validador_base import ValidadorBase
from ..utilidades.decoradores.decorador_logging import logging_metodo
from ..utilidades.decoradores.decorador_validacion import validar_parametros
from ..utilidades.helpers.helpers_pipeline import calcular_metricas_calidad


logger = structlog.get_logger()


@dataclass
class ConfiguracionPipeline:
    """Configuración del pipeline"""
    
    # Configuración general
    nombre_pipeline: str
    version: str = "1.0.0"
    descripcion: str = ""
    
    # Configuración de procesamiento
    tamano_lote: int = 10000
    max_workers: int = 4
    timeout_segundos: int = 300
    
    # Configuración de logging
    nivel_log: str = "INFO"
    incluir_metricas: bool = True
    
    # Configuración de validación
    validar_entrada: bool = True
    validar_salida: bool = True
    tolerancia_errores: float = 0.05  # 5% de errores permitidos


@dataclass
class ResultadoPipeline:
    """Resultado de la ejecución del pipeline"""
    
    # Información general
    nombre_pipeline: str
    fecha_inicio: datetime
    fecha_fin: datetime
    duracion_segundos: float
    
    # Métricas de procesamiento
    registros_procesados: int
    registros_exitosos: int
    registros_fallidos: int
    tasa_exito: float
    
    # Métricas de calidad
    completitud_datos: float
    consistencia_datos: float
    precision_datos: float
    
    # Información de errores
    errores: List[str]
    advertencias: List[str]
    
    # Archivos generados
    archivos_salida: List[str]
    reportes_generados: List[str]


class EjecutorPipeline:
    """
    Ejecutor principal del pipeline ETL
    Implementa el patrón Template Method para orquestar el procesamiento
    """
    
    def __init__(self, configuracion: ConfiguracionPipeline):
        """
        Inicializar ejecutor del pipeline
        
        Args:
            configuracion: Configuración del pipeline
        """
        self.configuracion = configuracion
        self.extractores: List[ExtractorBase] = []
        self.transformadores: List[TransformadorBase] = []
        self.cargadores: List[CargadorBase] = []
        self.validadores: List[ValidadorBase] = []
        
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
        
        self.logger = structlog.get_logger()
    
    def agregar_extractor(self, extractor: ExtractorBase) -> None:
        """Agregar extractor al pipeline"""
        self.extractores.append(extractor)
        self.logger.info("Extractor agregado", tipo=type(extractor).__name__)
    
    def agregar_transformador(self, transformador: TransformadorBase) -> None:
        """Agregar transformador al pipeline"""
        self.transformadores.append(transformador)
        self.logger.info("Transformador agregado", tipo=type(transformador).__name__)
    
    def agregar_cargador(self, cargador: CargadorBase) -> None:
        """Agregar cargador al pipeline"""
        self.cargadores.append(cargador)
        self.logger.info("Cargador agregado", tipo=type(cargador).__name__)
    
    def agregar_validador(self, validador: ValidadorBase) -> None:
        """Agregar validador al pipeline"""
        self.validadores.append(validador)
        self.logger.info("Validador agregado", tipo=type(validador).__name__)
    
    @logging_metodo(nombre_logger="pipeline", incluir_tiempo=True)
    async def ejecutar(self, parametros: Optional[Dict[str, Any]] = None) -> ResultadoPipeline:
        """
        Ejecutar el pipeline completo
        
        Args:
            parametros: Parámetros adicionales para la ejecución
            
        Returns:
            Resultado de la ejecución del pipeline
        """
        fecha_inicio = datetime.utcnow()
        errores = []
        advertencias = []
        archivos_salida = []
        reportes_generados = []
        
        try:
            self.logger.info(
                "Iniciando ejecución del pipeline",
                nombre=self.configuracion.nombre_pipeline,
                version=self.configuracion.version
            )
            
            # Fase 1: Extracción
            datos_extraidos = await self._ejecutar_extraccion(parametros)
            self.logger.info("Extracción completada", registros=len(datos_extraidos))
            
            # Fase 2: Validación de entrada
            if self.configuracion.validar_entrada:
                await self._ejecutar_validacion_entrada(datos_extraidos)
                self.logger.info("Validación de entrada completada")
            
            # Fase 3: Transformación
            datos_transformados = await self._ejecutar_transformacion(datos_extraidos)
            self.logger.info("Transformación completada", registros=len(datos_transformados))
            
            # Fase 4: Validación de salida
            if self.configuracion.validar_salida:
                await self._ejecutar_validacion_salida(datos_transformados)
                self.logger.info("Validación de salida completada")
            
            # Fase 5: Carga
            archivos_generados = await self._ejecutar_carga(datos_transformados)
            archivos_salida.extend(archivos_generados)
            self.logger.info("Carga completada", archivos=len(archivos_generados))
            
            # Calcular métricas finales
            metricas = calcular_metricas_calidad(datos_transformados)
            
            fecha_fin = datetime.utcnow()
            duracion = (fecha_fin - fecha_inicio).total_seconds()
            
            resultado = ResultadoPipeline(
                nombre_pipeline=self.configuracion.nombre_pipeline,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                duracion_segundos=duracion,
                registros_procesados=len(datos_extraidos),
                registros_exitosos=len(datos_transformados),
                registros_fallidos=len(datos_extraidos) - len(datos_transformados),
                tasa_exito=len(datos_transformados) / len(datos_extraidos) if datos_extraidos else 0,
                completitud_datos=metricas.get('completitud', 0),
                consistencia_datos=metricas.get('consistencia', 0),
                precision_datos=metricas.get('precision', 0),
                errores=errores,
                advertencias=advertencias,
                archivos_salida=archivos_salida,
                reportes_generados=reportes_generados
            )
            
            self.logger.info(
                "Pipeline ejecutado exitosamente",
                duracion_segundos=duracion,
                registros_procesados=resultado.registros_procesados,
                tasa_exito=resultado.tasa_exito
            )
            
            return resultado
            
        except Exception as e:
            fecha_fin = datetime.utcnow()
            duracion = (fecha_fin - fecha_inicio).total_seconds()
            
            self.logger.error(
                "Error en ejecución del pipeline",
                error=str(e),
                duracion_segundos=duracion
            )
            
            # Crear resultado con error
            return ResultadoPipeline(
                nombre_pipeline=self.configuracion.nombre_pipeline,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                duracion_segundos=duracion,
                registros_procesados=0,
                registros_exitosos=0,
                registros_fallidos=0,
                tasa_exito=0,
                completitud_datos=0,
                consistencia_datos=0,
                precision_datos=0,
                errores=[str(e)],
                advertencias=[],
                archivos_salida=[],
                reportes_generados=[]
            )
    
    async def _ejecutar_extraccion(self, parametros: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ejecutar fase de extracción"""
        datos_extraidos = []
        
        for extractor in self.extractores:
            try:
                datos = await extractor.extraer(parametros)
                datos_extraidos.extend(datos)
                self.logger.info(
                    "Datos extraídos",
                    extractor=type(extractor).__name__,
                    registros=len(datos)
                )
            except Exception as e:
                self.logger.error(
                    "Error en extracción",
                    extractor=type(extractor).__name__,
                    error=str(e)
                )
                raise
        
        return datos_extraidos
    
    async def _ejecutar_validacion_entrada(self, datos: List[Dict[str, Any]]) -> None:
        """Ejecutar validación de datos de entrada"""
        for validador in self.validadores:
            if hasattr(validador, 'validar_entrada'):
                await validador.validar_entrada(datos)
    
    async def _ejecutar_transformacion(self, datos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ejecutar fase de transformación"""
        datos_transformados = datos.copy()
        
        for transformador in self.transformadores:
            try:
                datos_transformados = await transformador.transformar(datos_transformados)
                self.logger.info(
                    "Datos transformados",
                    transformador=type(transformador).__name__,
                    registros=len(datos_transformados)
                )
            except Exception as e:
                self.logger.error(
                    "Error en transformación",
                    transformador=type(transformador).__name__,
                    error=str(e)
                )
                raise
        
        return datos_transformados
    
    async def _ejecutar_validacion_salida(self, datos: List[Dict[str, Any]]) -> None:
        """Ejecutar validación de datos de salida"""
        for validador in self.validadores:
            if hasattr(validador, 'validar_salida'):
                await validador.validar_salida(datos)
    
    async def _ejecutar_carga(self, datos: List[Dict[str, Any]]) -> List[str]:
        """Ejecutar fase de carga"""
        archivos_generados = []
        
        for cargador in self.cargadores:
            try:
                archivos = await cargador.cargar(datos)
                archivos_generados.extend(archivos)
                self.logger.info(
                    "Datos cargados",
                    cargador=type(cargador).__name__,
                    archivos=len(archivos)
                )
            except Exception as e:
                self.logger.error(
                    "Error en carga",
                    cargador=type(cargador).__name__,
                    error=str(e)
                )
                raise
        
        return archivos_generados
