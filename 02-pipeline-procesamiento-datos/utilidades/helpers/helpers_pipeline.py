"""
Helpers del Pipeline - Utilidades
Funciones auxiliares para el pipeline de procesamiento de datos
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog


def calcular_metricas_calidad(datos: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calcular métricas de calidad de los datos
    
    Args:
        datos: Lista de registros de datos
        
    Returns:
        Diccionario con métricas de calidad
    """
    if not datos:
        return {
            'completitud': 0.0,
            'consistencia': 0.0,
            'precision': 0.0,
            'total_registros': 0
        }
    
    df = pd.DataFrame(datos)
    
    # Completitud: porcentaje de valores no nulos
    total_celdas = df.size
    celdas_nulas = df.isnull().sum().sum()
    completitud = ((total_celdas - celdas_nulas) / total_celdas) * 100 if total_celdas > 0 else 0
    
    # Consistencia: porcentaje de registros sin duplicados
    registros_duplicados = df.duplicated().sum()
    total_registros = len(df)
    consistencia = ((total_registros - registros_duplicados) / total_registros) * 100 if total_registros > 0 else 0
    
    # Precisión: métrica basada en tipos de datos y rangos
    precision = _calcular_precision_datos(df)
    
    return {
        'completitud': round(completitud, 2),
        'consistencia': round(consistencia, 2),
        'precision': round(precision, 2),
        'total_registros': total_registros,
        'registros_duplicados': int(registros_duplicados),
        'celdas_nulas': int(celdas_nulas)
    }


def _calcular_precision_datos(df: pd.DataFrame) -> float:
    """
    Calcular precisión de los datos basada en tipos y rangos
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Puntuación de precisión (0-100)
    """
    puntuacion = 0
    total_columnas = len(df.columns)
    
    if total_columnas == 0:
        return 0.0
    
    for columna in df.columns:
        col_puntuacion = 0
        
        # Verificar si la columna tiene datos
        if df[columna].notna().sum() == 0:
            continue
        
        # Verificar consistencia de tipos
        if df[columna].dtype in ['int64', 'float64']:
            # Para columnas numéricas, verificar que no haya valores infinitos
            if not np.isinf(df[columna]).any():
                col_puntuacion += 1
            
            # Verificar que no haya valores extremos (outliers)
            if not _tiene_outliers_extremos(df[columna]):
                col_puntuacion += 1
        
        elif df[columna].dtype == 'object':
            # Para columnas de texto, verificar consistencia
            if _es_texto_consistente(df[columna]):
                col_puntuacion += 1
        
        # Verificar que no haya valores nulos inesperados
        if df[columna].isnull().sum() / len(df) < 0.5:  # Menos del 50% nulos
            col_puntuacion += 1
        
        puntuacion += col_puntuacion
    
    return (puntuacion / (total_columnas * 3)) * 100  # 3 criterios por columna


def _tiene_outliers_extremos(serie: pd.Series) -> bool:
    """Verificar si una serie tiene outliers extremos"""
    if serie.dtype not in ['int64', 'float64']:
        return False
    
    Q1 = serie.quantile(0.25)
    Q3 = serie.quantile(0.75)
    IQR = Q3 - Q1
    
    if IQR == 0:
        return False
    
    limite_inferior = Q1 - 3 * IQR
    limite_superior = Q3 + 3 * IQR
    
    return (serie < limite_inferior).any() or (serie > limite_superior).any()


def _es_texto_consistente(serie: pd.Series) -> bool:
    """Verificar si una serie de texto es consistente"""
    # Verificar que no haya mezcla de tipos
    valores_unicos = serie.dropna().unique()
    
    if len(valores_unicos) == 0:
        return True
    
    # Verificar que todos los valores sean strings
    return all(isinstance(v, str) for v in valores_unicos)


def detectar_outliers_iqr(serie: pd.Series, factor: float = 1.5) -> pd.Series:
    """
    Detectar outliers usando el método IQR
    
    Args:
        serie: Serie de datos
        factor: Factor para el cálculo de IQR
        
    Returns:
        Serie booleana indicando outliers
    """
    Q1 = serie.quantile(0.25)
    Q3 = serie.quantile(0.75)
    IQR = Q3 - Q1
    
    limite_inferior = Q1 - factor * IQR
    limite_superior = Q3 + factor * IQR
    
    return (serie < limite_inferior) | (serie > limite_superior)


def detectar_outliers_zscore(serie: pd.Series, umbral: float = 3.0) -> pd.Series:
    """
    Detectar outliers usando el método Z-Score
    
    Args:
        serie: Serie de datos
        umbral: Umbral para considerar outlier
        
    Returns:
        Serie booleana indicando outliers
    """
    if serie.std() == 0:
        return pd.Series([False] * len(serie), index=serie.index)
    
    z_scores = np.abs((serie - serie.mean()) / serie.std())
    return z_scores > umbral


def normalizar_texto(texto: str) -> str:
    """
    Normalizar texto para análisis
    
    Args:
        texto: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if not isinstance(texto, str):
        return str(texto)
    
    # Convertir a minúsculas
    texto = texto.lower()
    
    # Eliminar espacios extra
    texto = ' '.join(texto.split())
    
    # Eliminar caracteres especiales (mantener letras, números y espacios)
    import re
    texto = re.sub(r'[^a-zA-Z0-9\s]', '', texto)
    
    return texto


def convertir_tipos_datos(df: pd.DataFrame, configuracion: Dict[str, str]) -> pd.DataFrame:
    """
    Convertir tipos de datos según configuración
    
    Args:
        df: DataFrame a convertir
        configuracion: Diccionario con mapeo columna -> tipo
        
    Returns:
        DataFrame con tipos convertidos
    """
    df_convertido = df.copy()
    
    for columna, tipo in configuracion.items():
        if columna in df_convertido.columns:
            try:
                if tipo == 'datetime':
                    df_convertido[columna] = pd.to_datetime(df_convertido[columna])
                elif tipo == 'numeric':
                    df_convertido[columna] = pd.to_numeric(df_convertido[columna], errors='coerce')
                elif tipo == 'category':
                    df_convertido[columna] = df_convertido[columna].astype('category')
                else:
                    df_convertido[columna] = df_convertido[columna].astype(tipo)
            except Exception as e:
                structlog.get_logger().warning(f"Error convirtiendo columna {columna} a {tipo}: {str(e)}")
    
    return df_convertido


def calcular_estadisticas_resumen(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcular estadísticas resumen del DataFrame
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Diccionario con estadísticas resumen
    """
    return {
        'informacion_general': {
            'total_registros': len(df),
            'total_columnas': len(df.columns),
            'memoria_uso_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'tipos_datos': df.dtypes.value_counts().to_dict()
        },
        'calidad_datos': {
            'valores_nulos': df.isnull().sum().to_dict(),
            'porcentaje_nulos': (df.isnull().sum() / len(df) * 100).to_dict(),
            'valores_duplicados': df.duplicated().sum(),
            'porcentaje_duplicados': (df.duplicated().sum() / len(df) * 100)
        },
        'estadisticas_numericas': df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {}
    }


def generar_reporte_calidad(datos: List[Dict[str, Any]], nombre_archivo: str = "reporte_calidad") -> str:
    """
    Generar reporte de calidad de datos
    
    Args:
        datos: Lista de registros de datos
        nombre_archivo: Nombre del archivo de reporte
        
    Returns:
        Ruta del archivo de reporte generado
    """
    logger = structlog.get_logger()
    
    try:
        # Calcular métricas
        metricas = calcular_metricas_calidad(datos)
        df = pd.DataFrame(datos)
        estadisticas = calcular_estadisticas_resumen(df)
        
        # Crear reporte HTML
        reporte_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reporte de Calidad de Datos</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .metric {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007acc; }}
                .metric h3 {{ margin-top: 0; color: #007acc; }}
                .value {{ font-size: 24px; font-weight: bold; color: #333; }}
                .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .table th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Reporte de Calidad de Datos</h1>
                <p>Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metric">
                <h3>Completitud</h3>
                <div class="value">{metricas['completitud']}%</div>
                <p>Porcentaje de valores no nulos en el dataset</p>
            </div>
            
            <div class="metric">
                <h3>Consistencia</h3>
                <div class="value">{metricas['consistencia']}%</div>
                <p>Porcentaje de registros únicos (sin duplicados)</p>
            </div>
            
            <div class="metric">
                <h3>Precisión</h3>
                <div class="value">{metricas['precision']}%</div>
                <p>Puntuación de precisión basada en tipos y rangos</p>
            </div>
            
            <h2>Información General</h2>
            <table class="table">
                <tr><th>Métrica</th><th>Valor</th></tr>
                <tr><td>Total de Registros</td><td>{estadisticas['informacion_general']['total_registros']}</td></tr>
                <tr><td>Total de Columnas</td><td>{estadisticas['informacion_general']['total_columnas']}</td></tr>
                <tr><td>Uso de Memoria (MB)</td><td>{estadisticas['informacion_general']['memoria_uso_mb']:.2f}</td></tr>
            </table>
            
            <h2>Calidad de Datos</h2>
            <table class="table">
                <tr><th>Métrica</th><th>Valor</th></tr>
                <tr><td>Registros Duplicados</td><td>{estadisticas['calidad_datos']['valores_duplicados']}</td></tr>
                <tr><td>% Duplicados</td><td>{estadisticas['calidad_datos']['porcentaje_duplicados']:.2f}%</td></tr>
            </table>
        </body>
        </html>
        """
        
        # Guardar reporte
        ruta_archivo = f"{nombre_archivo}.html"
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(reporte_html)
        
        logger.info(f"Reporte de calidad generado: {ruta_archivo}")
        return ruta_archivo
        
    except Exception as e:
        logger.error(f"Error generando reporte de calidad: {str(e)}")
        return ""
