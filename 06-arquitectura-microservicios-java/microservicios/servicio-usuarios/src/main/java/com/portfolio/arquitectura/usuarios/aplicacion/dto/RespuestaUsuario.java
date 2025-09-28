package com.portfolio.arquitectura.usuarios.aplicacion.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * DTO para la respuesta de usuario
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RespuestaUsuario {

    private UUID id;
    private String correoElectronico;
    private String nombreUsuario;
    private String nombre;
    private String apellido;
    private String numeroTelefono;
    private String estado;
    private String rol;
    private Boolean correoVerificado;
    private LocalDateTime fechaCreacion;
    private LocalDateTime fechaActualizacion;
    private LocalDateTime ultimoAcceso;
}
