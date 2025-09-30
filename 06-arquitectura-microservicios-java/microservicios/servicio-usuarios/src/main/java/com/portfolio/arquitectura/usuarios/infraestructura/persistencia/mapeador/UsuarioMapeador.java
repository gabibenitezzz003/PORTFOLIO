package com.portfolio.arquitectura.usuarios.infraestructura.persistencia.mapeador;

import com.portfolio.arquitectura.usuarios.dominio.entidad.Usuario;
import com.portfolio.arquitectura.usuarios.dominio.objetoValor.CorreoElectronico;
import com.portfolio.arquitectura.usuarios.infraestructura.persistencia.entidad.UsuarioEntidad;
import org.springframework.stereotype.Component;

/**
 * Mapeador entre entidades de dominio y entidades JPA
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Component
public class UsuarioMapeador {

    /**
     * Convierte entidad de dominio a entidad JPA
     */
    public UsuarioEntidad aEntidad(Usuario usuario) {
        return UsuarioEntidad.builder()
                .id(usuario.getId())
                .correoElectronico(usuario.getCorreoElectronico().toString())
                .nombreUsuario(usuario.getNombreUsuario())
                .nombre(usuario.getNombre())
                .apellido(usuario.getApellido())
                .numeroTelefono(usuario.getNumeroTelefono())
                .estado(usuario.getEstado())
                .rol(usuario.getRol())
                .correoVerificado(usuario.getCorreoVerificado())
                .fechaCreacion(usuario.getFechaCreacion())
                .fechaActualizacion(usuario.getFechaActualizacion())
                .ultimoAcceso(usuario.getUltimoAcceso())
                .build();
    }

    /**
     * Convierte entidad JPA a entidad de dominio
     */
    public Usuario aDominio(UsuarioEntidad entidad) {
        return Usuario.builder()
                .id(entidad.getId())
                .correoElectronico(CorreoElectronico.de(entidad.getCorreoElectronico()))
                .nombreUsuario(entidad.getNombreUsuario())
                .nombre(entidad.getNombre())
                .apellido(entidad.getApellido())
                .numeroTelefono(entidad.getNumeroTelefono())
                .estado(entidad.getEstado())
                .rol(entidad.getRol())
                .correoVerificado(entidad.getCorreoVerificado())
                .fechaCreacion(entidad.getFechaCreacion())
                .fechaActualizacion(entidad.getFechaActualizacion())
                .ultimoAcceso(entidad.getUltimoAcceso())
                .build();
    }
}
