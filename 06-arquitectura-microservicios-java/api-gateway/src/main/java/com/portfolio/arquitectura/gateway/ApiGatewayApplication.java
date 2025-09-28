package com.portfolio.arquitectura.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

/**
 * API Gateway Principal
 * 
 * Punto de entrada único para todos los microservicios.
 * Implementa enrutamiento, filtros de seguridad, rate limiting,
 * circuit breakers y observabilidad.
 * 
 * @author Gabriel - Arquitecto de Software
 * @version 1.0.0
 */
@SpringBootApplication
@EnableDiscoveryClient
public class ApiGatewayApplication {

    public static void main(String[] args) {
        SpringApplication.run(ApiGatewayApplication.class, args);
    }
}
