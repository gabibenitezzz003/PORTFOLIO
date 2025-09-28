"""
Entidad Recomendación - Capa de Dominio
Representa una recomendación generada por el sistema
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TipoAlgoritmo(Enum):
    """Tipos de algoritmos de recomendación"""
    COLABORATIVO = "colaborativo"
    CONTENIDO = "contenido"
    HIBRIDO = "hibrido"
    DEEP_LEARNING = "deep_learning"
    MATRIX_FACTORIZATION = "matrix_factorization"


class TipoRecomendacion(Enum):
    """Tipos de recomendación"""
    USUARIO = "usuario"
    ITEM = "item"
    SIMILAR = "similar"
    POPULAR = "popular"
    TRENDING = "trending"


@dataclass
class Recomendacion:
    """
    Entidad que representa una recomendación generada por el sistema
    Contiene toda la información relevante de la recomendación
    """
    
    # Información básica
    item_id: str
    usuario_id: Optional[str] = None
    score: float = 0.0
    ranking: int = 0
    
    # Metadatos del algoritmo
    algoritmo_usado: TipoAlgoritmo = TipoAlgoritmo.HIBRIDO
    tipo_recomendacion: TipoRecomendacion = TipoRecomendacion.USUARIO
    
    # Información del item
    titulo: Optional[str] = None
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    imagen_url: Optional[str] = None
    
    # Justificación y explicación
    explicacion: Optional[str] = None
    razones: List[str] = None
    confianza: float = 0.0
    
    # Contexto y personalización
    contexto: Dict[str, Any] = None
    caracteristicas_usuario: Dict[str, Any] = None
    caracteristicas_item: Dict[str, Any] = None
    
    # Metadatos
    fecha_generacion: Optional[datetime] = None
    tiempo_procesamiento_ms: float = 0.0
    version_modelo: Optional[str] = None
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.fecha_generacion is None:
            self.fecha_generacion = datetime.utcnow()
        
        if self.razones is None:
            self.razones = []
        
        if self.contexto is None:
            self.contexto = {}
        
        if self.caracteristicas_usuario is None:
            self.caracteristicas_usuario = {}
        
        if self.caracteristicas_item is None:
            self.caracteristicas_item = {}
    
    def es_para_usuario(self) -> bool:
        """Verificar si es una recomendación para usuario"""
        return self.tipo_recomendacion == TipoRecomendacion.USUARIO
    
    def es_para_item(self) -> bool:
        """Verificar si es una recomendación para item"""
        return self.tipo_recomendacion == TipoRecomendacion.ITEM
    
    def es_similar(self) -> bool:
        """Verificar si es una recomendación de items similares"""
        return self.tipo_recomendacion == TipoRecomendacion.SIMILAR
    
    def es_popular(self) -> bool:
        """Verificar si es una recomendación popular"""
        return self.tipo_recomendacion == TipoRecomendacion.POPULAR
    
    def es_trending(self) -> bool:
        """Verificar si es una recomendación trending"""
        return self.tipo_recomendacion == TipoRecomendacion.TRENDING
    
    def obtener_nivel_confianza(self) -> str:
        """Obtener nivel de confianza de la recomendación"""
        if self.confianza >= 0.9:
            return "muy_alta"
        elif self.confianza >= 0.7:
            return "alta"
        elif self.confianza >= 0.5:
            return "media"
        elif self.confianza >= 0.3:
            return "baja"
        else:
            return "muy_baja"
    
    def es_confiable(self, umbral: float = 0.5) -> bool:
        """Verificar si la recomendación es confiable"""
        return self.confianza >= umbral
    
    def obtener_explicacion_completa(self) -> str:
        """Obtener explicación completa de la recomendación"""
        if self.explicacion:
            return self.explicacion
        
        explicacion_partes = []
        
        # Agregar tipo de recomendación
        if self.tipo_recomendacion == TipoRecomendacion.USUARIO:
            explicacion_partes.append("Recomendado para ti")
        elif self.tipo_recomendacion == TipoRecomendacion.SIMILAR:
            explicacion_partes.append("Similar a items que te gustan")
        elif self.tipo_recomendacion == TipoRecomendacion.POPULAR:
            explicacion_partes.append("Popular entre otros usuarios")
        elif self.tipo_recomendacion == TipoRecomendacion.TRENDING:
            explicacion_partes.append("Tendencia actual")
        
        # Agregar razones específicas
        if self.razones:
            explicacion_partes.append("Porque: " + ", ".join(self.razones))
        
        # Agregar nivel de confianza
        nivel_confianza = self.obtener_nivel_confianza()
        explicacion_partes.append(f"Confianza: {nivel_confianza}")
        
        return " | ".join(explicacion_partes)
    
    def calcular_relevancia(self) -> float:
        """Calcular relevancia de la recomendación"""
        factores = []
        
        # Factor de score
        if self.score > 0:
            factores.append(self.score)
        
        # Factor de confianza
        factores.append(self.confianza)
        
        # Factor de ranking (inverso)
        if self.ranking > 0:
            factor_ranking = 1.0 / self.ranking
            factores.append(factor_ranking)
        
        # Factor de contexto
        if self.contexto:
            factor_contexto = len(self.contexto) / 10.0  # Normalizar
            factores.append(min(1.0, factor_contexto))
        
        return sum(factores) / len(factores) if factores else 0.0
    
    def obtener_metadatos(self) -> Dict[str, Any]:
        """Obtener metadatos de la recomendación"""
        return {
            "item_id": self.item_id,
            "usuario_id": self.usuario_id,
            "score": self.score,
            "ranking": self.ranking,
            "algoritmo": self.algoritmo_usado.value,
            "tipo": self.tipo_recomendacion.value,
            "confianza": self.confianza,
            "relevancia": self.calcular_relevancia(),
            "fecha_generacion": self.fecha_generacion.isoformat() if self.fecha_generacion else None,
            "tiempo_procesamiento_ms": self.tiempo_procesamiento_ms
        }
    
    def es_valida(self) -> bool:
        """Verificar si la recomendación es válida"""
        # Verificar que tiene item_id
        if not self.item_id:
            return False
        
        # Verificar que tiene score válido
        if not isinstance(self.score, (int, float)) or self.score < 0:
            return False
        
        # Verificar que tiene ranking válido
        if not isinstance(self.ranking, int) or self.ranking < 0:
            return False
        
        # Verificar que tiene confianza válida
        if not isinstance(self.confianza, (int, float)) or not (0 <= self.confianza <= 1):
            return False
        
        return True
    
    def __str__(self) -> str:
        """Representación string de la recomendación"""
        return f"Recomendacion(item_id='{self.item_id}', score={self.score:.3f}, ranking={self.ranking})"
    
    def __repr__(self) -> str:
        """Representación detallada de la recomendación"""
        return (
            f"Recomendacion(item_id='{self.item_id}', usuario_id='{self.usuario_id}', "
            f"score={self.score:.3f}, ranking={self.ranking}, "
            f"algoritmo={self.algoritmo_usado.value}, confianza={self.confianza:.3f})"
        )
