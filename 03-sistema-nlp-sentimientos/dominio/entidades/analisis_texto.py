"""
Entidad Análisis de Texto - Capa de Dominio
Representa el resultado de un análisis completo de texto
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from .analisis_sentimiento import AnalisisSentimiento
from .entidad_nombrada import EntidadNombrada


class TipoAnalisis(Enum):
    """Tipos de análisis de texto"""
    SENTIMIENTO = "sentimiento"
    ENTIDADES = "entidades"
    COMPLETO = "completo"
    CLASIFICACION = "clasificacion"
    RESUMEN = "resumen"


class CategoriaTexto(Enum):
    """Categorías de clasificación de texto"""
    NOTICIA = "noticia"
    OPINION = "opinion"
    RESENA = "resena"
    SPAM = "spam"
    TECNICO = "tecnico"
    ACADEMICO = "academico"
    COMERCIAL = "comercial"
    SOCIAL = "social"
    OTRO = "otro"


@dataclass
class AnalisisTexto:
    """
    Entidad que representa el resultado de un análisis completo de texto
    Agrupa todos los análisis realizados sobre un texto
    """
    
    # Información básica
    texto: str
    idioma: str
    tipo_analisis: TipoAnalisis
    
    # Análisis de sentimientos
    analisis_sentimiento: Optional[AnalisisSentimiento] = None
    
    # Entidades extraídas
    entidades: List[EntidadNombrada] = None
    
    # Clasificación de texto
    categoria: Optional[CategoriaTexto] = None
    confianza_clasificacion: Optional[float] = None
    
    # Resumen
    resumen: Optional[str] = None
    palabras_clave: List[str] = None
    
    # Estadísticas del texto
    estadisticas: Dict[str, Any] = None
    
    # Metadatos
    fecha_analisis: Optional[datetime] = None
    tiempo_procesamiento_ms: float = 0.0
    version_modelos: Dict[str, str] = None
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.fecha_analisis is None:
            self.fecha_analisis = datetime.utcnow()
        
        if self.entidades is None:
            self.entidades = []
        
        if self.palabras_clave is None:
            self.palabras_clave = []
        
        if self.estadisticas is None:
            self.estadisticas = {}
        
        if self.version_modelos is None:
            self.version_modelos = {}
    
    def obtener_entidades_por_tipo(self, tipo: str) -> List[EntidadNombrada]:
        """Obtener entidades de un tipo específico"""
        return [entidad for entidad in self.entidades if entidad.tipo.value == tipo]
    
    def obtener_entidades_confiables(self, umbral: float = 0.7) -> List[EntidadNombrada]:
        """Obtener entidades confiables"""
        return [entidad for entidad in self.entidades if entidad.es_confiable(umbral)]
    
    def obtener_personas(self) -> List[EntidadNombrada]:
        """Obtener entidades de tipo persona"""
        return self.obtener_entidades_por_tipo("PERSON")
    
    def obtener_organizaciones(self) -> List[EntidadNombrada]:
        """Obtener entidades de tipo organización"""
        return self.obtener_entidades_por_tipo("ORG")
    
    def obtener_lugares(self) -> List[EntidadNombrada]:
        """Obtener entidades de tipo lugar"""
        lugares = []
        for entidad in self.entidades:
            if entidad.es_lugar():
                lugares.append(entidad)
        return lugares
    
    def obtener_fechas(self) -> List[EntidadNombrada]:
        """Obtener entidades de tipo fecha"""
        return self.obtener_entidades_por_tipo("DATE")
    
    def obtener_dinero(self) -> List[EntidadNombrada]:
        """Obtener entidades de tipo dinero"""
        return self.obtener_entidades_por_tipo("MONEY")
    
    def tiene_sentimiento_positivo(self) -> bool:
        """Verificar si el texto tiene sentimiento positivo"""
        if self.analisis_sentimiento:
            return self.analisis_sentimiento.es_positivo()
        return False
    
    def tiene_sentimiento_negativo(self) -> bool:
        """Verificar si el texto tiene sentimiento negativo"""
        if self.analisis_sentimiento:
            return self.analisis_sentimiento.es_negativo()
        return False
    
    def es_subjetivo(self) -> bool:
        """Verificar si el texto es subjetivo"""
        if self.analisis_sentimiento:
            return self.analisis_sentimiento.es_subjetivo()
        return False
    
    def obtener_resumen_entidades(self) -> Dict[str, int]:
        """Obtener resumen de entidades por tipo"""
        resumen = {}
        for entidad in self.entidades:
            tipo = entidad.tipo.value
            resumen[tipo] = resumen.get(tipo, 0) + 1
        return resumen
    
    def obtener_entidades_mas_importantes(self, limite: int = 5) -> List[EntidadNombrada]:
        """Obtener las entidades más importantes"""
        entidades_ordenadas = sorted(
            self.entidades,
            key=lambda e: e.calcular_puntuacion_compuesta(),
            reverse=True
        )
        return entidades_ordenadas[:limite]
    
    def calcular_complejidad(self) -> float:
        """Calcular complejidad del análisis"""
        factores = []
        
        # Factor de longitud del texto
        longitud = len(self.texto)
        factor_longitud = min(1.0, longitud / 1000)  # Normalizar a 1000 caracteres
        factores.append(factor_longitud)
        
        # Factor de número de entidades
        num_entidades = len(self.entidades)
        factor_entidades = min(1.0, num_entidades / 20)  # Normalizar a 20 entidades
        factores.append(factor_entidades)
        
        # Factor de diversidad de tipos de entidades
        tipos_unicos = len(set(entidad.tipo for entidad in self.entidades))
        factor_diversidad = min(1.0, tipos_unicos / 10)  # Normalizar a 10 tipos
        factores.append(factor_diversidad)
        
        # Factor de confianza promedio
        if self.entidades:
            confianza_promedio = sum(entidad.confianza for entidad in self.entidades) / len(self.entidades)
            factores.append(confianza_promedio)
        
        return sum(factores) / len(factores) if factores else 0.0
    
    def obtener_nivel_complejidad(self) -> str:
        """Obtener nivel de complejidad del análisis"""
        complejidad = self.calcular_complejidad()
        
        if complejidad >= 0.8:
            return "muy_alta"
        elif complejidad >= 0.6:
            return "alta"
        elif complejidad >= 0.4:
            return "media"
        elif complejidad >= 0.2:
            return "baja"
        else:
            return "muy_baja"
    
    def es_analisis_completo(self) -> bool:
        """Verificar si es un análisis completo"""
        return self.tipo_analisis == TipoAnalisis.COMPLETO
    
    def obtener_resumen_ejecutivo(self) -> str:
        """Obtener resumen ejecutivo del análisis"""
        resumen_partes = []
        
        # Información básica
        resumen_partes.append(f"Análisis de texto en {self.idioma}")
        
        # Sentimiento
        if self.analisis_sentimiento:
            sentimiento = self.analisis_sentimiento.obtener_resumen()
            resumen_partes.append(f"Sentimiento: {sentimiento}")
        
        # Entidades
        if self.entidades:
            num_entidades = len(self.entidades)
            resumen_entidades = self.obtener_resumen_entidades()
            entidades_principales = list(resumen_entidades.keys())[:3]
            resumen_partes.append(f"Entidades encontradas: {num_entidades} ({', '.join(entidades_principales)})")
        
        # Categoría
        if self.categoria:
            resumen_partes.append(f"Categoría: {self.categoria.value}")
        
        # Complejidad
        complejidad = self.obtener_nivel_complejidad()
        resumen_partes.append(f"Complejidad: {complejidad}")
        
        return " | ".join(resumen_partes)
    
    def __str__(self) -> str:
        """Representación string del análisis"""
        return f"AnalisisTexto(texto='{self.texto[:50]}...', tipo={self.tipo_analisis.value}, entidades={len(self.entidades)})"
    
    def __repr__(self) -> str:
        """Representación detallada del análisis"""
        return (
            f"AnalisisTexto(texto='{self.texto[:30]}...', "
            f"tipo={self.tipo_analisis.value}, idioma={self.idioma}, "
            f"entidades={len(self.entidades)}, "
            f"sentimiento={'Sí' if self.analisis_sentimiento else 'No'})"
        )
