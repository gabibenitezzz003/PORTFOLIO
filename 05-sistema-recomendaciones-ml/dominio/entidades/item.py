"""
Entidad Item - Capa de Dominio
Representa un item del sistema de recomendaciones
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CategoriaItem(Enum):
    """Categorías de items"""
    ELECTRONICA = "electronica"
    ROPA = "ropa"
    HOGAR = "hogar"
    DEPORTES = "deportes"
    LIBROS = "libros"
    MUSICA = "musica"
    PELICULAS = "peliculas"
    JUEGOS = "juegos"
    BELLEZA = "belleza"
    AUTOMOTRIZ = "automotriz"
    OTRO = "otro"


class EstadoItem(Enum):
    """Estados de items"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    AGOTADO = "agotado"
    DESCONTINUADO = "descontinuado"


@dataclass
class Item:
    """
    Entidad que representa un item del sistema de recomendaciones
    Contiene información del producto y sus características
    """
    
    # Información básica
    id_item: str
    titulo: str
    descripcion: Optional[str] = None
    categoria: CategoriaItem = CategoriaItem.OTRO
    
    # Información comercial
    precio: Optional[float] = None
    precio_original: Optional[float] = None
    descuento: Optional[float] = None
    moneda: str = "USD"
    
    # Información de disponibilidad
    stock: int = 0
    estado: EstadoItem = EstadoItem.ACTIVO
    
    # Información de calidad
    rating_promedio: Optional[float] = None
    total_ratings: int = 0
    total_ventas: int = 0
    total_vistas: int = 0
    
    # Características del item
    caracteristicas: Dict[str, Any] = None
    tags: List[str] = None
    imagenes: List[str] = None
    
    # Información de contenido
    contenido_texto: Optional[str] = None
    embeddings: Optional[List[float]] = None
    
    # Metadatos
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    version: int = 1
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.fecha_creacion is None:
            self.fecha_creacion = datetime.utcnow()
        
        if self.fecha_actualizacion is None:
            self.fecha_actualizacion = datetime.utcnow()
        
        if self.caracteristicas is None:
            self.caracteristicas = {}
        
        if self.tags is None:
            self.tags = []
        
        if self.imagenes is None:
            self.imagenes = []
    
    def es_activo(self) -> bool:
        """Verificar si el item está activo"""
        return self.estado == EstadoItem.ACTIVO
    
    def esta_disponible(self) -> bool:
        """Verificar si el item está disponible"""
        return self.estado == EstadoItem.ACTIVO and self.stock > 0
    
    def tiene_descuento(self) -> bool:
        """Verificar si el item tiene descuento"""
        return self.descuento is not None and self.descuento > 0
    
    def calcular_porcentaje_descuento(self) -> float:
        """Calcular porcentaje de descuento"""
        if not self.tiene_descuento() or not self.precio_original or not self.precio:
            return 0.0
        
        return ((self.precio_original - self.precio) / self.precio_original) * 100
    
    def calcular_precio_final(self) -> float:
        """Calcular precio final del item"""
        if self.precio is not None:
            return self.precio
        
        if self.precio_original is not None and self.descuento is not None:
            return self.precio_original - self.descuento
        
        return 0.0
    
    def calcular_popularidad(self) -> float:
        """Calcular popularidad del item"""
        factores = []
        
        # Factor de ventas
        if self.total_ventas > 0:
            factor_ventas = min(1.0, self.total_ventas / 1000)
            factores.append(factor_ventas)
        
        # Factor de vistas
        if self.total_vistas > 0:
            factor_vistas = min(1.0, self.total_vistas / 10000)
            factores.append(factor_vistas)
        
        # Factor de ratings
        if self.rating_promedio is not None and self.total_ratings > 0:
            factor_rating = (self.rating_promedio / 5.0) * min(1.0, self.total_ratings / 100)
            factores.append(factor_rating)
        
        # Factor de disponibilidad
        if self.esta_disponible():
            factores.append(1.0)
        else:
            factores.append(0.5)
        
        return sum(factores) / len(factores) if factores else 0.0
    
    def calcular_tendencia(self, dias: int = 30) -> float:
        """Calcular tendencia del item en los últimos días"""
        # Esta es una implementación simplificada
        # En un sistema real, se calcularía basado en datos históricos
        
        if self.total_ventas == 0:
            return 0.0
        
        # Simular cálculo de tendencia basado en ventas recientes
        # En la práctica, se usarían datos históricos reales
        factor_tiempo = 1.0  # Simular que es reciente
        factor_crecimiento = min(1.0, self.total_ventas / 100)
        
        return factor_tiempo * factor_crecimiento
    
    def obtener_nivel_precio(self) -> str:
        """Obtener nivel de precio del item"""
        if not self.precio:
            return "no_disponible"
        
        if self.precio < 50:
            return "bajo"
        elif self.precio < 200:
            return "medio"
        elif self.precio < 500:
            return "alto"
        else:
            return "premium"
    
    def obtener_nivel_rating(self) -> str:
        """Obtener nivel de rating del item"""
        if not self.rating_promedio:
            return "sin_rating"
        
        if self.rating_promedio >= 4.5:
            return "excelente"
        elif self.rating_promedio >= 4.0:
            return "muy_bueno"
        elif self.rating_promedio >= 3.5:
            return "bueno"
        elif self.rating_promedio >= 3.0:
            return "regular"
        else:
            return "malo"
    
    def calcular_similitud_contenido(self, otro_item: 'Item') -> float:
        """Calcular similitud de contenido con otro item"""
        similitud = 0.0
        
        # Similitud de categoría
        if self.categoria == otro_item.categoria:
            similitud += 0.4
        
        # Similitud de precio
        if self.precio and otro_item.precio:
            diferencia_precio = abs(self.precio - otro_item.precio)
            precio_promedio = (self.precio + otro_item.precio) / 2
            if precio_promedio > 0:
                similitud_precio = max(0, 1 - diferencia_precio / precio_promedio)
                similitud += similitud_precio * 0.3
        
        # Similitud de tags
        if self.tags and otro_item.tags:
            tags_comunes = set(self.tags) & set(otro_item.tags)
            total_tags = set(self.tags) | set(otro_item.tags)
            if total_tags:
                similitud_tags = len(tags_comunes) / len(total_tags)
                similitud += similitud_tags * 0.3
        
        return min(1.0, similitud)
    
    def obtener_resumen(self) -> str:
        """Obtener resumen del item"""
        resumen_partes = []
        
        # Título
        resumen_partes.append(self.titulo)
        
        # Categoría
        resumen_partes.append(f"Categoría: {self.categoria.value}")
        
        # Precio
        if self.precio:
            precio_final = self.calcular_precio_final()
            resumen_partes.append(f"Precio: ${precio_final:.2f}")
            
            if self.tiene_descuento():
                porcentaje = self.calcular_porcentaje_descuento()
                resumen_partes.append(f"Descuento: {porcentaje:.1f}%")
        
        # Rating
        if self.rating_promedio:
            resumen_partes.append(f"Rating: {self.rating_promedio:.1f}/5 ({self.total_ratings} reseñas)")
        
        # Disponibilidad
        if self.esta_disponible():
            resumen_partes.append(f"Stock: {self.stock} unidades")
        else:
            resumen_partes.append("No disponible")
        
        return " | ".join(resumen_partes)
    
    def obtener_metadatos(self) -> Dict[str, Any]:
        """Obtener metadatos del item"""
        return {
            "id_item": self.id_item,
            "titulo": self.titulo,
            "categoria": self.categoria.value,
            "precio": self.precio,
            "precio_final": self.calcular_precio_final(),
            "descuento": self.descuento,
            "porcentaje_descuento": self.calcular_porcentaje_descuento(),
            "stock": self.stock,
            "estado": self.estado.value,
            "rating_promedio": self.rating_promedio,
            "total_ratings": self.total_ratings,
            "total_ventas": self.total_ventas,
            "total_vistas": self.total_vistas,
            "popularidad": self.calcular_popularidad(),
            "nivel_precio": self.obtener_nivel_precio(),
            "nivel_rating": self.obtener_nivel_rating(),
            "tags": self.tags,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    def actualizar_rating(self, nuevo_rating: float) -> None:
        """Actualizar rating del item"""
        if self.rating_promedio is None:
            self.rating_promedio = nuevo_rating
        else:
            self.rating_promedio = (self.rating_promedio * self.total_ratings + nuevo_rating) / (self.total_ratings + 1)
        
        self.total_ratings += 1
        self.fecha_actualizacion = datetime.utcnow()
    
    def agregar_venta(self, cantidad: int = 1) -> None:
        """Agregar una venta del item"""
        self.total_ventas += cantidad
        self.stock = max(0, self.stock - cantidad)
        self.fecha_actualizacion = datetime.utcnow()
    
    def agregar_vista(self) -> None:
        """Agregar una vista del item"""
        self.total_vistas += 1
        self.fecha_actualizacion = datetime.utcnow()
    
    def __str__(self) -> str:
        """Representación string del item"""
        return f"Item(id='{self.id_item}', titulo='{self.titulo}', categoria={self.categoria.value})"
    
    def __repr__(self) -> str:
        """Representación detallada del item"""
        return (
            f"Item(id='{self.id_item}', titulo='{self.titulo}', "
            f"categoria={self.categoria.value}, precio={self.precio}, "
            f"rating={self.rating_promedio})"
        )
