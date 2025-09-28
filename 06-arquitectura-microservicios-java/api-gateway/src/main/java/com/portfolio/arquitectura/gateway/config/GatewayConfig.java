package com.portfolio.arquitectura.gateway.config;

import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Configuración del API Gateway
 * 
 * Define las rutas, filtros y políticas de enrutamiento
 * para todos los microservicios del sistema.
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Configuration
public class GatewayConfig {

    /**
     * Configuración de rutas del API Gateway
     * 
     * @param builder Builder para crear rutas
     * @return RouteLocator configurado
     */
    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
                // Ruta para el servicio de usuarios
                .route("user-service", r -> r
                        .path("/api/users/**")
                        .filters(f -> f
                                .stripPrefix(2)
                                .addRequestHeader("X-Gateway-Source", "api-gateway")
                                .circuitBreaker(config -> config
                                        .setName("user-service-cb")
                                        .setFallbackUri("forward:/fallback/user-service")
                                )
                                .requestRateLimiter(config -> config
                                        .setRateLimiter(redisRateLimiter())
                                        .setKeyResolver(userKeyResolver())
                                )
                        )
                        .uri("lb://user-service")
                )
                
                // Ruta para el servicio de órdenes
                .route("order-service", r -> r
                        .path("/api/orders/**")
                        .filters(f -> f
                                .stripPrefix(2)
                                .addRequestHeader("X-Gateway-Source", "api-gateway")
                                .circuitBreaker(config -> config
                                        .setName("order-service-cb")
                                        .setFallbackUri("forward:/fallback/order-service")
                                )
                                .requestRateLimiter(config -> config
                                        .setRateLimiter(redisRateLimiter())
                                        .setKeyResolver(userKeyResolver())
                                )
                        )
                        .uri("lb://order-service")
                )
                
                // Ruta para el servicio de pagos
                .route("payment-service", r -> r
                        .path("/api/payments/**")
                        .filters(f -> f
                                .stripPrefix(2)
                                .addRequestHeader("X-Gateway-Source", "api-gateway")
                                .circuitBreaker(config -> config
                                        .setName("payment-service-cb")
                                        .setFallbackUri("forward:/fallback/payment-service")
                                )
                                .requestRateLimiter(config -> config
                                        .setRateLimiter(redisRateLimiter())
                                        .setKeyResolver(userKeyResolver())
                                )
                        )
                        .uri("lb://payment-service")
                )
                
                // Ruta para el servicio de catálogo
                .route("catalog-service", r -> r
                        .path("/api/catalog/**")
                        .filters(f -> f
                                .stripPrefix(2)
                                .addRequestHeader("X-Gateway-Source", "api-gateway")
                                .circuitBreaker(config -> config
                                        .setName("catalog-service-cb")
                                        .setFallbackUri("forward:/fallback/catalog-service")
                                )
                        )
                        .uri("lb://catalog-service")
                )
                
                // Ruta para el servicio de inventario
                .route("inventory-service", r -> r
                        .path("/api/inventory/**")
                        .filters(f -> f
                                .stripPrefix(2)
                                .addRequestHeader("X-Gateway-Source", "api-gateway")
                                .circuitBreaker(config -> config
                                        .setName("inventory-service-cb")
                                        .setFallbackUri("forward:/fallback/inventory-service")
                                )
                        )
                        .uri("lb://inventory-service")
                )
                
                // Ruta para el servicio de notificaciones (WebSocket)
                .route("notification-service", r -> r
                        .path("/ws/**")
                        .filters(f -> f
                                .stripPrefix(1)
                        )
                        .uri("lb://notification-service")
                )
                
                .build();
    }

    /**
     * Configuración del rate limiter con Redis
     */
    @Bean
    public RedisRateLimiter redisRateLimiter() {
        return new RedisRateLimiter(10, 20, 1);
    }

    /**
     * Resolver de clave para rate limiting basado en usuario
     */
    @Bean
    public KeyResolver userKeyResolver() {
        return exchange -> {
            // Extraer user ID del JWT token
            String authHeader = exchange.getRequest().getHeaders().getFirst("Authorization");
            if (authHeader != null && authHeader.startsWith("Bearer ")) {
                String token = authHeader.substring(7);
                // Decodificar JWT y extraer user ID
                return Mono.just(extractUserIdFromToken(token));
            }
            return Mono.just("anonymous");
        };
    }
}
