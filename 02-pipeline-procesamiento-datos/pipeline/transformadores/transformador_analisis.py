"""
Transformador de Análisis - Pipeline ETL
Transformador para análisis estadístico y feature engineering
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_regression, f_classif
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

from .transformador_base import TransformadorBase
from ..excepciones.excepciones_pipeline import ErrorTransformacion, ErrorConfiguracion


class TransformadorAnalisis(TransformadorBase):
    """
    Transformador para análisis estadístico y feature engineering
    Incluye normalización, selección de características y análisis avanzado
    """
    
    def __init__(
        self, 
        nombre: str = "AnalisisDatos",
        configuracion: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializar transformador de análisis
        
        Args:
            nombre: Nombre del transformador
            configuracion: Configuración específica
        """
        super().__init__(nombre, configuracion)
        
        # Configuración por defecto
        self.configuracion_default = {
            "normalizacion": {
                "habilitada": True,
                "metodo": "standard",  # "standard", "minmax", "robust"
                "columnas_numericas": None,  # None = todas las numéricas
                "excluir_columnas": []
            },
            "seleccion_caracteristicas": {
                "habilitada": False,
                "metodo": "f_regression",  # "f_regression", "f_classif", "mutual_info"
                "k_caracteristicas": 10,
                "columna_objetivo": None
            },
            "reduccion_dimensionalidad": {
                "habilitada": False,
                "metodo": "pca",  # "pca", "lda"
                "n_componentes": 0.95,  # 0.95 = 95% de varianza, o número entero
                "columnas_numericas": None
            },
            "feature_engineering": {
                "habilitado": True,
                "crear_interacciones": False,
                "crear_polinomios": False,
                "grado_polinomio": 2,
                "crear_agregaciones": True,
                "ventana_temporal": 7,  # días para agregaciones temporales
                "columnas_categoricas": None
            },
            "analisis_temporal": {
                "habilitado": False,
                "columna_fecha": None,
                "crear_tendencias": True,
                "crear_estacionalidad": True,
                "crear_lags": True,
                "lags": [1, 7, 30]  # días de lag
            },
            "clustering": {
                "habilitado": False,
                "metodo": "kmeans",  # "kmeans", "dbscan"
                "n_clusters": 3,
                "columnas_numericas": None
            }
        }
        
        # Combinar configuración
        self.configuracion_final = {**self.configuracion_default, **self.configuracion}
        
        # Inicializar objetos de sklearn
        self.scaler = None
        self.label_encoders = {}
        self.feature_selector = None
        self.pca = None
        self.kmeans = None
    
    def validar_configuracion(self) -> bool:
        """
        Validar configuración del transformador
        
        Returns:
            True si la configuración es válida
            
        Raises:
            ErrorConfiguracion: Si la configuración es inválida
        """
        # Validar método de normalización
        metodos_norm = ["standard", "minmax", "robust"]
        if self.configuracion_final['normalizacion']['metodo'] not in metodos_norm:
            raise ErrorConfiguracion(f"Método de normalización inválido: {self.configuracion_final['normalizacion']['metodo']}")
        
        # Validar método de selección de características
        if self.configuracion_final['seleccion_caracteristicas']['habilitada']:
            metodos_sel = ["f_regression", "f_classif", "mutual_info"]
            if self.configuracion_final['seleccion_caracteristicas']['metodo'] not in metodos_sel:
                raise ErrorConfiguracion(f"Método de selección inválido: {self.configuracion_final['seleccion_caracteristicas']['metodo']}")
        
        # Validar método de reducción de dimensionalidad
        if self.configuracion_final['reduccion_dimensionalidad']['habilitada']:
            metodos_red = ["pca", "lda"]
            if self.configuracion_final['reduccion_dimensionalidad']['metodo'] not in metodos_red:
                raise ErrorConfiguracion(f"Método de reducción inválido: {self.configuracion_final['reduccion_dimensionalidad']['metodo']}")
        
        return True
    
    async def transformar(self, datos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transformar datos aplicando análisis
        
        Args:
            datos: Lista de registros a transformar
            
        Returns:
            Lista de registros transformados
            
        Raises:
            ErrorTransformacion: Si hay error en la transformación
        """
        try:
            self.logger.info(
                "Iniciando transformación de análisis",
                registros_entrada=len(datos)
            )
            
            # Validar configuración
            self.validar_configuracion()
            
            if not datos:
                self.logger.warning("No hay datos para transformar")
                return []
            
            # Convertir a DataFrame
            df = pd.DataFrame(datos)
            
            # Aplicar transformaciones
            df_analizado = await self._aplicar_analisis(df)
            
            # Convertir de vuelta a lista de diccionarios
            registros_analizados = df_analizado.to_dict('records')
            
            self.logger.info(
                "Transformación de análisis completada",
                registros_entrada=len(datos),
                registros_salida=len(registros_analizados),
                columnas_entrada=len(df.columns),
                columnas_salida=len(df_analizado.columns)
            )
            
            return registros_analizados
            
        except Exception as e:
            error_msg = f"Error en transformación de análisis: {str(e)}"
            self.logger.error("Error de transformación", error=error_msg)
            raise ErrorTransformacion(error_msg) from e
    
    async def _aplicar_analisis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar todas las transformaciones de análisis"""
        df_analizado = df.copy()
        
        # 1. Feature Engineering
        if self.configuracion_final['feature_engineering']['habilitado']:
            df_analizado = await self._aplicar_feature_engineering(df_analizado)
        
        # 2. Análisis temporal
        if self.configuracion_final['analisis_temporal']['habilitado']:
            df_analizado = await self._aplicar_analisis_temporal(df_analizado)
        
        # 3. Normalización
        if self.configuracion_final['normalizacion']['habilitada']:
            df_analizado = await self._aplicar_normalizacion(df_analizado)
        
        # 4. Selección de características
        if self.configuracion_final['seleccion_caracteristicas']['habilitada']:
            df_analizado = await self._aplicar_seleccion_caracteristicas(df_analizado)
        
        # 5. Reducción de dimensionalidad
        if self.configuracion_final['reduccion_dimensionalidad']['habilitada']:
            df_analizado = await self._aplicar_reduccion_dimensionalidad(df_analizado)
        
        # 6. Clustering
        if self.configuracion_final['clustering']['habilitado']:
            df_analizado = await self._aplicar_clustering(df_analizado)
        
        return df_analizado
    
    async def _aplicar_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar feature engineering"""
        config_fe = self.configuracion_final['feature_engineering']
        df_fe = df.copy()
        
        # Obtener columnas numéricas
        columnas_numericas = df_fe.select_dtypes(include=[np.number]).columns.tolist()
        
        # Crear interacciones
        if config_fe['crear_interacciones'] and len(columnas_numericas) >= 2:
            for i, col1 in enumerate(columnas_numericas):
                for col2 in columnas_numericas[i+1:]:
                    df_fe[f"{col1}_x_{col2}"] = df_fe[col1] * df_fe[col2]
        
        # Crear polinomios
        if config_fe['crear_polinomios'] and len(columnas_numericas) >= 1:
            grado = config_fe['grado_polinomio']
            for col in columnas_numericas:
                for g in range(2, grado + 1):
                    df_fe[f"{col}_grado_{g}"] = df_fe[col] ** g
        
        # Crear agregaciones
        if config_fe['crear_agregaciones']:
            # Agregaciones por fila
            df_fe['suma_numerica'] = df_fe[columnas_numericas].sum(axis=1)
            df_fe['media_numerica'] = df_fe[columnas_numericas].mean(axis=1)
            df_fe['std_numerica'] = df_fe[columnas_numericas].std(axis=1)
            df_fe['min_numerica'] = df_fe[columnas_numericas].min(axis=1)
            df_fe['max_numerica'] = df_fe[columnas_numericas].max(axis=1)
        
        # Codificar variables categóricas
        columnas_categoricas = config_fe['columnas_categoricas']
        if columnas_categoricas is None:
            columnas_categoricas = df_fe.select_dtypes(include=['object']).columns.tolist()
        
        for col in columnas_categoricas:
            if col in df_fe.columns:
                # Label encoding
                le = LabelEncoder()
                df_fe[f"{col}_encoded"] = le.fit_transform(df_fe[col].astype(str))
                self.label_encoders[col] = le
        
        self.logger.info("Feature engineering aplicado")
        return df_fe
    
    async def _aplicar_analisis_temporal(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar análisis temporal"""
        config_temp = self.configuracion_final['analisis_temporal']
        columna_fecha = config_temp['columna_fecha']
        
        if columna_fecha not in df.columns:
            self.logger.warning(f"Columna de fecha no encontrada: {columna_fecha}")
            return df
        
        df_temp = df.copy()
        df_temp[columna_fecha] = pd.to_datetime(df_temp[columna_fecha])
        df_temp = df_temp.sort_values(columna_fecha)
        
        # Crear tendencias
        if config_temp['crear_tendencias']:
            df_temp['tendencia'] = range(len(df_temp))
        
        # Crear estacionalidad
        if config_temp['crear_estacionalidad']:
            df_temp['dia_semana'] = df_temp[columna_fecha].dt.dayofweek
            df_temp['mes'] = df_temp[columna_fecha].dt.month
            df_temp['trimestre'] = df_temp[columna_fecha].dt.quarter
            df_temp['año'] = df_temp[columna_fecha].dt.year
        
        # Crear lags
        if config_temp['crear_lags']:
            columnas_numericas = df_temp.select_dtypes(include=[np.number]).columns.tolist()
            for lag in config_temp['lags']:
                for col in columnas_numericas:
                    if col != columna_fecha:
                        df_temp[f"{col}_lag_{lag}"] = df_temp[col].shift(lag)
        
        self.logger.info("Análisis temporal aplicado")
        return df_temp
    
    async def _aplicar_normalizacion(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar normalización a columnas numéricas"""
        config_norm = self.configuracion_final['normalizacion']
        columnas = config_norm['columnas_numericas']
        excluir = config_norm['excluir_columnas']
        
        if columnas is None:
            columnas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Excluir columnas especificadas
        columnas = [col for col in columnas if col not in excluir and col in df.columns]
        
        if not columnas:
            self.logger.warning("No hay columnas numéricas para normalizar")
            return df
        
        df_norm = df.copy()
        metodo = config_norm['metodo']
        
        # Inicializar scaler
        if metodo == "standard":
            self.scaler = StandardScaler()
        elif metodo == "minmax":
            self.scaler = MinMaxScaler()
        elif metodo == "robust":
            from sklearn.preprocessing import RobustScaler
            self.scaler = RobustScaler()
        
        # Aplicar normalización
        df_norm[columnas] = self.scaler.fit_transform(df_norm[columnas])
        
        self.logger.info(f"Normalización {metodo} aplicada a {len(columnas)} columnas")
        return df_norm
    
    async def _aplicar_seleccion_caracteristicas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar selección de características"""
        config_sel = self.configuracion_final['seleccion_caracteristicas']
        columna_objetivo = config_sel['columna_objetivo']
        k = config_sel['k_caracteristicas']
        metodo = config_sel['metodo']
        
        if columna_objetivo not in df.columns:
            self.logger.warning(f"Columna objetivo no encontrada: {columna_objetivo}")
            return df
        
        # Obtener características numéricas
        columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
        if columna_objetivo in columnas_numericas:
            columnas_numericas.remove(columna_objetivo)
        
        if len(columnas_numericas) == 0:
            self.logger.warning("No hay características numéricas para seleccionar")
            return df
        
        X = df[columnas_numericas]
        y = df[columna_objetivo]
        
        # Seleccionar características
        if metodo == "f_regression":
            self.feature_selector = SelectKBest(score_func=f_regression, k=k)
        elif metodo == "f_classif":
            self.feature_selector = SelectKBest(score_func=f_classif, k=k)
        elif metodo == "mutual_info":
            from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
            if df[columna_objetivo].dtype in ['int64', 'float64']:
                score_func = mutual_info_regression
            else:
                score_func = mutual_info_classif
            self.feature_selector = SelectKBest(score_func=score_func, k=k)
        
        X_selected = self.feature_selector.fit_transform(X, y)
        
        # Crear DataFrame con características seleccionadas
        columnas_seleccionadas = [columnas_numericas[i] for i in self.feature_selector.get_support(indices=True)]
        df_sel = df[columnas_seleccionadas + [columna_objetivo]].copy()
        
        self.logger.info(f"Seleccionadas {len(columnas_seleccionadas)} características de {len(columnas_numericas)}")
        return df_sel
    
    async def _aplicar_reduccion_dimensionalidad(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar reducción de dimensionalidad"""
        config_red = self.configuracion_final['reduccion_dimensionalidad']
        columnas = config_red['columnas_numericas']
        n_componentes = config_red['n_componentes']
        metodo = config_red['metodo']
        
        if columnas is None:
            columnas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(columnas) == 0:
            self.logger.warning("No hay columnas numéricas para reducir dimensionalidad")
            return df
        
        X = df[columnas]
        
        # Aplicar reducción de dimensionalidad
        if metodo == "pca":
            self.pca = PCA(n_components=n_componentes)
            X_reduced = self.pca.fit_transform(X)
            
            # Crear nombres de componentes
            n_comp = X_reduced.shape[1]
            nombres_componentes = [f"PC_{i+1}" for i in range(n_comp)]
            
            # Crear DataFrame con componentes principales
            df_red = df.drop(columns=columnas).copy()
            for i, nombre in enumerate(nombres_componentes):
                df_red[nombre] = X_reduced[:, i]
        
        self.logger.info(f"Reducción de dimensionalidad aplicada: {len(columnas)} -> {n_comp} componentes")
        return df_red
    
    async def _aplicar_clustering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar clustering"""
        config_cluster = self.configuracion_final['clustering']
        columnas = config_cluster['columnas_numericas']
        n_clusters = config_cluster['n_clusters']
        metodo = config_cluster['metodo']
        
        if columnas is None:
            columnas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(columnas) == 0:
            self.logger.warning("No hay columnas numéricas para clustering")
            return df
        
        X = df[columnas]
        
        # Aplicar clustering
        if metodo == "kmeans":
            self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = self.kmeans.fit_predict(X)
        
        # Agregar clusters al DataFrame
        df_cluster = df.copy()
        df_cluster['cluster'] = clusters
        
        self.logger.info(f"Clustering aplicado: {n_clusters} clusters")
        return df_cluster
