"""
Generador de Gráficos - Análisis de Datos
Generador para visualizaciones estadísticas e interactivas
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple
import structlog
from pathlib import Path
import json

from ..utilidades.decoradores.decorador_logging import logging_metodo
from ..utilidades.decoradores.decorador_validacion import validar_parametros


class GeneradorGraficos:
    """
    Generador de gráficos para análisis de datos
    Soporta matplotlib, seaborn y plotly
    """
    
    def __init__(self, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar generador de gráficos
        
        Args:
            configuracion: Configuración específica del generador
        """
        self.configuracion = configuracion or {}
        self.logger = structlog.get_logger()
        
        # Configuración por defecto
        self.configuracion_default = {
            "estilo": "whitegrid",
            "paleta_colores": "viridis",
            "tamaño_figura": (12, 8),
            "dpi": 300,
            "formato_archivo": "png",
            "directorio_salida": "./graficos",
            "incluir_titulo": True,
            "incluir_etiquetas": True,
            "incluir_leyenda": True,
            "tema_plotly": "plotly_white"
        }
        
        # Combinar configuración
        self.configuracion_final = {**self.configuracion_default, **self.configuracion}
        
        # Configurar matplotlib y seaborn
        plt.style.use('default')
        sns.set_style(self.configuracion_final['estilo'])
        sns.set_palette(self.configuracion_final['paleta_colores'])
        
        # Crear directorio de salida
        Path(self.configuracion_final['directorio_salida']).mkdir(parents=True, exist_ok=True)
    
    @logging_metodo(nombre_logger="generador_graficos", incluir_tiempo=True)
    @validar_parametros(validar_tipos=True)
    async def generar_grafico_barras(
        self, 
        df: pd.DataFrame, 
        columna_x: str, 
        columna_y: str,
        titulo: str = "Gráfico de Barras",
        guardar: bool = True,
        nombre_archivo: Optional[str] = None
    ) -> str:
        """
        Generar gráfico de barras
        
        Args:
            df: DataFrame con los datos
            columna_x: Columna para eje X
            columna_y: Columna para eje Y
            titulo: Título del gráfico
            guardar: Si guardar el gráfico
            nombre_archivo: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo guardado
        """
        try:
            # Crear figura
            fig, ax = plt.subplots(figsize=self.configuracion_final['tamaño_figura'])
            
            # Generar gráfico
            sns.barplot(data=df, x=columna_x, y=columna_y, ax=ax)
            
            # Configurar título y etiquetas
            if self.configuracion_final['incluir_titulo']:
                ax.set_title(titulo, fontsize=16, fontweight='bold')
            
            if self.configuracion_final['incluir_etiquetas']:
                ax.set_xlabel(columna_x, fontsize=12)
                ax.set_ylabel(columna_y, fontsize=12)
            
            # Rotar etiquetas del eje X si es necesario
            if len(df[columna_x].unique()) > 10:
                plt.xticks(rotation=45, ha='right')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Guardar si se solicita
            if guardar:
                if nombre_archivo is None:
                    nombre_archivo = f"grafico_barras_{columna_x}_{columna_y}"
                
                ruta_archivo = self._guardar_grafico(fig, nombre_archivo)
                self.logger.info(f"Gráfico de barras guardado: {ruta_archivo}")
                return ruta_archivo
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error generando gráfico de barras: {str(e)}")
            raise
    
    @logging_metodo(nombre_logger="generador_graficos", incluir_tiempo=True)
    @validar_parametros(validar_tipos=True)
    async def generar_grafico_lineas(
        self, 
        df: pd.DataFrame, 
        columna_x: str, 
        columna_y: str,
        titulo: str = "Gráfico de Líneas",
        guardar: bool = True,
        nombre_archivo: Optional[str] = None
    ) -> str:
        """
        Generar gráfico de líneas
        
        Args:
            df: DataFrame con los datos
            columna_x: Columna para eje X
            columna_y: Columna para eje Y
            titulo: Título del gráfico
            guardar: Si guardar el gráfico
            nombre_archivo: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo guardado
        """
        try:
            # Crear figura
            fig, ax = plt.subplots(figsize=self.configuracion_final['tamaño_figura'])
            
            # Generar gráfico
            sns.lineplot(data=df, x=columna_x, y=columna_y, ax=ax, marker='o')
            
            # Configurar título y etiquetas
            if self.configuracion_final['incluir_titulo']:
                ax.set_title(titulo, fontsize=16, fontweight='bold')
            
            if self.configuracion_final['incluir_etiquetas']:
                ax.set_xlabel(columna_x, fontsize=12)
                ax.set_ylabel(columna_y, fontsize=12)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Guardar si se solicita
            if guardar:
                if nombre_archivo is None:
                    nombre_archivo = f"grafico_lineas_{columna_x}_{columna_y}"
                
                ruta_archivo = self._guardar_grafico(fig, nombre_archivo)
                self.logger.info(f"Gráfico de líneas guardado: {ruta_archivo}")
                return ruta_archivo
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error generando gráfico de líneas: {str(e)}")
            raise
    
    @logging_metodo(nombre_logger="generador_graficos", incluir_tiempo=True)
    @validar_parametros(validar_tipos=True)
    async def generar_heatmap_correlacion(
        self, 
        df: pd.DataFrame, 
        columnas: Optional[List[str]] = None,
        titulo: str = "Mapa de Calor de Correlaciones",
        guardar: bool = True,
        nombre_archivo: Optional[str] = None
    ) -> str:
        """
        Generar heatmap de correlaciones
        
        Args:
            df: DataFrame con los datos
            columnas: Columnas a incluir (None = todas las numéricas)
            titulo: Título del gráfico
            guardar: Si guardar el gráfico
            nombre_archivo: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo guardado
        """
        try:
            # Seleccionar columnas numéricas
            if columnas is None:
                columnas = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(columnas) < 2:
                self.logger.warning("Se necesitan al menos 2 columnas numéricas para heatmap")
                return ""
            
            # Calcular matriz de correlación
            matriz_correlacion = df[columnas].corr()
            
            # Crear figura
            fig, ax = plt.subplots(figsize=self.configuracion_final['tamaño_figura'])
            
            # Generar heatmap
            sns.heatmap(
                matriz_correlacion,
                annot=True,
                cmap='coolwarm',
                center=0,
                square=True,
                ax=ax,
                fmt='.2f'
            )
            
            # Configurar título
            if self.configuracion_final['incluir_titulo']:
                ax.set_title(titulo, fontsize=16, fontweight='bold')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Guardar si se solicita
            if guardar:
                if nombre_archivo is None:
                    nombre_archivo = "heatmap_correlacion"
                
                ruta_archivo = self._guardar_grafico(fig, nombre_archivo)
                self.logger.info(f"Heatmap de correlación guardado: {ruta_archivo}")
                return ruta_archivo
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error generando heatmap: {str(e)}")
            raise
    
    @logging_metodo(nombre_logger="generador_graficos", incluir_tiempo=True)
    @validar_parametros(validar_tipos=True)
    async def generar_grafico_interactivo(
        self, 
        df: pd.DataFrame, 
        tipo_grafico: str,
        columna_x: str, 
        columna_y: str,
        titulo: str = "Gráfico Interactivo",
        guardar: bool = True,
        nombre_archivo: Optional[str] = None
    ) -> str:
        """
        Generar gráfico interactivo con Plotly
        
        Args:
            df: DataFrame con los datos
            tipo_grafico: Tipo de gráfico ('scatter', 'bar', 'line', 'box', 'histogram')
            columna_x: Columna para eje X
            columna_y: Columna para eje Y
            titulo: Título del gráfico
            guardar: Si guardar el gráfico
            nombre_archivo: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo guardado
        """
        try:
            # Crear gráfico según el tipo
            if tipo_grafico == 'scatter':
                fig = px.scatter(df, x=columna_x, y=columna_y, title=titulo)
            elif tipo_grafico == 'bar':
                fig = px.bar(df, x=columna_x, y=columna_y, title=titulo)
            elif tipo_grafico == 'line':
                fig = px.line(df, x=columna_x, y=columna_y, title=titulo)
            elif tipo_grafico == 'box':
                fig = px.box(df, x=columna_x, y=columna_y, title=titulo)
            elif tipo_grafico == 'histogram':
                fig = px.histogram(df, x=columna_x, title=titulo)
            else:
                raise ValueError(f"Tipo de gráfico no soportado: {tipo_grafico}")
            
            # Configurar tema
            fig.update_layout(template=self.configuracion_final['tema_plotly'])
            
            # Guardar si se solicita
            if guardar:
                if nombre_archivo is None:
                    nombre_archivo = f"grafico_interactivo_{tipo_grafico}_{columna_x}_{columna_y}"
                
                ruta_archivo = self._guardar_grafico_plotly(fig, nombre_archivo)
                self.logger.info(f"Gráfico interactivo guardado: {ruta_archivo}")
                return ruta_archivo
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error generando gráfico interactivo: {str(e)}")
            raise
    
    @logging_metodo(nombre_logger="generador_graficos", incluir_tiempo=True)
    @validar_parametros(validar_tipos=True)
    async def generar_dashboard(
        self, 
        df: pd.DataFrame, 
        configuracion_dashboard: Dict[str, Any],
        titulo: str = "Dashboard de Análisis",
        guardar: bool = True,
        nombre_archivo: Optional[str] = None
    ) -> str:
        """
        Generar dashboard con múltiples gráficos
        
        Args:
            df: DataFrame con los datos
            configuracion_dashboard: Configuración de los gráficos del dashboard
            titulo: Título del dashboard
            guardar: Si guardar el dashboard
            nombre_archivo: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo guardado
        """
        try:
            # Crear subplots
            filas = configuracion_dashboard.get('filas', 2)
            columnas = configuracion_dashboard.get('columnas', 2)
            
            fig = make_subplots(
                rows=filas,
                cols=columnas,
                subplot_titles=configuracion_dashboard.get('titulos', []),
                specs=configuracion_dashboard.get('specs', None)
            )
            
            # Agregar gráficos según configuración
            graficos = configuracion_dashboard.get('graficos', [])
            
            for i, grafico_config in enumerate(graficos):
                fila = (i // columnas) + 1
                col = (i % columnas) + 1
                
                tipo = grafico_config.get('tipo')
                columna_x = grafico_config.get('columna_x')
                columna_y = grafico_config.get('columna_y')
                
                if tipo == 'scatter':
                    fig.add_trace(
                        go.Scatter(
                            x=df[columna_x],
                            y=df[columna_y],
                            mode='markers',
                            name=grafico_config.get('nombre', f'Gráfico {i+1}')
                        ),
                        row=fila, col=col
                    )
                elif tipo == 'bar':
                    fig.add_trace(
                        go.Bar(
                            x=df[columna_x],
                            y=df[columna_y],
                            name=grafico_config.get('nombre', f'Gráfico {i+1}')
                        ),
                        row=fila, col=col
                    )
                elif tipo == 'line':
                    fig.add_trace(
                        go.Scatter(
                            x=df[columna_x],
                            y=df[columna_y],
                            mode='lines+markers',
                            name=grafico_config.get('nombre', f'Gráfico {i+1}')
                        ),
                        row=fila, col=col
                    )
            
            # Configurar layout
            fig.update_layout(
                title_text=titulo,
                showlegend=True,
                template=self.configuracion_final['tema_plotly']
            )
            
            # Guardar si se solicita
            if guardar:
                if nombre_archivo is None:
                    nombre_archivo = "dashboard_analisis"
                
                ruta_archivo = self._guardar_grafico_plotly(fig, nombre_archivo)
                self.logger.info(f"Dashboard guardado: {ruta_archivo}")
                return ruta_archivo
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error generando dashboard: {str(e)}")
            raise
    
    def _guardar_grafico(self, fig: plt.Figure, nombre_archivo: str) -> str:
        """Guardar gráfico de matplotlib"""
        ruta_completa = Path(self.configuracion_final['directorio_salida']) / f"{nombre_archivo}.{self.configuracion_final['formato_archivo']}"
        
        fig.savefig(
            ruta_completa,
            dpi=self.configuracion_final['dpi'],
            bbox_inches='tight',
            facecolor='white'
        )
        
        plt.close(fig)
        return str(ruta_completa)
    
    def _guardar_grafico_plotly(self, fig: go.Figure, nombre_archivo: str) -> str:
        """Guardar gráfico de Plotly"""
        ruta_completa = Path(self.configuracion_final['directorio_salida']) / f"{nombre_archivo}.html"
        
        fig.write_html(str(ruta_completa))
        return str(ruta_completa)
    
    @logging_metodo(nombre_logger="generador_graficos", incluir_tiempo=True)
    async def generar_graficos_automaticos(
        self, 
        df: pd.DataFrame, 
        directorio_salida: Optional[str] = None
    ) -> List[str]:
        """
        Generar automáticamente un conjunto de gráficos para el DataFrame
        
        Args:
            df: DataFrame a analizar
            directorio_salida: Directorio de salida (opcional)
            
        Returns:
            Lista de rutas de archivos generados
        """
        if directorio_salida:
            self.configuracion_final['directorio_salida'] = directorio_salida
            Path(directorio_salida).mkdir(parents=True, exist_ok=True)
        
        archivos_generados = []
        
        try:
            # Obtener columnas numéricas
            columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
            columnas_categoricas = df.select_dtypes(include=['object']).columns.tolist()
            
            # 1. Histogramas para columnas numéricas
            for col in columnas_numericas[:5]:  # Limitar a 5 para no sobrecargar
                ruta = await self.generar_grafico_interactivo(
                    df, 'histogram', col, None, f"Distribución de {col}"
                )
                if ruta:
                    archivos_generados.append(ruta)
            
            # 2. Gráficos de barras para columnas categóricas
            for col in columnas_categoricas[:5]:
                if df[col].nunique() <= 20:  # Solo si no hay demasiadas categorías
                    conteos = df[col].value_counts().head(10)
                    df_conteos = pd.DataFrame({
                        'categoria': conteos.index,
                        'conteo': conteos.values
                    })
                    ruta = await self.generar_grafico_barras(
                        df_conteos, 'categoria', 'conteo', f"Distribución de {col}"
                    )
                    if ruta:
                        archivos_generados.append(ruta)
            
            # 3. Heatmap de correlaciones
            if len(columnas_numericas) >= 2:
                ruta = await self.generar_heatmap_correlacion(df, columnas_numericas)
                if ruta:
                    archivos_generados.append(ruta)
            
            # 4. Scatter plots para pares de variables numéricas
            if len(columnas_numericas) >= 2:
                for i in range(min(3, len(columnas_numericas))):
                    for j in range(i+1, min(i+3, len(columnas_numericas))):
                        col1, col2 = columnas_numericas[i], columnas_numericas[j]
                        ruta = await self.generar_grafico_interactivo(
                            df, 'scatter', col1, col2, f"{col1} vs {col2}"
                        )
                        if ruta:
                            archivos_generados.append(ruta)
            
            self.logger.info(f"Generados {len(archivos_generados)} gráficos automáticamente")
            return archivos_generados
            
        except Exception as e:
            self.logger.error(f"Error generando gráficos automáticos: {str(e)}")
            return archivos_generados
