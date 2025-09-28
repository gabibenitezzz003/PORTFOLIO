"""
Dependencias de la API - Capa de Presentación
Dependencias para inyección de dependencias
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from ...infraestructura.base_datos.configuracion_bd import obtener_sesion
from ...infraestructura.persistencia.repositorio_usuario_sqlalchemy import RepositorioUsuarioSQLAlchemy


def obtener_repositorio_usuario(
    sesion: Session = Depends(obtener_sesion)
) -> RepositorioUsuarioSQLAlchemy:
    """
    Obtener instancia del repositorio de usuarios
    
    Args:
        sesion: Sesión de base de datos
        
    Returns:
        Repositorio de usuarios configurado
    """
    return RepositorioUsuarioSQLAlchemy(sesion)
