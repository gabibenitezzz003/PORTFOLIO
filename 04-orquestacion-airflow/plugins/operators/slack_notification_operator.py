"""
Operador de Notificación Slack
Envía notificaciones a Slack con información de las tareas
"""
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base_hook import BaseHook
import requests
import json
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime


class SlackNotificationOperator(BaseOperator):
    """
    Operador para enviar notificaciones a Slack
    """
    
    ui_color = '#4A154B'
    
    @apply_defaults
    def __init__(
        self,
        slack_conn_id: str = 'slack_default',
        channel: str = '#general',
        message: str = None,
        message_type: str = 'info',
        include_task_info: bool = True,
        include_dag_info: bool = True,
        include_execution_info: bool = True,
        *args, **kwargs
    ):
        """
        Inicializar operador de notificación Slack
        
        Args:
            slack_conn_id: ID de conexión de Slack
            channel: Canal de Slack para enviar el mensaje
            message: Mensaje personalizado
            message_type: Tipo de mensaje (info, success, warning, error)
            include_task_info: Incluir información de la tarea
            include_dag_info: Incluir información del DAG
            include_execution_info: Incluir información de ejecución
        """
        super(SlackNotificationOperator, self).__init__(*args, **kwargs)
        self.slack_conn_id = slack_conn_id
        self.channel = channel
        self.message = message
        self.message_type = message_type
        self.include_task_info = include_task_info
        self.include_dag_info = include_dag_info
        self.include_execution_info = include_execution_info
        self.logger = structlog.get_logger()
    
    def execute(self, context):
        """
        Ejecutar notificación a Slack
        """
        self.logger.info(f"Enviando notificación a Slack - Canal: {self.channel}")
        
        try:
            # Obtener conexión de Slack
            slack_hook = BaseHook.get_connection(self.slack_conn_id)
            webhook_url = slack_hook.password  # Asumiendo que el webhook está en el password
            
            # Construir mensaje
            mensaje_completo = self._construir_mensaje(context)
            
            # Enviar mensaje
            self._enviar_mensaje(webhook_url, mensaje_completo)
            
            self.logger.info("Notificación enviada exitosamente a Slack")
            
        except Exception as e:
            self.logger.error(f"Error enviando notificación a Slack: {str(e)}")
            raise
    
    def _construir_mensaje(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construir mensaje completo para Slack
        
        Args:
            context: Contexto de Airflow
            
        Returns:
            Mensaje estructurado para Slack
        """
        # Obtener información básica
        task_instance = context['task_instance']
        dag = context['dag']
        
        # Determinar color y emoji según el tipo de mensaje
        colores = {
            'info': '#36a64f',      # Verde
            'success': '#36a64f',   # Verde
            'warning': '#ff9500',   # Naranja
            'error': '#ff0000'      # Rojo
        }
        
        emojis = {
            'info': ':information_source:',
            'success': ':white_check_mark:',
            'warning': ':warning:',
            'error': ':x:'
        }
        
        color = colores.get(self.message_type, '#36a64f')
        emoji = emojis.get(self.message_type, ':information_source:')
        
        # Construir título
        titulo = f"{emoji} Airflow - {dag.dag_id}"
        
        # Construir campos del mensaje
        campos = []
        
        # Información del DAG
        if self.include_dag_info:
            campos.append({
                "title": "DAG",
                "value": dag.dag_id,
                "short": True
            })
            campos.append({
                "title": "Descripción",
                "value": dag.description or "Sin descripción",
                "short": True
            })
        
        # Información de la tarea
        if self.include_task_info:
            campos.append({
                "title": "Tarea",
                "value": task_instance.task_id,
                "short": True
            })
            campos.append({
                "title": "Operador",
                "value": task_instance.operator,
                "short": True
            })
        
        # Información de ejecución
        if self.include_execution_info:
            campos.append({
                "title": "Fecha de Ejecución",
                "value": context['ds'],
                "short": True
            })
            campos.append({
                "title": "Timestamp",
                "value": context['ts'],
                "short": True
            })
            
            # Estado de la tarea
            estado = task_instance.state
            campos.append({
                "title": "Estado",
                "value": estado,
                "short": True
            })
            
            # Duración si está disponible
            if hasattr(task_instance, 'duration') and task_instance.duration:
                duracion = f"{task_instance.duration:.2f} segundos"
                campos.append({
                    "title": "Duración",
                    "value": duracion,
                    "short": True
                })
        
        # Mensaje personalizado
        if self.message:
            campos.append({
                "title": "Mensaje",
                "value": self.message,
                "short": False
            })
        
        # Construir mensaje completo
        mensaje = {
            "channel": self.channel,
            "attachments": [
                {
                    "color": color,
                    "title": titulo,
                    "fields": campos,
                    "footer": "Apache Airflow",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        return mensaje
    
    def _enviar_mensaje(self, webhook_url: str, mensaje: Dict[str, Any]) -> None:
        """
        Enviar mensaje a Slack usando webhook
        
        Args:
            webhook_url: URL del webhook de Slack
            mensaje: Mensaje a enviar
        """
        try:
            # Preparar headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Airflow-SlackOperator/1.0'
            }
            
            # Enviar request
            response = requests.post(
                webhook_url,
                data=json.dumps(mensaje),
                headers=headers,
                timeout=30
            )
            
            # Verificar respuesta
            if response.status_code == 200:
                self.logger.info("Mensaje enviado exitosamente a Slack")
            else:
                self.logger.error(f"Error enviando mensaje a Slack: {response.status_code} - {response.text}")
                raise Exception(f"Error HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            self.logger.error("Timeout enviando mensaje a Slack")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error de conexión enviando mensaje a Slack: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado enviando mensaje a Slack: {str(e)}")
            raise


class SlackAlertOperator(SlackNotificationOperator):
    """
    Operador especializado para alertas de Slack
    """
    
    @apply_defaults
    def __init__(
        self,
        alert_type: str = 'error',
        severity: str = 'high',
        *args, **kwargs
    ):
        """
        Inicializar operador de alerta Slack
        
        Args:
            alert_type: Tipo de alerta (error, warning, info)
            severity: Severidad (low, medium, high, critical)
        """
        # Configurar canal según severidad
        canales_por_severidad = {
            'low': '#alerts-low',
            'medium': '#alerts-medium',
            'high': '#alerts-high',
            'critical': '#alerts-critical'
        }
        
        canal = canales_por_severidad.get(severity, '#alerts-high')
        
        super(SlackAlertOperator, self).__init__(
            channel=canal,
            message_type=alert_type,
            *args, **kwargs
        )
        
        self.alert_type = alert_type
        self.severity = severity
    
    def execute(self, context):
        """
        Ejecutar alerta de Slack
        """
        # Agregar información de severidad al mensaje
        if not self.message:
            self.message = f"🚨 ALERTA {self.severity.upper()}: {self.alert_type.upper()}"
        
        # Llamar al método padre
        super().execute(context)
