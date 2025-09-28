"""
Value Object Email - Capa de Dominio
Representa un email válido con validaciones de negocio
"""
import re
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """
    Value Object que representa un email válido
    Inmutable y con validaciones de negocio
    """
    
    valor: str
    
    def __post_init__(self):
        """Validar email después de la construcción"""
        if not self._es_email_valido(self.valor):
            raise ValueError(f"Email inválido: {self.valor}")
    
    def _es_email_valido(self, email: str) -> bool:
        """Validar formato de email"""
        if not email or not isinstance(email, str):
            return False
        
        # Patrón regex para validar email
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(patron, email))
    
    def obtener_dominio(self) -> str:
        """Obtener el dominio del email"""
        return self.valor.split('@')[1]
    
    def obtener_usuario(self) -> str:
        """Obtener la parte del usuario del email"""
        return self.valor.split('@')[0]
    
    def es_dominio_corporativo(self) -> bool:
        """Verificar si es un email corporativo"""
        dominios_corporativos = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 
            'outlook.com', 'live.com'
        ]
        return self.obtener_dominio().lower() not in dominios_corporativos
    
    def __str__(self) -> str:
        """Representación string del email"""
        return self.valor
    
    def __repr__(self) -> str:
        """Representación detallada del email"""
        return f"Email('{self.valor}')"
