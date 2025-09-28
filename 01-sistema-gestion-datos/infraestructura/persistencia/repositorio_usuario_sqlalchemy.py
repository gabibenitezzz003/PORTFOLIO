"""
Repositorio Usuario SQLAlchemy - Capa de Infraestructura
Implementación concreta del repositorio de usuarios usando SQLAlchemy
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dominio.entidades.usuario import Usuario
from dominio.value_objects.email import Email
from dominio.value_objects.nombre_usuario import NombreUsuario
from dominio.interfaces.repositorio_usuario import RepositorioUsuario
from aplicacion.excepciones.excepciones_aplicacion import (
    ErrorRepositorioError,
    UsuarioNoEncontradoError
)
from ..base_datos.modelos.usuario_modelo import UsuarioModelo
from ..base_datos.mappers.usuario_mapper import UsuarioMapper


class RepositorioUsuarioSQLAlchemy(RepositorioUsuario):
    """
    Implementación concreta del repositorio de usuarios usando SQLAlchemy
    Implementa el patrón Repository para el acceso a datos
    """
    
    def __init__(self, sesion: Session):
        """
        Inicializar repositorio con sesión de base de datos
        
        Args:
            sesion: Sesión de SQLAlchemy
        """
        self.sesion = sesion
        self.mapper = UsuarioMapper()
    
    async def guardar(self, usuario: Usuario) -> Usuario:
        """
        Guardar un usuario en el repositorio
        
        Args:
            usuario: Usuario a guardar
            
        Returns:
            Usuario guardado con ID asignado
            
        Raises:
            ErrorRepositorioError: Si hay error al guardar
        """
        try:
            # Convertir entidad a modelo
            modelo_usuario = self.mapper.entidad_a_modelo(usuario)
            
            # Agregar a la sesión
            self.sesion.add(modelo_usuario)
            self.sesion.commit()
            self.sesion.refresh(modelo_usuario)
            
            # Convertir modelo a entidad y retornar
            return self.mapper.modelo_a_entidad(modelo_usuario)
            
        except SQLAlchemyError as e:
            self.sesion.rollback()
            raise ErrorRepositorioError(f"Error al guardar usuario: {str(e)}")
    
    async def obtener_por_id(self, id_usuario: int) -> Optional[Usuario]:
        """
        Obtener usuario por ID
        
        Args:
            id_usuario: ID del usuario
            
        Returns:
            Usuario encontrado o None si no existe
            
        Raises:
            ErrorRepositorioError: Si hay error al consultar
        """
        try:
            modelo_usuario = self.sesion.query(UsuarioModelo).filter(
                UsuarioModelo.id == id_usuario
            ).first()
            
            if not modelo_usuario:
                return None
            
            return self.mapper.modelo_a_entidad(modelo_usuario)
            
        except SQLAlchemyError as e:
            raise ErrorRepositorioError(f"Error al obtener usuario por ID: {str(e)}")
    
    async def obtener_por_email(self, email: Email) -> Optional[Usuario]:
        """
        Obtener usuario por email
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario encontrado o None si no existe
            
        Raises:
            ErrorRepositorioError: Si hay error al consultar
        """
        try:
            modelo_usuario = self.sesion.query(UsuarioModelo).filter(
                UsuarioModelo.email == str(email)
            ).first()
            
            if not modelo_usuario:
                return None
            
            return self.mapper.modelo_a_entidad(modelo_usuario)
            
        except SQLAlchemyError as e:
            raise ErrorRepositorioError(f"Error al obtener usuario por email: {str(e)}")
    
    async def obtener_por_nombre_usuario(self, nombre_usuario: NombreUsuario) -> Optional[Usuario]:
        """
        Obtener usuario por nombre de usuario
        
        Args:
            nombre_usuario: Nombre de usuario
            
        Returns:
            Usuario encontrado o None si no existe
            
        Raises:
            ErrorRepositorioError: Si hay error al consultar
        """
        try:
            modelo_usuario = self.sesion.query(UsuarioModelo).filter(
                UsuarioModelo.nombre_usuario == str(nombre_usuario)
            ).first()
            
            if not modelo_usuario:
                return None
            
            return self.mapper.modelo_a_entidad(modelo_usuario)
            
        except SQLAlchemyError as e:
            raise ErrorRepositorioError(f"Error al obtener usuario por nombre: {str(e)}")
    
    async def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Usuario]:
        """
        Listar todos los usuarios con paginación
        
        Args:
            limite: Número máximo de usuarios a retornar
            offset: Número de usuarios a saltar
            
        Returns:
            Lista de usuarios
            
        Raises:
            ErrorRepositorioError: Si hay error al consultar
        """
        try:
            modelos_usuarios = self.sesion.query(UsuarioModelo).offset(offset).limit(limite).all()
            
            return [self.mapper.modelo_a_entidad(modelo) for modelo in modelos_usuarios]
            
        except SQLAlchemyError as e:
            raise ErrorRepositorioError(f"Error al listar usuarios: {str(e)}")
    
    async def listar_activos(self, limite: int = 100, offset: int = 0) -> List[Usuario]:
        """
        Listar usuarios activos con paginación
        
        Args:
            limite: Número máximo de usuarios a retornar
            offset: Número de usuarios a saltar
            
        Returns:
            Lista de usuarios activos
            
        Raises:
            ErrorRepositorioError: Si hay error al consultar
        """
        try:
            modelos_usuarios = self.sesion.query(UsuarioModelo).filter(
                UsuarioModelo.esta_activo == True
            ).offset(offset).limit(limite).all()
            
            return [self.mapper.modelo_a_entidad(modelo) for modelo in modelos_usuarios]
            
        except SQLAlchemyError as e:
            raise ErrorRepositorioError(f"Error al listar usuarios activos: {str(e)}")
    
    async def actualizar(self, usuario: Usuario) -> Usuario:
        """
        Actualizar un usuario existente
        
        Args:
            usuario: Usuario con datos actualizados
            
        Returns:
            Usuario actualizado
            
        Raises:
            ErrorRepositorioError: Si hay error al actualizar
            UsuarioNoEncontradoError: Si el usuario no existe
        """
        try:
            modelo_usuario = self.sesion.query(UsuarioModelo).filter(
                UsuarioModelo.id == usuario.id
            ).first()
            
            if not modelo_usuario:
                raise UsuarioNoEncontradoError(f"Usuario con ID {usuario.id} no encontrado")
            
            # Actualizar campos
            modelo_usuario.email = str(usuario.email) if usuario.email else None
            modelo_usuario.nombre_usuario = str(usuario.nombre_usuario) if usuario.nombre_usuario else None
            modelo_usuario.nombre_completo = usuario.nombre_completo
            modelo_usuario.biografia = usuario.biografia
            modelo_usuario.esta_activo = usuario.esta_activo
            modelo_usuario.es_superusuario = usuario.es_superusuario
            modelo_usuario.fecha_actualizacion = usuario.fecha_actualizacion
            
            # Actualizar contraseña si se proporciona
            if usuario.contraseña:
                modelo_usuario.hash_contraseña = usuario.contraseña.generar_hash()
            
            self.sesion.commit()
            self.sesion.refresh(modelo_usuario)
            
            return self.mapper.modelo_a_entidad(modelo_usuario)
            
        except SQLAlchemyError as e:
            self.sesion.rollback()
            raise ErrorRepositorioError(f"Error al actualizar usuario: {str(e)}")
    
    async def eliminar(self, id_usuario: int) -> bool:
        """
        Eliminar un usuario por ID
        
        Args:
            id_usuario: ID del usuario a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existía
            
        Raises:
            ErrorRepositorioError: Si hay error al eliminar
        """
        try:
            modelo_usuario = self.sesion.query(UsuarioModelo).filter(
                UsuarioModelo.id == id_usuario
            ).first()
            
            if not modelo_usuario:
                return False
            
            self.sesion.delete(modelo_usuario)
            self.sesion.commit()
            
            return True
            
        except SQLAlchemyError as e:
            self.sesion.rollback()
            raise ErrorRepositorioError(f"Error al eliminar usuario: {str(e)}")
    
    async def existe_email(self, email: Email) -> bool:
        """
        Verificar si existe un usuario con el email dado
        
        Args:
            email: Email a verificar
            
        Returns:
            True si existe, False si no
            
        Raises:
            ErrorRepositorioError: Si hay error al consultar
        """
        try:
            count = self.sesion.query(UsuarioModelo).filter(
                UsuarioModelo.email == str(email)
            ).count()
            
            return count > 0
            
        except SQLAlchemyError as e:
            raise ErrorRepositorioError(f"Error al verificar email: {str(e)}")
    
    async def existe_nombre_usuario(self, nombre_usuario: NombreUsuario) -> bool:
        """
        Verificar si existe un usuario con el nombre de usuario dado
        
        Args:
            nombre_usuario: Nombre de usuario a verificar
            
        Returns:
            True si existe, False si no
            
        Raises:
            ErrorRepositorioError: Si hay error al consultar
        """
        try:
            count = self.sesion.query(UsuarioModelo).filter(
                UsuarioModelo.nombre_usuario == str(nombre_usuario)
            ).count()
            
            return count > 0
            
        except SQLAlchemyError as e:
            raise ErrorRepositorioError(f"Error al verificar nombre de usuario: {str(e)}")
    
    async def contar_usuarios(self) -> int:
        """
        Contar el número total de usuarios
        
        Returns:
            Número total de usuarios
            
        Raises:
            ErrorRepositorioError: Si hay error al consultar
        """
        try:
            return self.sesion.query(UsuarioModelo).count()
            
        except SQLAlchemyError as e:
            raise ErrorRepositorioError(f"Error al contar usuarios: {str(e)}")
