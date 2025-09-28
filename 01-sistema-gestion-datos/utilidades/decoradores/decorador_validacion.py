"""
Decorador de Validación - Utilidades
Decorador para validación automática de parámetros
"""
import functools
from typing import Callable, Any, Type, Union, get_type_hints
from pydantic import BaseModel, ValidationError
import structlog


def validar_parametros(
    validar_tipos: bool = True,
    validar_pydantic: bool = True,
    nombre_logger: str = "validacion"
):
    """
    Decorador para validación automática de parámetros
    
    Args:
        validar_tipos: Si validar tipos de Python
        validar_pydantic: Si validar modelos Pydantic
        nombre_logger: Nombre del logger
        
    Returns:
        Decorador configurado
    """
    def decorador(funcion: Callable) -> Callable:
        """
        Decorador interno
        
        Args:
            funcion: Función a decorar
            
        Returns:
            Función decorada
        """
        @functools.wraps(funcion)
        async def wrapper_async(*args, **kwargs) -> Any:
            """
            Wrapper asíncrono para la función
            """
            logger = structlog.get_logger(nombre_logger)
            
            try:
                # Validar tipos si se solicita
                if validar_tipos:
                    _validar_tipos_funcion(funcion, args, kwargs, logger)
                
                # Validar modelos Pydantic si se solicita
                if validar_pydantic:
                    _validar_pydantic_funcion(funcion, args, kwargs, logger)
                
                # Ejecutar función
                resultado = await funcion(*args, **kwargs)
                
                return resultado
                
            except ValidationError as e:
                logger.error("Error de validación", error=str(e), funcion=funcion.__name__)
                raise
            except TypeError as e:
                logger.error("Error de tipo", error=str(e), funcion=funcion.__name__)
                raise
            except Exception as e:
                logger.error("Error inesperado en validación", error=str(e), funcion=funcion.__name__)
                raise
        
        @functools.wraps(funcion)
        def wrapper_sync(*args, **kwargs) -> Any:
            """
            Wrapper síncrono para la función
            """
            logger = structlog.get_logger(nombre_logger)
            
            try:
                # Validar tipos si se solicita
                if validar_tipos:
                    _validar_tipos_funcion(funcion, args, kwargs, logger)
                
                # Validar modelos Pydantic si se solicita
                if validar_pydantic:
                    _validar_pydantic_funcion(funcion, args, kwargs, logger)
                
                # Ejecutar función
                resultado = funcion(*args, **kwargs)
                
                return resultado
                
            except ValidationError as e:
                logger.error("Error de validación", error=str(e), funcion=funcion.__name__)
                raise
            except TypeError as e:
                logger.error("Error de tipo", error=str(e), funcion=funcion.__name__)
                raise
            except Exception as e:
                logger.error("Error inesperado en validación", error=str(e), funcion=funcion.__name__)
                raise
        
        # Retornar wrapper apropiado según si la función es async
        if funcion.__code__.co_flags & 0x80:  # CO_ITERABLE_COROUTINE
            return wrapper_async
        else:
            return wrapper_sync
    
    return decorador


def _validar_tipos_funcion(funcion: Callable, args: tuple, kwargs: dict, logger: structlog.BoundLogger) -> None:
    """
    Validar tipos de parámetros de una función
    
    Args:
        funcion: Función a validar
        args: Argumentos posicionales
        kwargs: Argumentos con nombre
        logger: Logger para errores
    """
    try:
        # Obtener type hints
        type_hints = get_type_hints(funcion)
        
        # Obtener nombres de parámetros
        import inspect
        sig = inspect.signature(funcion)
        param_names = list(sig.parameters.keys())
        
        # Validar argumentos posicionales
        for i, arg in enumerate(args):
            if i < len(param_names):
                param_name = param_names[i]
                if param_name in type_hints:
                    expected_type = type_hints[param_name]
                    if not isinstance(arg, expected_type):
                        raise TypeError(
                            f"Parámetro '{param_name}' debe ser de tipo {expected_type.__name__}, "
                            f"pero se recibió {type(arg).__name__}"
                        )
        
        # Validar argumentos con nombre
        for param_name, value in kwargs.items():
            if param_name in type_hints:
                expected_type = type_hints[param_name]
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"Parámetro '{param_name}' debe ser de tipo {expected_type.__name__}, "
                        f"pero se recibió {type(value).__name__}"
                    )
    
    except Exception as e:
        logger.error("Error en validación de tipos", error=str(e))
        raise


def _validar_pydantic_funcion(funcion: Callable, args: tuple, kwargs: dict, logger: structlog.BoundLogger) -> None:
    """
    Validar modelos Pydantic en parámetros de una función
    
    Args:
        funcion: Función a validar
        args: Argumentos posicionales
        kwargs: Argumentos con nombre
        logger: Logger para errores
    """
    try:
        # Obtener type hints
        type_hints = get_type_hints(funcion)
        
        # Obtener nombres de parámetros
        import inspect
        sig = inspect.signature(funcion)
        param_names = list(sig.parameters.keys())
        
        # Validar argumentos posicionales
        for i, arg in enumerate(args):
            if i < len(param_names):
                param_name = param_names[i]
                if param_name in type_hints:
                    expected_type = type_hints[param_name]
                    if issubclass(expected_type, BaseModel):
                        # Validar modelo Pydantic
                        if not isinstance(arg, expected_type):
                            raise ValidationError(
                                f"Parámetro '{param_name}' debe ser una instancia de {expected_type.__name__}",
                                model=expected_type
                            )
        
        # Validar argumentos con nombre
        for param_name, value in kwargs.items():
            if param_name in type_hints:
                expected_type = type_hints[param_name]
                if issubclass(expected_type, BaseModel):
                    # Validar modelo Pydantic
                    if not isinstance(value, expected_type):
                        raise ValidationError(
                            f"Parámetro '{param_name}' debe ser una instancia de {expected_type.__name__}",
                            model=expected_type
                        )
    
    except Exception as e:
        logger.error("Error en validación Pydantic", error=str(e))
        raise


def validar_entrada_pydantic(modelo: Type[BaseModel]):
    """
    Decorador para validar entrada con modelo Pydantic específico
    
    Args:
        modelo: Modelo Pydantic para validación
        
    Returns:
        Decorador configurado
    """
    def decorador(funcion: Callable) -> Callable:
        """
        Decorador interno
        
        Args:
            funcion: Función a decorar
            
        Returns:
            Función decorada
        """
        @functools.wraps(funcion)
        async def wrapper_async(*args, **kwargs) -> Any:
            """
            Wrapper asíncrono para la función
            """
            logger = structlog.get_logger("validacion_pydantic")
            
            try:
                # Validar primer argumento con el modelo
                if args and isinstance(args[0], dict):
                    # Si es un diccionario, validar con el modelo
                    datos_validados = modelo(**args[0])
                    # Reemplazar el primer argumento con el modelo validado
                    args = (datos_validados,) + args[1:]
                elif args and not isinstance(args[0], modelo):
                    # Si no es del tipo correcto, intentar validar
                    if hasattr(args[0], 'dict'):
                        # Si tiene método dict, convertir y validar
                        datos_validados = modelo(**args[0].dict())
                        args = (datos_validados,) + args[1:]
                    else:
                        # Intentar validar directamente
                        datos_validados = modelo(**args[0])
                        args = (datos_validados,) + args[1:]
                
                # Ejecutar función
                resultado = await funcion(*args, **kwargs)
                
                return resultado
                
            except ValidationError as e:
                logger.error("Error de validación Pydantic", error=str(e), modelo=modelo.__name__)
                raise
            except Exception as e:
                logger.error("Error inesperado en validación Pydantic", error=str(e), modelo=modelo.__name__)
                raise
        
        @functools.wraps(funcion)
        def wrapper_sync(*args, **kwargs) -> Any:
            """
            Wrapper síncrono para la función
            """
            logger = structlog.get_logger("validacion_pydantic")
            
            try:
                # Validar primer argumento con el modelo
                if args and isinstance(args[0], dict):
                    # Si es un diccionario, validar con el modelo
                    datos_validados = modelo(**args[0])
                    # Reemplazar el primer argumento con el modelo validado
                    args = (datos_validados,) + args[1:]
                elif args and not isinstance(args[0], modelo):
                    # Si no es del tipo correcto, intentar validar
                    if hasattr(args[0], 'dict'):
                        # Si tiene método dict, convertir y validar
                        datos_validados = modelo(**args[0].dict())
                        args = (datos_validados,) + args[1:]
                    else:
                        # Intentar validar directamente
                        datos_validados = modelo(**args[0])
                        args = (datos_validados,) + args[1:]
                
                # Ejecutar función
                resultado = funcion(*args, **kwargs)
                
                return resultado
                
            except ValidationError as e:
                logger.error("Error de validación Pydantic", error=str(e), modelo=modelo.__name__)
                raise
            except Exception as e:
                logger.error("Error inesperado en validación Pydantic", error=str(e), modelo=modelo.__name__)
                raise
        
        # Retornar wrapper apropiado según si la función es async
        if funcion.__code__.co_flags & 0x80:  # CO_ITERABLE_COROUTINE
            return wrapper_async
        else:
            return wrapper_sync
    
    return decorador
