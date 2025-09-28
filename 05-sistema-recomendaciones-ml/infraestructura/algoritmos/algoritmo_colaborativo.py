"""
Algoritmo de Filtrado Colaborativo - Infraestructura
Implementación concreta usando scikit-learn para filtrado colaborativo
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import structlog
from datetime import datetime
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import joblib

from dominio.algoritmos.algoritmo_recomendacion import AlgoritmoRecomendacion
from dominio.entidades.recomendacion import Recomendacion, TipoAlgoritmo, TipoRecomendacion


class AlgoritmoColaborativo(AlgoritmoRecomendacion):
    """
    Implementación de filtrado colaborativo usando Matrix Factorization
    Utiliza SVD (Singular Value Decomposition) para encontrar patrones latentes
    """
    
    def __init__(self, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar algoritmo colaborativo
        
        Args:
            configuracion: Configuración específica del algoritmo
        """
        super().__init__("colaborativo", configuracion)
        
        # Configuración por defecto
        self.configuracion_default = {
            "n_components": 50,
            "random_state": 42,
            "n_iter": 5,
            "min_ratings": 5,
            "min_users": 2,
            "normalize": True,
            "use_implicit": False
        }
        
        # Combinar configuración
        self.configuracion_final = {**self.configuracion_default, **self.configuracion}
        
        # Modelo entrenado
        self.modelo: Optional[TruncatedSVD] = None
        self.matriz_ratings: Optional[pd.DataFrame] = None
        self.scaler: Optional[StandardScaler] = None
        self.item_ids: List[str] = []
        self.usuario_ids: List[str] = []
        
        self.logger = structlog.get_logger()
    
    def validar_configuracion(self) -> bool:
        """
        Validar configuración del algoritmo
        
        Returns:
            True si la configuración es válida
        """
        # Verificar parámetros numéricos
        if not isinstance(self.configuracion_final["n_components"], int) or self.configuracion_final["n_components"] <= 0:
            return False
        
        if not isinstance(self.configuracion_final["min_ratings"], int) or self.configuracion_final["min_ratings"] < 1:
            return False
        
        if not isinstance(self.configuracion_final["min_users"], int) or self.configuracion_final["min_users"] < 1:
            return False
        
        return True
    
    async def entrenar(self, datos_entrenamiento: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entrenar el algoritmo colaborativo
        
        Args:
            datos_entrenamiento: Datos para entrenar el modelo
            
        Returns:
            Métricas de entrenamiento
        """
        try:
            self.logger.info("Iniciando entrenamiento del algoritmo colaborativo")
            
            # Extraer datos
            ratings_df = datos_entrenamiento.get('ratings')
            if ratings_df is None:
                raise ValueError("Datos de ratings no encontrados")
            
            # Preprocesar datos
            ratings_procesados = self._preprocesar_datos(ratings_df)
            
            # Crear matriz de ratings
            self.matriz_ratings = self._crear_matriz_ratings(ratings_procesados)
            
            # Filtrar datos por criterios mínimos
            self.matriz_ratings = self._filtrar_matriz(self.matriz_ratings)
            
            if self.matriz_ratings.empty:
                raise ValueError("No hay suficientes datos para entrenar el modelo")
            
            # Normalizar datos si está habilitado
            if self.configuracion_final["normalize"]:
                self.scaler = StandardScaler()
                self.matriz_ratings.iloc[:, :] = self.scaler.fit_transform(self.matriz_ratings)
            
            # Crear y entrenar modelo SVD
            self.modelo = TruncatedSVD(
                n_components=self.configuracion_final["n_components"],
                random_state=self.configuracion_final["random_state"],
                n_iter=self.configuracion_final["n_iter"]
            )
            
            # Entrenar modelo
            self.modelo.fit(self.matriz_ratings)
            
            # Calcular métricas de entrenamiento
            metricas = self._calcular_metricas_entrenamiento()
            
            self.logger.info(
                "Entrenamiento del algoritmo colaborativo completado",
                metricas=metricas
            )
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error entrenando algoritmo colaborativo: {str(e)}")
            raise
    
    def _preprocesar_datos(self, ratings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocesar datos de ratings
        
        Args:
            ratings_df: DataFrame con ratings
            
        Returns:
            DataFrame procesado
        """
        # Crear copia para no modificar el original
        df = ratings_df.copy()
        
        # Renombrar columnas si es necesario
        columnas_esperadas = ['usuario_id', 'item_id', 'rating']
        if not all(col in df.columns for col in columnas_esperadas):
            # Intentar mapear columnas existentes
            mapeo_columnas = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'user' in col_lower or 'usuario' in col_lower:
                    mapeo_columnas[col] = 'usuario_id'
                elif 'item' in col_lower or 'producto' in col_lower:
                    mapeo_columnas[col] = 'item_id'
                elif 'rating' in col_lower or 'puntuacion' in col_lower or 'score' in col_lower:
                    mapeo_columnas[col] = 'rating'
            
            df = df.rename(columns=mapeo_columnas)
        
        # Filtrar columnas necesarias
        df = df[['usuario_id', 'item_id', 'rating']].copy()
        
        # Limpiar datos
        df = df.dropna()
        df = df[df['rating'] > 0]  # Solo ratings positivos
        
        # Convertir IDs a string
        df['usuario_id'] = df['usuario_id'].astype(str)
        df['item_id'] = df['item_id'].astype(str)
        
        return df
    
    def _crear_matriz_ratings(self, ratings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Crear matriz de ratings usuario-item
        
        Args:
            ratings_df: DataFrame con ratings
            
        Returns:
            Matriz de ratings
        """
        # Crear matriz pivote
        matriz = ratings_df.pivot_table(
            index='usuario_id',
            columns='item_id',
            values='rating',
            fill_value=0
        )
        
        # Guardar IDs para referencia
        self.usuario_ids = matriz.index.tolist()
        self.item_ids = matriz.columns.tolist()
        
        return matriz
    
    def _filtrar_matriz(self, matriz: pd.DataFrame) -> pd.DataFrame:
        """
        Filtrar matriz por criterios mínimos
        
        Args:
            matriz: Matriz de ratings
            
        Returns:
            Matriz filtrada
        """
        # Filtrar items con mínimo de ratings
        min_ratings = self.configuracion_final["min_ratings"]
        items_con_suficientes_ratings = matriz.columns[matriz.astype(bool).sum() >= min_ratings]
        
        # Filtrar usuarios con mínimo de ratings
        min_users = self.configuracion_final["min_users"]
        usuarios_con_suficientes_ratings = matriz.index[matriz.astype(bool).sum(axis=1) >= min_users]
        
        # Aplicar filtros
        matriz_filtrada = matriz.loc[usuarios_con_suficientes_ratings, items_con_suficientes_ratings]
        
        # Actualizar IDs
        self.usuario_ids = matriz_filtrada.index.tolist()
        self.item_ids = matriz_filtrada.columns.tolist()
        
        return matriz_filtrada
    
    def _calcular_metricas_entrenamiento(self) -> Dict[str, Any]:
        """
        Calcular métricas de entrenamiento
        
        Returns:
            Diccionario con métricas
        """
        if self.modelo is None:
            return {}
        
        # Calcular varianza explicada
        varianza_explicada = self.modelo.explained_variance_ratio_.sum()
        
        # Calcular sparsity de la matriz
        total_elementos = self.matriz_ratings.size
        elementos_no_cero = (self.matriz_ratings != 0).sum().sum()
        sparsity = 1 - (elementos_no_cero / total_elementos)
        
        return {
            "varianza_explicada": round(varianza_explicada, 4),
            "n_components": self.modelo.n_components,
            "n_usuarios": len(self.usuario_ids),
            "n_items": len(self.item_ids),
            "sparsity": round(sparsity, 4),
            "total_ratings": elementos_no_cero
        }
    
    async def recomendar(
        self, 
        usuario_id: str, 
        limit: int = 10,
        contexto: Optional[Dict[str, Any]] = None
    ) -> List[Recomendacion]:
        """
        Generar recomendaciones para un usuario
        
        Args:
            usuario_id: ID del usuario
            limit: Número máximo de recomendaciones
            contexto: Contexto adicional
            
        Returns:
            Lista de recomendaciones
        """
        try:
            if self.modelo is None:
                raise ValueError("Modelo no entrenado")
            
            # Verificar si el usuario existe en el modelo
            if usuario_id not in self.usuario_ids:
                # Usuario nuevo - usar recomendaciones populares
                return await self._recomendar_popular(limit)
            
            # Obtener índice del usuario
            usuario_idx = self.usuario_ids.index(usuario_id)
            
            # Obtener ratings del usuario
            ratings_usuario = self.matriz_ratings.iloc[usuario_idx].values
            
            # Obtener items ya calificados por el usuario
            items_calificados = set(self.matriz_ratings.columns[ratings_usuario > 0])
            
            # Calcular scores para todos los items
            scores = self._calcular_scores_usuario(usuario_idx)
            
            # Crear recomendaciones
            recomendaciones = []
            ranking = 1
            
            for item_idx, score in enumerate(scores):
                if ranking > limit:
                    break
                
                item_id = self.item_ids[item_idx]
                
                # Saltar items ya calificados
                if item_id in items_calificados:
                    continue
                
                # Crear recomendación
                recomendacion = self._crear_recomendacion(
                    item_id=item_id,
                    usuario_id=usuario_id,
                    score=float(score),
                    ranking=ranking,
                    algoritmo=TipoAlgoritmo.COLABORATIVO,
                    tipo=TipoRecomendacion.USUARIO
                )
                
                recomendaciones.append(recomendacion)
                ranking += 1
            
            return recomendaciones
            
        except Exception as e:
            self.logger.error(f"Error generando recomendaciones colaborativas: {str(e)}")
            raise
    
    async def recomendar_similares(
        self, 
        item_id: str, 
        limit: int = 10
    ) -> List[Recomendacion]:
        """
        Generar recomendaciones de items similares
        
        Args:
            item_id: ID del item de referencia
            limit: Número máximo de recomendaciones
            
        Returns:
            Lista de recomendaciones similares
        """
        try:
            if self.modelo is None:
                raise ValueError("Modelo no entrenado")
            
            # Verificar si el item existe en el modelo
            if item_id not in self.item_ids:
                return []
            
            # Obtener índice del item
            item_idx = self.item_ids.index(item_id)
            
            # Calcular similitudes
            similitudes = self._calcular_similitudes_item(item_idx)
            
            # Crear recomendaciones
            recomendaciones = []
            ranking = 1
            
            for sim_item_idx, similitud in enumerate(similitudes):
                if ranking > limit:
                    break
                
                # Saltar el item original
                if sim_item_idx == item_idx:
                    continue
                
                sim_item_id = self.item_ids[sim_item_idx]
                
                # Crear recomendación
                recomendacion = self._crear_recomendacion(
                    item_id=sim_item_id,
                    usuario_id=None,
                    score=float(similitud),
                    ranking=ranking,
                    algoritmo=TipoAlgoritmo.COLABORATIVO,
                    tipo=TipoRecomendacion.SIMILAR
                )
                
                recomendaciones.append(recomendacion)
                ranking += 1
            
            return recomendaciones
            
        except Exception as e:
            self.logger.error(f"Error generando recomendaciones similares: {str(e)}")
            raise
    
    def _calcular_scores_usuario(self, usuario_idx: int) -> np.ndarray:
        """
        Calcular scores de recomendación para un usuario
        
        Args:
            usuario_idx: Índice del usuario en la matriz
            
        Returns:
            Array con scores para todos los items
        """
        # Obtener ratings del usuario
        ratings_usuario = self.matriz_ratings.iloc[usuario_idx].values
        
        # Transformar usando el modelo SVD
        usuario_latent = self.modelo.transform(ratings_usuario.reshape(1, -1))
        
        # Obtener representación latente de todos los items
        items_latent = self.modelo.components_.T
        
        # Calcular scores usando producto punto
        scores = np.dot(usuario_latent, items_latent.T).flatten()
        
        return scores
    
    def _calcular_similitudes_item(self, item_idx: int) -> np.ndarray:
        """
        Calcular similitudes de un item con todos los demás
        
        Args:
            item_idx: Índice del item en la matriz
            
        Returns:
            Array con similitudes
        """
        # Obtener representación latente del item
        item_latent = self.modelo.components_[:, item_idx]
        
        # Obtener representación latente de todos los items
        items_latent = self.modelo.components_.T
        
        # Calcular similitudes usando cosine similarity
        similitudes = cosine_similarity([item_latent], items_latent).flatten()
        
        return similitudes
    
    async def _recomendar_popular(self, limit: int) -> List[Recomendacion]:
        """
        Generar recomendaciones populares para usuarios nuevos
        
        Args:
            limit: Número máximo de recomendaciones
            
        Returns:
            Lista de recomendaciones populares
        """
        # Calcular popularidad de items (suma de ratings)
        popularidad = self.matriz_ratings.sum().sort_values(ascending=False)
        
        recomendaciones = []
        ranking = 1
        
        for item_id, score in popularidad.items():
            if ranking > limit:
                break
            
            recomendacion = self._crear_recomendacion(
                item_id=item_id,
                usuario_id=None,
                score=float(score),
                ranking=ranking,
                algoritmo=TipoAlgoritmo.COLABORATIVO,
                tipo=TipoRecomendacion.POPULAR
            )
            
            recomendaciones.append(recomendacion)
            ranking += 1
        
        return recomendaciones
    
    def _crear_recomendacion(
        self,
        item_id: str,
        usuario_id: Optional[str],
        score: float,
        ranking: int,
        algoritmo: TipoAlgoritmo,
        tipo: TipoRecomendacion
    ) -> Recomendacion:
        """
        Crear una recomendación con la información proporcionada
        
        Args:
            item_id: ID del item
            usuario_id: ID del usuario
            score: Puntuación de la recomendación
            ranking: Posición en el ranking
            algoritmo: Tipo de algoritmo usado
            tipo: Tipo de recomendación
            
        Returns:
            Recomendación creada
        """
        # Calcular confianza basada en el score
        confianza = min(1.0, max(0.0, score / 5.0))  # Normalizar a 0-1
        
        # Generar explicación
        explicacion = self._generar_explicacion(tipo)
        
        # Generar razones
        razones = self._generar_razones(tipo)
        
        return Recomendacion(
            item_id=item_id,
            usuario_id=usuario_id,
            score=score,
            ranking=ranking,
            algoritmo_usado=algoritmo,
            tipo_recomendacion=tipo,
            explicacion=explicacion,
            razones=razones,
            confianza=confianza
        )
    
    def _generar_explicacion(self, tipo: TipoRecomendacion) -> str:
        """Generar explicación para la recomendación"""
        explicaciones = {
            TipoRecomendacion.USUARIO: "Recomendado basado en usuarios similares",
            TipoRecomendacion.SIMILAR: "Similar a items que te gustan",
            TipoRecomendacion.POPULAR: "Popular entre otros usuarios"
        }
        return explicaciones.get(tipo, "Recomendado por filtrado colaborativo")
    
    def _generar_razones(self, tipo: TipoRecomendacion) -> List[str]:
        """Generar razones para la recomendación"""
        razones = {
            TipoRecomendacion.USUARIO: [
                "Basado en usuarios con gustos similares",
                "Patrones de comportamiento compartidos"
            ],
            TipoRecomendacion.SIMILAR: [
                "Características similares",
                "Misma categoría de preferencia"
            ],
            TipoRecomendacion.POPULAR: [
                "Muy valorado por otros usuarios",
                "Alta demanda en el mercado"
            ]
        }
        return razones.get(tipo, ["Recomendación colaborativa"])
    
    def guardar_modelo(self, ruta: str) -> None:
        """
        Guardar modelo entrenado
        
        Args:
            ruta: Ruta donde guardar el modelo
        """
        if self.modelo is None:
            raise ValueError("No hay modelo entrenado para guardar")
        
        modelo_data = {
            'modelo': self.modelo,
            'matriz_ratings': self.matriz_ratings,
            'scaler': self.scaler,
            'item_ids': self.item_ids,
            'usuario_ids': self.usuario_ids,
            'configuracion': self.configuracion_final
        }
        
        joblib.dump(modelo_data, ruta)
        self.logger.info(f"Modelo guardado en: {ruta}")
    
    def cargar_modelo(self, ruta: str) -> None:
        """
        Cargar modelo entrenado
        
        Args:
            ruta: Ruta del modelo a cargar
        """
        modelo_data = joblib.load(ruta)
        
        self.modelo = modelo_data['modelo']
        self.matriz_ratings = modelo_data['matriz_ratings']
        self.scaler = modelo_data['scaler']
        self.item_ids = modelo_data['item_ids']
        self.usuario_ids = modelo_data['usuario_ids']
        self.configuracion_final = modelo_data['configuracion']
        
        self.logger.info(f"Modelo cargado desde: {ruta}")
