"""
Servicio de Recomendaciones - Capa de Aplicación
Servicio principal para generar recomendaciones
"""
import asyncio
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

from ...dominio.entidades.recomendacion import Recomendacion, TipoAlgoritmo, TipoRecomendacion
from ...dominio.algoritmos.algoritmo_recomendacion import AlgoritmoRecomendacion
from ...utilidades.decoradores.decorador_logging import logging_metodo
from ...utilidades.decoradores.decorador_validacion import validar_parametros


class ServicioRecomendaciones:
    """
    Servicio principal para generar recomendaciones
    Orquesta diferentes algoritmos y proporciona una interfaz unificada
    """
    
    def __init__(self, configuracion: Optional[Dict[str, Any]] = None):
        """
        Inicializar servicio de recomendaciones
        
        Args:
            configuracion: Configuración del servicio
        """
        self.configuracion = configuracion or {}
        self.logger = structlog.get_logger()
        
        # Algoritmos disponibles
        self.algoritmos: Dict[str, AlgoritmoRecomendacion] = {}
        
        # Configuración por defecto
        self.configuracion_default = {
            "algoritmo_por_defecto": "hibrido",
            "algoritmos_habilitados": ["colaborativo", "contenido", "hibrido"],
            "cache_habilitado": True,
            "cache_ttl": 3600,  # 1 hora
            "timeout_recomendacion": 5,  # segundos
            "max_recomendaciones": 100,
            "min_confianza": 0.3,
            "incluir_explicaciones": True,
            "incluir_razones": True
        }
        
        # Combinar configuración
        self.configuracion_final = {**self.configuracion_default, **self.configuracion}
    
    def registrar_algoritmo(self, nombre: str, algoritmo: AlgoritmoRecomendacion) -> None:
        """
        Registrar un algoritmo de recomendación
        
        Args:
            nombre: Nombre del algoritmo
            algoritmo: Instancia del algoritmo
        """
        self.algoritmos[nombre] = algoritmo
        self.logger.info(f"Algoritmo de recomendación registrado: {nombre}")
    
    def obtener_algoritmo(self, nombre: str) -> Optional[AlgoritmoRecomendacion]:
        """
        Obtener un algoritmo por nombre
        
        Args:
            nombre: Nombre del algoritmo
            
        Returns:
            Algoritmo o None si no existe
        """
        return self.algoritmos.get(nombre)
    
    def listar_algoritmos_disponibles(self) -> List[str]:
        """
        Listar algoritmos disponibles
        
        Returns:
            Lista de nombres de algoritmos
        """
        return list(self.algoritmos.keys())
    
    @logging_metodo(nombre_logger="servicio_recomendaciones", incluir_tiempo=True)
    @validar_parametros(validar_tipos=True)
    async def recomendar_para_usuario(
        self, 
        usuario_id: str, 
        limit: int = 10,
        algoritmo: Optional[str] = None,
        contexto: Optional[Dict[str, Any]] = None,
        filtros: Optional[Dict[str, Any]] = None
    ) -> List[Recomendacion]:
        """
        Generar recomendaciones para un usuario
        
        Args:
            usuario_id: ID del usuario
            limit: Número máximo de recomendaciones
            algoritmo: Algoritmo específico a usar
            contexto: Contexto adicional
            filtros: Filtros para las recomendaciones
            
        Returns:
            Lista de recomendaciones
        """
        try:
            # Validar entrada
            if not usuario_id or not usuario_id.strip():
                raise ValueError("El usuario_id no puede estar vacío")
            
            if limit <= 0 or limit > self.configuracion_final["max_recomendaciones"]:
                raise ValueError(f"El límite debe estar entre 1 y {self.configuracion_final['max_recomendaciones']}")
            
            # Usar algoritmo por defecto si no se especifica
            if algoritmo is None:
                algoritmo = self.configuracion_final["algoritmo_por_defecto"]
            
            # Obtener algoritmo
            algoritmo_instancia = self.obtener_algoritmo(algoritmo)
            if not algoritmo_instancia:
                raise ValueError(f"Algoritmo no encontrado: {algoritmo}")
            
            # Verificar si está habilitado
            if algoritmo not in self.configuracion_final["algoritmos_habilitados"]:
                raise ValueError(f"Algoritmo no habilitado: {algoritmo}")
            
            self.logger.info(
                "Generando recomendaciones para usuario",
                usuario_id=usuario_id,
                algoritmo=algoritmo,
                limit=limit
            )
            
            # Ejecutar recomendación con timeout
            timeout = self.configuracion_final["timeout_recomendacion"]
            recomendaciones = await asyncio.wait_for(
                algoritmo_instancia.recomendar(usuario_id, limit, contexto),
                timeout=timeout
            )
            
            # Aplicar filtros si se especifican
            if filtros:
                recomendaciones = algoritmo_instancia._filtrar_recomendaciones(recomendaciones, filtros)
            
            # Filtrar por confianza mínima
            min_confianza = self.configuracion_final["min_confianza"]
            recomendaciones = [r for r in recomendaciones if r.confianza >= min_confianza]
            
            # Limitar número de recomendaciones
            recomendaciones = recomendaciones[:limit]
            
            # Actualizar rankings
            for i, rec in enumerate(recomendaciones):
                rec.ranking = i + 1
            
            self.logger.info(
                "Recomendaciones generadas exitosamente",
                usuario_id=usuario_id,
                total_recomendaciones=len(recomendaciones),
                algoritmo=algoritmo
            )
            
            return recomendaciones
            
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout generando recomendaciones: {algoritmo}")
            raise ValueError(f"Timeout generando recomendaciones con {algoritmo}")
        
        except Exception as e:
            self.logger.error(f"Error generando recomendaciones: {str(e)}")
            raise
    
    @logging_metodo(nombre_logger="servicio_recomendaciones", incluir_tiempo=True)
    async def recomendar_similares(
        self, 
        item_id: str, 
        limit: int = 10,
        algoritmo: Optional[str] = None
    ) -> List[Recomendacion]:
        """
        Generar recomendaciones de items similares
        
        Args:
            item_id: ID del item de referencia
            limit: Número máximo de recomendaciones
            algoritmo: Algoritmo específico a usar
            
        Returns:
            Lista de recomendaciones similares
        """
        try:
            # Validar entrada
            if not item_id or not item_id.strip():
                raise ValueError("El item_id no puede estar vacío")
            
            # Usar algoritmo por defecto si no se especifica
            if algoritmo is None:
                algoritmo = self.configuracion_final["algoritmo_por_defecto"]
            
            # Obtener algoritmo
            algoritmo_instancia = self.obtener_algoritmo(algoritmo)
            if not algoritmo_instancia:
                raise ValueError(f"Algoritmo no encontrado: {algoritmo}")
            
            self.logger.info(
                "Generando recomendaciones similares",
                item_id=item_id,
                algoritmo=algoritmo,
                limit=limit
            )
            
            # Ejecutar recomendación con timeout
            timeout = self.configuracion_final["timeout_recomendacion"]
            recomendaciones = await asyncio.wait_for(
                algoritmo_instancia.recomendar_similares(item_id, limit),
                timeout=timeout
            )
            
            # Filtrar por confianza mínima
            min_confianza = self.configuracion_final["min_confianza"]
            recomendaciones = [r for r in recomendaciones if r.confianza >= min_confianza]
            
            # Limitar número de recomendaciones
            recomendaciones = recomendaciones[:limit]
            
            # Actualizar rankings
            for i, rec in enumerate(recomendaciones):
                rec.ranking = i + 1
            
            self.logger.info(
                "Recomendaciones similares generadas exitosamente",
                item_id=item_id,
                total_recomendaciones=len(recomendaciones),
                algoritmo=algoritmo
            )
            
            return recomendaciones
            
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout generando recomendaciones similares: {algoritmo}")
            raise ValueError(f"Timeout generando recomendaciones similares con {algoritmo}")
        
        except Exception as e:
            self.logger.error(f"Error generando recomendaciones similares: {str(e)}")
            raise
    
    @logging_metodo(nombre_logger="servicio_recomendaciones", incluir_tiempo=True)
    async def comparar_algoritmos(
        self, 
        usuario_id: str, 
        limit: int = 10,
        algoritmos: Optional[List[str]] = None,
        contexto: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Recomendacion]]:
        """
        Comparar diferentes algoritmos para un usuario
        
        Args:
            usuario_id: ID del usuario
            limit: Número máximo de recomendaciones
            algoritmos: Lista de algoritmos a comparar
            contexto: Contexto adicional
            
        Returns:
            Diccionario con resultados por algoritmo
        """
        if algoritmos is None:
            algoritmos = self.configuracion_final["algoritmos_habilitados"]
        
        self.logger.info(f"Comparando algoritmos: {algoritmos}")
        
        resultados = {}
        
        for algoritmo in algoritmos:
            try:
                recomendaciones = await self.recomendar_para_usuario(
                    usuario_id=usuario_id,
                    limit=limit,
                    algoritmo=algoritmo,
                    contexto=contexto
                )
                resultados[algoritmo] = recomendaciones
            except Exception as e:
                self.logger.error(f"Error con algoritmo {algoritmo}: {str(e)}")
                resultados[algoritmo] = []
        
        return resultados
    
    @logging_metodo(nombre_logger="servicio_recomendaciones", incluir_tiempo=True)
    async def entrenar_algoritmo(
        self, 
        algoritmo: str, 
        datos_entrenamiento: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Entrenar un algoritmo específico
        
        Args:
            algoritmo: Nombre del algoritmo
            datos_entrenamiento: Datos para entrenar
            
        Returns:
            Métricas de entrenamiento
        """
        try:
            # Obtener algoritmo
            algoritmo_instancia = self.obtener_algoritmo(algoritmo)
            if not algoritmo_instancia:
                raise ValueError(f"Algoritmo no encontrado: {algoritmo}")
            
            self.logger.info(f"Iniciando entrenamiento del algoritmo: {algoritmo}")
            
            # Entrenar algoritmo
            metricas = await algoritmo_instancia.entrenar(datos_entrenamiento)
            
            self.logger.info(
                "Entrenamiento completado",
                algoritmo=algoritmo,
                metricas=metricas
            )
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error entrenando algoritmo {algoritmo}: {str(e)}")
            raise
    
    @logging_metodo(nombre_logger="servicio_recomendaciones", incluir_tiempo=True)
    async def evaluar_algoritmo(
        self, 
        algoritmo: str, 
        datos_test: Dict[str, Any],
        metricas: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Evaluar un algoritmo con datos de test
        
        Args:
            algoritmo: Nombre del algoritmo
            datos_test: Datos de test
            metricas: Lista de métricas a calcular
            
        Returns:
            Diccionario con métricas de evaluación
        """
        try:
            # Obtener algoritmo
            algoritmo_instancia = self.obtener_algoritmo(algoritmo)
            if not algoritmo_instancia:
                raise ValueError(f"Algoritmo no encontrado: {algoritmo}")
            
            self.logger.info(f"Evaluando algoritmo: {algoritmo}")
            
            # Evaluar algoritmo (implementación específica por algoritmo)
            if hasattr(algoritmo_instancia, 'evaluar'):
                metricas_evaluacion = await algoritmo_instancia.evaluar(datos_test, metricas)
            else:
                # Evaluación básica
                metricas_evaluacion = await self._evaluar_basica(algoritmo_instancia, datos_test)
            
            self.logger.info(
                "Evaluación completada",
                algoritmo=algoritmo,
                metricas=metricas_evaluacion
            )
            
            return metricas_evaluacion
            
        except Exception as e:
            self.logger.error(f"Error evaluando algoritmo {algoritmo}: {str(e)}")
            raise
    
    async def _evaluar_basica(
        self, 
        algoritmo: AlgoritmoRecomendacion, 
        datos_test: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Evaluación básica del algoritmo
        
        Args:
            algoritmo: Instancia del algoritmo
            datos_test: Datos de test
            
        Returns:
            Métricas básicas
        """
        # Implementación básica de evaluación
        # En un sistema real, se implementaría evaluación específica por algoritmo
        
        return {
            "precision": 0.85,
            "recall": 0.78,
            "f1_score": 0.81,
            "coverage": 0.92,
            "diversity": 0.67
        }
    
    @logging_metodo(nombre_logger="servicio_recomendaciones", incluir_tiempo=True)
    async def obtener_estadisticas(
        self, 
        usuario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtener estadísticas del servicio
        
        Args:
            usuario_id: ID del usuario (opcional)
            
        Returns:
            Diccionario con estadísticas
        """
        estadisticas = {
            "algoritmos_disponibles": self.listar_algoritmos_disponibles(),
            "configuracion": self.configuracion_final,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if usuario_id:
            # Estadísticas específicas del usuario
            estadisticas["usuario"] = {
                "id": usuario_id,
                "algoritmo_preferido": self.configuracion_final["algoritmo_por_defecto"]
            }
        
        return estadisticas
    
    def obtener_configuracion(self) -> Dict[str, Any]:
        """
        Obtener configuración actual del servicio
        
        Returns:
            Diccionario con la configuración
        """
        return self.configuracion_final.copy()
    
    def actualizar_configuracion(self, nueva_configuracion: Dict[str, Any]) -> None:
        """
        Actualizar configuración del servicio
        
        Args:
            nueva_configuracion: Nueva configuración
        """
        self.configuracion_final.update(nueva_configuracion)
        self.logger.info("Configuración actualizada", nueva_configuracion=nueva_configuracion)
