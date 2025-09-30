package com.portfolio.arquitectura.usuarios.aplicacion.servicios;

import com.portfolio.arquitectura.usuarios.dominio.entidad.Usuario;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

/**
 * Servicio para publicar eventos de usuario
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class PublicadorEventoUsuario {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    /**
     * Publica evento de usuario creado
     */
    public void publicarUsuarioCreado(Usuario usuario) {
        try {
            EventoUsuarioCreado evento = EventoUsuarioCreado.builder()
                    .usuarioId(usuario.getId().toString())
                    .correoElectronico(usuario.getCorreoElectronico().toString())
                    .nombreUsuario(usuario.getNombreUsuario())
                    .nombre(usuario.getNombre())
                    .apellido(usuario.getApellido())
                    .rol(usuario.getRol().name())
                    .fechaCreacion(usuario.getFechaCreacion())
                    .build();

            kafkaTemplate.send("usuario-creado", evento);
            log.info("Evento usuario creado publicado: {}", usuario.getId());

        } catch (Exception e) {
            log.error("Error publicando evento usuario creado: {}", e.getMessage(), e);
        }
    }

    /**
     * Publica solicitud de verificación de correo
     */
    public void publicarSolicitudVerificacionCorreo(Usuario usuario) {
        try {
            EventoSolicitudVerificacionCorreo evento = EventoSolicitudVerificacionCorreo.builder()
                    .usuarioId(usuario.getId().toString())
                    .correoElectronico(usuario.getCorreoElectronico().toString())
                    .nombreUsuario(usuario.getNombreUsuario())
                    .fechaCreacion(usuario.getFechaCreacion())
                    .build();

            kafkaTemplate.send("solicitud-verificacion-correo", evento);
            log.info("Evento solicitud verificación correo publicado: {}", usuario.getId());

        } catch (Exception e) {
            log.error("Error publicando evento solicitud verificación correo: {}", e.getMessage(), e);
        }
    }

    /**
     * Evento de usuario creado
     */
    @lombok.Data
    @lombok.Builder
    public static class EventoUsuarioCreado {
        private String usuarioId;
        private String correoElectronico;
        private String nombreUsuario;
        private String nombre;
        private String apellido;
        private String rol;
        private java.time.LocalDateTime fechaCreacion;
    }

    /**
     * Evento de solicitud de verificación de correo
     */
    @lombok.Data
    @lombok.Builder
    public static class EventoSolicitudVerificacionCorreo {
        private String usuarioId;
        private String correoElectronico;
        private String nombreUsuario;
        private java.time.LocalDateTime fechaCreacion;
    }
}
