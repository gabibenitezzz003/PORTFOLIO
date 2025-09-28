"""
Tests para Casos de Uso - Capa de Aplicación
Tests unitarios para casos de uso de la aplicación
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from aplicacion.casos_uso.caso_uso_crear_usuario import CasoUsoCrearUsuario
from aplicacion.dto.crear_usuario_dto import CrearUsuarioDTO
from aplicacion.dto.usuario_dto import UsuarioDTO
from aplicacion.excepciones.excepciones_aplicacion import (
    EmailYaExisteError,
    NombreUsuarioYaExisteError,
    ErrorValidacionError
)
from dominio.entidades.usuario import Usuario
from dominio.value_objects.email import Email
from dominio.value_objects.nombre_usuario import NombreUsuario
from dominio.value_objects.contraseña import Contraseña


class TestCasoUsoCrearUsuario:
    """Tests para el caso de uso de crear usuario"""
    
    @pytest.fixture
    def repositorio_mock(self):
        """Mock del repositorio de usuarios"""
        repositorio = AsyncMock()
        repositorio.existe_email.return_value = False
        repositorio.existe_nombre_usuario.return_value = False
        repositorio.guardar.return_value = Usuario(
            id=1,
            email=Email("test@ejemplo.com"),
            nombre_usuario=NombreUsuario("testuser"),
            contraseña=Contraseña("TestPass123!"),
            nombre_completo="Usuario Test",
            biografia="Biografía de prueba",
            esta_activo=True,
            es_superusuario=False,
            fecha_creacion=datetime.utcnow()
        )
        return repositorio
    
    @pytest.fixture
    def servicio_autenticacion_mock(self):
        """Mock del servicio de autenticación"""
        return AsyncMock()
    
    @pytest.fixture
    def caso_uso(self, repositorio_mock, servicio_autenticacion_mock):
        """Instancia del caso de uso"""
        return CasoUsoCrearUsuario(
            repositorio_usuario=repositorio_mock,
            servicio_autenticacion=servicio_autenticacion_mock
        )
    
    @pytest.fixture
    def datos_usuario_validos(self):
        """Datos válidos para crear usuario"""
        return CrearUsuarioDTO(
            email="test@ejemplo.com",
            nombre_usuario="testuser",
            contraseña="TestPass123!",
            nombre_completo="Usuario Test",
            biografia="Biografía de prueba"
        )
    
    @pytest.mark.asyncio
    async def test_crear_usuario_exitoso(self, caso_uso, datos_usuario_validos, repositorio_mock):
        """Test para crear usuario exitosamente"""
        # Ejecutar caso de uso
        resultado = await caso_uso.ejecutar(datos_usuario_validos)
        
        # Verificar resultado
        assert isinstance(resultado, UsuarioDTO)
        assert resultado.email == "test@ejemplo.com"
        assert resultado.nombre_usuario == "testuser"
        assert resultado.nombre_completo == "Usuario Test"
        assert resultado.esta_activo is True
        
        # Verificar que se llamaron los métodos del repositorio
        repositorio_mock.existe_email.assert_called_once()
        repositorio_mock.existe_nombre_usuario.assert_called_once()
        repositorio_mock.guardar.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_crear_usuario_email_ya_existe(self, caso_uso, datos_usuario_validos, repositorio_mock):
        """Test para crear usuario con email ya existente"""
        # Configurar mock para que el email ya existe
        repositorio_mock.existe_email.return_value = True
        
        # Ejecutar caso de uso y verificar excepción
        with pytest.raises(EmailYaExisteError):
            await caso_uso.ejecutar(datos_usuario_validos)
        
        # Verificar que se llamó existe_email pero no guardar
        repositorio_mock.existe_email.assert_called_once()
        repositorio_mock.guardar.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_crear_usuario_nombre_ya_existe(self, caso_uso, datos_usuario_validos, repositorio_mock):
        """Test para crear usuario con nombre de usuario ya existente"""
        # Configurar mock para que el nombre de usuario ya existe
        repositorio_mock.existe_nombre_usuario.return_value = True
        
        # Ejecutar caso de uso y verificar excepción
        with pytest.raises(NombreUsuarioYaExisteError):
            await caso_uso.ejecutar(datos_usuario_validos)
        
        # Verificar que se llamaron los métodos de verificación
        repositorio_mock.existe_email.assert_called_once()
        repositorio_mock.existe_nombre_usuario.assert_called_once()
        repositorio_mock.guardar.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_crear_usuario_datos_invalidos(self, caso_uso):
        """Test para crear usuario con datos inválidos"""
        # Datos inválidos (email vacío)
        datos_invalidos = CrearUsuarioDTO(
            email="",
            nombre_usuario="testuser",
            contraseña="TestPass123!",
            nombre_completo="Usuario Test"
        )
        
        # Ejecutar caso de uso y verificar excepción
        with pytest.raises(ErrorValidacionError):
            await caso_uso.ejecutar(datos_invalidos)
    
    @pytest.mark.asyncio
    async def test_crear_usuario_contraseña_debil(self, caso_uso):
        """Test para crear usuario con contraseña débil"""
        # Datos con contraseña débil
        datos_contraseña_debil = CrearUsuarioDTO(
            email="test@ejemplo.com",
            nombre_usuario="testuser",
            contraseña="123",  # Contraseña muy débil
            nombre_completo="Usuario Test"
        )
        
        # Ejecutar caso de uso y verificar excepción
        with pytest.raises(ErrorValidacionError):
            await caso_uso.ejecutar(datos_contraseña_debil)
    
    @pytest.mark.asyncio
    async def test_crear_usuario_nombre_usuario_invalido(self, caso_uso):
        """Test para crear usuario con nombre de usuario inválido"""
        # Datos con nombre de usuario inválido
        datos_nombre_invalido = CrearUsuarioDTO(
            email="test@ejemplo.com",
            nombre_usuario="",  # Nombre vacío
            contraseña="TestPass123!",
            nombre_completo="Usuario Test"
        )
        
        # Ejecutar caso de uso y verificar excepción
        with pytest.raises(ErrorValidacionError):
            await caso_uso.ejecutar(datos_nombre_invalido)
    
    @pytest.mark.asyncio
    async def test_crear_usuario_solo_datos_obligatorios(self, caso_uso, repositorio_mock):
        """Test para crear usuario solo con datos obligatorios"""
        # Datos mínimos
        datos_minimos = CrearUsuarioDTO(
            email="test@ejemplo.com",
            nombre_usuario="testuser",
            contraseña="TestPass123!"
        )
        
        # Ejecutar caso de uso
        resultado = await caso_uso.ejecutar(datos_minimos)
        
        # Verificar resultado
        assert isinstance(resultado, UsuarioDTO)
        assert resultado.email == "test@ejemplo.com"
        assert resultado.nombre_usuario == "testuser"
        assert resultado.nombre_completo is None
        assert resultado.biografia is None
        assert resultado.esta_activo is True
