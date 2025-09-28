package com.portfolio.arquitectura.usuarios.dominio.entidad;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entidad Usuario - Capa de Dominio
 * 
 * Representa un usuario en el sistema de e-commerce.
 * Implementa los principios de DDD con agregados bien definidos.
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Entity
@Table(name = "usuarios")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Usuario {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private UUID id;

    @Column(unique = true, nullable = false)
    private String correoElectronico;

    @Column(unique = true, nullable = false)
    private String nombreUsuario;

    @Column(nullable = false)
    private String contrasena;

    @Column(name = "nombre", nullable = false)
    private String nombre;

    @Column(name = "apellido", nullable = false)
    private String apellido;

    @Column(name = "numero_telefono")
    private String numeroTelefono;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private EstadoUsuario estado;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RolUsuario rol;

    @Column(name = "correo_verificado")
    private Boolean correoVerificado;

    @Column(name = "fecha_creacion", nullable = false)
    private LocalDateTime fechaCreacion;

    @Column(name = "fecha_actualizacion")
    private LocalDateTime fechaActualizacion;

    @Column(name = "ultimo_acceso")
    private LocalDateTime ultimoAcceso;

    @PrePersist
    protected void alCrear() {
        fechaCreacion = LocalDateTime.now();
        fechaActualizacion = LocalDateTime.now();
        if (estado == null) {
            estado = EstadoUsuario.ACTIVO;
        }
        if (rol == null) {
            rol = RolUsuario.CLIENTE;
        }
        if (correoVerificado == null) {
            correoVerificado = false;
        }
    }

    @PreUpdate
    protected void alActualizar() {
        fechaActualizacion = LocalDateTime.now();
    }

    /**
     * Verifica si el usuario está activo
     */
    public boolean estaActivo() {
        return EstadoUsuario.ACTIVO.equals(this.estado);
    }

    /**
     * Verifica si el usuario es administrador
     */
    public boolean esAdministrador() {
        return RolUsuario.ADMINISTRADOR.equals(this.rol);
    }

    /**
     * Verifica si el usuario es vendedor
     */
    public boolean esVendedor() {
        return RolUsuario.VENDEDOR.equals(this.rol);
    }

    /**
     * Actualiza el último acceso
     */
    public void actualizarUltimoAcceso() {
        this.ultimoAcceso = LocalDateTime.now();
    }

    /**
     * Marca el correo como verificado
     */
    public void verificarCorreo() {
        this.correoVerificado = true;
    }

    /**
     * Desactiva el usuario
     */
    public void desactivar() {
        this.estado = EstadoUsuario.INACTIVO;
    }

    /**
     * Activa el usuario
     */
    public void activar() {
        this.estado = EstadoUsuario.ACTIVO;
    }
}
