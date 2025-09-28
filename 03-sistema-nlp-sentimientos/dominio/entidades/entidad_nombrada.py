"""
Entidad Entidad Nombrada - Capa de Dominio
Representa una entidad extraída del texto
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TipoEntidad(Enum):
    """Tipos de entidades nombradas"""
    PERSONA = "PERSON"
    ORGANIZACION = "ORG"
    LUGAR = "GPE"
    FECHA = "DATE"
    TIEMPO = "TIME"
    DINERO = "MONEY"
    PORCENTAJE = "PERCENT"
    CANTIDAD = "QUANTITY"
    EVENTO = "EVENT"
    OBRA_ARTE = "WORK_OF_ART"
    LEY = "LAW"
    IDIOMA = "LANGUAGE"
    NORP = "NORP"  # Nacionalidades, grupos religiosos o políticos
    FAC = "FAC"    # Instalaciones
    LOC = "LOC"    # Ubicaciones no geopolíticas
    PRODUCTO = "PRODUCT"
    TECNOLOGIA = "TECHNOLOGY"
    MEDICINA = "MEDICINE"
    CIENCIA = "SCIENCE"
    OTRO = "MISC"


@dataclass
class EntidadNombrada:
    """
    Entidad que representa una entidad extraída del texto
    Contiene información sobre la entidad y su contexto
    """
    
    # Información básica
    texto: str
    tipo: TipoEntidad
    inicio: int  # Posición de inicio en el texto
    fin: int     # Posición de fin en el texto
    
    # Confianza y calidad
    confianza: float  # 0.0 a 1.0
    calidad_extraccion: float  # 0.0 a 1.0
    
    # Información contextual
    contexto_anterior: Optional[str] = None
    contexto_posterior: Optional[str] = None
    oracion_completa: Optional[str] = None
    
    # Información adicional
    lema: Optional[str] = None
    etiqueta_pos: Optional[str] = None
    dependencias: List[Dict[str, Any]] = None
    
    # Metadatos
    modelo_usado: Optional[str] = None
    fecha_extraccion: Optional[datetime] = None
    version_modelo: Optional[str] = None
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.fecha_extraccion is None:
            self.fecha_extraccion = datetime.utcnow()
        
        if self.dependencias is None:
            self.dependencias = []
    
    def es_persona(self) -> bool:
        """Verificar si es una persona"""
        return self.tipo == TipoEntidad.PERSONA
    
    def es_organizacion(self) -> bool:
        """Verificar si es una organización"""
        return self.tipo == TipoEntidad.ORGANIZACION
    
    def es_lugar(self) -> bool:
        """Verificar si es un lugar"""
        return self.tipo in [TipoEntidad.LUGAR, TipoEntidad.LOC, TipoEntidad.FAC]
    
    def es_fecha(self) -> bool:
        """Verificar si es una fecha"""
        return self.tipo == TipoEntidad.FECHA
    
    def es_dinero(self) -> bool:
        """Verificar si es una cantidad de dinero"""
        return self.tipo == TipoEntidad.DINERO
    
    def es_porcentaje(self) -> bool:
        """Verificar si es un porcentaje"""
        return self.tipo == TipoEntidad.PORCENTAJE
    
    def es_temporal(self) -> bool:
        """Verificar si es temporal (fecha o tiempo)"""
        return self.tipo in [TipoEntidad.FECHA, TipoEntidad.TIEMPO]
    
    def es_cuantitativo(self) -> bool:
        """Verificar si es cuantitativo (dinero, porcentaje, cantidad)"""
        return self.tipo in [TipoEntidad.DINERO, TipoEntidad.PORCENTAJE, TipoEntidad.CANTIDAD]
    
    def obtener_longitud(self) -> int:
        """Obtener longitud de la entidad en caracteres"""
        return self.fin - self.inicio
    
    def obtener_contexto_completo(self) -> str:
        """Obtener contexto completo de la entidad"""
        contexto = ""
        if self.contexto_anterior:
            contexto += self.contexto_anterior + " "
        contexto += f"[{self.texto}]"
        if self.contexto_posterior:
            contexto += " " + self.contexto_posterior
        return contexto.strip()
    
    def es_confiable(self, umbral: float = 0.7) -> bool:
        """Verificar si la extracción es confiable"""
        return self.confianza >= umbral and self.calidad_extraccion >= umbral
    
    def obtener_importancia(self) -> str:
        """Obtener nivel de importancia de la entidad"""
        if self.confianza >= 0.9 and self.calidad_extraccion >= 0.9:
            return "muy_alta"
        elif self.confianza >= 0.8 and self.calidad_extraccion >= 0.8:
            return "alta"
        elif self.confianza >= 0.7 and self.calidad_extraccion >= 0.7:
            return "media"
        elif self.confianza >= 0.6 and self.calidad_extraccion >= 0.6:
            return "baja"
        else:
            return "muy_baja"
    
    def obtener_resumen(self) -> str:
        """Obtener resumen de la entidad"""
        importancia = self.obtener_importancia()
        return f"{self.tipo.value}: '{self.texto}' (confianza: {self.confianza:.2f}, importancia: {importancia})"
    
    def calcular_puntuacion_compuesta(self) -> float:
        """Calcular puntuación compuesta de la entidad"""
        # Combinar confianza, calidad y longitud
        factor_confianza = self.confianza
        factor_calidad = self.calidad_extraccion
        factor_longitud = min(1.0, self.obtener_longitud() / 50)  # Normalizar longitud
        
        return (factor_confianza * factor_calidad * factor_longitud)
    
    def es_similar_a(self, otra_entidad: 'EntidadNombrada', umbral: float = 0.8) -> bool:
        """Verificar si es similar a otra entidad"""
        if self.tipo != otra_entidad.tipo:
            return False
        
        # Comparar texto (similitud simple)
        texto1 = self.texto.lower().strip()
        texto2 = otra_entidad.texto.lower().strip()
        
        if texto1 == texto2:
            return True
        
        # Verificar si uno contiene al otro
        if texto1 in texto2 or texto2 in texto1:
            return True
        
        # Aquí se podría implementar similitud más sofisticada
        # usando embeddings o algoritmos de distancia
        
        return False
    
    def __str__(self) -> str:
        """Representación string de la entidad"""
        return f"EntidadNombrada(texto='{self.texto}', tipo={self.tipo.value}, confianza={self.confianza:.2f})"
    
    def __repr__(self) -> str:
        """Representación detallada de la entidad"""
        return (
            f"EntidadNombrada(texto='{self.texto}', tipo={self.tipo.value}, "
            f"posicion=({self.inicio}, {self.fin}), confianza={self.confianza:.2f})"
        )
