"""
DTO para Usuario - Capa de Aplicación
Data Transfer Object para representar usuarios
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UsuarioDTO(BaseModel):
    """
    DTO para representar un usuario
    Incluye toda la información del usuario sin datos sensibles
    """
    
    id: Optional[int] = Field(None, description="ID único del usuario")
    email: str = Field(..., description="Email del usuario")
    nombre_usuario: str = Field(..., description="Nombre de usuario")
    nombre_completo: Optional[str] = Field(None, description="Nombre completo del usuario")
    biografia: Optional[str] = Field(None, description="Biografía del usuario")
    esta_activo: bool = Field(True, description="Indica si el usuario está activo")
    es_superusuario: bool = Field(False, description="Indica si el usuario es superusuario")
    fecha_creacion: Optional[datetime] = Field(None, description="Fecha de creación del usuario")
    fecha_actualizacion: Optional[datetime] = Field(None, description="Fecha de última actualización")
    
    @classmethod
    def desde_entidad(cls, usuario) -> 'UsuarioDTO':
        """
        Crear DTO desde una entidad Usuario
        
        Args:
            usuario: Entidad Usuario
            
        Returns:
            UsuarioDTO creado desde la entidad
        """
        return cls(
            id=usuario.id,
            email=str(usuario.email) if usuario.email else None,
            nombre_usuario=str(usuario.nombre_usuario) if usuario.nombre_usuario else None,
            nombre_completo=usuario.nombre_completo,
            biografia=usuario.biografia,
            esta_activo=usuario.esta_activo,
            es_superusuario=usuario.es_superusuario,
            fecha_creacion=usuario.fecha_creacion,
            fecha_actualizacion=usuario.fecha_actualizacion
        )
    
    def a_entidad(self) -> 'Usuario':
        """
        Convertir DTO a entidad Usuario
        
        Returns:
            Entidad Usuario creada desde el DTO
        """
        from dominio.entidades.usuario import Usuario
        from dominio.value_objects.email import Email
        from dominio.value_objects.nombre_usuario import NombreUsuario
        
        return Usuario(
            id=self.id,
            email=Email(self.email) if self.email else None,
            nombre_usuario=NombreUsuario(self.nombre_usuario) if self.nombre_usuario else None,
            nombre_completo=self.nombre_completo,
            biografia=self.biografia,
            esta_activo=self.esta_activo,
            es_superusuario=self.es_superusuario,
            fecha_creacion=self.fecha_creacion,
            fecha_actualizacion=self.fecha_actualizacion
        )
    
    class Config:
        """Configuración del modelo"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": 1,
                "email": "usuario@ejemplo.com",
                "nombre_usuario": "usuario123",
                "nombre_completo": "Juan Pérez",
                "biografia": "Desarrollador Python apasionado por la tecnología",
                "esta_activo": True,
                "es_superusuario": False,
                "fecha_creacion": "2024-01-01T00:00:00Z",
                "fecha_actualizacion": "2024-01-01T00:00:00Z"
            }
        }


class UsuarioResumenDTO(BaseModel):
    """
    DTO resumido para usuario
    Contiene solo información básica
    """
    
    id: int = Field(..., description="ID único del usuario")
    email: str = Field(..., description="Email del usuario")
    nombre_usuario: str = Field(..., description="Nombre de usuario")
    nombre_completo: Optional[str] = Field(None, description="Nombre completo del usuario")
    esta_activo: bool = Field(True, description="Indica si el usuario está activo")
    
    @classmethod
    def desde_entidad(cls, usuario) -> 'UsuarioResumenDTO':
        """
        Crear DTO resumido desde una entidad Usuario
        
        Args:
            usuario: Entidad Usuario
            
        Returns:
            UsuarioResumenDTO creado desde la entidad
        """
        return cls(
            id=usuario.id,
            email=str(usuario.email) if usuario.email else None,
            nombre_usuario=str(usuario.nombre_usuario) if usuario.nombre_usuario else None,
            nombre_completo=usuario.nombre_completo,
            esta_activo=usuario.esta_activo
        )
    
    class Config:
        """Configuración del modelo"""
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "email": "usuario@ejemplo.com",
                "nombre_usuario": "usuario123",
                "nombre_completo": "Juan Pérez",
                "esta_activo": True
            }
        }
