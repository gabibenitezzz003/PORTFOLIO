"""
Operador de Calidad de Datos
Valida la calidad de los datos procesados
"""
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.postgres_hook import PostgresHook
import pandas as pd
import structlog
from typing import Dict, Any, List, Optional


class DataQualityOperator(BaseOperator):
    """
    Operador para validar la calidad de los datos
    """
    
    ui_color = '#89DA59'
    
    @apply_defaults
    def __init__(
        self,
        postgres_conn_id: str = 'postgres_default',
        table_name: str = None,
        quality_checks: List[Dict[str, Any]] = None,
        *args, **kwargs
    ):
        """
        Inicializar operador de calidad de datos
        
        Args:
            postgres_conn_id: ID de conexión de PostgreSQL
            table_name: Nombre de la tabla a validar
            quality_checks: Lista de verificaciones de calidad
        """
        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.postgres_conn_id = postgres_conn_id
        self.table_name = table_name
        self.quality_checks = quality_checks or []
        self.logger = structlog.get_logger()
    
    def execute(self, context):
        """
        Ejecutar verificaciones de calidad de datos
        """
        self.logger.info(f"Iniciando verificaciones de calidad para tabla: {self.table_name}")
        
        # Conectar a la base de datos
        postgres_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        
        # Ejecutar verificaciones
        resultados = []
        
        for check in self.quality_checks:
            resultado = self._ejecutar_verificacion(postgres_hook, check)
            resultados.append(resultado)
        
        # Consolidar resultados
        self._consolidar_resultados(resultados, context)
        
        self.logger.info("Verificaciones de calidad completadas")
    
    def _ejecutar_verificacion(self, postgres_hook: PostgresHook, check: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar una verificación específica
        
        Args:
            postgres_hook: Hook de PostgreSQL
            check: Configuración de la verificación
            
        Returns:
            Resultado de la verificación
        """
        nombre_check = check.get('nombre', 'Verificación sin nombre')
        tipo_check = check.get('tipo', 'sql')
        query = check.get('query', '')
        valor_esperado = check.get('valor_esperado', None)
        operador = check.get('operador', '==')
        tolerancia = check.get('tolerancia', 0)
        
        try:
            # Ejecutar query
            if tipo_check == 'sql':
                resultado = postgres_hook.get_first(query)
                valor_obtenido = resultado[0] if resultado else None
            elif tipo_check == 'count':
                df = postgres_hook.get_pandas_df(query)
                valor_obtenido = len(df)
            elif tipo_check == 'sum':
                df = postgres_hook.get_pandas_df(query)
                valor_obtenido = df.iloc[0, 0] if not df.empty else 0
            else:
                raise ValueError(f"Tipo de verificación no soportado: {tipo_check}")
            
            # Evaluar resultado
            es_valido = self._evaluar_resultado(
                valor_obtenido, valor_esperado, operador, tolerancia
            )
            
            resultado_check = {
                'nombre': nombre_check,
                'tipo': tipo_check,
                'valor_obtenido': valor_obtenido,
                'valor_esperado': valor_esperado,
                'operador': operador,
                'tolerancia': tolerancia,
                'es_valido': es_valido,
                'error': None
            }
            
            self.logger.info(
                f"Verificación '{nombre_check}': {'✅ VÁLIDA' if es_valido else '❌ INVÁLIDA'}",
                valor_obtenido=valor_obtenido,
                valor_esperado=valor_esperado
            )
            
        except Exception as e:
            resultado_check = {
                'nombre': nombre_check,
                'tipo': tipo_check,
                'valor_obtenido': None,
                'valor_esperado': valor_esperado,
                'operador': operador,
                'tolerancia': tolerancia,
                'es_valido': False,
                'error': str(e)
            }
            
            self.logger.error(f"Error en verificación '{nombre_check}': {str(e)}")
        
        return resultado_check
    
    def _evaluar_resultado(
        self, 
        valor_obtenido: Any, 
        valor_esperado: Any, 
        operador: str, 
        tolerancia: float
    ) -> bool:
        """
        Evaluar si el resultado cumple con la expectativa
        
        Args:
            valor_obtenido: Valor obtenido de la verificación
            valor_esperado: Valor esperado
            operador: Operador de comparación
            tolerancia: Tolerancia permitida
            
        Returns:
            True si la verificación es válida
        """
        if valor_obtenido is None or valor_esperado is None:
            return False
        
        try:
            # Convertir a números si es posible
            if isinstance(valor_obtenido, (int, float)) and isinstance(valor_esperado, (int, float)):
                if operador == '==':
                    return abs(valor_obtenido - valor_esperado) <= tolerancia
                elif operador == '>=':
                    return valor_obtenido >= (valor_esperado - tolerancia)
                elif operador == '<=':
                    return valor_obtenido <= (valor_esperado + tolerancia)
                elif operador == '>':
                    return valor_obtenido > (valor_esperado - tolerancia)
                elif operador == '<':
                    return valor_obtenido < (valor_esperado + tolerancia)
                else:
                    return False
            else:
                # Comparación de strings
                if operador == '==':
                    return str(valor_obtenido) == str(valor_esperado)
                elif operador == '!=':
                    return str(valor_obtenido) != str(valor_esperado)
                else:
                    return False
        except Exception:
            return False
    
    def _consolidar_resultados(self, resultados: List[Dict[str, Any]], context: Dict[str, Any]) -> None:
        """
        Consolidar resultados de todas las verificaciones
        
        Args:
            resultados: Lista de resultados de verificaciones
            context: Contexto de Airflow
        """
        # Calcular métricas
        total_verificaciones = len(resultados)
        verificaciones_validas = sum(1 for r in resultados if r['es_valido'])
        verificaciones_invalidas = total_verificaciones - verificaciones_validas
        verificaciones_con_error = sum(1 for r in resultados if r['error'] is not None)
        
        # Calcular porcentaje de éxito
        porcentaje_exito = (verificaciones_validas / total_verificaciones * 100) if total_verificaciones > 0 else 0
        
        # Determinar estado general
        if verificaciones_con_error > 0:
            estado_general = 'error'
        elif verificaciones_invalidas > 0:
            estado_general = 'warning'
        else:
            estado_general = 'success'
        
        # Crear resumen
        resumen = {
            'tabla': self.table_name,
            'timestamp': context['ts'],
            'estado_general': estado_general,
            'total_verificaciones': total_verificaciones,
            'verificaciones_validas': verificaciones_validas,
            'verificaciones_invalidas': verificaciones_invalidas,
            'verificaciones_con_error': verificaciones_con_error,
            'porcentaje_exito': round(porcentaje_exito, 2),
            'resultados_detallados': resultados
        }
        
        # Almacenar en XCom
        context['task_instance'].xcom_push(key='data_quality_summary', value=resumen)
        
        # Log resumen
        self.logger.info(
            f"Resumen de calidad de datos - {self.table_name}",
            estado=estado_general,
            total=total_verificaciones,
            validas=verificaciones_validas,
            invalidas=verificaciones_invalidas,
            errores=verificaciones_con_error,
            porcentaje_exito=porcentaje_exito
        )
        
        # Fallar si hay errores críticos
        if verificaciones_con_error > 0:
            raise ValueError(f"Se encontraron {verificaciones_con_error} errores en las verificaciones de calidad")
        
        # Warning si hay verificaciones inválidas
        if verificaciones_invalidas > 0:
            self.logger.warning(f"Se encontraron {verificaciones_invalidas} verificaciones inválidas")
