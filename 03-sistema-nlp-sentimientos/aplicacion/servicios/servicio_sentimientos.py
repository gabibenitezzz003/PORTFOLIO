"""
Servicio de Análisis de Sentimientos - Capa de Aplicación
Servicio principal para análisis de sentimientos
"""
import asyncio
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

from dominio.entidades.analisis_sentimiento import AnalisisSentimiento, CategoriaSentimiento, ModeloSentimiento
from dominio.algoritmos.algoritmo_sentimientos import AlgoritmoSentimientos
from ...utilidades.decoradores.decorador_logging import logging_metodo
from ...utilidades.decoradores.decorador_validacion import validar_parametros


class ServicioSentimientos:
    """
    Servicio principal para análisis de sentimientos
    Orquesta diferentes algoritmos y proporciona una interfaz unificada
    """
    
    def __init__(self, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar servicio de sentimientos
        
        Args:
            configuracion: Configuración del servicio
        """
        self.configuracion = configuracion or {}
        self.logger = structlog.get_logger()
        
        # Algoritmos disponibles
        self.algoritmos: Dict[str, AlgoritmoSentimientos] = {}
        
        # Configuración por defecto
        self.configuracion_default = {
            "algoritmo_por_defecto": "spacy",
            "algoritmos_habilitados": ["spacy", "textblob", "vader"],
            "cache_habilitado": True,
            "cache_ttl": 3600,  # 1 hora
            "timeout_analisis": 30,  # segundos
            "incluir_emociones": True,
            "incluir_palabras_clave": True
        }
        
        # Combinar configuración
        self.configuracion_final = {**self.configuracion_default, **self.configuracion}
    
    def registrar_algoritmo(self, nombre: str, algoritmo: AlgoritmoSentimientos) -> None:
        """
        Registrar un algoritmo de análisis de sentimientos
        
        Args:
            nombre: Nombre del algoritmo
            algoritmo: Instancia del algoritmo
        """
        self.algoritmos[nombre] = algoritmo
        self.logger.info(f"Algoritmo registrado: {nombre}")
    
    def obtener_algoritmo(self, nombre: str) -> Optional[AlgoritmoSentimientos]:
        """
        Obtener un algoritmo por nombre
        
        Args:
            nombre: Nombre del algoritmo
            
        Returns:
            Algoritmo o None si no existe
        """
        return self.algoritmos.get(nombre)
    
    def listar_algoritmos_disponibles(self) -> List[str]:
        """
        Listar algoritmos disponibles
        
        Returns:
            Lista de nombres de algoritmos
        """
        return list(self.algoritmos.keys())
    
    @logging_metodo(nombre_logger="servicio_sentimientos", incluir_tiempo=True)
    @validar_parametros(validar_tipos=True)
    async def analizar_sentimiento(
        self, 
        texto: str, 
        idioma: str = "es",
        algoritmo: Optional[str] = None,
        incluir_emociones: Optional[bool] = None,
        incluir_palabras_clave: Optional[bool] = None
    ) -> AnalisisSentimiento:
        """
        Analizar sentimientos de un texto
        
        Args:
            texto: Texto a analizar
            idioma: Idioma del texto
            algoritmo: Algoritmo específico a usar (opcional)
            incluir_emociones: Si incluir análisis de emociones
            incluir_palabras_clave: Si incluir palabras clave
            
        Returns:
            Resultado del análisis de sentimientos
        """
        try:
            # Validar entrada
            if not texto or not texto.strip():
                raise ValueError("El texto no puede estar vacío")
            
            # Usar configuración por defecto si no se especifica
            if algoritmo is None:
                algoritmo = self.configuracion_final["algoritmo_por_defecto"]
            
            if incluir_emociones is None:
                incluir_emociones = self.configuracion_final["incluir_emociones"]
            
            if incluir_palabras_clave is None:
                incluir_palabras_clave = self.configuracion_final["incluir_palabras_clave"]
            
            # Obtener algoritmo
            algoritmo_instancia = self.obtener_algoritmo(algoritmo)
            if not algoritmo_instancia:
                raise ValueError(f"Algoritmo no encontrado: {algoritmo}")
            
            # Verificar si está habilitado
            if algoritmo not in self.configuracion_final["algoritmos_habilitados"]:
                raise ValueError(f"Algoritmo no habilitado: {algoritmo}")
            
            self.logger.info(
                "Iniciando análisis de sentimientos",
                texto_preview=texto[:100] + "..." if len(texto) > 100 else texto,
                idioma=idioma,
                algoritmo=algoritmo
            )
            
            # Ejecutar análisis con timeout
            timeout = self.configuracion_final["timeout_analisis"]
            resultado = await asyncio.wait_for(
                algoritmo_instancia.analizar(texto, idioma),
                timeout=timeout
            )
            
            # Enriquecer resultado si es necesario
            if incluir_emociones and not resultado.emociones_detectadas:
                resultado.emociones_detectadas = algoritmo_instancia._detectar_emociones(texto)
            
            if incluir_palabras_clave and not resultado.palabras_clave:
                resultado.palabras_clave = algoritmo_instancia._extraer_palabras_clave(texto)
            
            self.logger.info(
                "Análisis de sentimientos completado",
                categoria=resultado.categoria.value,
                polaridad=resultado.polaridad,
                confianza=resultado.confianza
            )
            
            return resultado
            
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout en análisis de sentimientos: {algoritmo}")
            raise ValueError(f"Timeout en análisis de sentimientos con {algoritmo}")
        
        except Exception as e:
            self.logger.error(f"Error en análisis de sentimientos: {str(e)}")
            raise
    
    @logging_metodo(nombre_logger="servicio_sentimientos", incluir_tiempo=True)
    async def analizar_sentimientos_lote(
        self, 
        textos: List[str], 
        idioma: str = "es",
        algoritmo: Optional[str] = None
    ) -> List[AnalisisSentimiento]:
        """
        Analizar sentimientos de múltiples textos
        
        Args:
            textos: Lista de textos a analizar
            idioma: Idioma de los textos
            algoritmo: Algoritmo específico a usar
            
        Returns:
            Lista de resultados de análisis
        """
        self.logger.info(f"Iniciando análisis de lote: {len(textos)} textos")
        
        # Procesar en paralelo
        tareas = [
            self.analizar_sentimiento(texto, idioma, algoritmo)
            for texto in textos
        ]
        
        resultados = await asyncio.gather(*tareas, return_exceptions=True)
        
        # Filtrar errores
        resultados_validos = []
        errores = 0
        
        for i, resultado in enumerate(resultados):
            if isinstance(resultado, Exception):
                self.logger.error(f"Error en texto {i}: {str(resultado)}")
                errores += 1
            else:
                resultados_validos.append(resultado)
        
        self.logger.info(
            f"Análisis de lote completado: {len(resultados_validos)} exitosos, {errores} errores"
        )
        
        return resultados_validos
    
    @logging_metodo(nombre_logger="servicio_sentimientos", incluir_tiempo=True)
    async def comparar_algoritmos(
        self, 
        texto: str, 
        idioma: str = "es",
        algoritmos: Optional[List[str]] = None
    ) -> Dict[str, AnalisisSentimiento]:
        """
        Comparar diferentes algoritmos en el mismo texto
        
        Args:
            texto: Texto a analizar
            idioma: Idioma del texto
            algoritmos: Lista de algoritmos a comparar
            
        Returns:
            Diccionario con resultados por algoritmo
        """
        if algoritmos is None:
            algoritmos = self.configuracion_final["algoritmos_habilitados"]
        
        self.logger.info(f"Comparando algoritmos: {algoritmos}")
        
        resultados = {}
        
        for algoritmo in algoritmos:
            try:
                resultado = await self.analizar_sentimiento(texto, idioma, algoritmo)
                resultados[algoritmo] = resultado
            except Exception as e:
                self.logger.error(f"Error con algoritmo {algoritmo}: {str(e)}")
                resultados[algoritmo] = None
        
        return resultados
    
    @logging_metodo(nombre_logger="servicio_sentimientos", incluir_tiempo=True)
    async def obtener_estadisticas_analisis(
        self, 
        analisis: List[AnalisisSentimiento]
    ) -> Dict[str, Any]:
        """
        Obtener estadísticas de una lista de análisis
        
        Args:
            analisis: Lista de análisis de sentimientos
            
        Returns:
            Diccionario con estadísticas
        """
        if not analisis:
            return {}
        
        # Estadísticas básicas
        total_analisis = len(analisis)
        
        # Distribución por categoría
        categorias = {}
        for analisis_item in analisis:
            categoria = analisis_item.categoria.value
            categorias[categoria] = categorias.get(categoria, 0) + 1
        
        # Estadísticas de polaridad
        polaridades = [a.polaridad for a in analisis]
        polaridad_promedio = sum(polaridades) / len(polaridades)
        polaridad_min = min(polaridades)
        polaridad_max = max(polaridades)
        
        # Estadísticas de subjetividad
        subjetividades = [a.subjetividad for a in analisis]
        subjetividad_promedio = sum(subjetividades) / len(subjetividades)
        
        # Estadísticas de confianza
        confianzas = [a.confianza for a in analisis]
        confianza_promedio = sum(confianzas) / len(confianzas)
        
        # Análisis de emociones
        emociones_totales = {}
        for analisis_item in analisis:
            for emocion, intensidad in analisis_item.emociones_detectadas.items():
                emociones_totales[emocion] = emociones_totales.get(emocion, 0) + intensidad
        
        # Normalizar emociones
        if emociones_totales:
            total_emociones = sum(emociones_totales.values())
            emociones_normalizadas = {
                emocion: intensidad / total_emociones
                for emocion, intensidad in emociones_totales.items()
            }
        else:
            emociones_normalizadas = {}
        
        estadisticas = {
            "total_analisis": total_analisis,
            "distribucion_categorias": categorias,
            "polaridad": {
                "promedio": round(polaridad_promedio, 3),
                "minima": round(polaridad_min, 3),
                "maxima": round(polaridad_max, 3)
            },
            "subjetividad": {
                "promedio": round(subjetividad_promedio, 3)
            },
            "confianza": {
                "promedio": round(confianza_promedio, 3)
            },
            "emociones_dominantes": emociones_normalizadas
        }
        
        self.logger.info(f"Estadísticas calculadas para {total_analisis} análisis")
        
        return estadisticas
    
    def obtener_configuracion(self) -> Dict[str, Any]:
        """
        Obtener configuración actual del servicio
        
        Returns:
            Diccionario con la configuración
        """
        return self.configuracion_final.copy()
    
    def actualizar_configuracion(self, nueva_configuracion: Dict[str, Any]) -> None:
        """
        Actualizar configuración del servicio
        
        Args:
            nueva_configuracion: Nueva configuración
        """
        self.configuracion_final.update(nueva_configuracion)
        self.logger.info("Configuración actualizada", nueva_configuracion=nueva_configuracion)
