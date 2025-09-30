package com.portfolio.arquitectura.usuarios.aplicacion.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * DTO para la solicitud de creación de usuario
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SolicitudCrearUsuario {

    @NotBlank(message = "Correo electrónico es requerido")
    @Email(message = "Formato de correo electrónico inválido")
    private String correoElectronico;

    @NotBlank(message = "Nombre de usuario es requerido")
    @Size(min = 3, max = 20, message = "Nombre de usuario debe tener entre 3 y 20 caracteres")
    private String nombreUsuario;

    @NotBlank(message = "Contraseña es requerida")
    @Size(min = 8, message = "Contraseña debe tener al menos 8 caracteres")
    private String contrasena;

    @NotBlank(message = "Nombre es requerido")
    private String nombre;

    @NotBlank(message = "Apellido es requerido")
    private String apellido;

    private String numeroTelefono;
}
