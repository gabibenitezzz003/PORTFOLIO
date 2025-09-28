"""
Servicio de Autenticación - Capa de Dominio
Contiene la lógica de negocio para autenticación de usuarios
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..entidades.usuario import Usuario
from ..value_objects.email import Email
from ..value_objects.nombre_usuario import NombreUsuario
from ..value_objects.contraseña import Contraseña


class ServicioAutenticacion(ABC):
    """
    Servicio de dominio para autenticación de usuarios
    Define el contrato para la autenticación
    """
    
    @abstractmethod
    async def autenticar_usuario(
        self, 
        identificador: str, 
        contraseña: str
    ) -> Optional[Usuario]:
        """
        Autenticar un usuario por email o nombre de usuario
        
        Args:
            identificador: Email o nombre de usuario
            contraseña: Contraseña del usuario
            
        Returns:
            Usuario autenticado o None si falla la autenticación
            
        Raises:
            ErrorAutenticacion: Si hay error en el proceso de autenticación
        """
        pass
    
    @abstractmethod
    async def generar_token_acceso(self, usuario: Usuario) -> str:
        """
        Generar token de acceso para un usuario
        
        Args:
            usuario: Usuario para el cual generar el token
            
        Returns:
            Token de acceso JWT
            
        Raises:
            ErrorGeneracionToken: Si hay error al generar el token
        """
        pass
    
    @abstractmethod
    async def verificar_token(self, token: str) -> Optional[Usuario]:
        """
        Verificar y decodificar un token de acceso
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Usuario asociado al token o None si es inválido
            
        Raises:
            ErrorVerificacionToken: Si hay error al verificar el token
        """
        pass
    
    @abstractmethod
    async def renovar_token(self, token_actual: str) -> str:
        """
        Renovar un token de acceso
        
        Args:
            token_actual: Token actual a renovar
            
        Returns:
            Nuevo token de acceso
            
        Raises:
            ErrorRenovacionToken: Si hay error al renovar el token
        """
        pass
    
    @abstractmethod
    async def invalidar_token(self, token: str) -> bool:
        """
        Invalidar un token de acceso
        
        Args:
            token: Token a invalidar
            
        Returns:
            True si se invalidó correctamente
            
        Raises:
            ErrorInvalidacionToken: Si hay error al invalidar el token
        """
        pass
    
    @abstractmethod
    async def verificar_permisos(
        self, 
        usuario: Usuario, 
        accion: str
    ) -> bool:
        """
        Verificar si un usuario tiene permisos para realizar una acción
        
        Args:
            usuario: Usuario a verificar
            accion: Acción a verificar
            
        Returns:
            True si tiene permisos, False si no
            
        Raises:
            ErrorVerificacionPermisos: Si hay error al verificar permisos
        """
        pass
