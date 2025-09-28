"""
Analizador Estadístico - Análisis de Datos
Analizador para estadísticas descriptivas y análisis avanzado
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import structlog

from ..utilidades.decoradores.decorador_logging import logging_metodo
from ..utilidades.decoradores.decorador_validacion import validar_parametros


@dataclass
class EstadisticasDescriptivas:
    """Resultado de estadísticas descriptivas"""
    
    # Estadísticas básicas
    conteo: int
    media: float
    mediana: float
    moda: Any
    desviacion_estandar: float
    varianza: float
    
    # Estadísticas de posición
    minimo: float
    maximo: float
    q1: float  # Primer cuartil
    q3: float  # Tercer cuartil
    iqr: float  # Rango intercuartílico
    
    # Estadísticas de forma
    asimetria: float
    curtosis: float
    
    # Estadísticas de dispersión
    rango: float
    coeficiente_variacion: float
    
    # Valores nulos
    valores_nulos: int
    porcentaje_nulos: float


@dataclass
class AnalisisCorrelacion:
    """Resultado de análisis de correlación"""
    
    matriz_correlacion: pd.DataFrame
    correlaciones_fuertes: List[Dict[str, Any]]
    correlaciones_significativas: List[Dict[str, Any]]
    estadisticas_generales: Dict[str, float]


@dataclass
class AnalisisTendencias:
    """Resultado de análisis de tendencias"""
    
    tendencia_lineal: Dict[str, float]
    tendencia_cuadratica: Dict[str, float]
    estacionalidad: Dict[str, Any]
    prediccion: List[float]
    metricas_prediccion: Dict[str, float]


class AnalizadorEstadistico:
    """
    Analizador estadístico para datos empresariales
    Implementa análisis descriptivo, correlaciones y tendencias
    """
    
    def __init__(self, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar analizador estadístico
        
        Args:
            configuracion: Configuración específica del analizador
        """
        self.configuracion = configuracion or {}
        self.logger = structlog.get_logger()
        
        # Configuración por defecto
        self.configuracion_default = {
            "nivel_significancia": 0.05,
            "correlacion_minima": 0.3,
            "correlacion_fuerte": 0.7,
            "incluir_outliers": True,
            "metodo_imputacion": "media",
            "ventana_movil": 7
        }
        
        # Combinar configuración
        self.configuracion_final = {**self.configuracion_default, **self.configuracion}
    
    @logging_metodo(nombre_logger="analisis_estadistico", incluir_tiempo=True)
    @validar_parametros(validar_tipos=True)
    async def analizar_estadisticas_descriptivas(
        self, 
        df: pd.DataFrame, 
        columnas: Optional[List[str]] = None
    ) -> Dict[str, EstadisticasDescriptivas]:
        """
        Calcular estadísticas descriptivas para columnas numéricas
        
        Args:
            df: DataFrame con los datos
            columnas: Lista de columnas a analizar (None = todas las numéricas)
            
        Returns:
            Diccionario con estadísticas por columna
        """
        if columnas is None:
            columnas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        estadisticas = {}
        
        for columna in columnas:
            if columna not in df.columns:
                self.logger.warning(f"Columna no encontrada: {columna}")
                continue
            
            serie = df[columna].dropna()
            
            if len(serie) == 0:
                self.logger.warning(f"Columna {columna} no tiene datos válidos")
                continue
            
            # Estadísticas básicas
            conteo = len(serie)
            media = serie.mean()
            mediana = serie.median()
            moda = serie.mode().iloc[0] if not serie.mode().empty else None
            desviacion_estandar = serie.std()
            varianza = serie.var()
            
            # Estadísticas de posición
            minimo = serie.min()
            maximo = serie.max()
            q1 = serie.quantile(0.25)
            q3 = serie.quantile(0.75)
            iqr = q3 - q1
            
            # Estadísticas de forma
            asimetria = serie.skew()
            curtosis = serie.kurtosis()
            
            # Estadísticas de dispersión
            rango = maximo - minimo
            coeficiente_variacion = (desviacion_estandar / media) * 100 if media != 0 else 0
            
            # Valores nulos
            valores_nulos = df[columna].isnull().sum()
            porcentaje_nulos = (valores_nulos / len(df)) * 100
            
            estadisticas[columna] = EstadisticasDescriptivas(
                conteo=conteo,
                media=media,
                mediana=mediana,
                moda=moda,
                desviacion_estandar=desviacion_estandar,
                varianza=varianza,
                minimo=minimo,
                maximo=maximo,
                q1=q1,
                q3=q3,
                iqr=iqr,
                asimetria=asimetria,
                curtosis=curtosis,
                rango=rango,
                coeficiente_variacion=coeficiente_variacion,
                valores_nulos=valores_nulos,
                porcentaje_nulos=porcentaje_nulos
            )
        
        self.logger.info(f"Estadísticas descriptivas calculadas para {len(estadisticas)} columnas")
        return estadisticas
    
    @logging_metodo(nombre_logger="analisis_estadistico", incluir_tiempo=True)
    @validar_parametros(validar_tipos=True)
    async def analizar_correlaciones(
        self, 
        df: pd.DataFrame, 
        columnas: Optional[List[str]] = None
    ) -> AnalisisCorrelacion:
        """
        Analizar correlaciones entre variables numéricas
        
        Args:
            df: DataFrame con los datos
            columnas: Lista de columnas a analizar (None = todas las numéricas)
            
        Returns:
            Análisis de correlación
        """
        if columnas is None:
            columnas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Filtrar columnas existentes
        columnas = [col for col in columnas if col in df.columns]
        
        if len(columnas) < 2:
            self.logger.warning("Se necesitan al menos 2 columnas numéricas para análisis de correlación")
            return AnalisisCorrelacion(
                matriz_correlacion=pd.DataFrame(),
                correlaciones_fuertes=[],
                correlaciones_significativas=[],
                estadisticas_generales={}
            )
        
        # Calcular matriz de correlación
        df_numerico = df[columnas].dropna()
        matriz_correlacion = df_numerico.corr()
        
        # Encontrar correlaciones fuertes
        correlaciones_fuertes = []
        correlaciones_significativas = []
        
        for i in range(len(columnas)):
            for j in range(i + 1, len(columnas)):
                col1, col2 = columnas[i], columnas[j]
                correlacion = matriz_correlacion.loc[col1, col2]
                
                # Verificar si es correlación fuerte
                if abs(correlacion) >= self.configuracion_final['correlacion_fuerte']:
                    correlaciones_fuertes.append({
                        'variable1': col1,
                        'variable2': col2,
                        'correlacion': correlacion,
                        'magnitud': 'muy_fuerte' if abs(correlacion) >= 0.8 else 'fuerte'
                    })
                
                # Verificar significancia estadística
                if len(df_numerico) > 3:  # Mínimo para test de correlación
                    try:
                        _, p_value = stats.pearsonr(df_numerico[col1], df_numerico[col2])
                        if p_value < self.configuracion_final['nivel_significancia']:
                            correlaciones_significativas.append({
                                'variable1': col1,
                                'variable2': col2,
                                'correlacion': correlacion,
                                'p_value': p_value,
                                'significativa': True
                            })
                    except Exception as e:
                        self.logger.warning(f"Error calculando significancia para {col1}-{col2}: {str(e)}")
        
        # Estadísticas generales
        correlaciones_absolutas = np.abs(matriz_correlacion.values)
        np.fill_diagonal(correlaciones_absolutas, 0)  # Excluir diagonal
        
        estadisticas_generales = {
            'correlacion_promedio': float(np.mean(correlaciones_absolutas)),
            'correlacion_maxima': float(np.max(correlaciones_absolutas)),
            'correlacion_minima': float(np.min(correlaciones_absolutas)),
            'total_pares': len(correlaciones_fuertes) + len(correlaciones_significativas),
            'correlaciones_fuertes': len(correlaciones_fuertes),
            'correlaciones_significativas': len(correlaciones_significativas)
        }
        
        self.logger.info(
            f"Análisis de correlación completado: {len(correlaciones_fuertes)} fuertes, "
            f"{len(correlaciones_significativas)} significativas"
        )
        
        return AnalisisCorrelacion(
            matriz_correlacion=matriz_correlacion,
            correlaciones_fuertes=correlaciones_fuertes,
            correlaciones_significativas=correlaciones_significativas,
            estadisticas_generales=estadisticas_generales
        )
    
    @logging_metodo(nombre_logger="analisis_estadistico", incluir_tiempo=True)
    @validar_parametros(validar_tipos=True)
    async def analizar_tendencias(
        self, 
        df: pd.DataFrame, 
        columna_fecha: str,
        columna_valor: str,
        ventana_prediccion: int = 30
    ) -> AnalisisTendencias:
        """
        Analizar tendencias temporales
        
        Args:
            df: DataFrame con los datos
            columna_fecha: Nombre de la columna de fecha
            columna_valor: Nombre de la columna de valor
            ventana_prediccion: Días para predicción
            
        Returns:
            Análisis de tendencias
        """
        if columna_fecha not in df.columns or columna_valor not in df.columns:
            raise ValueError(f"Columnas no encontradas: {columna_fecha}, {columna_valor}")
        
        # Preparar datos
        df_temp = df[[columna_fecha, columna_valor]].dropna().copy()
        df_temp[columna_fecha] = pd.to_datetime(df_temp[columna_fecha])
        df_temp = df_temp.sort_values(columna_fecha)
        
        if len(df_temp) < 2:
            self.logger.warning("No hay suficientes datos para análisis de tendencias")
            return AnalisisTendencias(
                tendencia_lineal={},
                tendencia_cuadratica={},
                estacionalidad={},
                prediccion=[],
                metricas_prediccion={}
            )
        
        # Crear variable temporal
        df_temp['dias'] = (df_temp[columna_fecha] - df_temp[columna_fecha].min()).dt.days
        X = df_temp['dias'].values.reshape(-1, 1)
        y = df_temp[columna_valor].values
        
        # Tendencia lineal
        try:
            from sklearn.linear_model import LinearRegression
            modelo_lineal = LinearRegression()
            modelo_lineal.fit(X, y)
            y_pred_lineal = modelo_lineal.predict(X)
            
            tendencia_lineal = {
                'pendiente': float(modelo_lineal.coef_[0]),
                'intercepto': float(modelo_lineal.intercept_),
                'r2': float(r2_score(y, y_pred_lineal)),
                'rmse': float(np.sqrt(mean_squared_error(y, y_pred_lineal))),
                'mae': float(mean_absolute_error(y, y_pred_lineal))
            }
        except Exception as e:
            self.logger.warning(f"Error en tendencia lineal: {str(e)}")
            tendencia_lineal = {}
        
        # Tendencia cuadrática
        try:
            from sklearn.preprocessing import PolynomialFeatures
            from sklearn.linear_model import LinearRegression
            from sklearn.pipeline import Pipeline
            
            modelo_cuadratico = Pipeline([
                ('poly', PolynomialFeatures(degree=2)),
                ('linear', LinearRegression())
            ])
            modelo_cuadratico.fit(X, y)
            y_pred_cuadratico = modelo_cuadratico.predict(X)
            
            tendencia_cuadratica = {
                'r2': float(r2_score(y, y_pred_cuadratico)),
                'rmse': float(np.sqrt(mean_squared_error(y, y_pred_cuadratico))),
                'mae': float(mean_absolute_error(y, y_pred_cuadratico))
            }
        except Exception as e:
            self.logger.warning(f"Error en tendencia cuadrática: {str(e)}")
            tendencia_cuadratica = {}
        
        # Análisis de estacionalidad
        estacionalidad = await self._analizar_estacionalidad(df_temp, columna_fecha, columna_valor)
        
        # Predicción
        prediccion = []
        metricas_prediccion = {}
        
        if tendencia_lineal and 'pendiente' in tendencia_lineal:
            try:
                # Generar fechas futuras
                ultima_fecha = df_temp[columna_fecha].max()
                fechas_futuras = pd.date_range(
                    start=ultima_fecha + pd.Timedelta(days=1),
                    periods=ventana_prediccion,
                    freq='D'
                )
                
                # Calcular días futuros
                dias_futuros = (fechas_futuras - df_temp[columna_fecha].min()).days
                X_futuro = np.array(dias_futuros).reshape(-1, 1)
                
                # Predecir valores
                prediccion = modelo_lineal.predict(X_futuro).tolist()
                
                # Calcular métricas de predicción (usando últimos datos como validación)
                if len(df_temp) >= ventana_prediccion:
                    datos_validacion = df_temp.tail(ventana_prediccion)
                    dias_val = (datos_validacion[columna_fecha] - df_temp[columna_fecha].min()).days
                    X_val = np.array(dias_val).reshape(-1, 1)
                    y_val_pred = modelo_lineal.predict(X_val)
                    y_val_real = datos_validacion[columna_valor].values
                    
                    metricas_prediccion = {
                        'rmse': float(np.sqrt(mean_squared_error(y_val_real, y_val_pred))),
                        'mae': float(mean_absolute_error(y_val_real, y_val_pred)),
                        'mape': float(np.mean(np.abs((y_val_real - y_val_pred) / y_val_real)) * 100)
                    }
                
            except Exception as e:
                self.logger.warning(f"Error en predicción: {str(e)}")
        
        self.logger.info("Análisis de tendencias completado")
        
        return AnalisisTendencias(
            tendencia_lineal=tendencia_lineal,
            tendencia_cuadratica=tendencia_cuadratica,
            estacionalidad=estacionalidad,
            prediccion=prediccion,
            metricas_prediccion=metricas_prediccion
        )
    
    async def _analizar_estacionalidad(
        self, 
        df: pd.DataFrame, 
        columna_fecha: str, 
        columna_valor: str
    ) -> Dict[str, Any]:
        """Analizar estacionalidad en los datos"""
        try:
            # Crear variables de estacionalidad
            df['dia_semana'] = df[columna_fecha].dt.dayofweek
            df['mes'] = df[columna_fecha].dt.month
            df['trimestre'] = df[columna_fecha].dt.quarter
            
            # Calcular promedios por período
            estacionalidad = {
                'por_dia_semana': df.groupby('dia_semana')[columna_valor].mean().to_dict(),
                'por_mes': df.groupby('mes')[columna_valor].mean().to_dict(),
                'por_trimestre': df.groupby('trimestre')[columna_valor].mean().to_dict(),
                'variacion_diaria': df.groupby('dia_semana')[columna_valor].std().to_dict(),
                'variacion_mensual': df.groupby('mes')[columna_valor].std().to_dict()
            }
            
            return estacionalidad
            
        except Exception as e:
            self.logger.warning(f"Error en análisis de estacionalidad: {str(e)}")
            return {}
    
    @logging_metodo(nombre_logger="analisis_estadistico", incluir_tiempo=True)
    async def generar_resumen_estadistico(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generar resumen estadístico completo del DataFrame
        
        Args:
            df: DataFrame a analizar
            
        Returns:
            Resumen estadístico completo
        """
        resumen = {
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
            }
        }
        
        # Estadísticas descriptivas para columnas numéricas
        columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
        if columnas_numericas:
            estadisticas_desc = await self.analizar_estadisticas_descriptivas(df, columnas_numericas)
            resumen['estadisticas_descriptivas'] = {
                col: {
                    'media': stats.media,
                    'mediana': stats.mediana,
                    'desviacion_estandar': stats.desviacion_estandar,
                    'minimo': stats.minimo,
                    'maximo': stats.maximo,
                    'asimetria': stats.asimetria,
                    'curtosis': stats.curtosis
                }
                for col, stats in estadisticas_desc.items()
            }
        
        # Análisis de correlaciones
        if len(columnas_numericas) >= 2:
            correlaciones = await self.analizar_correlaciones(df, columnas_numericas)
            resumen['correlaciones'] = {
                'matriz': correlaciones.matriz_correlacion.to_dict(),
                'fuertes': correlaciones.correlaciones_fuertes,
                'significativas': correlaciones.correlaciones_significativas,
                'estadisticas': correlaciones.estadisticas_generales
            }
        
        self.logger.info("Resumen estadístico generado")
        return resumen
