"""
Middleware de Manejo de Errores - Capa de Presentación
Middleware para manejo centralizado de errores
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
from typing import Callable


class MiddlewareErrores(BaseHTTPMiddleware):
    """
    Middleware para manejo centralizado de errores
    Implementa el patrón Decorator para funcionalidad transversal
    """
    
    def __init__(self, app):
        """
        Inicializar middleware de errores
        
        Args:
            app: Aplicación FastAPI
        """
        super().__init__(app)
        self.logger = structlog.get_logger("error_handler")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesar request con manejo de errores
        
        Args:
            request: Request HTTP
            call_next: Función siguiente en el pipeline
            
        Returns:
            Response HTTP
        """
        try:
            # Procesar request normalmente
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Log del error
            self.logger.error(
                "Error no controlado en middleware",
                error=str(e),
                tipo_error=type(e).__name__,
                url=str(request.url),
                metodo=request.method
            )
            
            # Crear respuesta de error
            error_response = {
                "error": True,
                "mensaje": "Error interno del servidor",
                "tipo": "ErrorInterno",
                "request_id": getattr(request.state, "request_id", None)
            }
            
            return JSONResponse(
                status_code=500,
                content=error_response
            )
