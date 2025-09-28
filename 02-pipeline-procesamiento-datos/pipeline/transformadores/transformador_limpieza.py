"""
Transformador de Limpieza - Pipeline ETL
Transformador para limpieza y normalización de datos
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from .transformador_base import TransformadorBase
from ..excepciones.excepciones_pipeline import ErrorTransformacion, ErrorConfiguracion


class TransformadorLimpieza(TransformadorBase):
    """
    Transformador para limpieza de datos
    Maneja valores nulos, outliers, duplicados y normalización
    """
    
    def __init__(
        self, 
        nombre: str = "LimpiezaDatos",
        configuracion: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializar transformador de limpieza
        
        Args:
            nombre: Nombre del transformador
            configuracion: Configuración específica
        """
        super().__init__(nombre, configuracion)
        
        # Configuración por defecto
        self.configuracion_default = {
            "manejo_nulos": {
                "estrategia": "eliminar",  # "eliminar", "imputar", "marcar"
                "imputacion": "media",  # "media", "mediana", "moda", "valor_fijo"
                "valor_fijo": None,
                "columnas_especificas": {}
            },
            "manejo_outliers": {
                "habilitado": True,
                "metodo": "iqr",  # "iqr", "zscore", "isolation_forest"
                "factor": 1.5,
                "columnas_numericas": None  # None = todas las numéricas
            },
            "manejo_duplicados": {
                "habilitado": True,
                "mantener": "primero",  # "primero", "ultimo", "ninguno"
                "subset": None  # None = todas las columnas
            },
            "normalizacion_texto": {
                "habilitada": True,
                "minusculas": True,
                "eliminar_espacios": True,
                "eliminar_caracteres_especiales": False,
                "normalizar_acentos": True
            },
            "normalizacion_fechas": {
                "habilitada": True,
                "formato_entrada": "auto",  # "auto" o formato específico
                "formato_salida": "%Y-%m-%d %H:%M:%S",
                "zona_horaria": "UTC"
            },
            "validacion_datos": {
                "habilitada": True,
                "rangos_numericos": {},
                "valores_permitidos": {},
                "longitud_texto": {}
            }
        }
        
        # Combinar configuración
        self.configuracion_final = {**self.configuracion_default, **self.configuracion}
    
    def validar_configuracion(self) -> bool:
        """
        Validar configuración del transformador
        
        Returns:
            True si la configuración es válida
            
        Raises:
            ErrorConfiguracion: Si la configuración es inválida
        """
        # Validar estrategia de manejo de nulos
        estrategias_validas = ["eliminar", "imputar", "marcar"]
        if self.configuracion_final['manejo_nulos']['estrategia'] not in estrategias_validas:
            raise ErrorConfiguracion(f"Estrategia de nulos inválida: {self.configuracion_final['manejo_nulos']['estrategia']}")
        
        # Validar método de imputación
        if self.configuracion_final['manejo_nulos']['estrategia'] == "imputar":
            metodos_validos = ["media", "mediana", "moda", "valor_fijo"]
            if self.configuracion_final['manejo_nulos']['imputacion'] not in metodos_validos:
                raise ErrorConfiguracion(f"Método de imputación inválido: {self.configuracion_final['manejo_nulos']['imputacion']}")
        
        # Validar método de detección de outliers
        metodos_outliers = ["iqr", "zscore", "isolation_forest"]
        if self.configuracion_final['manejo_outliers']['metodo'] not in metodos_outliers:
            raise ErrorConfiguracion(f"Método de outliers inválido: {self.configuracion_final['manejo_outliers']['metodo']}")
        
        return True
    
    async def transformar(self, datos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transformar datos aplicando limpieza
        
        Args:
            datos: Lista de registros a transformar
            
        Returns:
            Lista de registros transformados
            
        Raises:
            ErrorTransformacion: Si hay error en la transformación
        """
        try:
            self.logger.info(
                "Iniciando transformación de limpieza",
                registros_entrada=len(datos)
            )
            
            # Validar configuración
            self.validar_configuracion()
            
            if not datos:
                self.logger.warning("No hay datos para transformar")
                return []
            
            # Convertir a DataFrame para facilitar el procesamiento
            df = pd.DataFrame(datos)
            
            # Aplicar transformaciones
            df_limpio = await self._aplicar_limpieza(df)
            
            # Convertir de vuelta a lista de diccionarios
            registros_limpios = df_limpio.to_dict('records')
            
            self.logger.info(
                "Transformación de limpieza completada",
                registros_entrada=len(datos),
                registros_salida=len(registros_limpios),
                registros_eliminados=len(datos) - len(registros_limpios)
            )
            
            return registros_limpios
            
        except Exception as e:
            error_msg = f"Error en transformación de limpieza: {str(e)}"
            self.logger.error("Error de transformación", error=error_msg)
            raise ErrorTransformacion(error_msg) from e
    
    async def _aplicar_limpieza(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar todas las transformaciones de limpieza"""
        df_limpio = df.copy()
        
        # 1. Manejo de valores nulos
        df_limpio = await self._manejar_valores_nulos(df_limpio)
        
        # 2. Normalización de texto
        if self.configuracion_final['normalizacion_texto']['habilitada']:
            df_limpio = await self._normalizar_texto(df_limpio)
        
        # 3. Normalización de fechas
        if self.configuracion_final['normalizacion_fechas']['habilitada']:
            df_limpio = await self._normalizar_fechas(df_limpio)
        
        # 4. Manejo de duplicados
        if self.configuracion_final['manejo_duplicados']['habilitado']:
            df_limpio = await self._manejar_duplicados(df_limpio)
        
        # 5. Manejo de outliers
        if self.configuracion_final['manejo_outliers']['habilitado']:
            df_limpio = await self._manejar_outliers(df_limpio)
        
        # 6. Validación de datos
        if self.configuracion_final['validacion_datos']['habilitada']:
            df_limpio = await self._validar_datos(df_limpio)
        
        return df_limpio
    
    async def _manejar_valores_nulos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Manejar valores nulos en el DataFrame"""
        config_nulos = self.configuracion_final['manejo_nulos']
        estrategia = config_nulos['estrategia']
        
        if estrategia == "eliminar":
            # Eliminar filas con valores nulos
            df_limpio = df.dropna()
            self.logger.info(f"Eliminadas {len(df) - len(df_limpio)} filas con valores nulos")
        
        elif estrategia == "imputar":
            # Imputar valores nulos
            df_limpio = df.copy()
            metodo = config_nulos['imputacion']
            
            for columna in df.columns:
                if df[columna].dtype in ['int64', 'float64']:
                    if metodo == "media":
                        df_limpio[columna].fillna(df[columna].mean(), inplace=True)
                    elif metodo == "mediana":
                        df_limpio[columna].fillna(df[columna].median(), inplace=True)
                    elif metodo == "moda":
                        df_limpio[columna].fillna(df[columna].mode()[0], inplace=True)
                    elif metodo == "valor_fijo":
                        valor = config_nulos['valor_fijo']
                        if valor is not None:
                            df_limpio[columna].fillna(valor, inplace=True)
                else:
                    # Para columnas no numéricas, usar moda o valor fijo
                    if metodo == "moda":
                        moda = df[columna].mode()
                        if not moda.empty:
                            df_limpio[columna].fillna(moda[0], inplace=True)
                    elif metodo == "valor_fijo":
                        valor = config_nulos['valor_fijo']
                        if valor is not None:
                            df_limpio[columna].fillna(valor, inplace=True)
            
            self.logger.info("Valores nulos imputados")
        
        elif estrategia == "marcar":
            # Marcar valores nulos con un indicador
            df_limpio = df.copy()
            for columna in df.columns:
                df_limpio[f"{columna}_es_nulo"] = df[columna].isnull()
            self.logger.info("Valores nulos marcados")
        
        return df_limpio
    
    async def _normalizar_texto(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalizar columnas de texto"""
        config_texto = self.configuracion_final['normalizacion_texto']
        df_limpio = df.copy()
        
        for columna in df.columns:
            if df[columna].dtype == 'object':
                # Convertir a string y manejar nulos
                serie = df[columna].astype(str)
                
                # Aplicar normalizaciones
                if config_texto['minusculas']:
                    serie = serie.str.lower()
                
                if config_texto['eliminar_espacios']:
                    serie = serie.str.strip()
                
                if config_texto['eliminar_caracteres_especiales']:
                    serie = serie.str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
                
                if config_texto['normalizar_acentos']:
                    # Normalizar acentos (simplificado)
                    serie = serie.str.normalize('NFD').str.encode('ascii', errors='ignore').str.decode('utf-8')
                
                df_limpio[columna] = serie
        
        self.logger.info("Texto normalizado")
        return df_limpio
    
    async def _normalizar_fechas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalizar columnas de fechas"""
        config_fechas = self.configuracion_final['normalizacion_fechas']
        df_limpio = df.copy()
        
        for columna in df.columns:
            if df[columna].dtype == 'object':
                try:
                    # Intentar convertir a datetime
                    if config_fechas['formato_entrada'] == "auto":
                        df_limpio[columna] = pd.to_datetime(df[columna], infer_datetime_format=True)
                    else:
                        df_limpio[columna] = pd.to_datetime(df[columna], format=config_fechas['formato_entrada'])
                    
                    # Aplicar zona horaria si se especifica
                    if config_fechas['zona_horaria']:
                        df_limpio[columna] = df_limpio[columna].dt.tz_localize(config_fechas['zona_horaria'])
                    
                    # Formatear según el formato de salida
                    df_limpio[columna] = df_limpio[columna].dt.strftime(config_fechas['formato_salida'])
                    
                except Exception as e:
                    self.logger.warning(f"No se pudo normalizar fecha en columna {columna}: {str(e)}")
        
        self.logger.info("Fechas normalizadas")
        return df_limpio
    
    async def _manejar_duplicados(self, df: pd.DataFrame) -> pd.DataFrame:
        """Manejar registros duplicados"""
        config_duplicados = self.configuracion_final['manejo_duplicados']
        subset = config_duplicados['subset']
        mantener = config_duplicados['mantener']
        
        duplicados_antes = df.duplicated(subset=subset).sum()
        
        if mantener == "primero":
            df_limpio = df.drop_duplicates(subset=subset, keep='first')
        elif mantener == "ultimo":
            df_limpio = df.drop_duplicates(subset=subset, keep='last')
        elif mantener == "ninguno":
            df_limpio = df.drop_duplicates(subset=subset, keep=False)
        else:
            df_limpio = df
        
        duplicados_eliminados = duplicados_antes - df_limpio.duplicated(subset=subset).sum()
        self.logger.info(f"Eliminados {duplicados_eliminados} registros duplicados")
        
        return df_limpio
    
    async def _manejar_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Manejar valores atípicos (outliers)"""
        config_outliers = self.configuracion_final['manejo_outliers']
        metodo = config_outliers['metodo']
        factor = config_outliers['factor']
        columnas = config_outliers['columnas_numericas']
        
        if columnas is None:
            columnas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        df_limpio = df.copy()
        outliers_eliminados = 0
        
        for columna in columnas:
            if columna in df.columns and df[columna].dtype in ['int64', 'float64']:
                if metodo == "iqr":
                    Q1 = df[columna].quantile(0.25)
                    Q3 = df[columna].quantile(0.75)
                    IQR = Q3 - Q1
                    limite_inferior = Q1 - factor * IQR
                    limite_superior = Q3 + factor * IQR
                    
                    outliers = (df[columna] < limite_inferior) | (df[columna] > limite_superior)
                    df_limpio = df_limpio[~outliers]
                    outliers_eliminados += outliers.sum()
                
                elif metodo == "zscore":
                    z_scores = np.abs((df[columna] - df[columna].mean()) / df[columna].std())
                    outliers = z_scores > factor
                    df_limpio = df_limpio[~outliers]
                    outliers_eliminados += outliers.sum()
        
        self.logger.info(f"Eliminados {outliers_eliminados} outliers")
        return df_limpio
    
    async def _validar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validar datos según reglas configuradas"""
        config_validacion = self.configuracion_final['validacion_datos']
        df_limpio = df.copy()
        
        # Validar rangos numéricos
        for columna, rango in config_validacion['rangos_numericos'].items():
            if columna in df.columns and df[columna].dtype in ['int64', 'float64']:
                if 'min' in rango:
                    df_limpio = df_limpio[df_limpio[columna] >= rango['min']]
                if 'max' in rango:
                    df_limpio = df_limpio[df_limpio[columna] <= rango['max']]
        
        # Validar valores permitidos
        for columna, valores in config_validacion['valores_permitidos'].items():
            if columna in df.columns:
                df_limpio = df_limpio[df_limpio[columna].isin(valores)]
        
        # Validar longitud de texto
        for columna, longitud in config_validacion['longitud_texto'].items():
            if columna in df.columns and df[columna].dtype == 'object':
                if 'min' in longitud:
                    df_limpio = df_limpio[df_limpio[columna].str.len() >= longitud['min']]
                if 'max' in longitud:
                    df_limpio = df_limpio[df_limpio[columna].str.len() <= longitud['max']]
        
        self.logger.info("Validación de datos aplicada")
        return df_limpio
