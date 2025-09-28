"""
Transformador Base - Pipeline ETL
Clase base abstracta para transformadores de datos
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import structlog


class TransformadorBase(ABC):
    """
    Clase base abstracta para transformadores de datos
    Implementa el patrón Template Method para transformación
    """
    
    def __init__(self, nombre: str, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar transformador
        
        Args:
            nombre: Nombre del transformador
            configuracion: Configuración específica del transformador
        """
        self.nombre = nombre
        self.configuracion = configuracion or {}
        self.logger = structlog.get_logger()
    
    @abstractmethod
    async def transformar(self, datos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transformar datos
        
        Args:
            datos: Lista de registros a transformar
            
        Returns:
            Lista de registros transformados
            
        Raises:
            ErrorTransformacion: Si hay error en la transformación
        """
        pass
    
    @abstractmethod
    def validar_configuracion(self) -> bool:
        """
        Validar configuración del transformador
        
        Returns:
            True si la configuración es válida
            
        Raises:
            ErrorConfiguracion: Si la configuración es inválida
        """
        pass
    
    def obtener_metadatos(self) -> Dict[str, Any]:
        """
        Obtener metadatos del transformador
        
        Returns:
            Diccionario con metadatos
        """
        return {
            "nombre": self.nombre,
            "tipo": type(self).__name__,
            "configuracion": self.configuracion
        }
    
    def __str__(self) -> str:
        """Representación string del transformador"""
        return f"{type(self).__name__}(nombre='{self.nombre}')"
    
    def __repr__(self) -> str:
        """Representación detallada del transformador"""
        return f"{type(self).__name__}(nombre='{self.nombre}', configuracion={self.configuracion})"
