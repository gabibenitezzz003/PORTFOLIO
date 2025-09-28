"""
DTOs para respuestas de API - Capa de Presentación
DTOs estandarizados para respuestas de la API
"""
from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class RespuestaAPI(BaseModel, Generic[T]):
    """
    DTO genérico para respuestas exitosas de la API
    """
    
    exito: bool = Field(True, description="Indica si la operación fue exitosa")
    mensaje: str = Field(..., description="Mensaje descriptivo de la operación")
    datos: T = Field(..., description="Datos de la respuesta")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de la respuesta")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "exito": True,
                "mensaje": "Operación exitosa",
                "datos": {},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


class RespuestaErrorAPI(BaseModel):
    """
    DTO para respuestas de error de la API
    """
    
    exito: bool = Field(False, description="Indica si la operación fue exitosa")
    mensaje: str = Field(..., description="Mensaje de error")
    codigo_error: Optional[str] = Field(None, description="Código de error específico")
    detalles: Optional[dict] = Field(None, description="Detalles adicionales del error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp del error")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "exito": False,
                "mensaje": "Error en la operación",
                "codigo_error": "ERROR_001",
                "detalles": {"campo": "valor"},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


class RespuestaPaginadaAPI(BaseModel, Generic[T]):
    """
    DTO para respuestas paginadas de la API
    """
    
    exito: bool = Field(True, description="Indica si la operación fue exitosa")
    mensaje: str = Field(..., description="Mensaje descriptivo de la operación")
    datos: list[T] = Field(..., description="Lista de datos")
    paginacion: dict = Field(..., description="Información de paginación")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de la respuesta")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "exito": True,
                "mensaje": "Datos obtenidos exitosamente",
                "datos": [],
                "paginacion": {
                    "total": 100,
                    "limite": 10,
                    "offset": 0,
                    "pagina_actual": 1,
                    "total_paginas": 10
                },
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
