"""
Entidad Usuario - Capa de Dominio
Representa un usuario en el sistema con sus reglas de negocio
"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from ..value_objects.email import Email
from ..value_objects.nombre_usuario import NombreUsuario
from ..value_objects.contraseña import Contraseña


@dataclass
class Usuario:
    """
    Entidad Usuario que encapsula las reglas de negocio
    y el estado de un usuario en el sistema
    """
    
    # Identificadores
    id: Optional[int] = None
    email: Optional[Email] = None
    nombre_usuario: Optional[NombreUsuario] = None
    
    # Información personal
    nombre_completo: Optional[str] = None
    biografia: Optional[str] = None
    
    # Estado del usuario
    esta_activo: bool = True
    es_superusuario: bool = False
    
    # Contraseña (solo para creación/actualización)
    contraseña: Optional[Contraseña] = None
    
    # Timestamps
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    
    def __post_init__(self):
        """Inicialización post-construcción"""
        if self.fecha_creacion is None:
            self.fecha_creacion = datetime.utcnow()
        if self.fecha_actualizacion is None:
            self.fecha_actualizacion = datetime.utcnow()
    
    def activar(self) -> None:
        """Activar el usuario"""
        self.esta_activo = True
        self.fecha_actualizacion = datetime.utcnow()
    
    def desactivar(self) -> None:
        """Desactivar el usuario"""
        self.esta_activo = False
        self.fecha_actualizacion = datetime.utcnow()
    
    def promover_a_superusuario(self) -> None:
        """Promover usuario a superusuario"""
        self.es_superusuario = True
        self.fecha_actualizacion = datetime.utcnow()
    
    def degradar_de_superusuario(self) -> None:
        """Degradar usuario de superusuario"""
        self.es_superusuario = False
        self.fecha_actualizacion = datetime.utcnow()
    
    def actualizar_informacion_personal(
        self, 
        nombre_completo: Optional[str] = None,
        biografia: Optional[str] = None
    ) -> None:
        """Actualizar información personal del usuario"""
        if nombre_completo is not None:
            self.nombre_completo = nombre_completo
        if biografia is not None:
            self.biografia = biografia
        self.fecha_actualizacion = datetime.utcnow()
    
    def puede_realizar_accion(self, accion: str) -> bool:
        """
        Verificar si el usuario puede realizar una acción específica
        """
        if not self.esta_activo:
            return False
        
        # Superusuarios pueden hacer todo
        if self.es_superusuario:
            return True
        
        # Lógica específica para cada acción
        acciones_permitidas = [
            "ver_perfil",
            "actualizar_perfil",
            "crear_producto",
            "ver_productos",
            "crear_orden"
        ]
        
        return accion in acciones_permitidas
    
    def es_valido(self) -> bool:
        """Verificar si el usuario es válido"""
        return (
            self.email is not None and
            self.nombre_usuario is not None and
            self.esta_activo
        )
    
    def __str__(self) -> str:
        """Representación string del usuario"""
        return f"Usuario(id={self.id}, email={self.email}, nombre_usuario={self.nombre_usuario})"
    
    def __repr__(self) -> str:
        """Representación detallada del usuario"""
        return (
            f"Usuario(id={self.id}, email={self.email}, "
            f"nombre_usuario={self.nombre_usuario}, esta_activo={self.esta_activo})"
        )
