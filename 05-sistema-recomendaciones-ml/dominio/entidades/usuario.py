"""
Entidad Usuario - Capa de Dominio
Representa un usuario del sistema de recomendaciones
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TipoUsuario(Enum):
    """Tipos de usuario"""
    NUEVO = "nuevo"
    ACTIVO = "activo"
    PREMIUM = "premium"
    INACTIVO = "inactivo"


class Genero(Enum):
    """Géneros de usuario"""
    MASCULINO = "masculino"
    FEMENINO = "femenino"
    OTRO = "otro"
    NO_ESPECIFICADO = "no_especificado"


@dataclass
class Usuario:
    """
    Entidad que representa un usuario del sistema de recomendaciones
    Contiene información del perfil y comportamiento del usuario
    """
    
    # Información básica
    id_usuario: str
    email: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    
    # Información demográfica
    edad: Optional[int] = None
    genero: Optional[Genero] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    
    # Información del perfil
    tipo_usuario: TipoUsuario = TipoUsuario.NUEVO
    fecha_registro: Optional[datetime] = None
    ultima_actividad: Optional[datetime] = None
    
    # Preferencias explícitas
    categorias_preferidas: List[str] = None
    marcas_preferidas: List[str] = None
    rango_precio_preferido: Optional[Dict[str, float]] = None
    
    # Comportamiento y estadísticas
    total_interacciones: int = 0
    total_compras: int = 0
    total_ratings: int = 0
    rating_promedio_dado: Optional[float] = None
    
    # Características calculadas
    caracteristicas: Dict[str, Any] = None
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
        
        if self.categorias_preferidas is None:
            self.categorias_preferidas = []
        
        if self.marcas_preferidas is None:
            self.marcas_preferidas = []
        
        if self.caracteristicas is None:
            self.caracteristicas = {}
    
    def es_nuevo(self) -> bool:
        """Verificar si es un usuario nuevo"""
        return self.tipo_usuario == TipoUsuario.NUEVO
    
    def es_activo(self) -> bool:
        """Verificar si es un usuario activo"""
        return self.tipo_usuario == TipoUsuario.ACTIVO
    
    def es_premium(self) -> bool:
        """Verificar si es un usuario premium"""
        return self.tipo_usuario == TipoUsuario.PREMIUM
    
    def es_inactivo(self) -> bool:
        """Verificar si es un usuario inactivo"""
        return self.tipo_usuario == TipoUsuario.INACTIVO
    
    def calcular_dias_registro(self) -> int:
        """Calcular días desde el registro"""
        if not self.fecha_registro:
            return 0
        
        delta = datetime.utcnow() - self.fecha_registro
        return delta.days
    
    def calcular_dias_inactividad(self) -> int:
        """Calcular días de inactividad"""
        if not self.ultima_actividad:
            return self.calcular_dias_registro()
        
        delta = datetime.utcnow() - self.ultima_actividad
        return delta.days
    
    def es_activo_reciente(self, dias: int = 30) -> bool:
        """Verificar si ha estado activo recientemente"""
        return self.calcular_dias_inactividad() <= dias
    
    def calcular_nivel_actividad(self) -> str:
        """Calcular nivel de actividad del usuario"""
        dias_inactividad = self.calcular_dias_inactividad()
        
        if dias_inactividad <= 7:
            return "muy_activo"
        elif dias_inactividad <= 30:
            return "activo"
        elif dias_inactividad <= 90:
            return "moderado"
        elif dias_inactividad <= 180:
            return "bajo"
        else:
            return "inactivo"
    
    def calcular_valor_usuario(self) -> float:
        """Calcular valor del usuario basado en su comportamiento"""
        factores = []
        
        # Factor de interacciones
        if self.total_interacciones > 0:
            factor_interacciones = min(1.0, self.total_interacciones / 100)
            factores.append(factor_interacciones)
        
        # Factor de compras
        if self.total_compras > 0:
            factor_compras = min(1.0, self.total_compras / 50)
            factores.append(factor_compras)
        
        # Factor de ratings
        if self.total_ratings > 0:
            factor_ratings = min(1.0, self.total_ratings / 20)
            factores.append(factor_ratings)
        
        # Factor de antigüedad
        dias_registro = self.calcular_dias_registro()
        if dias_registro > 0:
            factor_antiguedad = min(1.0, dias_registro / 365)
            factores.append(factor_antiguedad)
        
        # Factor de actividad reciente
        if self.es_activo_reciente():
            factores.append(1.0)
        else:
            factores.append(0.5)
        
        # Factor de tipo de usuario
        if self.tipo_usuario == TipoUsuario.PREMIUM:
            factores.append(1.5)
        elif self.tipo_usuario == TipoUsuario.ACTIVO:
            factores.append(1.0)
        else:
            factores.append(0.5)
        
        return sum(factores) / len(factores) if factores else 0.0
    
    def obtener_perfil_completo(self) -> Dict[str, Any]:
        """Obtener perfil completo del usuario"""
        return {
            "id_usuario": self.id_usuario,
            "email": self.email,
            "nombre_completo": f"{self.nombre} {self.apellido}" if self.nombre and self.apellido else None,
            "edad": self.edad,
            "genero": self.genero.value if self.genero else None,
            "ubicacion": f"{self.ciudad}, {self.pais}" if self.ciudad and self.pais else None,
            "tipo_usuario": self.tipo_usuario.value,
            "dias_registro": self.calcular_dias_registro(),
            "dias_inactividad": self.calcular_dias_inactividad(),
            "nivel_actividad": self.calcular_nivel_actividad(),
            "valor_usuario": self.calcular_valor_usuario(),
            "estadisticas": {
                "total_interacciones": self.total_interacciones,
                "total_compras": self.total_compras,
                "total_ratings": self.total_ratings,
                "rating_promedio_dado": self.rating_promedio_dado
            },
            "preferencias": {
                "categorias": self.categorias_preferidas,
                "marcas": self.marcas_preferidas,
                "rango_precio": self.rango_precio_preferido
            }
        }
    
    def actualizar_actividad(self) -> None:
        """Actualizar timestamp de última actividad"""
        self.ultima_actividad = datetime.utcnow()
        self.fecha_actualizacion = datetime.utcnow()
    
    def agregar_interaccion(self, tipo: str, item_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Agregar una interacción del usuario"""
        self.total_interacciones += 1
        self.actualizar_actividad()
        
        # Actualizar tipo de usuario si es necesario
        if self.tipo_usuario == TipoUsuario.NUEVO and self.total_interacciones >= 5:
            self.tipo_usuario = TipoUsuario.ACTIVO
        
        # Agregar a características si es necesario
        if metadata:
            if "categoria" in metadata:
                categoria = metadata["categoria"]
                if categoria not in self.categorias_preferidas:
                    self.categorias_preferidas.append(categoria)
    
    def agregar_rating(self, item_id: str, rating: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Agregar un rating del usuario"""
        self.total_ratings += 1
        
        # Actualizar rating promedio
        if self.rating_promedio_dado is None:
            self.rating_promedio_dado = rating
        else:
            self.rating_promedio_dado = (self.rating_promedio_dado * (self.total_ratings - 1) + rating) / self.total_ratings
        
        self.actualizar_actividad()
    
    def agregar_compra(self, item_id: str, monto: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Agregar una compra del usuario"""
        self.total_compras += 1
        self.actualizar_actividad()
        
        # Actualizar tipo de usuario si es necesario
        if self.tipo_usuario == TipoUsuario.ACTIVO and self.total_compras >= 10:
            self.tipo_usuario = TipoUsuario.PREMIUM
    
    def es_similar_a(self, otro_usuario: 'Usuario', umbral: float = 0.7) -> bool:
        """Verificar si es similar a otro usuario"""
        # Comparar características demográficas
        similitud_demografica = 0.0
        if self.edad and otro_usuario.edad:
            diferencia_edad = abs(self.edad - otro_usuario.edad)
            similitud_demografica += max(0, 1 - diferencia_edad / 50)
        
        if self.genero and otro_usuario.genero and self.genero == otro_usuario.genero:
            similitud_demografica += 1.0
        
        if self.pais and otro_usuario.pais and self.pais == otro_usuario.pais:
            similitud_demografica += 1.0
        
        # Comparar preferencias
        similitud_preferencias = 0.0
        if self.categorias_preferidas and otro_usuario.categorias_preferidas:
            categorias_comunes = set(self.categorias_preferidas) & set(otro_usuario.categorias_preferidas)
            total_categorias = set(self.categorias_preferidas) | set(otro_usuario.categorias_preferidas)
            if total_categorias:
                similitud_preferencias = len(categorias_comunes) / len(total_categorias)
        
        # Calcular similitud total
        similitud_total = (similitud_demografica + similitud_preferencias) / 2
        
        return similitud_total >= umbral
    
    def __str__(self) -> str:
        """Representación string del usuario"""
        return f"Usuario(id='{self.id_usuario}', email='{self.email}', tipo={self.tipo_usuario.value})"
    
    def __repr__(self) -> str:
        """Representación detallada del usuario"""
        return (
            f"Usuario(id='{self.id_usuario}', email='{self.email}', "
            f"tipo={self.tipo_usuario.value}, interacciones={self.total_interacciones})"
        )
