"""
Extractor Base - Pipeline ETL
Clase base abstracta para extractores de datos
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import structlog


class ExtractorBase(ABC):
    """
    Clase base abstracta para extractores de datos
    Implementa el patrón Template Method para extracción
    """
    
    def __init__(self, nombre: str, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar extractor
        
        Args:
            nombre: Nombre del extractor
            configuracion: Configuración específica del extractor
        """
        self.nombre = nombre
        self.configuracion = configuracion or {}
        self.logger = structlog.get_logger()
    
    @abstractmethod
    async def extraer(self, parametros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extraer datos de la fuente
        
        Args:
            parametros: Parámetros adicionales para la extracción
            
        Returns:
            Lista de registros extraídos
            
        Raises:
            ErrorExtraccion: Si hay error en la extracción
        """
        pass
    
    @abstractmethod
    def validar_configuracion(self) -> bool:
        """
        Validar configuración del extractor
        
        Returns:
            True si la configuración es válida
            
        Raises:
            ErrorConfiguracion: Si la configuración es inválida
        """
        pass
    
    def obtener_metadatos(self) -> Dict[str, Any]:
        """
        Obtener metadatos del extractor
        
        Returns:
            Diccionario con metadatos
        """
        return {
            "nombre": self.nombre,
            "tipo": type(self).__name__,
            "configuracion": self.configuracion
        }
    
    def __str__(self) -> str:
        """Representación string del extractor"""
        return f"{type(self).__name__}(nombre='{self.nombre}')"
    
    def __repr__(self) -> str:
        """Representación detallada del extractor"""
        return f"{type(self).__name__}(nombre='{self.nombre}', configuracion={self.configuracion})"
