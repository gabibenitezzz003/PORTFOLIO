package com.portfolio.arquitectura.usuarios.aplicacion.excepcion;

/**
 * Excepción lanzada cuando se intenta crear un usuario que ya existe
 * 
 * @author Gabriel - Arquitecto de Software
 */
public class UsuarioYaExisteExcepcion extends RuntimeException {

    public UsuarioYaExisteExcepcion(String mensaje) {
        super(mensaje);
    }

    public UsuarioYaExisteExcepcion(String mensaje, Throwable causa) {
        super(mensaje, causa);
    }
}
