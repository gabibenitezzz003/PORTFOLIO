package com.portfolio.arquitectura.usuarios;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;

/**
 * Aplicación Principal del Servicio de Usuarios
 * 
 * Microservicio de gestión de usuarios implementando Clean Architecture,
 * principios SOLID y patrones de diseño modernos.
 * 
 * @author Gabriel - Arquitecto de Software
 * @version 1.0.0
 */
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
public class ServicioUsuariosAplicacion {

    public static void main(String[] args) {
        SpringApplication.run(ServicioUsuariosAplicacion.class, args);
    }
}
