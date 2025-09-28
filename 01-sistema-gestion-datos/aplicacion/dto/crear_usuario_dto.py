"""
DTO para crear usuario - Capa de Aplicación
Data Transfer Object para la creación de usuarios
"""
from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class CrearUsuarioDTO(BaseModel):
    """
    DTO para crear un nuevo usuario
    Incluye validaciones de Pydantic
    """
    
    email: EmailStr = Field(..., description="Email del usuario")
    nombre_usuario: str = Field(..., min_length=3, max_length=20, description="Nombre de usuario")
    contraseña: str = Field(..., min_length=8, max_length=128, description="Contraseña del usuario")
    nombre_completo: Optional[str] = Field(None, max_length=255, description="Nombre completo del usuario")
    biografia: Optional[str] = Field(None, max_length=500, description="Biografía del usuario")
    
    @validator('nombre_usuario')
    def validar_nombre_usuario(cls, v):
        """Validar formato del nombre de usuario"""
        if not v or not v.strip():
            raise ValueError('El nombre de usuario es requerido')
        
        # Solo letras, números, guiones y guiones bajos
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El nombre de usuario solo puede contener letras, números, guiones y guiones bajos')
        
        # No puede empezar o terminar con guión o guión bajo
        if v.startswith(('-', '_')) or v.endswith(('-', '_')):
            raise ValueError('El nombre de usuario no puede empezar o terminar con guión o guión bajo')
        
        # No puede tener guiones o guiones bajos consecutivos
        if '--' in v or '__' in v or '_-' in v or '-_' in v:
            raise ValueError('El nombre de usuario no puede tener guiones o guiones bajos consecutivos')
        
        return v
    
    @validator('contraseña')
    def validar_contraseña(cls, v):
        """Validar fortaleza de la contraseña"""
        if not v or not v.strip():
            raise ValueError('La contraseña es requerida')
        
        import re
        
        # Longitud mínima de 8 caracteres
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        # Debe contener al menos una letra minúscula
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        # Debe contener al menos una letra mayúscula
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        
        # Debe contener al menos un número
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        # Debe contener al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        
        # No debe contener espacios
        if ' ' in v:
            raise ValueError('La contraseña no puede contener espacios')
        
        return v
    
    @validator('nombre_completo')
    def validar_nombre_completo(cls, v):
        """Validar nombre completo"""
        if v is not None and v.strip() and len(v.strip()) < 2:
            raise ValueError('El nombre completo debe tener al menos 2 caracteres')
        return v
    
    @validator('biografia')
    def validar_biografia(cls, v):
        """Validar biografía"""
        if v is not None and len(v) > 500:
            raise ValueError('La biografía no puede exceder 500 caracteres')
        return v
    
    class Config:
        """Configuración del modelo"""
        json_encoders = {
            # Configuraciones adicionales si es necesario
        }
        schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "nombre_usuario": "usuario123",
                "contraseña": "MiContraseña123!",
                "nombre_completo": "Juan Pérez",
                "biografia": "Desarrollador Python apasionado por la tecnología"
            }
        }
