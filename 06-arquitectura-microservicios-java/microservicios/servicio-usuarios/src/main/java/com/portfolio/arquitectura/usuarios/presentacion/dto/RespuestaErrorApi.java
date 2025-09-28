package com.portfolio.arquitectura.usuarios.presentacion.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO para errores de la API
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RespuestaErrorApi {

    private String codigo;
    private String mensaje;
    private String detalles;
}
