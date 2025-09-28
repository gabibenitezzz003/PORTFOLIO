"""
Extractor API REST - Pipeline ETL
Extractor para APIs REST con funcionalidades avanzadas
"""
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
import structlog
from urllib.parse import urljoin, urlparse
import json

from .extractor_base import ExtractorBase
from ..excepciones.excepciones_pipeline import ErrorExtraccion, ErrorConfiguracion


class ExtractorAPI(ExtractorBase):
    """
    Extractor para APIs REST
    Soporta autenticación, paginación y rate limiting
    """
    
    def __init__(
        self, 
        nombre: str, 
        url_base: str,
        configuracion: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializar extractor API
        
        Args:
            nombre: Nombre del extractor
            url_base: URL base de la API
            configuracion: Configuración específica
        """
        super().__init__(nombre, configuracion)
        self.url_base = url_base
        
        # Configuración por defecto
        self.configuracion_default = {
            "endpoint": "/",
            "metodo": "GET",
            "headers": {"Content-Type": "application/json"},
            "timeout": 30,
            "max_retries": 3,
            "delay_retry": 1,
            "rate_limit": 100,  # requests por minuto
            "paginacion": {
                "habilitada": False,
                "parametro_pagina": "page",
                "parametro_tamano": "size",
                "tamano_pagina": 100,
                "max_paginas": 1000
            },
            "autenticacion": {
                "tipo": None,  # None, "bearer", "basic", "api_key"
                "token": None,
                "usuario": None,
                "contraseña": None,
                "api_key": None,
                "header_auth": "Authorization"
            },
            "filtros": {},
            "transformacion_respuesta": None
        }
        
        # Combinar configuración
        self.configuracion_final = {**self.configuracion_default, **self.configuracion}
    
    def validar_configuracion(self) -> bool:
        """
        Validar configuración del extractor
        
        Returns:
            True si la configuración es válida
            
        Raises:
            ErrorConfiguracion: Si la configuración es inválida
        """
        # Validar URL base
        try:
            urlparse(self.url_base)
        except Exception:
            raise ErrorConfiguracion(f"URL base inválida: {self.url_base}")
        
        # Validar método HTTP
        metodos_validos = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        if self.configuracion_final['metodo'] not in metodos_validos:
            raise ErrorConfiguracion(f"Método HTTP inválido: {self.configuracion_final['metodo']}")
        
        # Validar autenticación
        auth_config = self.configuracion_final['autenticacion']
        if auth_config['tipo'] and auth_config['tipo'] not in ["bearer", "basic", "api_key"]:
            raise ErrorConfiguracion(f"Tipo de autenticación inválido: {auth_config['tipo']}")
        
        # Validar rate limit
        if self.configuracion_final['rate_limit'] <= 0:
            raise ErrorConfiguracion("Rate limit debe ser mayor a 0")
        
        return True
    
    async def extraer(self, parametros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extraer datos de la API
        
        Args:
            parametros: Parámetros adicionales (opcional)
            
        Returns:
            Lista de registros extraídos
            
        Raises:
            ErrorExtraccion: Si hay error en la extracción
        """
        try:
            self.logger.info(
                "Iniciando extracción API",
                url_base=self.url_base,
                endpoint=self.configuracion_final['endpoint']
            )
            
            # Validar configuración
            self.validar_configuracion()
            
            # Construir URL completa
            url = urljoin(self.url_base, self.configuracion_final['endpoint'])
            
            # Preparar headers
            headers = self.configuracion_final['headers'].copy()
            
            # Agregar autenticación
            await self._agregar_autenticacion(headers)
            
            # Preparar parámetros de consulta
            params = self.configuracion_final['filtros'].copy()
            if parametros:
                params.update(parametros)
            
            # Ejecutar extracción
            if self.configuracion_final['paginacion']['habilitada']:
                registros = await self._extraer_con_paginacion(url, headers, params)
            else:
                registros = await self._extraer_sin_paginacion(url, headers, params)
            
            # Aplicar transformación si está configurada
            if self.configuracion_final['transformacion_respuesta']:
                registros = await self._aplicar_transformacion(registros)
            
            self.logger.info(
                "Extracción API completada",
                url=url,
                registros=len(registros)
            )
            
            return registros
            
        except Exception as e:
            error_msg = f"Error en extracción API: {str(e)}"
            self.logger.error("Error de extracción", error=error_msg)
            raise ErrorExtraccion(error_msg) from e
    
    async def _agregar_autenticacion(self, headers: Dict[str, str]) -> None:
        """Agregar autenticación a los headers"""
        auth_config = self.configuracion_final['autenticacion']
        
        if auth_config['tipo'] == "bearer" and auth_config['token']:
            headers[auth_config['header_auth']] = f"Bearer {auth_config['token']}"
        
        elif auth_config['tipo'] == "api_key" and auth_config['api_key']:
            headers[auth_config['header_auth']] = auth_config['api_key']
    
    async def _extraer_sin_paginacion(
        self, 
        url: str, 
        headers: Dict[str, str], 
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extraer datos sin paginación"""
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=self.configuracion_final['metodo'],
                url=url,
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.configuracion_final['timeout'])
            ) as response:
                
                if response.status != 200:
                    raise ErrorExtraccion(f"Error HTTP {response.status}: {await response.text()}")
                
                data = await response.json()
                
                # Si la respuesta es una lista, devolverla directamente
                if isinstance(data, list):
                    return data
                
                # Si es un diccionario, buscar la clave de datos
                if isinstance(data, dict):
                    # Buscar claves comunes que contengan los datos
                    claves_datos = ['data', 'results', 'items', 'records', 'content']
                    for clave in claves_datos:
                        if clave in data and isinstance(data[clave], list):
                            return data[clave]
                    
                    # Si no se encuentra, devolver el diccionario como un elemento de lista
                    return [data]
                
                return []
    
    async def _extraer_con_paginacion(
        self, 
        url: str, 
        headers: Dict[str, str], 
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extraer datos con paginación"""
        registros = []
        paginacion_config = self.configuracion_final['paginacion']
        
        pagina_actual = 1
        max_paginas = paginacion_config['max_paginas']
        tamano_pagina = paginacion_config['tamano_pagina']
        
        async with aiohttp.ClientSession() as session:
            while pagina_actual <= max_paginas:
                # Agregar parámetros de paginación
                params_pagina = params.copy()
                params_pagina[paginacion_config['parametro_pagina']] = pagina_actual
                params_pagina[paginacion_config['parametro_tamano']] = tamano_pagina
                
                try:
                    async with session.request(
                        method=self.configuracion_final['metodo'],
                        url=url,
                        headers=headers,
                        params=params_pagina,
                        timeout=aiohttp.ClientTimeout(total=self.configuracion_final['timeout'])
                    ) as response:
                        
                        if response.status != 200:
                            self.logger.warning(
                                "Error en página",
                                pagina=pagina_actual,
                                status=response.status
                            )
                            break
                        
                        data = await response.json()
                        
                        # Extraer registros de la respuesta
                        registros_pagina = self._extraer_registros_de_respuesta(data)
                        
                        if not registros_pagina:
                            # No hay más datos
                            break
                        
                        registros.extend(registros_pagina)
                        
                        # Si recibimos menos registros que el tamaño de página, es la última página
                        if len(registros_pagina) < tamano_pagina:
                            break
                        
                        pagina_actual += 1
                        
                        # Rate limiting
                        if self.configuracion_final['rate_limit'] > 0:
                            delay = 60 / self.configuracion_final['rate_limit']
                            await asyncio.sleep(delay)
                
                except Exception as e:
                    self.logger.error(
                        "Error en página",
                        pagina=pagina_actual,
                        error=str(e)
                    )
                    break
        
        return registros
    
    def _extraer_registros_de_respuesta(self, data: Any) -> List[Dict[str, Any]]:
        """Extraer registros de la respuesta de la API"""
        if isinstance(data, list):
            return data
        
        if isinstance(data, dict):
            # Buscar claves comunes que contengan los datos
            claves_datos = ['data', 'results', 'items', 'records', 'content']
            for clave in claves_datos:
                if clave in data and isinstance(data[clave], list):
                    return data[clave]
            
            # Si no se encuentra, devolver el diccionario como un elemento de lista
            return [data]
        
        return []
    
    async def _aplicar_transformacion(self, registros: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aplicar transformación a los registros"""
        # Aquí se implementaría la lógica de transformación específica
        # Por ahora, devolver los registros sin modificar
        return registros
    
    async def probar_conexion(self) -> Dict[str, Any]:
        """
        Probar conexión a la API
        
        Returns:
            Diccionario con resultado de la prueba
        """
        try:
            url = urljoin(self.url_base, self.configuracion_final['endpoint'])
            headers = self.configuracion_final['headers'].copy()
            
            # Agregar autenticación
            await self._agregar_autenticacion(headers)
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method="GET",
                    url=url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    return {
                        "conexion_exitosa": True,
                        "status_code": response.status,
                        "headers_respuesta": dict(response.headers),
                        "tiempo_respuesta_ms": response.headers.get('X-Response-Time', 'N/A')
                    }
        
        except Exception as e:
            return {
                "conexion_exitosa": False,
                "error": str(e)
            }
