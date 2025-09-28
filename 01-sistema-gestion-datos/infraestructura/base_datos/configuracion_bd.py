"""
Configuración de Base de Datos - Capa de Infraestructura
Configuración de SQLAlchemy para PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from typing import Optional
import os


class ConfiguracionBaseDatos(BaseSettings):
    """Configuración de base de datos"""
    
    # URL de conexión a la base de datos
    database_url: str = "postgresql://usuario:password@localhost:5432/sistema_gestion_datos"
    
    # Configuración del pool de conexiones
    pool_size: int = 10
    max_overflow: int = 20
    pool_pre_ping: bool = True
    pool_recycle: int = 300
    
    # Configuración de logging
    echo_sql: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
configuracion_bd = ConfiguracionBaseDatos()

# Crear engine de SQLAlchemy
engine = create_engine(
    configuracion_bd.database_url,
    pool_size=configuracion_bd.pool_size,
    max_overflow=configuracion_bd.max_overflow,
    pool_pre_ping=configuracion_bd.pool_pre_ping,
    pool_recycle=configuracion_bd.pool_recycle,
    echo=configuracion_bd.echo_sql
)

# Crear sesión de base de datos
SesionBaseDatos = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def obtener_sesion():
    """
    Dependency para obtener sesión de base de datos
    """
    sesion = SesionBaseDatos()
    try:
        yield sesion
    finally:
        sesion.close()


def crear_tablas():
    """Crear todas las tablas en la base de datos"""
    Base.metadata.create_all(bind=engine)


def eliminar_tablas():
    """Eliminar todas las tablas de la base de datos"""
    Base.metadata.drop_all(bind=engine)
