"""
Excepciones de la Aplicación - Capa de Aplicación
Excepciones específicas para la lógica de aplicación
"""


class ExcepcionAplicacion(Exception):
    """Excepción base para la capa de aplicación"""
    pass


class UsuarioYaExisteError(ExcepcionAplicacion):
    """Excepción cuando se intenta crear un usuario que ya existe"""
    pass


class UsuarioNoEncontradoError(ExcepcionAplicacion):
    """Excepción cuando no se encuentra un usuario"""
    pass


class EmailYaExisteError(ExcepcionAplicacion):
    """Excepción cuando se intenta usar un email que ya existe"""
    pass


class NombreUsuarioYaExisteError(ExcepcionAplicacion):
    """Excepción cuando se intenta usar un nombre de usuario que ya existe"""
    pass


class ErrorValidacionError(ExcepcionAplicacion):
    """Excepción cuando hay errores de validación"""
    pass


class ErrorAutenticacionError(ExcepcionAplicacion):
    """Excepción cuando hay errores de autenticación"""
    pass


class ErrorAutorizacionError(ExcepcionAplicacion):
    """Excepción cuando hay errores de autorización"""
    pass


class ErrorRepositorioError(ExcepcionAplicacion):
    """Excepción cuando hay errores en el repositorio"""
    pass


class ErrorServicioError(ExcepcionAplicacion):
    """Excepción cuando hay errores en los servicios"""
    pass


class ErrorConfiguracionError(ExcepcionAplicacion):
    """Excepción cuando hay errores de configuración"""
    pass
