"""
Value Object NombreUsuario - Capa de Dominio
Representa un nombre de usuario válido con validaciones de negocio
"""
import re
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class NombreUsuario:
    """
    Value Object que representa un nombre de usuario válido
    Inmutable y con validaciones de negocio
    """
    
    valor: str
    
    def __post_init__(self):
        """Validar nombre de usuario después de la construcción"""
        if not self._es_nombre_usuario_valido(self.valor):
            raise ValueError(f"Nombre de usuario inválido: {self.valor}")
    
    def _es_nombre_usuario_valido(self, nombre: str) -> bool:
        """Validar formato de nombre de usuario"""
        if not nombre or not isinstance(nombre, str):
            return False
        
        # Longitud entre 3 y 20 caracteres
        if len(nombre) < 3 or len(nombre) > 20:
            return False
        
        # Solo letras, números, guiones y guiones bajos
        patron = r'^[a-zA-Z0-9_-]+$'
        if not re.match(patron, nombre):
            return False
        
        # No puede empezar o terminar con guión o guión bajo
        if nombre.startswith(('-', '_')) or nombre.endswith(('-', '_')):
            return False
        
        # No puede tener guiones o guiones bajos consecutivos
        if '--' in nombre or '__' in nombre or '_-' in nombre or '-_' in nombre:
            return False
        
        return True
    
    def es_nombre_reservado(self) -> bool:
        """Verificar si es un nombre de usuario reservado"""
        nombres_reservados = [
            'admin', 'administrator', 'root', 'system', 'api',
            'www', 'mail', 'ftp', 'support', 'help', 'info',
            'test', 'demo', 'guest', 'user', 'null', 'undefined'
        ]
        return self.valor.lower() in nombres_reservados
    
    def obtener_longitud(self) -> int:
        """Obtener la longitud del nombre de usuario"""
        return len(self.valor)
    
    def es_corto(self) -> bool:
        """Verificar si el nombre es corto"""
        return len(self.valor) < 5
    
    def es_largo(self) -> bool:
        """Verificar si el nombre es largo"""
        return len(self.valor) > 15
    
    def __str__(self) -> str:
        """Representación string del nombre de usuario"""
        return self.valor
    
    def __repr__(self) -> str:
        """Representación detallada del nombre de usuario"""
        return f"NombreUsuario('{self.valor}')"
