package com.portfolio.arquitectura.usuarios.dominio.objetoValor;

import lombok.EqualsAndHashCode;
import lombok.Getter;

import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;
import java.util.regex.Pattern;

/**
 * Objeto Valor para Correo Electrónico
 * 
 * Implementa validación de correo electrónico y encapsula la lógica de negocio
 * relacionada con direcciones de correo electrónico.
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Getter
@EqualsAndHashCode
public class CorreoElectronico {

    private static final Pattern PATRON_CORREO = Pattern.compile(
        "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    );

    @NotBlank
    @Email
    private final String valor;

    /**
     * Constructor privado para crear instancias válidas
     * 
     * @param correo Dirección de correo electrónico
     * @throws IllegalArgumentException si el correo no es válido
     */
    private CorreoElectronico(String correo) {
        if (correo == null || correo.trim().isEmpty()) {
            throw new IllegalArgumentException("Correo electrónico no puede ser nulo o vacío");
        }
        
        String correoLimpio = correo.trim().toLowerCase();
        
        if (!PATRON_CORREO.matcher(correoLimpio).matches()) {
            throw new IllegalArgumentException("Formato de correo electrónico inválido: " + correo);
        }
        
        this.valor = correoLimpio;
    }

    /**
     * Método de fábrica para crear un CorreoElectronico válido
     * 
     * @param correo Dirección de correo electrónico
     * @return Instancia de CorreoElectronico
     * @throws IllegalArgumentException si el correo no es válido
     */
    public static CorreoElectronico de(String correo) {
        return new CorreoElectronico(correo);
    }

    /**
     * Verifica si el correo es de un dominio específico
     * 
     * @param dominio Dominio a verificar
     * @return true si el correo es del dominio especificado
     */
    public boolean esDelDominio(String dominio) {
        return valor.endsWith("@" + dominio.toLowerCase());
    }

    /**
     * Obtiene el dominio del correo electrónico
     * 
     * @return Dominio del correo electrónico
     */
    public String obtenerDominio() {
        int indiceArroba = valor.indexOf('@');
        return indiceArroba > 0 ? valor.substring(indiceArroba + 1) : "";
    }

    /**
     * Obtiene la parte local del correo (antes del @)
     * 
     * @return Parte local del correo electrónico
     */
    public String obtenerParteLocal() {
        int indiceArroba = valor.indexOf('@');
        return indiceArroba > 0 ? valor.substring(0, indiceArroba) : valor;
    }

    /**
     * Verifica si el correo es un correo corporativo
     * 
     * @return true si es un correo corporativo
     */
    public boolean esCorreoCorporativo() {
        String[] dominiosCorporativos = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com"
        };
        
        for (String dominio : dominiosCorporativos) {
            if (esDelDominio(dominio)) {
                return false;
            }
        }
        
        return true;
    }

    @Override
    public String toString() {
        return valor;
    }
}
