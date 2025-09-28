"""
Entidad Análisis de Sentimiento - Capa de Dominio
Representa el resultado de un análisis de sentimientos
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CategoriaSentimiento(Enum):
    """Categorías de sentimiento"""
    POSITIVO = "positivo"
    NEGATIVO = "negativo"
    NEUTRAL = "neutral"


class ModeloSentimiento(Enum):
    """Modelos de análisis de sentimientos"""
    VADER = "vader"
    TEXTBLOB = "textblob"
    BERT = "bert"
    ROBERTA = "roberta"
    SPACY = "spacy"


@dataclass
class AnalisisSentimiento:
    """
    Entidad que representa el resultado de un análisis de sentimientos
    Encapsula toda la información del análisis realizado
    """
    
    # Información básica
    texto: str
    idioma: str
    modelo_usado: ModeloSentimiento
    
    # Métricas de sentimiento
    polaridad: float  # -1.0 a 1.0
    subjetividad: float  # 0.0 a 1.0
    categoria: CategoriaSentimiento
    
    # Confianza y calidad
    confianza: float  # 0.0 a 1.0
    calidad_analisis: float  # 0.0 a 1.0
    
    # Información adicional
    palabras_clave: List[str]
    emociones_detectadas: Dict[str, float]
    
    # Metadatos
    fecha_analisis: datetime
    tiempo_procesamiento_ms: float
    version_modelo: Optional[str] = None
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.fecha_analisis is None:
            self.fecha_analisis = datetime.utcnow()
    
    def es_positivo(self) -> bool:
        """Verificar si el sentimiento es positivo"""
        return self.categoria == CategoriaSentimiento.POSITIVO
    
    def es_negativo(self) -> bool:
        """Verificar si el sentimiento es negativo"""
        return self.categoria == CategoriaSentimiento.NEGATIVO
    
    def es_neutral(self) -> bool:
        """Verificar si el sentimiento es neutral"""
        return self.categoria == CategoriaSentimiento.NEUTRAL
    
    def es_subjetivo(self) -> bool:
        """Verificar si el texto es subjetivo"""
        return self.subjetividad > 0.5
    
    def es_objetivo(self) -> bool:
        """Verificar si el texto es objetivo"""
        return self.subjetividad <= 0.5
    
    def obtener_intensidad(self) -> str:
        """Obtener intensidad del sentimiento"""
        intensidad_absoluta = abs(self.polaridad)
        
        if intensidad_absoluta >= 0.8:
            return "muy_alta"
        elif intensidad_absoluta >= 0.6:
            return "alta"
        elif intensidad_absoluta >= 0.4:
            return "media"
        elif intensidad_absoluta >= 0.2:
            return "baja"
        else:
            return "muy_baja"
    
    def obtener_resumen(self) -> str:
        """Obtener resumen del análisis"""
        intensidad = self.obtener_intensidad()
        subjetividad = "subjetivo" if self.es_subjetivo() else "objetivo"
        
        return f"Sentimiento {self.categoria.value} con intensidad {intensidad} ({subjetividad})"
    
    def es_confiable(self, umbral: float = 0.7) -> bool:
        """Verificar si el análisis es confiable"""
        return self.confianza >= umbral and self.calidad_analisis >= umbral
    
    def obtener_emocion_principal(self) -> Optional[str]:
        """Obtener la emoción principal detectada"""
        if not self.emociones_detectadas:
            return None
        
        return max(self.emociones_detectadas.items(), key=lambda x: x[1])[0]
    
    def obtener_palabras_mas_importantes(self, limite: int = 5) -> List[str]:
        """Obtener las palabras más importantes del análisis"""
        return self.palabras_clave[:limite]
    
    def calcular_puntuacion_compuesta(self) -> float:
        """Calcular puntuación compuesta del análisis"""
        # Combinar polaridad, confianza y calidad
        puntuacion_base = (self.polaridad + 1) / 2  # Normalizar a 0-1
        factor_confianza = self.confianza
        factor_calidad = self.calidad_analisis
        
        return (puntuacion_base * factor_confianza * factor_calidad)
    
    def __str__(self) -> str:
        """Representación string del análisis"""
        return f"AnalisisSentimiento(texto='{self.texto[:50]}...', categoria={self.categoria.value}, polaridad={self.polaridad:.2f})"
    
    def __repr__(self) -> str:
        """Representación detallada del análisis"""
        return (
            f"AnalisisSentimiento(texto='{self.texto[:30]}...', "
            f"categoria={self.categoria.value}, polaridad={self.polaridad:.2f}, "
            f"confianza={self.confianza:.2f}, modelo={self.modelo_usado.value})"
        )
