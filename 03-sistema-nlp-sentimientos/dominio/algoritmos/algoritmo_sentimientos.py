"""
Algoritmo de Análisis de Sentimientos - Capa de Dominio
Implementa diferentes algoritmos para análisis de sentimientos
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import structlog
from enum import Enum

from ..entidades.analisis_sentimiento import AnalisisSentimiento, CategoriaSentimiento, ModeloSentimiento


class AlgoritmoSentimientos(ABC):
    """
    Clase base abstracta para algoritmos de análisis de sentimientos
    Implementa el patrón Strategy para diferentes algoritmos
    """
    
    def __init__(self, nombre: str, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar algoritmo de sentimientos
        
        Args:
            nombre: Nombre del algoritmo
            configuracion: Configuración específica del algoritmo
        """
        self.nombre = nombre
        self.configuracion = configuracion or {}
        self.logger = structlog.get_logger()
    
    @abstractmethod
    async def analizar(self, texto: str, idioma: str = "es") -> AnalisisSentimiento:
        """
        Analizar sentimientos de un texto
        
        Args:
            texto: Texto a analizar
            idioma: Idioma del texto
            
        Returns:
            Resultado del análisis de sentimientos
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
    
    def _categorizar_sentimiento(self, polaridad: float, subjetividad: float) -> CategoriaSentimiento:
        """
        Categorizar sentimiento basado en polaridad y subjetividad
        
        Args:
            polaridad: Valor de polaridad (-1.0 a 1.0)
            subjetividad: Valor de subjetividad (0.0 a 1.0)
            
        Returns:
            Categoría del sentimiento
        """
        # Umbrales configurables
        umbral_positivo = self.configuracion.get('umbral_positivo', 0.1)
        umbral_negativo = self.configuracion.get('umbral_negativo', -0.1)
        
        if polaridad > umbral_positivo:
            return CategoriaSentimiento.POSITIVO
        elif polaridad < umbral_negativo:
            return CategoriaSentimiento.NEGATIVO
        else:
            return CategoriaSentimiento.NEUTRAL
    
    def _calcular_confianza(self, polaridad: float, subjetividad: float) -> float:
        """
        Calcular confianza del análisis
        
        Args:
            polaridad: Valor de polaridad
            subjetividad: Valor de subjetividad
            
        Returns:
            Valor de confianza (0.0 a 1.0)
        """
        # Confianza basada en la intensidad de la polaridad
        intensidad_polaridad = abs(polaridad)
        
        # Confianza basada en la subjetividad (textos subjetivos son más fáciles de analizar)
        factor_subjetividad = subjetividad
        
        # Combinar factores
        confianza = (intensidad_polaridad * 0.7) + (factor_subjetividad * 0.3)
        
        return min(1.0, max(0.0, confianza))
    
    def _calcular_calidad(self, texto: str, polaridad: float) -> float:
        """
        Calcular calidad del análisis
        
        Args:
            texto: Texto analizado
            polaridad: Valor de polaridad obtenido
            
        Returns:
            Valor de calidad (0.0 a 1.0)
        """
        factores = []
        
        # Factor de longitud del texto
        longitud = len(texto.strip())
        if longitud > 0:
            factor_longitud = min(1.0, longitud / 100)  # Normalizar a 100 caracteres
            factores.append(factor_longitud)
        
        # Factor de consistencia (polaridad no extrema)
        if -0.5 <= polaridad <= 0.5:
            factor_consistencia = 1.0
        else:
            factor_consistencia = 0.8
        
        factores.append(factor_consistencia)
        
        # Factor de presencia de palabras de sentimiento
        palabras_sentimiento = self._contar_palabras_sentimiento(texto)
        factor_palabras = min(1.0, palabras_sentimiento / 5)  # Normalizar a 5 palabras
        factores.append(factor_palabras)
        
        return sum(factores) / len(factores) if factores else 0.5
    
    def _contar_palabras_sentimiento(self, texto: str) -> int:
        """
        Contar palabras relacionadas con sentimientos
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Número de palabras de sentimiento
        """
        # Lista básica de palabras de sentimiento (se puede expandir)
        palabras_positivas = [
            'bueno', 'excelente', 'fantástico', 'genial', 'perfecto', 'maravilloso',
            'increíble', 'asombroso', 'magnífico', 'estupendo', 'formidable',
            'good', 'excellent', 'fantastic', 'great', 'perfect', 'wonderful',
            'amazing', 'awesome', 'magnificent', 'terrific', 'outstanding'
        ]
        
        palabras_negativas = [
            'malo', 'terrible', 'horrible', 'pésimo', 'fatal', 'desastroso',
            'abominable', 'atroz', 'espantoso', 'repugnante', 'odioso',
            'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hateful',
            'atrocious', 'abominable', 'repugnant', 'odious'
        ]
        
        texto_lower = texto.lower()
        palabras_positivas_encontradas = sum(1 for palabra in palabras_positivas if palabra in texto_lower)
        palabras_negativas_encontradas = sum(1 for palabra in palabras_negativas if palabra in texto_lower)
        
        return palabras_positivas_encontradas + palabras_negativas_encontradas
    
    def _extraer_palabras_clave(self, texto: str, limite: int = 10) -> List[str]:
        """
        Extraer palabras clave del texto
        
        Args:
            texto: Texto a analizar
            limite: Número máximo de palabras clave
            
        Returns:
            Lista de palabras clave
        """
        # Implementación simple (se puede mejorar con TF-IDF, etc.)
        palabras = texto.lower().split()
        
        # Filtrar palabras comunes
        palabras_comunes = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'pero', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'era', 'muy', 'años', 'hasta', 'desde', 'está', 'mi', 'porque', 'qué', 'sólo', 'han', 'yo', 'hay', 'vez', 'puede', 'todos', 'así', 'nos', 'ni', 'parte', 'tiene', 'él', 'uno', 'donde', 'bien', 'tiempo', 'mismo', 'ese', 'ahora', 'cada', 'e', 'vida', 'otro', 'después', 'te', 'otros', 'aunque', 'esa', 'esos', 'estas', 'estos', 'otra', 'otras', 'otro', 'otros', 'poco', 'tan', 'tanto', 'toda', 'todas', 'todo', 'todos', 'tres', 'tu', 'tus', 'tuya', 'tuyas', 'tuyo', 'tuyos', 'tu', 'tus', 'tuya', 'tuyas', 'tuyo', 'tuyos', 'tu', 'tus', 'tuya', 'tuyas', 'tuyo', 'tuyos'
        }
        
        palabras_filtradas = [palabra for palabra in palabras if palabra not in palabras_comunes and len(palabra) > 2]
        
        # Contar frecuencia
        frecuencia = {}
        for palabra in palabras_filtradas:
            frecuencia[palabra] = frecuencia.get(palabra, 0) + 1
        
        # Ordenar por frecuencia y devolver las más frecuentes
        palabras_ordenadas = sorted(frecuencia.items(), key=lambda x: x[1], reverse=True)
        
        return [palabra for palabra, _ in palabras_ordenadas[:limite]]
    
    def _detectar_emociones(self, texto: str) -> Dict[str, float]:
        """
        Detectar emociones en el texto
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Diccionario con emociones y sus intensidades
        """
        # Implementación básica de detección de emociones
        emociones = {
            'alegria': 0.0,
            'tristeza': 0.0,
            'ira': 0.0,
            'miedo': 0.0,
            'sorpresa': 0.0,
            'disgusto': 0.0
        }
        
        # Palabras clave para cada emoción (se puede expandir)
        palabras_emociones = {
            'alegria': ['feliz', 'contento', 'alegre', 'gozoso', 'dichoso', 'happy', 'joyful', 'cheerful'],
            'tristeza': ['triste', 'melancólico', 'deprimido', 'apenado', 'sad', 'melancholy', 'depressed'],
            'ira': ['enojado', 'furioso', 'irritado', 'molesto', 'angry', 'furious', 'irritated'],
            'miedo': ['asustado', 'aterrorizado', 'nervioso', 'ansioso', 'afraid', 'terrified', 'nervous'],
            'sorpresa': ['sorprendido', 'asombrado', 'impresionado', 'surprised', 'amazed', 'impressed'],
            'disgusto': ['disgustado', 'repugnado', 'asqueado', 'disgusted', 'repulsed', 'revolted']
        }
        
        texto_lower = texto.lower()
        
        for emocion, palabras in palabras_emociones.items():
            conteo = sum(1 for palabra in palabras if palabra in texto_lower)
            emociones[emocion] = min(1.0, conteo / 3)  # Normalizar a 3 palabras
        
        return emociones
