"""
Controlador de Usuario - Capa de Presentación
Endpoints REST para gestión de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import structlog

from aplicacion.casos_uso.caso_uso_crear_usuario import CasoUsoCrearUsuario
from aplicacion.dto.crear_usuario_dto import CrearUsuarioDTO
from aplicacion.dto.usuario_dto import UsuarioDTO, UsuarioResumenDTO
from aplicacion.excepciones.excepciones_aplicacion import (
    UsuarioYaExisteError,
    EmailYaExisteError,
    NombreUsuarioYaExisteError,
    ErrorValidacionError
)
from infraestructura.persistencia.repositorio_usuario_sqlalchemy import RepositorioUsuarioSQLAlchemy
from infraestructura.base_datos.configuracion_bd import obtener_sesion
from ..dependencias.dependencias import obtener_repositorio_usuario
from ..dto.respuesta_api_dto import RespuestaAPI, RespuestaErrorAPI

logger = structlog.get_logger()

# Crear router
router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post(
    "/",
    response_model=RespuestaAPI[UsuarioDTO],
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo usuario",
    description="Crear un nuevo usuario en el sistema"
)
async def crear_usuario(
    datos_usuario: CrearUsuarioDTO,
    repositorio_usuario: RepositorioUsuarioSQLAlchemy = Depends(obtener_repositorio_usuario)
) -> RespuestaAPI[UsuarioDTO]:
    """
    Crear un nuevo usuario
    
    Args:
        datos_usuario: Datos del usuario a crear
        repositorio_usuario: Repositorio de usuarios
        
    Returns:
        Usuario creado
        
    Raises:
        HTTPException: Si hay error en la creación
    """
    try:
        logger.info("Iniciando creación de usuario", email=datos_usuario.email)
        
        # Crear caso de uso (por ahora sin servicio de autenticación)
        caso_uso = CasoUsoCrearUsuario(
            repositorio_usuario=repositorio_usuario,
            servicio_autenticacion=None  # TODO: Implementar servicio de autenticación
        )
        
        # Ejecutar caso de uso
        usuario_creado = await caso_uso.ejecutar(datos_usuario)
        
        logger.info("Usuario creado exitosamente", usuario_id=usuario_creado.id)
        
        return RespuestaAPI(
            exito=True,
            mensaje="Usuario creado exitosamente",
            datos=usuario_creado
        )
        
    except EmailYaExisteError as e:
        logger.warning("Error al crear usuario: email ya existe", email=datos_usuario.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un usuario con el email: {datos_usuario.email}"
        )
    
    except NombreUsuarioYaExisteError as e:
        logger.warning("Error al crear usuario: nombre de usuario ya existe", 
                      nombre_usuario=datos_usuario.nombre_usuario)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un usuario con el nombre: {datos_usuario.nombre_usuario}"
        )
    
    except ErrorValidacionError as e:
        logger.warning("Error de validación al crear usuario", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error inesperado al crear usuario", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/",
    response_model=RespuestaAPI[List[UsuarioResumenDTO]],
    summary="Listar usuarios",
    description="Obtener lista de usuarios con paginación"
)
async def listar_usuarios(
    limite: int = 100,
    offset: int = 0,
    repositorio_usuario: RepositorioUsuarioSQLAlchemy = Depends(obtener_repositorio_usuario)
) -> RespuestaAPI[List[UsuarioResumenDTO]]:
    """
    Listar usuarios con paginación
    
    Args:
        limite: Número máximo de usuarios a retornar
        offset: Número de usuarios a saltar
        repositorio_usuario: Repositorio de usuarios
        
    Returns:
        Lista de usuarios
    """
    try:
        logger.info("Listando usuarios", limite=limite, offset=offset)
        
        # Obtener usuarios del repositorio
        usuarios = await repositorio_usuario.listar_todos(limite=limite, offset=offset)
        
        # Convertir a DTOs
        usuarios_dto = [UsuarioResumenDTO.desde_entidad(usuario) for usuario in usuarios]
        
        logger.info("Usuarios listados exitosamente", cantidad=len(usuarios_dto))
        
        return RespuestaAPI(
            exito=True,
            mensaje=f"Se encontraron {len(usuarios_dto)} usuarios",
            datos=usuarios_dto
        )
        
    except Exception as e:
        logger.error("Error al listar usuarios", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/{usuario_id}",
    response_model=RespuestaAPI[UsuarioDTO],
    summary="Obtener usuario por ID",
    description="Obtener un usuario específico por su ID"
)
async def obtener_usuario(
    usuario_id: int,
    repositorio_usuario: RepositorioUsuarioSQLAlchemy = Depends(obtener_repositorio_usuario)
) -> RespuestaAPI[UsuarioDTO]:
    """
    Obtener usuario por ID
    
    Args:
        usuario_id: ID del usuario
        repositorio_usuario: Repositorio de usuarios
        
    Returns:
        Usuario encontrado
        
    Raises:
        HTTPException: Si el usuario no existe
    """
    try:
        logger.info("Obteniendo usuario por ID", usuario_id=usuario_id)
        
        # Obtener usuario del repositorio
        usuario = await repositorio_usuario.obtener_por_id(usuario_id)
        
        if not usuario:
            logger.warning("Usuario no encontrado", usuario_id=usuario_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        
        # Convertir a DTO
        usuario_dto = UsuarioDTO.desde_entidad(usuario)
        
        logger.info("Usuario obtenido exitosamente", usuario_id=usuario_id)
        
        return RespuestaAPI(
            exito=True,
            mensaje="Usuario obtenido exitosamente",
            datos=usuario_dto
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error al obtener usuario", usuario_id=usuario_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
