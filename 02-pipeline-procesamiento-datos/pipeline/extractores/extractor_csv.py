"""
Extractor CSV - Pipeline ETL
Extractor para archivos CSV con funcionalidades avanzadas
"""
import pandas as pd
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import structlog

from .extractor_base import ExtractorBase
from ..excepciones.excepciones_pipeline import ErrorExtraccion, ErrorConfiguracion


class ExtractorCSV(ExtractorBase):
    """
    Extractor para archivos CSV
    Soporta múltiples formatos y configuraciones
    """
    
    def __init__(
        self, 
        nombre: str, 
        ruta_archivo: str,
        configuracion: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializar extractor CSV
        
        Args:
            nombre: Nombre del extractor
            ruta_archivo: Ruta al archivo CSV
            configuracion: Configuración específica
        """
        super().__init__(nombre, configuracion)
        self.ruta_archivo = ruta_archivo
        
        # Configuración por defecto
        self.configuracion_default = {
            "separador": ",",
            "encoding": "utf-8",
            "header": 0,
            "skip_blank_lines": True,
            "na_values": ["", "NULL", "null", "N/A", "n/a"],
            "chunksize": None,
            "usecols": None,
            "dtype": None,
            "parse_dates": None,
            "date_parser": None
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
        # Verificar que el archivo existe
        if not os.path.exists(self.ruta_archivo):
            raise ErrorConfiguracion(f"Archivo no encontrado: {self.ruta_archivo}")
        
        # Verificar que es un archivo CSV
        if not self.ruta_archivo.lower().endswith('.csv'):
            raise ErrorConfiguracion(f"El archivo debe ser CSV: {self.ruta_archivo}")
        
        # Verificar encoding válido
        encodings_validos = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        if self.configuracion_final['encoding'] not in encodings_validos:
            raise ErrorConfiguracion(f"Encoding no válido: {self.configuracion_final['encoding']}")
        
        # Verificar separador válido
        separadores_validos = [',', ';', '\t', '|', ' ']
        if self.configuracion_final['separador'] not in separadores_validos:
            raise ErrorConfiguracion(f"Separador no válido: {self.configuracion_final['separador']}")
        
        return True
    
    async def extraer(self, parametros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extraer datos del archivo CSV
        
        Args:
            parametros: Parámetros adicionales (opcional)
            
        Returns:
            Lista de registros extraídos
            
        Raises:
            ErrorExtraccion: Si hay error en la extracción
        """
        try:
            self.logger.info(
                "Iniciando extracción CSV",
                archivo=self.ruta_archivo,
                configuracion=self.configuracion_final
            )
            
            # Validar configuración
            self.validar_configuracion()
            
            # Leer archivo CSV
            df = pd.read_csv(
                self.ruta_archivo,
                sep=self.configuracion_final['separador'],
                encoding=self.configuracion_final['encoding'],
                header=self.configuracion_final['header'],
                skip_blank_lines=self.configuracion_final['skip_blank_lines'],
                na_values=self.configuracion_final['na_values'],
                chunksize=self.configuracion_final['chunksize'],
                usecols=self.configuracion_final['usecols'],
                dtype=self.configuracion_final['dtype'],
                parse_dates=self.configuracion_final['parse_dates'],
                date_parser=self.configuracion_final['date_parser']
            )
            
            # Si se especificó chunksize, procesar en lotes
            if self.configuracion_final['chunksize']:
                registros = []
                for chunk in df:
                    registros.extend(chunk.to_dict('records'))
            else:
                registros = df.to_dict('records')
            
            self.logger.info(
                "Extracción CSV completada",
                archivo=self.ruta_archivo,
                registros=len(registros)
            )
            
            return registros
            
        except FileNotFoundError as e:
            error_msg = f"Archivo no encontrado: {self.ruta_archivo}"
            self.logger.error("Error de archivo", error=error_msg)
            raise ErrorExtraccion(error_msg) from e
        
        except pd.errors.EmptyDataError as e:
            error_msg = f"Archivo CSV vacío: {self.ruta_archivo}"
            self.logger.error("Error de datos vacíos", error=error_msg)
            raise ErrorExtraccion(error_msg) from e
        
        except pd.errors.ParserError as e:
            error_msg = f"Error de parsing CSV: {str(e)}"
            self.logger.error("Error de parsing", error=error_msg)
            raise ErrorExtraccion(error_msg) from e
        
        except UnicodeDecodeError as e:
            error_msg = f"Error de encoding: {str(e)}"
            self.logger.error("Error de encoding", error=error_msg)
            raise ErrorExtraccion(error_msg) from e
        
        except Exception as e:
            error_msg = f"Error inesperado en extracción CSV: {str(e)}"
            self.logger.error("Error inesperado", error=error_msg)
            raise ErrorExtraccion(error_msg) from e
    
    def obtener_informacion_archivo(self) -> Dict[str, Any]:
        """
        Obtener información del archivo CSV
        
        Returns:
            Diccionario con información del archivo
        """
        try:
            if not os.path.exists(self.ruta_archivo):
                return {"error": "Archivo no encontrado"}
            
            stat = os.stat(self.ruta_archivo)
            
            # Leer solo las primeras líneas para obtener información
            df_info = pd.read_csv(
                self.ruta_archivo,
                sep=self.configuracion_final['separador'],
                encoding=self.configuracion_final['encoding'],
                nrows=5
            )
            
            return {
                "ruta_archivo": self.ruta_archivo,
                "tamaño_bytes": stat.st_size,
                "columnas": list(df_info.columns),
                "tipos_datos": df_info.dtypes.to_dict(),
                "muestra_datos": df_info.head(3).to_dict('records'),
                "configuracion": self.configuracion_final
            }
            
        except Exception as e:
            return {"error": f"Error al obtener información: {str(e)}"}
    
    def validar_estructura_archivo(self) -> Dict[str, Any]:
        """
        Validar estructura del archivo CSV
        
        Returns:
            Diccionario con resultados de validación
        """
        try:
            # Leer archivo completo
            df = pd.read_csv(
                self.ruta_archivo,
                sep=self.configuracion_final['separador'],
                encoding=self.configuracion_final['encoding']
            )
            
            # Calcular métricas de calidad
            total_registros = len(df)
            registros_nulos = df.isnull().sum().sum()
            columnas_nulas = df.isnull().all().sum()
            filas_duplicadas = df.duplicated().sum()
            
            return {
                "valido": True,
                "total_registros": total_registros,
                "total_columnas": len(df.columns),
                "registros_nulos": int(registros_nulos),
                "porcentaje_nulos": float(registros_nulos / (total_registros * len(df.columns)) * 100),
                "columnas_nulas": int(columnas_nulas),
                "filas_duplicadas": int(filas_duplicadas),
                "tipos_datos": df.dtypes.to_dict(),
                "estadisticas": df.describe().to_dict()
            }
            
        except Exception as e:
            return {
                "valido": False,
                "error": str(e)
            }
