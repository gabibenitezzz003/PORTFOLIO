"""
Tests para Entidades - Capa de Dominio
Tests unitarios para entidades del dominio
"""
import pytest
from datetime import datetime
from dominio.entidades.usuario import Usuario
from dominio.value_objects.email import Email
from dominio.value_objects.nombre_usuario import NombreUsuario
from dominio.value_objects.contraseña import Contraseña


class TestUsuario:
    """Tests para la entidad Usuario"""
    
    @pytest.fixture
    def usuario_valido(self):
        """Fixture para usuario válido"""
        return Usuario(
            id=1,
            email=Email("test@ejemplo.com"),
            nombre_usuario=NombreUsuario("testuser"),
            contraseña=Contraseña("TestPass123!"),
            nombre_completo="Usuario Test",
            biografia="Biografía de prueba",
            esta_activo=True,
            es_superusuario=False
        )
    
    def test_crear_usuario_valido(self, usuario_valido):
        """Test para crear usuario válido"""
        assert usuario_valido.id == 1
        assert str(usuario_valido.email) == "test@ejemplo.com"
        assert str(usuario_valido.nombre_usuario) == "testuser"
        assert usuario_valido.nombre_completo == "Usuario Test"
        assert usuario_valido.biografia == "Biografía de prueba"
        assert usuario_valido.esta_activo is True
        assert usuario_valido.es_superusuario is False
        assert usuario_valido.fecha_creacion is not None
        assert usuario_valido.fecha_actualizacion is not None
    
    def test_activar_usuario(self, usuario_valido):
        """Test para activar usuario"""
        usuario_valido.desactivar()
        assert usuario_valido.esta_activo is False
        
        usuario_valido.activar()
        assert usuario_valido.esta_activo is True
        assert usuario_valido.fecha_actualizacion is not None
    
    def test_desactivar_usuario(self, usuario_valido):
        """Test para desactivar usuario"""
        assert usuario_valido.esta_activo is True
        
        usuario_valido.desactivar()
        assert usuario_valido.esta_activo is False
        assert usuario_valido.fecha_actualizacion is not None
    
    def test_promover_a_superusuario(self, usuario_valido):
        """Test para promover usuario a superusuario"""
        assert usuario_valido.es_superusuario is False
        
        usuario_valido.promover_a_superusuario()
        assert usuario_valido.es_superusuario is True
        assert usuario_valido.fecha_actualizacion is not None
    
    def test_degradar_de_superusuario(self, usuario_valido):
        """Test para degradar usuario de superusuario"""
        usuario_valido.promover_a_superusuario()
        assert usuario_valido.es_superusuario is True
        
        usuario_valido.degradar_de_superusuario()
        assert usuario_valido.es_superusuario is False
        assert usuario_valido.fecha_actualizacion is not None
    
    def test_actualizar_informacion_personal(self, usuario_valido):
        """Test para actualizar información personal"""
        nuevo_nombre = "Nuevo Nombre"
        nueva_biografia = "Nueva biografía"
        
        usuario_valido.actualizar_informacion_personal(
            nombre_completo=nuevo_nombre,
            biografia=nueva_biografia
        )
        
        assert usuario_valido.nombre_completo == nuevo_nombre
        assert usuario_valido.biografia == nueva_biografia
        assert usuario_valido.fecha_actualizacion is not None
    
    def test_actualizar_solo_nombre(self, usuario_valido):
        """Test para actualizar solo el nombre"""
        nuevo_nombre = "Solo Nombre"
        biografia_original = usuario_valido.biografia
        
        usuario_valido.actualizar_informacion_personal(
            nombre_completo=nuevo_nombre
        )
        
        assert usuario_valido.nombre_completo == nuevo_nombre
        assert usuario_valido.biografia == biografia_original
    
    def test_actualizar_solo_biografia(self, usuario_valido):
        """Test para actualizar solo la biografía"""
        nueva_biografia = "Solo biografía"
        nombre_original = usuario_valido.nombre_completo
        
        usuario_valido.actualizar_informacion_personal(
            biografia=nueva_biografia
        )
        
        assert usuario_valido.biografia == nueva_biografia
        assert usuario_valido.nombre_completo == nombre_original
    
    def test_puede_realizar_accion_usuario_activo(self, usuario_valido):
        """Test para verificar permisos de usuario activo"""
        assert usuario_valido.puede_realizar_accion("ver_perfil") is True
        assert usuario_valido.puede_realizar_accion("actualizar_perfil") is True
        assert usuario_valido.puede_realizar_accion("crear_producto") is True
        assert usuario_valido.puede_realizar_accion("ver_productos") is True
        assert usuario_valido.puede_realizar_accion("crear_orden") is True
        assert usuario_valido.puede_realizar_accion("accion_no_permitida") is False
    
    def test_puede_realizar_accion_usuario_inactivo(self, usuario_valido):
        """Test para verificar permisos de usuario inactivo"""
        usuario_valido.desactivar()
        
        assert usuario_valido.puede_realizar_accion("ver_perfil") is False
        assert usuario_valido.puede_realizar_accion("actualizar_perfil") is False
        assert usuario_valido.puede_realizar_accion("crear_producto") is False
        assert usuario_valido.puede_realizar_accion("ver_productos") is False
        assert usuario_valido.puede_realizar_accion("crear_orden") is False
        assert usuario_valido.puede_realizar_accion("accion_no_permitida") is False
    
    def test_puede_realizar_accion_superusuario(self, usuario_valido):
        """Test para verificar permisos de superusuario"""
        usuario_valido.promover_a_superusuario()
        
        # Superusuarios pueden hacer todo
        assert usuario_valido.puede_realizar_accion("ver_perfil") is True
        assert usuario_valido.puede_realizar_accion("actualizar_perfil") is True
        assert usuario_valido.puede_realizar_accion("crear_producto") is True
        assert usuario_valido.puede_realizar_accion("ver_productos") is True
        assert usuario_valido.puede_realizar_accion("crear_orden") is True
        assert usuario_valido.puede_realizar_accion("accion_no_permitida") is True
    
    def test_es_valido_usuario_completo(self, usuario_valido):
        """Test para verificar validez de usuario completo"""
        assert usuario_valido.es_valido() is True
    
    def test_es_valido_usuario_sin_email(self):
        """Test para verificar validez de usuario sin email"""
        usuario = Usuario(
            id=1,
            email=None,
            nombre_usuario=NombreUsuario("testuser"),
            contraseña=Contraseña("TestPass123!"),
            esta_activo=True
        )
        assert usuario.es_valido() is False
    
    def test_es_valido_usuario_sin_nombre_usuario(self):
        """Test para verificar validez de usuario sin nombre de usuario"""
        usuario = Usuario(
            id=1,
            email=Email("test@ejemplo.com"),
            nombre_usuario=None,
            contraseña=Contraseña("TestPass123!"),
            esta_activo=True
        )
        assert usuario.es_valido() is False
    
    def test_es_valido_usuario_inactivo(self, usuario_valido):
        """Test para verificar validez de usuario inactivo"""
        usuario_valido.desactivar()
        assert usuario_valido.es_valido() is False
    
    def test_str_representation(self, usuario_valido):
        """Test para representación string del usuario"""
        str_repr = str(usuario_valido)
        assert "Usuario" in str_repr
        assert "test@ejemplo.com" in str_repr
        assert "testuser" in str_repr
    
    def test_repr_representation(self, usuario_valido):
        """Test para representación detallada del usuario"""
        repr_str = repr(usuario_valido)
        assert "Usuario" in repr_str
        assert "test@ejemplo.com" in repr_str
        assert "testuser" in repr_str
        assert "esta_activo=True" in repr_str
    
    def test_fecha_creacion_automatica(self):
        """Test para verificar que la fecha de creación se asigna automáticamente"""
        usuario = Usuario(
            email=Email("test@ejemplo.com"),
            nombre_usuario=NombreUsuario("testuser"),
            contraseña=Contraseña("TestPass123!")
        )
        
        assert usuario.fecha_creacion is not None
        assert isinstance(usuario.fecha_creacion, datetime)
    
    def test_fecha_actualizacion_automatica(self):
        """Test para verificar que la fecha de actualización se asigna automáticamente"""
        usuario = Usuario(
            email=Email("test@ejemplo.com"),
            nombre_usuario=NombreUsuario("testuser"),
            contraseña=Contraseña("TestPass123!")
        )
        
        assert usuario.fecha_actualizacion is not None
        assert isinstance(usuario.fecha_actualizacion, datetime)
