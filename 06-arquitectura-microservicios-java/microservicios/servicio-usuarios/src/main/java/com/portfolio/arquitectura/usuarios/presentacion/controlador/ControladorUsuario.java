package com.portfolio.arquitectura.usuarios.presentacion.controlador;

import com.portfolio.arquitectura.usuarios.aplicacion.casosUso.CasoUsoCrearUsuario;
import com.portfolio.arquitectura.usuarios.aplicacion.dto.SolicitudCrearUsuario;
import com.portfolio.arquitectura.usuarios.aplicacion.dto.RespuestaUsuario;
import com.portfolio.arquitectura.usuarios.aplicacion.excepcion.UsuarioYaExisteExcepcion;
import com.portfolio.arquitectura.usuarios.aplicacion.excepcion.DatosUsuarioInvalidosExcepcion;
import com.portfolio.arquitectura.usuarios.presentacion.dto.RespuestaApi;
import com.portfolio.arquitectura.usuarios.presentacion.dto.RespuestaErrorApi;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;

/**
 * Controlador REST para la gestión de usuarios
 * 
 * @author Gabriel - Arquitecto de Software
 */
@RestController
@RequestMapping("/api/usuarios")
@RequiredArgsConstructor
@Slf4j
public class ControladorUsuario {

    private final CasoUsoCrearUsuario casoUsoCrearUsuario;

    /**
     * Crea un nuevo usuario
     * 
     * @param solicitud Datos del usuario a crear
     * @return Usuario creado
     */
    @PostMapping
    public ResponseEntity<RespuestaApi<RespuestaUsuario>> crearUsuario(
            @Valid @RequestBody SolicitudCrearUsuario solicitud) {
        
        try {
            log.info("Recibida solicitud para crear usuario: {}", solicitud.getCorreoElectronico());
            
            RespuestaUsuario usuario = casoUsoCrearUsuario.ejecutar(solicitud);
            
            RespuestaApi<RespuestaUsuario> respuesta = RespuestaApi.<RespuestaUsuario>builder()
                    .exito(true)
                    .mensaje("Usuario creado exitosamente")
                    .datos(usuario)
                    .build();
            
            return ResponseEntity.status(HttpStatus.CREATED).body(respuesta);
            
        } catch (UsuarioYaExisteExcepcion e) {
            log.warn("Error al crear usuario: {}", e.getMessage());
            
            RespuestaErrorApi error = RespuestaErrorApi.builder()
                    .codigo("USUARIO_YA_EXISTE")
                    .mensaje(e.getMessage())
                    .build();
            
            RespuestaApi<RespuestaUsuario> respuesta = RespuestaApi.<RespuestaUsuario>builder()
                    .exito(false)
                    .mensaje("Error al crear usuario")
                    .error(error)
                    .build();
            
            return ResponseEntity.status(HttpStatus.CONFLICT).body(respuesta);
            
        } catch (DatosUsuarioInvalidosExcepcion e) {
            log.warn("Error de validación al crear usuario: {}", e.getMessage());
            
            RespuestaErrorApi error = RespuestaErrorApi.builder()
                    .codigo("DATOS_INVALIDOS")
                    .mensaje(e.getMessage())
                    .build();
            
            RespuestaApi<RespuestaUsuario> respuesta = RespuestaApi.<RespuestaUsuario>builder()
                    .exito(false)
                    .mensaje("Error de validación")
                    .error(error)
                    .build();
            
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(respuesta);
            
        } catch (Exception e) {
            log.error("Error inesperado al crear usuario", e);
            
            RespuestaErrorApi error = RespuestaErrorApi.builder()
                    .codigo("ERROR_INTERNO")
                    .mensaje("Error interno del servidor")
                    .build();
            
            RespuestaApi<RespuestaUsuario> respuesta = RespuestaApi.<RespuestaUsuario>builder()
                    .exito(false)
                    .mensaje("Error interno del servidor")
                    .error(error)
                    .build();
            
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(respuesta);
        }
    }

    /**
     * Health check del servicio
     * 
     * @return Estado del servicio
     */
    @GetMapping("/health")
    public ResponseEntity<RespuestaApi<String>> healthCheck() {
        RespuestaApi<String> respuesta = RespuestaApi.<String>builder()
                .exito(true)
                .mensaje("Servicio de usuarios funcionando correctamente")
                .datos("OK")
                .build();
        
        return ResponseEntity.ok(respuesta);
    }
}
