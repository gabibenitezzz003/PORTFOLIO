"""
Algoritmo de Recomendación - Capa de Dominio
Clase base abstracta para algoritmos de recomendación
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import structlog
from enum import Enum

from ..entidades.recomendacion import Recomendacion, TipoAlgoritmo, TipoRecomendacion
from ..entidades.usuario import Usuario
from ..entidades.item import Item


class AlgoritmoRecomendacion(ABC):
    """
    Clase base abstracta para algoritmos de recomendación
    Implementa el patrón Strategy para diferentes algoritmos
    """
    
    def __init__(self, nombre: str, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar algoritmo de recomendación
        
        Args:
            nombre: Nombre del algoritmo
            configuracion: Configuración específica del algoritmo
        """
        self.nombre = nombre
        self.configuracion = configuracion or {}
        self.logger = structlog.get_logger()
    
    @abstractmethod
    async def entrenar(self, datos_entrenamiento: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entrenar el algoritmo con datos de entrenamiento
        
        Args:
            datos_entrenamiento: Datos para entrenar el modelo
            
        Returns:
            Métricas de entrenamiento
        """
        pass
    
    @abstractmethod
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
            contexto: Contexto adicional para la recomendación
            
        Returns:
            Lista de recomendaciones
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def validar_configuracion(self) -> bool:
        """
        Validar configuración del algoritmo
        
        Returns:
            True si la configuración es válida
        """
        pass
    
    def obtener_metadatos(self) -> Dict[str, Any]:
        """
        Obtener metadatos del algoritmo
        
        Returns:
            Diccionario con metadatos
        """
        return {
            "nombre": self.nombre,
            "tipo": type(self).__name__,
            "configuracion": self.configuracion
        }
    
    def _crear_recomendacion(
        self,
        item_id: str,
        usuario_id: str,
        score: float,
        ranking: int,
        algoritmo: TipoAlgoritmo,
        tipo: TipoRecomendacion,
        item_info: Optional[Dict[str, Any]] = None,
        explicacion: Optional[str] = None,
        razones: Optional[List[str]] = None,
        confianza: float = 0.5
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
            item_info: Información adicional del item
            explicacion: Explicación de la recomendación
            razones: Lista de razones
            confianza: Nivel de confianza
            
        Returns:
            Recomendación creada
        """
        # Información del item
        titulo = item_info.get('titulo') if item_info else None
        categoria = item_info.get('categoria') if item_info else None
        descripcion = item_info.get('descripcion') if item_info else None
        precio = item_info.get('precio') if item_info else None
        imagen_url = item_info.get('imagen_url') if item_info else None
        
        return Recomendacion(
            item_id=item_id,
            usuario_id=usuario_id,
            score=score,
            ranking=ranking,
            algoritmo_usado=algoritmo,
            tipo_recomendacion=tipo,
            titulo=titulo,
            categoria=categoria,
            descripcion=descripcion,
            precio=precio,
            imagen_url=imagen_url,
            explicacion=explicacion,
            razones=razones or [],
            confianza=confianza
        )
    
    def _calcular_confianza(
        self, 
        score: float, 
        datos_usuario: Optional[Dict[str, Any]] = None,
        datos_item: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calcular confianza de la recomendación
        
        Args:
            score: Puntuación de la recomendación
            datos_usuario: Datos del usuario
            datos_item: Datos del item
            
        Returns:
            Valor de confianza (0.0 a 1.0)
        """
        factores = []
        
        # Factor de score
        factor_score = min(1.0, score)
        factores.append(factor_score)
        
        # Factor de datos del usuario
        if datos_usuario:
            if datos_usuario.get('total_interacciones', 0) > 10:
                factores.append(0.8)
            elif datos_usuario.get('total_interacciones', 0) > 5:
                factores.append(0.6)
            else:
                factores.append(0.4)
        
        # Factor de datos del item
        if datos_item:
            if datos_item.get('total_ratings', 0) > 50:
                factores.append(0.9)
            elif datos_item.get('total_ratings', 0) > 10:
                factores.append(0.7)
            else:
                factores.append(0.5)
        
        return sum(factores) / len(factores) if factores else 0.5
    
    def _generar_explicacion(
        self,
        tipo: TipoRecomendacion,
        datos_usuario: Optional[Dict[str, Any]] = None,
        datos_item: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generar explicación para la recomendación
        
        Args:
            tipo: Tipo de recomendación
            datos_usuario: Datos del usuario
            datos_item: Datos del item
            
        Returns:
            Explicación de la recomendación
        """
        explicaciones = {
            TipoRecomendacion.USUARIO: "Recomendado para ti",
            TipoRecomendacion.SIMILAR: "Similar a items que te gustan",
            TipoRecomendacion.POPULAR: "Popular entre otros usuarios",
            TipoRecomendacion.TRENDING: "Tendencia actual"
        }
        
        explicacion_base = explicaciones.get(tipo, "Recomendado")
        
        # Agregar contexto específico
        if datos_usuario and datos_usuario.get('categorias_preferidas'):
            categorias = datos_usuario['categorias_preferidas'][:2]
            explicacion_base += f" basado en tu interés en {', '.join(categorias)}"
        
        return explicacion_base
    
    def _generar_razones(
        self,
        tipo: TipoRecomendacion,
        datos_usuario: Optional[Dict[str, Any]] = None,
        datos_item: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Generar razones para la recomendación
        
        Args:
            tipo: Tipo de recomendación
            datos_usuario: Datos del usuario
            datos_item: Datos del item
            
        Returns:
            Lista de razones
        """
        razones = []
        
        if tipo == TipoRecomendacion.USUARIO:
            if datos_usuario and datos_usuario.get('categorias_preferidas'):
                razones.append("Coincide con tus categorías preferidas")
            
            if datos_usuario and datos_usuario.get('total_compras', 0) > 0:
                razones.append("Basado en tu historial de compras")
        
        elif tipo == TipoRecomendacion.SIMILAR:
            razones.append("Similar a items que has visto")
            razones.append("Misma categoría que tus favoritos")
        
        elif tipo == TipoRecomendacion.POPULAR:
            if datos_item and datos_item.get('total_ventas', 0) > 100:
                razones.append("Muy vendido")
            
            if datos_item and datos_item.get('rating_promedio', 0) > 4.0:
                razones.append("Bien calificado")
        
        elif tipo == TipoRecomendacion.TRENDING:
            razones.append("Tendencia actual")
            razones.append("Aumento en popularidad")
        
        return razones
    
    def _filtrar_recomendaciones(
        self,
        recomendaciones: List[Recomendacion],
        filtros: Optional[Dict[str, Any]] = None
    ) -> List[Recomendacion]:
        """
        Filtrar recomendaciones según criterios
        
        Args:
            recomendaciones: Lista de recomendaciones
            filtros: Criterios de filtrado
            
        Returns:
            Lista de recomendaciones filtradas
        """
        if not filtros:
            return recomendaciones
        
        recomendaciones_filtradas = []
        
        for rec in recomendaciones:
            incluir = True
            
            # Filtro por categoría
            if 'categoria' in filtros and rec.categoria:
                if rec.categoria not in filtros['categoria']:
                    incluir = False
            
            # Filtro por rango de precio
            if 'precio_min' in filtros and rec.precio:
                if rec.precio < filtros['precio_min']:
                    incluir = False
            
            if 'precio_max' in filtros and rec.precio:
                if rec.precio > filtros['precio_max']:
                    incluir = False
            
            # Filtro por confianza mínima
            if 'confianza_min' in filtros:
                if rec.confianza < filtros['confianza_min']:
                    incluir = False
            
            if incluir:
                recomendaciones_filtradas.append(rec)
        
        return recomendaciones_filtradas
    
    def _ordenar_recomendaciones(
        self,
        recomendaciones: List[Recomendacion],
        criterio: str = 'score'
    ) -> List[Recomendacion]:
        """
        Ordenar recomendaciones según criterio
        
        Args:
            recomendaciones: Lista de recomendaciones
            criterio: Criterio de ordenamiento
            
        Returns:
            Lista de recomendaciones ordenadas
        """
        if criterio == 'score':
            return sorted(recomendaciones, key=lambda x: x.score, reverse=True)
        elif criterio == 'confianza':
            return sorted(recomendaciones, key=lambda x: x.confianza, reverse=True)
        elif criterio == 'ranking':
            return sorted(recomendaciones, key=lambda x: x.ranking)
        else:
            return recomendaciones
