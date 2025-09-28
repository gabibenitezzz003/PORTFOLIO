"""
Mapper Usuario - Capa de Infraestructura
Convierte entre entidades de dominio y modelos de base de datos
"""
from typing import Optional
from ...dominio.entidades.usuario import Usuario
from ...dominio.value_objects.email import Email
from ...dominio.value_objects.nombre_usuario import NombreUsuario
from ...dominio.value_objects.contraseña import Contraseña
from ..modelos.usuario_modelo import UsuarioModelo


class UsuarioMapper:
    """
    Mapper para convertir entre entidades Usuario y modelos UsuarioModelo
    Implementa el patrón Mapper para la conversión de datos
    """
    
    def entidad_a_modelo(self, usuario: Usuario) -> UsuarioModelo:
        """
        Convertir entidad Usuario a modelo UsuarioModelo
        
        Args:
            usuario: Entidad Usuario
            
        Returns:
            Modelo UsuarioModelo
        """
        modelo = UsuarioModelo()
        
        # Campos básicos
        if usuario.id:
            modelo.id = usuario.id
        
        if usuario.email:
            modelo.email = str(usuario.email)
        
        if usuario.nombre_usuario:
            modelo.nombre_usuario = str(usuario.nombre_usuario)
        
        # Información personal
        modelo.nombre_completo = usuario.nombre_completo
        modelo.biografia = usuario.biografia
        
        # Estado del usuario
        modelo.esta_activo = usuario.esta_activo
        modelo.es_superusuario = usuario.es_superusuario
        
        # Timestamps
        modelo.fecha_creacion = usuario.fecha_creacion
        modelo.fecha_actualizacion = usuario.fecha_actualizacion
        
        # Contraseña (hash)
        if usuario.contraseña:
            modelo.hash_contraseña = usuario.contraseña.generar_hash()
        
        return modelo
    
    def modelo_a_entidad(self, modelo: UsuarioModelo) -> Usuario:
        """
        Convertir modelo UsuarioModelo a entidad Usuario
        
        Args:
            modelo: Modelo UsuarioModelo
            
        Returns:
            Entidad Usuario
        """
        # Crear value objects
        email = Email(modelo.email) if modelo.email else None
        nombre_usuario = NombreUsuario(modelo.nombre_usuario) if modelo.nombre_usuario else None
        
        # Crear entidad
        usuario = Usuario(
            id=modelo.id,
            email=email,
            nombre_usuario=nombre_usuario,
            nombre_completo=modelo.nombre_completo,
            biografia=modelo.biografia,
            esta_activo=modelo.esta_activo,
            es_superusuario=modelo.es_superusuario,
            fecha_creacion=modelo.fecha_creacion,
            fecha_actualizacion=modelo.fecha_actualizacion
        )
        
        return usuario
    
    def actualizar_modelo_desde_entidad(self, modelo: UsuarioModelo, usuario: Usuario) -> UsuarioModelo:
        """
        Actualizar modelo existente con datos de la entidad
        
        Args:
            modelo: Modelo existente a actualizar
            usuario: Entidad con datos actualizados
            
        Returns:
            Modelo actualizado
        """
        # Actualizar campos básicos
        if usuario.email:
            modelo.email = str(usuario.email)
        
        if usuario.nombre_usuario:
            modelo.nombre_usuario = str(usuario.nombre_usuario)
        
        # Actualizar información personal
        modelo.nombre_completo = usuario.nombre_completo
        modelo.biografia = usuario.biografia
        
        # Actualizar estado
        modelo.esta_activo = usuario.esta_activo
        modelo.es_superusuario = usuario.es_superusuario
        
        # Actualizar timestamps
        modelo.fecha_actualizacion = usuario.fecha_actualizacion
        
        # Actualizar contraseña si se proporciona
        if usuario.contraseña:
            modelo.hash_contraseña = usuario.contraseña.generar_hash()
        
        return modelo
