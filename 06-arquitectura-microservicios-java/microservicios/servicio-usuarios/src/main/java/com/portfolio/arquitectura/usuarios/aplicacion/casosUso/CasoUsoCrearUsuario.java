package com.portfolio.arquitectura.usuarios.aplicacion.casosUso;

import com.portfolio.arquitectura.usuarios.dominio.entidad.Usuario;
import com.portfolio.arquitectura.usuarios.dominio.entidad.RolUsuario;
import com.portfolio.arquitectura.usuarios.dominio.entidad.EstadoUsuario;
import com.portfolio.arquitectura.usuarios.dominio.repositorio.RepositorioUsuario;
import com.portfolio.arquitectura.usuarios.dominio.objetoValor.CorreoElectronico;
import com.portfolio.arquitectura.usuarios.aplicacion.dto.SolicitudCrearUsuario;
import com.portfolio.arquitectura.usuarios.aplicacion.dto.RespuestaUsuario;
import com.portfolio.arquitectura.usuarios.aplicacion.mapeador.MapeadorUsuario;
import com.portfolio.arquitectura.usuarios.aplicacion.excepcion.UsuarioYaExisteExcepcion;
import com.portfolio.arquitectura.usuarios.aplicacion.excepcion.DatosUsuarioInvalidosExcepcion;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Caso de Uso para Crear un Nuevo Usuario
 * 
 * Implementa la lógica de negocio para la creación de usuarios,
 * incluyendo validaciones, encriptación de contraseña y notificaciones.
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class CasoUsoCrearUsuario {

    private final RepositorioUsuario repositorioUsuario;
    private final PasswordEncoder codificadorContrasena;
    private final MapeadorUsuario mapeadorUsuario;
    private final PublicadorEventoUsuario publicadorEventoUsuario;

    /**
     * Crea un nuevo usuario en el sistema
     * 
     * @param solicitud Datos del usuario a crear
     * @return Usuario creado
     * @throws UsuarioYaExisteExcepcion si el usuario ya existe
     * @throws DatosUsuarioInvalidosExcepcion si los datos son inválidos
     */
    public RespuestaUsuario ejecutar(SolicitudCrearUsuario solicitud) {
        log.info("Iniciando creación de usuario con correo: {}", solicitud.getCorreoElectronico());

        // Validar datos de entrada
        validarSolicitud(solicitud);

        // Crear correo electrónico objeto valor
        CorreoElectronico correo = CorreoElectronico.de(solicitud.getCorreoElectronico());

        // Verificar si el usuario ya existe
        if (repositorioUsuario.existePorCorreo(correo)) {
            log.warn("Intento de crear usuario con correo existente: {}", solicitud.getCorreoElectronico());
            throw new UsuarioYaExisteExcepcion("Ya existe un usuario con el correo: " + solicitud.getCorreoElectronico());
        }

        if (repositorioUsuario.existePorNombreUsuario(solicitud.getNombreUsuario())) {
            log.warn("Intento de crear usuario con nombre de usuario existente: {}", solicitud.getNombreUsuario());
            throw new UsuarioYaExisteExcepcion("Ya existe un usuario con el nombre de usuario: " + solicitud.getNombreUsuario());
        }

        // Crear entidad usuario
        Usuario usuario = Usuario.builder()
                .correoElectronico(correo.getValor())
                .nombreUsuario(solicitud.getNombreUsuario())
                .contrasena(codificadorContrasena.encode(solicitud.getContrasena()))
                .nombre(solicitud.getNombre())
                .apellido(solicitud.getApellido())
                .numeroTelefono(solicitud.getNumeroTelefono())
                .estado(EstadoUsuario.PENDIENTE_VERIFICACION)
                .rol(determinarRolUsuario(solicitud))
                .correoVerificado(false)
                .build();

        // Guardar usuario
        Usuario usuarioGuardado = repositorioUsuario.guardar(usuario);
        log.info("Usuario creado exitosamente con ID: {}", usuarioGuardado.getId());

        // Publicar evento de usuario creado
        publicadorEventoUsuario.publicarUsuarioCreado(usuarioGuardado);

        // Enviar correo de verificación
        publicadorEventoUsuario.publicarSolicitudVerificacionCorreo(usuarioGuardado);

        return mapeadorUsuario.aRespuesta(usuarioGuardado);
    }

    /**
     * Valida los datos de entrada
     */
    private void validarSolicitud(SolicitudCrearUsuario solicitud) {
        if (solicitud == null) {
            throw new DatosUsuarioInvalidosExcepcion("Solicitud no puede ser nula");
        }

        if (solicitud.getCorreoElectronico() == null || solicitud.getCorreoElectronico().trim().isEmpty()) {
            throw new DatosUsuarioInvalidosExcepcion("Correo electrónico es requerido");
        }

        if (solicitud.getNombreUsuario() == null || solicitud.getNombreUsuario().trim().isEmpty()) {
            throw new DatosUsuarioInvalidosExcepcion("Nombre de usuario es requerido");
        }

        if (solicitud.getContrasena() == null || solicitud.getContrasena().length() < 8) {
            throw new DatosUsuarioInvalidosExcepcion("Contraseña debe tener al menos 8 caracteres");
        }

        if (solicitud.getNombre() == null || solicitud.getNombre().trim().isEmpty()) {
            throw new DatosUsuarioInvalidosExcepcion("Nombre es requerido");
        }

        if (solicitud.getApellido() == null || solicitud.getApellido().trim().isEmpty()) {
            throw new DatosUsuarioInvalidosExcepcion("Apellido es requerido");
        }

        // Validar formato de nombre de usuario
        if (!solicitud.getNombreUsuario().matches("^[a-zA-Z0-9_]{3,20}$")) {
            throw new DatosUsuarioInvalidosExcepcion("Nombre de usuario debe contener solo letras, números y guiones bajos, entre 3 y 20 caracteres");
        }
    }

    /**
     * Determina el rol del usuario basado en el contexto
     */
    private RolUsuario determinarRolUsuario(SolicitudCrearUsuario solicitud) {
        // Por defecto, todos los usuarios son CLIENTE
        // En un sistema real, esto podría basarse en:
        // - Código de invitación
        // - Dominio de correo electrónico
        // - Configuración del sistema
        return RolUsuario.CLIENTE;
    }
}
