"""
Servicio de Extracción de Entidades - Capa de Aplicación
Servicio principal para extracción de entidades nombradas
"""
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import structlog
from datetime import datetime

from ...dominio.entidades.entidad_nombrada import EntidadNombrada, TipoEntidad
from ...dominio.algoritmos.algoritmo_entidades import AlgoritmoEntidades
from ...utilidades.decoradores.decorador_logging import logging_metodo
from ...utilidades.decoradores.decorador_validacion import validar_parametros


class ServicioEntidades:
    """
    Servicio principal para extracción de entidades nombradas
    Orquesta diferentes algoritmos y proporciona una interfaz unificada
    """
    
    def __init__(self, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar servicio de entidades
        
        Args:
            configuracion: Configuración del servicio
        """
        self.configuracion = configuracion or {}
        self.logger = structlog.get_logger()
        
        # Algoritmos disponibles
        self.algoritmos: Dict[str, AlgoritmoEntidades] = {}
        
        # Configuración por defecto
        self.configuracion_default = {
            "algoritmo_por_defecto": "spacy",
            "algoritmos_habilitados": ["spacy"],
            "cache_habilitado": True,
            "cache_ttl": 3600,  # 1 hora
            "timeout_extraccion": 30,  # segundos
            "filtro_duplicados": True,
            "umbral_confianza": 0.5,
            "incluir_contexto": True,
            "incluir_dependencias": False
        }
        
        # Combinar configuración
        self.configuracion_final = {**self.configuracion_default, **self.configuracion}
    
    def registrar_algoritmo(self, nombre: str, algoritmo: AlgoritmoEntidades) -> None:
        """
        Registrar un algoritmo de extracción de entidades
        
        Args:
            nombre: Nombre del algoritmo
            algoritmo: Instancia del algoritmo
        """
        self.algoritmos[nombre] = algoritmo
        self.logger.info(f"Algoritmo de entidades registrado: {nombre}")
    
    def obtener_algoritmo(self, nombre: str) -> Optional[AlgoritmoEntidades]:
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
    
    @logging_metodo(nombre_logger="servicio_entidades", incluir_tiempo=True)
    @validar_parametros(validar_tipos=True)
    async def extraer_entidades(
        self, 
        texto: str, 
        idioma: str = "es",
        algoritmo: Optional[str] = None,
        tipos_entidades: Optional[List[str]] = None,
        umbral_confianza: Optional[float] = None
    ) -> List[EntidadNombrada]:
        """
        Extraer entidades de un texto
        
        Args:
            texto: Texto a analizar
            idioma: Idioma del texto
            algoritmo: Algoritmo específico a usar (opcional)
            tipos_entidades: Tipos de entidades a extraer (opcional)
            umbral_confianza: Umbral mínimo de confianza
            
        Returns:
            Lista de entidades extraídas
        """
        try:
            # Validar entrada
            if not texto or not texto.strip():
                raise ValueError("El texto no puede estar vacío")
            
            # Usar configuración por defecto si no se especifica
            if algoritmo is None:
                algoritmo = self.configuracion_final["algoritmo_por_defecto"]
            
            if umbral_confianza is None:
                umbral_confianza = self.configuracion_final["umbral_confianza"]
            
            # Obtener algoritmo
            algoritmo_instancia = self.obtener_algoritmo(algoritmo)
            if not algoritmo_instancia:
                raise ValueError(f"Algoritmo no encontrado: {algoritmo}")
            
            # Verificar si está habilitado
            if algoritmo not in self.configuracion_final["algoritmos_habilitados"]:
                raise ValueError(f"Algoritmo no habilitado: {algoritmo}")
            
            self.logger.info(
                "Iniciando extracción de entidades",
                texto_preview=texto[:100] + "..." if len(texto) > 100 else texto,
                idioma=idioma,
                algoritmo=algoritmo
            )
            
            # Ejecutar extracción con timeout
            timeout = self.configuracion_final["timeout_extraccion"]
            entidades = await asyncio.wait_for(
                algoritmo_instancia.extraer(texto, idioma),
                timeout=timeout
            )
            
            # Filtrar por tipos si se especifica
            if tipos_entidades:
                entidades = [
                    entidad for entidad in entidades
                    if entidad.tipo.value in tipos_entidades
                ]
            
            # Filtrar por confianza
            entidades = [
                entidad for entidad in entidades
                if entidad.confianza >= umbral_confianza
            ]
            
            # Filtrar duplicados si está habilitado
            if self.configuracion_final["filtro_duplicados"]:
                entidades = algoritmo_instancia._filtrar_entidades_duplicadas(entidades)
            
            self.logger.info(
                "Extracción de entidades completada",
                entidades_encontradas=len(entidades),
                tipos_unicos=len(set(entidad.tipo for entidad in entidades))
            )
            
            return entidades
            
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout en extracción de entidades: {algoritmo}")
            raise ValueError(f"Timeout en extracción de entidades con {algoritmo}")
        
        except Exception as e:
            self.logger.error(f"Error en extracción de entidades: {str(e)}")
            raise
    
    @logging_metodo(nombre_logger="servicio_entidades", incluir_tiempo=True)
    async def extraer_entidades_lote(
        self, 
        textos: List[str], 
        idioma: str = "es",
        algoritmo: Optional[str] = None,
        tipos_entidades: Optional[List[str]] = None
    ) -> List[List[EntidadNombrada]]:
        """
        Extraer entidades de múltiples textos
        
        Args:
            textos: Lista de textos a analizar
            idioma: Idioma de los textos
            algoritmo: Algoritmo específico a usar
            tipos_entidades: Tipos de entidades a extraer
            
        Returns:
            Lista de listas de entidades por texto
        """
        self.logger.info(f"Iniciando extracción de lote: {len(textos)} textos")
        
        # Procesar en paralelo
        tareas = [
            self.extraer_entidades(texto, idioma, algoritmo, tipos_entidades)
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
                resultados_validos.append([])
            else:
                resultados_validos.append(resultado)
        
        self.logger.info(
            f"Extracción de lote completada: {len(resultados_validos)} exitosos, {errores} errores"
        )
        
        return resultados_validos
    
    @logging_metodo(nombre_logger="servicio_entidades", incluir_tiempo=True)
    async def obtener_entidades_por_tipo(
        self, 
        texto: str, 
        tipo_entidad: str,
        idioma: str = "es",
        algoritmo: Optional[str] = None
    ) -> List[EntidadNombrada]:
        """
        Obtener entidades de un tipo específico
        
        Args:
            texto: Texto a analizar
            tipo_entidad: Tipo de entidad a extraer
            idioma: Idioma del texto
            algoritmo: Algoritmo específico a usar
            
        Returns:
            Lista de entidades del tipo especificado
        """
        entidades = await self.extraer_entidades(texto, idioma, algoritmo, [tipo_entidad])
        return entidades
    
    @logging_metodo(nombre_logger="servicio_entidades", incluir_tiempo=True)
    async def obtener_estadisticas_entidades(
        self, 
        entidades: List[EntidadNombrada]
    ) -> Dict[str, Any]:
        """
        Obtener estadísticas de una lista de entidades
        
        Args:
            entidades: Lista de entidades
            
        Returns:
            Diccionario con estadísticas
        """
        if not entidades:
            return {}
        
        # Estadísticas básicas
        total_entidades = len(entidades)
        
        # Distribución por tipo
        tipos = {}
        for entidad in entidades:
            tipo = entidad.tipo.value
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        # Estadísticas de confianza
        confianzas = [entidad.confianza for entidad in entidades]
        confianza_promedio = sum(confianzas) / len(confianzas)
        confianza_min = min(confianzas)
        confianza_max = max(confianzas)
        
        # Estadísticas de calidad
        calidades = [entidad.calidad_extraccion for entidad in entidades]
        calidad_promedio = sum(calidades) / len(calidades)
        
        # Entidades más confiables
        entidades_confiables = [e for e in entidades if e.es_confiable()]
        porcentaje_confiables = (len(entidades_confiables) / total_entidades) * 100
        
        # Entidades más importantes
        entidades_importantes = sorted(
            entidades, 
            key=lambda e: e.calcular_puntuacion_compuesta(), 
            reverse=True
        )[:5]
        
        estadisticas = {
            "total_entidades": total_entidades,
            "distribucion_tipos": tipos,
            "confianza": {
                "promedio": round(confianza_promedio, 3),
                "minima": round(confianza_min, 3),
                "maxima": round(confianza_max, 3)
            },
            "calidad": {
                "promedio": round(calidad_promedio, 3)
            },
            "entidades_confiables": {
                "cantidad": len(entidades_confiables),
                "porcentaje": round(porcentaje_confiables, 2)
            },
            "entidades_mas_importantes": [
                {
                    "texto": e.texto,
                    "tipo": e.tipo.value,
                    "confianza": e.confianza,
                    "puntuacion": e.calcular_puntuacion_compuesta()
                }
                for e in entidades_importantes
            ]
        }
        
        self.logger.info(f"Estadísticas calculadas para {total_entidades} entidades")
        
        return estadisticas
    
    @logging_metodo(nombre_logger="servicio_entidades", incluir_tiempo=True)
    async def buscar_entidades_similares(
        self, 
        entidad_referencia: EntidadNombrada,
        entidades: List[EntidadNombrada],
        umbral_similitud: float = 0.8
    ) -> List[EntidadNombrada]:
        """
        Buscar entidades similares a una entidad de referencia
        
        Args:
            entidad_referencia: Entidad de referencia
            entidades: Lista de entidades donde buscar
            umbral_similitud: Umbral de similitud
            
        Returns:
            Lista de entidades similares
        """
        entidades_similares = []
        
        for entidad in entidades:
            if entidad.es_similar_a(entidad_referencia, umbral_similitud):
                entidades_similares.append(entidad)
        
        # Ordenar por similitud (confianza)
        entidades_similares.sort(key=lambda e: e.confianza, reverse=True)
        
        self.logger.info(f"Encontradas {len(entidades_similares)} entidades similares")
        
        return entidades_similares
    
    @logging_metodo(nombre_logger="servicio_entidades", incluir_tiempo=True)
    async def agrupar_entidades_por_tipo(
        self, 
        entidades: List[EntidadNombrada]
    ) -> Dict[str, List[EntidadNombrada]]:
        """
        Agrupar entidades por tipo
        
        Args:
            entidades: Lista de entidades
            
        Returns:
            Diccionario con entidades agrupadas por tipo
        """
        grupos = {}
        
        for entidad in entidades:
            tipo = entidad.tipo.value
            if tipo not in grupos:
                grupos[tipo] = []
            grupos[tipo].append(entidad)
        
        # Ordenar cada grupo por confianza
        for tipo in grupos:
            grupos[tipo].sort(key=lambda e: e.confianza, reverse=True)
        
        self.logger.info(f"Entidades agrupadas en {len(grupos)} tipos")
        
        return grupos
    
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
