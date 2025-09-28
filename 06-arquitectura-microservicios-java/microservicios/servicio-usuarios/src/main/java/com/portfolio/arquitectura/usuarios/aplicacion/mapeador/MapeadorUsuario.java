package com.portfolio.arquitectura.usuarios.aplicacion.mapeador;

import com.portfolio.arquitectura.usuarios.dominio.entidad.Usuario;
import com.portfolio.arquitectura.usuarios.aplicacion.dto.RespuestaUsuario;
import com.portfolio.arquitectura.usuarios.aplicacion.dto.SolicitudCrearUsuario;
import org.springframework.stereotype.Component;

/**
 * Mapeador para convertir entre entidades de dominio y DTOs
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Component
public class MapeadorUsuario {

    /**
     * Convierte una entidad Usuario a RespuestaUsuario
     */
    public RespuestaUsuario aRespuesta(Usuario usuario) {
        return RespuestaUsuario.builder()
                .id(usuario.getId())
                .correoElectronico(usuario.getCorreoElectronico())
                .nombreUsuario(usuario.getNombreUsuario())
                .nombre(usuario.getNombre())
                .apellido(usuario.getApellido())
                .numeroTelefono(usuario.getNumeroTelefono())
                .estado(usuario.getEstado().name())
                .rol(usuario.getRol().name())
                .correoVerificado(usuario.getCorreoVerificado())
                .fechaCreacion(usuario.getFechaCreacion())
                .fechaActualizacion(usuario.getFechaActualizacion())
                .ultimoAcceso(usuario.getUltimoAcceso())
                .build();
    }

    /**
     * Convierte una SolicitudCrearUsuario a entidad Usuario
     */
    public Usuario aEntidad(SolicitudCrearUsuario solicitud) {
        return Usuario.builder()
                .correoElectronico(solicitud.getCorreoElectronico())
                .nombreUsuario(solicitud.getNombreUsuario())
                .nombre(solicitud.getNombre())
                .apellido(solicitud.getApellido())
                .numeroTelefono(solicitud.getNumeroTelefono())
                .build();
    }
}
