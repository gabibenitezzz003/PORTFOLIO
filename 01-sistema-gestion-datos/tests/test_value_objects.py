"""
Tests para Value Objects - Capa de Dominio
Tests unitarios para value objects del dominio
"""
import pytest
from dominio.value_objects.email import Email
from dominio.value_objects.nombre_usuario import NombreUsuario
from dominio.value_objects.contraseña import Contraseña


class TestEmail:
    """Tests para el value object Email"""
    
    def test_email_valido(self):
        """Test para email válido"""
        email = Email("test@ejemplo.com")
        assert str(email) == "test@ejemplo.com"
        assert email.obtener_dominio() == "ejemplo.com"
        assert email.obtener_usuario() == "test"
    
    def test_email_invalido_vacio(self):
        """Test para email vacío"""
        with pytest.raises(ValueError):
            Email("")
    
    def test_email_invalido_sin_arroba(self):
        """Test para email sin @"""
        with pytest.raises(ValueError):
            Email("testejemplo.com")
    
    def test_email_invalido_sin_dominio(self):
        """Test para email sin dominio"""
        with pytest.raises(ValueError):
            Email("test@")
    
    def test_email_invalido_sin_usuario(self):
        """Test para email sin usuario"""
        with pytest.raises(ValueError):
            Email("@ejemplo.com")
    
    def test_email_dominio_corporativo(self):
        """Test para verificar dominio corporativo"""
        email_corporativo = Email("usuario@empresa.com")
        email_personal = Email("usuario@gmail.com")
        
        assert email_corporativo.es_dominio_corporativo() is True
        assert email_personal.es_dominio_corporativo() is False
    
    def test_email_inmutable(self):
        """Test para verificar que el email es inmutable"""
        email = Email("test@ejemplo.com")
        
        # No se puede modificar el valor
        with pytest.raises(AttributeError):
            email.valor = "otro@ejemplo.com"


class TestNombreUsuario:
    """Tests para el value object NombreUsuario"""
    
    def test_nombre_usuario_valido(self):
        """Test para nombre de usuario válido"""
        nombre = NombreUsuario("testuser")
        assert str(nombre) == "testuser"
        assert nombre.obtener_longitud() == 8
    
    def test_nombre_usuario_muy_corto(self):
        """Test para nombre de usuario muy corto"""
        with pytest.raises(ValueError):
            NombreUsuario("ab")
    
    def test_nombre_usuario_muy_largo(self):
        """Test para nombre de usuario muy largo"""
        with pytest.raises(ValueError):
            NombreUsuario("a" * 21)
    
    def test_nombre_usuario_con_caracteres_invalidos(self):
        """Test para nombre de usuario con caracteres inválidos"""
        with pytest.raises(ValueError):
            NombreUsuario("test user")  # Con espacio
        
        with pytest.raises(ValueError):
            NombreUsuario("test@user")  # Con @
    
    def test_nombre_usuario_empieza_con_guion(self):
        """Test para nombre de usuario que empieza con guión"""
        with pytest.raises(ValueError):
            NombreUsuario("-testuser")
    
    def test_nombre_usuario_termina_con_guion(self):
        """Test para nombre de usuario que termina con guión"""
        with pytest.raises(ValueError):
            NombreUsuario("testuser-")
    
    def test_nombre_usuario_con_guiones_consecutivos(self):
        """Test para nombre de usuario con guiones consecutivos"""
        with pytest.raises(ValueError):
            NombreUsuario("test--user")
        
        with pytest.raises(ValueError):
            NombreUsuario("test__user")
    
    def test_nombre_usuario_reservado(self):
        """Test para nombre de usuario reservado"""
        nombre_reservado = NombreUsuario("admin")
        nombre_normal = NombreUsuario("usuario123")
        
        assert nombre_reservado.es_nombre_reservado() is True
        assert nombre_normal.es_nombre_reservado() is False
    
    def test_nombre_usuario_corto_largo(self):
        """Test para verificar métodos de longitud"""
        nombre_corto = NombreUsuario("test")
        nombre_largo = NombreUsuario("usuario123456")
        
        assert nombre_corto.es_corto() is True
        assert nombre_corto.es_largo() is False
        assert nombre_largo.es_corto() is False
        assert nombre_largo.es_largo() is True
    
    def test_nombre_usuario_inmutable(self):
        """Test para verificar que el nombre de usuario es inmutable"""
        nombre = NombreUsuario("testuser")
        
        # No se puede modificar el valor
        with pytest.raises(AttributeError):
            nombre.valor = "otrouser"


class TestContraseña:
    """Tests para el value object Contraseña"""
    
    def test_contraseña_valida(self):
        """Test para contraseña válida"""
        contraseña = Contraseña("TestPass123!")
        assert str(contraseña) == "*" * 12  # Ocultada
        assert contraseña.obtener_fortaleza() in ["Fuerte", "Muy Fuerte"]
    
    def test_contraseña_muy_corta(self):
        """Test para contraseña muy corta"""
        with pytest.raises(ValueError):
            Contraseña("Test1!")
    
    def test_contraseña_muy_larga(self):
        """Test para contraseña muy larga"""
        with pytest.raises(ValueError):
            Contraseña("A" * 129 + "1!")
    
    def test_contraseña_sin_minuscula(self):
        """Test para contraseña sin letra minúscula"""
        with pytest.raises(ValueError):
            Contraseña("TESTPASS123!")
    
    def test_contraseña_sin_mayuscula(self):
        """Test para contraseña sin letra mayúscula"""
        with pytest.raises(ValueError):
            Contraseña("testpass123!")
    
    def test_contraseña_sin_numero(self):
        """Test para contraseña sin número"""
        with pytest.raises(ValueError):
            Contraseña("TestPass!")
    
    def test_contraseña_sin_caracter_especial(self):
        """Test para contraseña sin carácter especial"""
        with pytest.raises(ValueError):
            Contraseña("TestPass123")
    
    def test_contraseña_con_espacios(self):
        """Test para contraseña con espacios"""
        with pytest.raises(ValueError):
            Contraseña("Test Pass 123!")
    
    def test_contraseña_fortaleza(self):
        """Test para verificar fortaleza de contraseña"""
        contraseña_fuerte = Contraseña("TestPass123!")
        contraseña_debil = Contraseña("Test123!")
        
        assert contraseña_fuerte.obtener_fortaleza() in ["Fuerte", "Muy Fuerte"]
        assert contraseña_debil.obtener_fortaleza() in ["Media", "Débil"]
    
    def test_contraseña_comun(self):
        """Test para verificar contraseñas comunes"""
        contraseña_comun = Contraseña("password123")
        contraseña_normal = Contraseña("MiContraseña123!")
        
        assert contraseña_comun.es_contraseña_comun() is True
        assert contraseña_normal.es_contraseña_comun() is False
    
    def test_generar_hash(self):
        """Test para generar hash de contraseña"""
        contraseña = Contraseña("TestPass123!")
        hash1 = contraseña.generar_hash()
        hash2 = contraseña.generar_hash()
        
        # El hash debe ser consistente
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produce hash de 64 caracteres
    
    def test_verificar_contraseña(self):
        """Test para verificar contraseña"""
        contraseña = Contraseña("TestPass123!")
        
        assert contraseña.verificar_contraseña("TestPass123!") is True
        assert contraseña.verificar_contraseña("otracontraseña") is False
    
    def test_contraseña_inmutable(self):
        """Test para verificar que la contraseña es inmutable"""
        contraseña = Contraseña("TestPass123!")
        
        # No se puede modificar el valor
        with pytest.raises(AttributeError):
            contraseña.valor = "OtraPass123!"
