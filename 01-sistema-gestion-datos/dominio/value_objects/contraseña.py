"""
Value Object Contraseña - Capa de Dominio
Representa una contraseña válida con validaciones de seguridad
"""
import re
import hashlib
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Contraseña:
    """
    Value Object que representa una contraseña válida
    Inmutable y con validaciones de seguridad
    """
    
    valor: str
    hash_contraseña: Optional[str] = None
    
    def __post_init__(self):
        """Validar contraseña después de la construcción"""
        if not self._es_contraseña_valida(self.valor):
            raise ValueError("Contraseña no cumple con los requisitos de seguridad")
    
    def _es_contraseña_valida(self, contraseña: str) -> bool:
        """Validar fortaleza de la contraseña"""
        if not contraseña or not isinstance(contraseña, str):
            return False
        
        # Longitud mínima de 8 caracteres
        if len(contraseña) < 8:
            return False
        
        # Longitud máxima de 128 caracteres
        if len(contraseña) > 128:
            return False
        
        # Debe contener al menos una letra minúscula
        if not re.search(r'[a-z]', contraseña):
            return False
        
        # Debe contener al menos una letra mayúscula
        if not re.search(r'[A-Z]', contraseña):
            return False
        
        # Debe contener al menos un número
        if not re.search(r'\d', contraseña):
            return False
        
        # Debe contener al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', contraseña):
            return False
        
        # No debe contener espacios
        if ' ' in contraseña:
            return False
        
        return True
    
    def obtener_fortaleza(self) -> str:
        """Obtener nivel de fortaleza de la contraseña"""
        puntuacion = 0
        
        # Longitud
        if len(self.valor) >= 12:
            puntuacion += 2
        elif len(self.valor) >= 8:
            puntuacion += 1
        
        # Complejidad
        if re.search(r'[a-z]', self.valor):
            puntuacion += 1
        if re.search(r'[A-Z]', self.valor):
            puntuacion += 1
        if re.search(r'\d', self.valor):
            puntuacion += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', self.valor):
            puntuacion += 1
        
        # Caracteres únicos
        caracteres_unicos = len(set(self.valor))
        if caracteres_unicos >= len(self.valor) * 0.8:
            puntuacion += 1
        
        if puntuacion >= 6:
            return "Muy Fuerte"
        elif puntuacion >= 4:
            return "Fuerte"
        elif puntuacion >= 2:
            return "Media"
        else:
            return "Débil"
    
    def generar_hash(self) -> str:
        """Generar hash de la contraseña usando SHA-256"""
        return hashlib.sha256(self.valor.encode()).hexdigest()
    
    def verificar_contraseña(self, contraseña_plana: str) -> bool:
        """Verificar si una contraseña coincide"""
        return self.valor == contraseña_plana
    
    def es_contraseña_comun(self) -> bool:
        """Verificar si es una contraseña común"""
        contraseñas_comunes = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            '1234567890', 'password1', 'qwerty123', 'dragon', 'master'
        ]
        return self.valor.lower() in contraseñas_comunes
    
    def __str__(self) -> str:
        """Representación string de la contraseña (oculta)"""
        return "*" * len(self.valor)
    
    def __repr__(self) -> str:
        """Representación detallada de la contraseña (oculta)"""
        return f"Contraseña('{self.__str__()}')"
