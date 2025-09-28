package com.portfolio.arquitectura.usuarios.aplicacion.excepcion;

/**
 * Excepción lanzada cuando los datos del usuario son inválidos
 * 
 * @author Gabriel - Arquitecto de Software
 */
public class DatosUsuarioInvalidosExcepcion extends RuntimeException {

    public DatosUsuarioInvalidosExcepcion(String mensaje) {
        super(mensaje);
    }

    public DatosUsuarioInvalidosExcepcion(String mensaje, Throwable causa) {
        super(mensaje, causa);
    }
}
