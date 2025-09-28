"""
Caso de Uso: Crear Usuario
Implementa la lógica de negocio para crear un nuevo usuario
"""
from typing import Optional
from dataclasses import dataclass
from dominio.entidades.usuario import Usuario
from dominio.value_objects.email import Email
from dominio.value_objects.nombre_usuario import NombreUsuario
from dominio.value_objects.contraseña import Contraseña
from dominio.interfaces.repositorio_usuario import RepositorioUsuario
from dominio.servicios.servicio_autenticacion import ServicioAutenticacion
from aplicacion.dto.crear_usuario_dto import CrearUsuarioDTO
from aplicacion.dto.usuario_dto import UsuarioDTO
from aplicacion.excepciones.excepciones_aplicacion import (
    UsuarioYaExisteError,
    EmailYaExisteError,
    NombreUsuarioYaExisteError,
    ErrorValidacionError
)


@dataclass
class CasoUsoCrearUsuario:
    """
    Caso de uso para crear un nuevo usuario
    Implementa el patrón Use Case de Clean Architecture
    """
    
    repositorio_usuario: RepositorioUsuario
    servicio_autenticacion: ServicioAutenticacion
    
    async def ejecutar(self, datos_usuario: CrearUsuarioDTO) -> UsuarioDTO:
        """
        Ejecutar el caso de uso para crear usuario
        
        Args:
            datos_usuario: Datos del usuario a crear
            
        Returns:
            UsuarioDTO del usuario creado
            
        Raises:
            UsuarioYaExisteError: Si el usuario ya existe
            EmailYaExisteError: Si el email ya está en uso
            NombreUsuarioYaExisteError: Si el nombre de usuario ya está en uso
            ErrorValidacionError: Si los datos no son válidos
        """
        # Validar datos de entrada
        await self._validar_datos_entrada(datos_usuario)
        
        # Crear value objects
        email = Email(datos_usuario.email)
        nombre_usuario = NombreUsuario(datos_usuario.nombre_usuario)
        contraseña = Contraseña(datos_usuario.contraseña)
        
        # Verificar que no exista un usuario con el mismo email
        if await self.repositorio_usuario.existe_email(email):
            raise EmailYaExisteError(f"Ya existe un usuario con el email: {email}")
        
        # Verificar que no exista un usuario con el mismo nombre de usuario
        if await self.repositorio_usuario.existe_nombre_usuario(nombre_usuario):
            raise NombreUsuarioYaExisteError(
                f"Ya existe un usuario con el nombre: {nombre_usuario}"
            )
        
        # Crear entidad usuario
        usuario = Usuario(
            email=email,
            nombre_usuario=nombre_usuario,
            contraseña=contraseña,
            nombre_completo=datos_usuario.nombre_completo,
            biografia=datos_usuario.biografia,
            esta_activo=True,
            es_superusuario=False
        )
        
        # Guardar usuario en el repositorio
        usuario_creado = await self.repositorio_usuario.guardar(usuario)
        
        # Convertir a DTO y retornar
        return UsuarioDTO.desde_entidad(usuario_creado)
    
    async def _validar_datos_entrada(self, datos_usuario: CrearUsuarioDTO) -> None:
        """
        Validar los datos de entrada del usuario
        
        Args:
            datos_usuario: Datos del usuario a validar
            
        Raises:
            ErrorValidacionError: Si los datos no son válidos
        """
        errores = []
        
        # Validar email
        if not datos_usuario.email or not datos_usuario.email.strip():
            errores.append("El email es requerido")
        
        # Validar nombre de usuario
        if not datos_usuario.nombre_usuario or not datos_usuario.nombre_usuario.strip():
            errores.append("El nombre de usuario es requerido")
        
        # Validar contraseña
        if not datos_usuario.contraseña or not datos_usuario.contraseña.strip():
            errores.append("La contraseña es requerida")
        
        # Validar nombre completo (opcional pero si se proporciona debe ser válido)
        if datos_usuario.nombre_completo and len(datos_usuario.nombre_completo.strip()) < 2:
            errores.append("El nombre completo debe tener al menos 2 caracteres")
        
        # Validar biografía (opcional pero si se proporciona debe ser válida)
        if datos_usuario.biografia and len(datos_usuario.biografia.strip()) > 500:
            errores.append("La biografía no puede exceder 500 caracteres")
        
        if errores:
            raise ErrorValidacionError(f"Errores de validación: {'; '.join(errores)}")
