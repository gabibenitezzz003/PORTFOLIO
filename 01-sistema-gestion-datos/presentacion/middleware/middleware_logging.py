"""
Middleware de Logging - Capa de Presentación
Middleware para logging estructurado de requests
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
import time
import uuid
from typing import Callable


class MiddlewareLogging(BaseHTTPMiddleware):
    """
    Middleware para logging estructurado de requests HTTP
    Implementa el patrón Decorator para funcionalidad transversal
    """
    
    def __init__(self, app, logger_name: str = "api"):
        """
        Inicializar middleware de logging
        
        Args:
            app: Aplicación FastAPI
            logger_name: Nombre del logger
        """
        super().__init__(app)
        self.logger = structlog.get_logger(logger_name)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesar request y response con logging
        
        Args:
            request: Request HTTP
            call_next: Función siguiente en el pipeline
            
        Returns:
            Response HTTP
        """
        # Generar ID único para el request
        request_id = str(uuid.uuid4())
        
        # Agregar request_id al contexto
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        # Obtener información del request
        metodo = request.method
        url = str(request.url)
        cliente_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log del request
        self.logger.info(
            "Request recibido",
            metodo=metodo,
            url=url,
            cliente_ip=cliente_ip,
            user_agent=user_agent,
            request_id=request_id
        )
        
        # Medir tiempo de procesamiento
        inicio_tiempo = time.time()
        
        try:
            # Procesar request
            response = await call_next(request)
            
            # Calcular tiempo de procesamiento
            tiempo_procesamiento = time.time() - inicio_tiempo
            
            # Log del response exitoso
            self.logger.info(
                "Response enviado",
                status_code=response.status_code,
                tiempo_procesamiento_ms=round(tiempo_procesamiento * 1000, 2),
                request_id=request_id
            )
            
            # Agregar headers de respuesta
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{tiempo_procesamiento:.3f}s"
            
            return response
            
        except Exception as e:
            # Calcular tiempo de procesamiento
            tiempo_procesamiento = time.time() - inicio_tiempo
            
            # Log del error
            self.logger.error(
                "Error en request",
                error=str(e),
                tipo_error=type(e).__name__,
                tiempo_procesamiento_ms=round(tiempo_procesamiento * 1000, 2),
                request_id=request_id
            )
            
            # Re-lanzar excepción
            raise
