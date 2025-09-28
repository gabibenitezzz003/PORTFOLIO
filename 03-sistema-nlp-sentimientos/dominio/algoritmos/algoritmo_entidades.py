"""
Algoritmo de Extracción de Entidades - Capa de Dominio
Implementa diferentes algoritmos para extracción de entidades nombradas
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import structlog
from enum import Enum

from ..entidades.entidad_nombrada import EntidadNombrada, TipoEntidad


class AlgoritmoEntidades(ABC):
    """
    Clase base abstracta para algoritmos de extracción de entidades
    Implementa el patrón Strategy para diferentes algoritmos
    """
    
    def __init__(self, nombre: str, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar algoritmo de entidades
        
        Args:
            nombre: Nombre del algoritmo
            configuracion: Configuración específica del algoritmo
        """
        self.nombre = nombre
        self.configuracion = configuracion or {}
        self.logger = structlog.get_logger()
    
    @abstractmethod
    async def extraer(self, texto: str, idioma: str = "es") -> List[EntidadNombrada]:
        """
        Extraer entidades de un texto
        
        Args:
            texto: Texto a analizar
            idioma: Idioma del texto
            
        Returns:
            Lista de entidades extraídas
        """
        pass
    
    @abstractmethod
    def validar_configuracion(self) -> bool:
        """
        Validar configuración del algoritmo
        
        Returns:
            True si la configuración es válida
        """
        pass
    
    def obtener_metadatos(self) -> Dict[str, Any]:
        """
        Obtener metadatos del algoritmo
        
        Returns:
            Diccionario con metadatos
        """
        return {
            "nombre": self.nombre,
            "tipo": type(self).__name__,
            "configuracion": self.configuracion
        }
    
    def _mapear_tipo_entidad(self, tipo_spacy: str) -> TipoEntidad:
        """
        Mapear tipo de entidad de spaCy a tipo interno
        
        Args:
            tipo_spacy: Tipo de entidad de spaCy
            
        Returns:
            Tipo de entidad interno
        """
        mapeo = {
            'PERSON': TipoEntidad.PERSONA,
            'PER': TipoEntidad.PERSONA,
            'ORG': TipoEntidad.ORGANIZACION,
            'ORGANIZATION': TipoEntidad.ORGANIZACION,
            'GPE': TipoEntidad.LUGAR,
            'LOC': TipoEntidad.LOC,
            'FAC': TipoEntidad.FAC,
            'DATE': TipoEntidad.FECHA,
            'TIME': TipoEntidad.TIEMPO,
            'MONEY': TipoEntidad.DINERO,
            'PERCENT': TipoEntidad.PORCENTAJE,
            'QUANTITY': TipoEntidad.CANTIDAD,
            'EVENT': TipoEntidad.EVENTO,
            'WORK_OF_ART': TipoEntidad.OBRA_ARTE,
            'LAW': TipoEntidad.LEY,
            'LANGUAGE': TipoEntidad.IDIOMA,
            'NORP': TipoEntidad.NORP,
            'PRODUCT': TipoEntidad.PRODUCTO,
            'TECHNOLOGY': TipoEntidad.TECNOLOGIA,
            'MEDICINE': TipoEntidad.MEDICINA,
            'SCIENCE': TipoEntidad.CIENCIA,
            'MISC': TipoEntidad.OTRO
        }
        
        return mapeo.get(tipo_spacy, TipoEntidad.OTRO)
    
    def _calcular_confianza_entidad(
        self, 
        texto: str, 
        tipo: TipoEntidad, 
        contexto: str = ""
    ) -> float:
        """
        Calcular confianza de una entidad extraída
        
        Args:
            texto: Texto de la entidad
            tipo: Tipo de entidad
            contexto: Contexto de la entidad
            
        Returns:
            Valor de confianza (0.0 a 1.0)
        """
        factores = []
        
        # Factor de longitud del texto
        longitud = len(texto.strip())
        if longitud > 0:
            factor_longitud = min(1.0, longitud / 20)  # Normalizar a 20 caracteres
            factores.append(factor_longitud)
        
        # Factor de tipo de entidad
        tipos_confiables = [TipoEntidad.PERSONA, TipoEntidad.ORGANIZACION, TipoEntidad.LUGAR]
        if tipo in tipos_confiables:
            factor_tipo = 1.0
        else:
            factor_tipo = 0.8
        
        factores.append(factor_tipo)
        
        # Factor de contexto
        if contexto:
            factor_contexto = min(1.0, len(contexto) / 100)  # Normalizar a 100 caracteres
            factores.append(factor_contexto)
        
        # Factor de formato (capitalización, etc.)
        factor_formato = self._evaluar_formato_entidad(texto, tipo)
        factores.append(factor_formato)
        
        return sum(factores) / len(factores) if factores else 0.5
    
    def _evaluar_formato_entidad(self, texto: str, tipo: TipoEntidad) -> float:
        """
        Evaluar formato de la entidad
        
        Args:
            texto: Texto de la entidad
            tipo: Tipo de entidad
            
        Returns:
            Puntuación de formato (0.0 a 1.0)
        """
        puntuacion = 0.5  # Base
        
        # Verificar capitalización apropiada
        if tipo in [TipoEntidad.PERSONA, TipoEntidad.ORGANIZACION, TipoEntidad.LUGAR]:
            if texto.istitle() or texto.isupper():
                puntuacion += 0.3
        
        # Verificar longitud apropiada
        if 2 <= len(texto) <= 50:
            puntuacion += 0.2
        
        # Verificar caracteres apropiados
        if texto.replace(' ', '').replace('-', '').replace('.', '').isalnum():
            puntuacion += 0.2
        
        return min(1.0, puntuacion)
    
    def _calcular_calidad_extraccion(
        self, 
        entidades: List[EntidadNombrada], 
        texto: str
    ) -> float:
        """
        Calcular calidad general de la extracción
        
        Args:
            entidades: Lista de entidades extraídas
            texto: Texto original
            
        Returns:
            Valor de calidad (0.0 a 1.0)
        """
        if not entidades:
            return 0.0
        
        factores = []
        
        # Factor de cobertura (porcentaje del texto cubierto por entidades)
        caracteres_cubiertos = sum(entidad.fin - entidad.inicio for entidad in entidades)
        cobertura = caracteres_cubiertos / len(texto) if len(texto) > 0 else 0
        factor_cobertura = min(1.0, cobertura * 2)  # Normalizar
        factores.append(factor_cobertura)
        
        # Factor de diversidad de tipos
        tipos_unicos = len(set(entidad.tipo for entidad in entidades))
        factor_diversidad = min(1.0, tipos_unicos / 5)  # Normalizar a 5 tipos
        factores.append(factor_diversidad)
        
        # Factor de confianza promedio
        confianza_promedio = sum(entidad.confianza for entidad in entidades) / len(entidades)
        factores.append(confianza_promedio)
        
        # Factor de solapamiento (penalizar entidades que se solapan)
        factor_solapamiento = self._calcular_factor_solapamiento(entidades)
        factores.append(factor_solapamiento)
        
        return sum(factores) / len(factores)
    
    def _calcular_factor_solapamiento(self, entidades: List[EntidadNombrada]) -> float:
        """
        Calcular factor de solapamiento entre entidades
        
        Args:
            entidades: Lista de entidades
            
        Returns:
            Factor de solapamiento (0.0 a 1.0, donde 1.0 es sin solapamiento)
        """
        if len(entidades) <= 1:
            return 1.0
        
        solapamientos = 0
        total_comparaciones = 0
        
        for i in range(len(entidades)):
            for j in range(i + 1, len(entidades)):
                entidad1 = entidades[i]
                entidad2 = entidades[j]
                
                # Verificar si hay solapamiento
                if (entidad1.inicio < entidad2.fin and entidad2.inicio < entidad1.fin):
                    solapamientos += 1
                
                total_comparaciones += 1
        
        if total_comparaciones == 0:
            return 1.0
        
        factor_solapamiento = 1.0 - (solapamientos / total_comparaciones)
        return max(0.0, factor_solapamiento)
    
    def _filtrar_entidades_duplicadas(self, entidades: List[EntidadNombrada]) -> List[EntidadNombrada]:
        """
        Filtrar entidades duplicadas o muy similares
        
        Args:
            entidades: Lista de entidades
            
        Returns:
            Lista de entidades sin duplicados
        """
        if not entidades:
            return []
        
        entidades_filtradas = []
        
        for entidad in entidades:
            es_duplicada = False
            
            for entidad_existente in entidades_filtradas:
                if entidad.es_similar_a(entidad_existente):
                    # Mantener la entidad con mayor confianza
                    if entidad.confianza > entidad_existente.confianza:
                        entidades_filtradas.remove(entidad_existente)
                        entidades_filtradas.append(entidad)
                    es_duplicada = True
                    break
            
            if not es_duplicada:
                entidades_filtradas.append(entidad)
        
        return entidades_filtradas
    
    def _obtener_contexto_entidad(
        self, 
        texto: str, 
        inicio: int, 
        fin: int, 
        ventana: int = 50
    ) -> Tuple[str, str]:
        """
        Obtener contexto anterior y posterior de una entidad
        
        Args:
            texto: Texto completo
            inicio: Posición de inicio de la entidad
            fin: Posición de fin de la entidad
            ventana: Tamaño de la ventana de contexto
            
        Returns:
            Tupla con (contexto_anterior, contexto_posterior)
        """
        # Contexto anterior
        inicio_contexto_anterior = max(0, inicio - ventana)
        contexto_anterior = texto[inicio_contexto_anterior:inicio].strip()
        
        # Contexto posterior
        fin_contexto_posterior = min(len(texto), fin + ventana)
        contexto_posterior = texto[fin:fin_contexto_posterior].strip()
        
        return contexto_anterior, contexto_posterior
    
    def _obtener_oracion_completa(
        self, 
        texto: str, 
        posicion: int
    ) -> Optional[str]:
        """
        Obtener la oración completa que contiene una posición
        
        Args:
            texto: Texto completo
            posicion: Posición en el texto
            
        Returns:
            Oración completa o None si no se encuentra
        """
        # Buscar inicio de la oración
        inicio_oracion = posicion
        while inicio_oracion > 0 and texto[inicio_oracion - 1] not in '.!?':
            inicio_oracion -= 1
        
        # Buscar fin de la oración
        fin_oracion = posicion
        while fin_oracion < len(texto) and texto[fin_oracion] not in '.!?':
            fin_oracion += 1
        
        if inicio_oracion < fin_oracion:
            return texto[inicio_oracion:fin_oracion].strip()
        
        return None
