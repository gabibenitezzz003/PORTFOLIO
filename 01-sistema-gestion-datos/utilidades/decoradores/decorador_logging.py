"""
Decorador de Logging - Utilidades
Decorador para logging automático de funciones
"""
import functools
import structlog
from typing import Callable, Any
import time


def logging_funcion(
    nombre_logger: str = "funcion",
    incluir_args: bool = True,
    incluir_resultado: bool = True,
    incluir_tiempo: bool = True
):
    """
    Decorador para logging automático de funciones
    
    Args:
        nombre_logger: Nombre del logger
        incluir_args: Si incluir argumentos en el log
        incluir_resultado: Si incluir resultado en el log
        incluir_tiempo: Si incluir tiempo de ejecución
        
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
            
            # Preparar información del log
            log_info = {
                "funcion": funcion.__name__,
                "modulo": funcion.__module__
            }
            
            # Incluir argumentos si se solicita
            if incluir_args:
                log_info.update({
                    "args": str(args) if args else None,
                    "kwargs": str(kwargs) if kwargs else None
                })
            
            # Log de inicio
            logger.info("Iniciando ejecución de función", **log_info)
            
            # Medir tiempo si se solicita
            inicio_tiempo = time.time() if incluir_tiempo else None
            
            try:
                # Ejecutar función
                resultado = await funcion(*args, **kwargs)
                
                # Calcular tiempo si se midió
                if incluir_tiempo and inicio_tiempo:
                    tiempo_ejecucion = time.time() - inicio_tiempo
                    log_info["tiempo_ejecucion_ms"] = round(tiempo_ejecucion * 1000, 2)
                
                # Incluir resultado si se solicita
                if incluir_resultado:
                    log_info["resultado"] = str(resultado)[:200]  # Limitar tamaño
                
                # Log de éxito
                logger.info("Función ejecutada exitosamente", **log_info)
                
                return resultado
                
            except Exception as e:
                # Calcular tiempo si se midió
                if incluir_tiempo and inicio_tiempo:
                    tiempo_ejecucion = time.time() - inicio_tiempo
                    log_info["tiempo_ejecucion_ms"] = round(tiempo_ejecucion * 1000, 2)
                
                # Log de error
                log_info.update({
                    "error": str(e),
                    "tipo_error": type(e).__name__
                })
                
                logger.error("Error en ejecución de función", **log_info)
                
                # Re-lanzar excepción
                raise
        
        @functools.wraps(funcion)
        def wrapper_sync(*args, **kwargs) -> Any:
            """
            Wrapper síncrono para la función
            """
            logger = structlog.get_logger(nombre_logger)
            
            # Preparar información del log
            log_info = {
                "funcion": funcion.__name__,
                "modulo": funcion.__module__
            }
            
            # Incluir argumentos si se solicita
            if incluir_args:
                log_info.update({
                    "args": str(args) if args else None,
                    "kwargs": str(kwargs) if kwargs else None
                })
            
            # Log de inicio
            logger.info("Iniciando ejecución de función", **log_info)
            
            # Medir tiempo si se solicita
            inicio_tiempo = time.time() if incluir_tiempo else None
            
            try:
                # Ejecutar función
                resultado = funcion(*args, **kwargs)
                
                # Calcular tiempo si se midió
                if incluir_tiempo and inicio_tiempo:
                    tiempo_ejecucion = time.time() - inicio_tiempo
                    log_info["tiempo_ejecucion_ms"] = round(tiempo_ejecucion * 1000, 2)
                
                # Incluir resultado si se solicita
                if incluir_resultado:
                    log_info["resultado"] = str(resultado)[:200]  # Limitar tamaño
                
                # Log de éxito
                logger.info("Función ejecutada exitosamente", **log_info)
                
                return resultado
                
            except Exception as e:
                # Calcular tiempo si se midió
                if incluir_tiempo and inicio_tiempo:
                    tiempo_ejecucion = time.time() - inicio_tiempo
                    log_info["tiempo_ejecucion_ms"] = round(tiempo_ejecucion * 1000, 2)
                
                # Log de error
                log_info.update({
                    "error": str(e),
                    "tipo_error": type(e).__name__
                })
                
                logger.error("Error en ejecución de función", **log_info)
                
                # Re-lanzar excepción
                raise
        
        # Retornar wrapper apropiado según si la función es async
        if funcion.__code__.co_flags & 0x80:  # CO_ITERABLE_COROUTINE
            return wrapper_async
        else:
            return wrapper_sync
    
    return decorador


def logging_metodo(
    nombre_logger: str = "metodo",
    incluir_self: bool = False,
    incluir_args: bool = True,
    incluir_resultado: bool = True,
    incluir_tiempo: bool = True
):
    """
    Decorador para logging automático de métodos de clase
    
    Args:
        nombre_logger: Nombre del logger
        incluir_self: Si incluir información de self
        incluir_args: Si incluir argumentos en el log
        incluir_resultado: Si incluir resultado en el log
        incluir_tiempo: Si incluir tiempo de ejecución
        
    Returns:
        Decorador configurado
    """
    def decorador(metodo: Callable) -> Callable:
        """
        Decorador interno para métodos
        
        Args:
            metodo: Método a decorar
            
        Returns:
            Método decorado
        """
        @functools.wraps(metodo)
        async def wrapper_async(self, *args, **kwargs) -> Any:
            """
            Wrapper asíncrono para el método
            """
            logger = structlog.get_logger(nombre_logger)
            
            # Preparar información del log
            log_info = {
                "metodo": metodo.__name__,
                "clase": self.__class__.__name__,
                "modulo": metodo.__module__
            }
            
            # Incluir información de self si se solicita
            if incluir_self:
                log_info["instancia"] = str(self)[:100]  # Limitar tamaño
            
            # Incluir argumentos si se solicita
            if incluir_args:
                log_info.update({
                    "args": str(args) if args else None,
                    "kwargs": str(kwargs) if kwargs else None
                })
            
            # Log de inicio
            logger.info("Iniciando ejecución de método", **log_info)
            
            # Medir tiempo si se solicita
            inicio_tiempo = time.time() if incluir_tiempo else None
            
            try:
                # Ejecutar método
                resultado = await metodo(self, *args, **kwargs)
                
                # Calcular tiempo si se midió
                if incluir_tiempo and inicio_tiempo:
                    tiempo_ejecucion = time.time() - inicio_tiempo
                    log_info["tiempo_ejecucion_ms"] = round(tiempo_ejecucion * 1000, 2)
                
                # Incluir resultado si se solicita
                if incluir_resultado:
                    log_info["resultado"] = str(resultado)[:200]  # Limitar tamaño
                
                # Log de éxito
                logger.info("Método ejecutado exitosamente", **log_info)
                
                return resultado
                
            except Exception as e:
                # Calcular tiempo si se midió
                if incluir_tiempo and inicio_tiempo:
                    tiempo_ejecucion = time.time() - inicio_tiempo
                    log_info["tiempo_ejecucion_ms"] = round(tiempo_ejecucion * 1000, 2)
                
                # Log de error
                log_info.update({
                    "error": str(e),
                    "tipo_error": type(e).__name__
                })
                
                logger.error("Error en ejecución de método", **log_info)
                
                # Re-lanzar excepción
                raise
        
        @functools.wraps(metodo)
        def wrapper_sync(self, *args, **kwargs) -> Any:
            """
            Wrapper síncrono para el método
            """
            logger = structlog.get_logger(nombre_logger)
            
            # Preparar información del log
            log_info = {
                "metodo": metodo.__name__,
                "clase": self.__class__.__name__,
                "modulo": metodo.__module__
            }
            
            # Incluir información de self si se solicita
            if incluir_self:
                log_info["instancia"] = str(self)[:100]  # Limitar tamaño
            
            # Incluir argumentos si se solicita
            if incluir_args:
                log_info.update({
                    "args": str(args) if args else None,
                    "kwargs": str(kwargs) if kwargs else None
                })
            
            # Log de inicio
            logger.info("Iniciando ejecución de método", **log_info)
            
            # Medir tiempo si se solicita
            inicio_tiempo = time.time() if incluir_tiempo else None
            
            try:
                # Ejecutar método
                resultado = metodo(self, *args, **kwargs)
                
                # Calcular tiempo si se midió
                if incluir_tiempo and inicio_tiempo:
                    tiempo_ejecucion = time.time() - inicio_tiempo
                    log_info["tiempo_ejecucion_ms"] = round(tiempo_ejecucion * 1000, 2)
                
                # Incluir resultado si se solicita
                if incluir_resultado:
                    log_info["resultado"] = str(resultado)[:200]  # Limitar tamaño
                
                # Log de éxito
                logger.info("Método ejecutado exitosamente", **log_info)
                
                return resultado
                
            except Exception as e:
                # Calcular tiempo si se midió
                if incluir_tiempo and inicio_tiempo:
                    tiempo_ejecucion = time.time() - inicio_tiempo
                    log_info["tiempo_ejecucion_ms"] = round(tiempo_ejecucion * 1000, 2)
                
                # Log de error
                log_info.update({
                    "error": str(e),
                    "tipo_error": type(e).__name__
                })
                
                logger.error("Error en ejecución de método", **log_info)
                
                # Re-lanzar excepción
                raise
        
        # Retornar wrapper apropiado según si el método es async
        if metodo.__code__.co_flags & 0x80:  # CO_ITERABLE_COROUTINE
            return wrapper_async
        else:
            return wrapper_sync
    
    return decorador
