"""
Interface RepositorioUsuario - Capa de Dominio
Define el contrato para el repositorio de usuarios
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entidades.usuario import Usuario
from ..value_objects.email import Email
from ..value_objects.nombre_usuario import NombreUsuario


class RepositorioUsuario(ABC):
    """
    Interface que define el contrato para el repositorio de usuarios
    Implementa el patrón Repository para abstraer el acceso a datos
    """
    
    @abstractmethod
    async def guardar(self, usuario: Usuario) -> Usuario:
        """
        Guardar un usuario en el repositorio
        
        Args:
            usuario: Usuario a guardar
            
        Returns:
            Usuario guardado con ID asignado
            
        Raises:
            ErrorRepositorio: Si hay error al guardar
        """
        pass
    
    @abstractmethod
    async def obtener_por_id(self, id_usuario: int) -> Optional[Usuario]:
        """
        Obtener usuario por ID
        
        Args:
            id_usuario: ID del usuario
            
        Returns:
            Usuario encontrado o None si no existe
            
        Raises:
            ErrorRepositorio: Si hay error al consultar
        """
        pass
    
    @abstractmethod
    async def obtener_por_email(self, email: Email) -> Optional[Usuario]:
        """
        Obtener usuario por email
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario encontrado o None si no existe
            
        Raises:
            ErrorRepositorio: Si hay error al consultar
        """
        pass
    
    @abstractmethod
    async def obtener_por_nombre_usuario(self, nombre_usuario: NombreUsuario) -> Optional[Usuario]:
        """
        Obtener usuario por nombre de usuario
        
        Args:
            nombre_usuario: Nombre de usuario
            
        Returns:
            Usuario encontrado o None si no existe
            
        Raises:
            ErrorRepositorio: Si hay error al consultar
        """
        pass
    
    @abstractmethod
    async def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Usuario]:
        """
        Listar todos los usuarios con paginación
        
        Args:
            limite: Número máximo de usuarios a retornar
            offset: Número de usuarios a saltar
            
        Returns:
            Lista de usuarios
            
        Raises:
            ErrorRepositorio: Si hay error al consultar
        """
        pass
    
    @abstractmethod
    async def listar_activos(self, limite: int = 100, offset: int = 0) -> List[Usuario]:
        """
        Listar usuarios activos con paginación
        
        Args:
            limite: Número máximo de usuarios a retornar
            offset: Número de usuarios a saltar
            
        Returns:
            Lista de usuarios activos
            
        Raises:
            ErrorRepositorio: Si hay error al consultar
        """
        pass
    
    @abstractmethod
    async def actualizar(self, usuario: Usuario) -> Usuario:
        """
        Actualizar un usuario existente
        
        Args:
            usuario: Usuario con datos actualizados
            
        Returns:
            Usuario actualizado
            
        Raises:
            ErrorRepositorio: Si hay error al actualizar
            UsuarioNoEncontrado: Si el usuario no existe
        """
        pass
    
    @abstractmethod
    async def eliminar(self, id_usuario: int) -> bool:
        """
        Eliminar un usuario por ID
        
        Args:
            id_usuario: ID del usuario a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existía
            
        Raises:
            ErrorRepositorio: Si hay error al eliminar
        """
        pass
    
    @abstractmethod
    async def existe_email(self, email: Email) -> bool:
        """
        Verificar si existe un usuario con el email dado
        
        Args:
            email: Email a verificar
            
        Returns:
            True si existe, False si no
            
        Raises:
            ErrorRepositorio: Si hay error al consultar
        """
        pass
    
    @abstractmethod
    async def existe_nombre_usuario(self, nombre_usuario: NombreUsuario) -> bool:
        """
        Verificar si existe un usuario con el nombre de usuario dado
        
        Args:
            nombre_usuario: Nombre de usuario a verificar
            
        Returns:
            True si existe, False si no
            
        Raises:
            ErrorRepositorio: Si hay error al consultar
        """
        pass
    
    @abstractmethod
    async def contar_usuarios(self) -> int:
        """
        Contar el número total de usuarios
        
        Returns:
            Número total de usuarios
            
        Raises:
            ErrorRepositorio: Si hay error al consultar
        """
        pass
