package com.portfolio.arquitectura.users.domain.valueobject;

import lombok.EqualsAndHashCode;
import lombok.Getter;

import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;
import java.util.regex.Pattern;

/**
 * Value Object para Email
 * 
 * Implementa validación de email y encapsula la lógica de negocio
 * relacionada con direcciones de correo electrónico.
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Getter
@EqualsAndHashCode
public class Email {

    private static final Pattern EMAIL_PATTERN = Pattern.compile(
        "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    );

    @NotBlank
    @Email
    private final String value;

    /**
     * Constructor privado para crear instancias válidas
     * 
     * @param email Dirección de email
     * @throws IllegalArgumentException si el email no es válido
     */
    private Email(String email) {
        if (email == null || email.trim().isEmpty()) {
            throw new IllegalArgumentException("Email no puede ser nulo o vacío");
        }
        
        String trimmedEmail = email.trim().toLowerCase();
        
        if (!EMAIL_PATTERN.matcher(trimmedEmail).matches()) {
            throw new IllegalArgumentException("Formato de email inválido: " + email);
        }
        
        this.value = trimmedEmail;
    }

    /**
     * Factory method para crear un Email válido
     * 
     * @param email Dirección de email
     * @return Instancia de Email
     * @throws IllegalArgumentException si el email no es válido
     */
    public static Email of(String email) {
        return new Email(email);
    }

    /**
     * Verifica si el email es de un dominio específico
     * 
     * @param domain Dominio a verificar
     * @return true si el email es del dominio especificado
     */
    public boolean isFromDomain(String domain) {
        return value.endsWith("@" + domain.toLowerCase());
    }

    /**
     * Obtiene el dominio del email
     * 
     * @return Dominio del email
     */
    public String getDomain() {
        int atIndex = value.indexOf('@');
        return atIndex > 0 ? value.substring(atIndex + 1) : "";
    }

    /**
     * Obtiene la parte local del email (antes del @)
     * 
     * @return Parte local del email
     */
    public String getLocalPart() {
        int atIndex = value.indexOf('@');
        return atIndex > 0 ? value.substring(0, atIndex) : value;
    }

    /**
     * Verifica si el email es un email corporativo
     * 
     * @return true si es un email corporativo
     */
    public boolean isCorporateEmail() {
        String[] corporateDomains = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com"
        };
        
        for (String domain : corporateDomains) {
            if (isFromDomain(domain)) {
                return false;
            }
        }
        
        return true;
    }

    @Override
    public String toString() {
        return value;
    }
}
