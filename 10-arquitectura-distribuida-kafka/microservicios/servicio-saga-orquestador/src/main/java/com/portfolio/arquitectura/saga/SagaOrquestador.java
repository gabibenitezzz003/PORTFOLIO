package com.portfolio.arquitectura.saga;

import com.portfolio.arquitectura.eventos.EventoDominio;
import com.portfolio.arquitectura.saga.pasos.PasoSaga;
import com.portfolio.arquitectura.saga.pasos.PasoCompensacion;
import com.portfolio.arquitectura.saga.estado.EstadoSaga;
import com.portfolio.arquitectura.saga.estado.EstadoSagaRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Orquestador de Saga para coordinar transacciones distribuidas
 * 
 * Implementa el patrón Saga para manejar transacciones distribuidas
 * de manera consistente y resiliente.
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Component
public class SagaOrquestador {

    private static final Logger logger = LoggerFactory.getLogger(SagaOrquestador.class);
    
    private final EstadoSagaRepository estadoSagaRepository;
    private final ExecutorService executorService;
    private final List<PasoSaga> pasosSaga;

    public SagaOrquestador(EstadoSagaRepository estadoSagaRepository, 
                          List<PasoSaga> pasosSaga) {
        this.estadoSagaRepository = estadoSagaRepository;
        this.pasosSaga = pasosSaga;
        this.executorService = Executors.newFixedThreadPool(10);
    }

    /**
     * Ejecuta un saga completo
     */
    public CompletableFuture<ResultadoSaga> ejecutarSaga(String sagaId, EventoDominio eventoInicial) {
        logger.info("Iniciando saga: {} con evento: {}", sagaId, eventoInicial.getTipo());
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                // Crear estado inicial del saga
                EstadoSaga estadoSaga = new EstadoSaga(sagaId, eventoInicial);
                estadoSagaRepository.guardar(estadoSaga);

                // Ejecutar pasos secuencialmente
                for (PasoSaga paso : pasosSaga) {
                    if (!paso.esAplicable(eventoInicial)) {
                        continue;
                    }

                    logger.info("Ejecutando paso: {} para saga: {}", paso.getNombre(), sagaId);
                    
                    try {
                        // Ejecutar paso
                        ResultadoPaso resultado = paso.ejecutar(eventoInicial);
                        
                        if (!resultado.esExitoso()) {
                            logger.error("Paso falló: {} - {}", paso.getNombre(), resultado.getMensajeError());
                            return compensarSaga(sagaId, estadoSaga);
                        }

                        // Actualizar estado del saga
                        estadoSaga.agregarPasoEjecutado(paso.getNombre(), resultado);
                        estadoSagaRepository.actualizar(estadoSaga);

                        logger.info("Paso completado exitosamente: {}", paso.getNombre());

                    } catch (Exception e) {
                        logger.error("Error ejecutando paso: {} - {}", paso.getNombre(), e.getMessage(), e);
                        return compensarSaga(sagaId, estadoSaga);
                    }
                }

                // Saga completado exitosamente
                estadoSaga.marcarComoCompletado();
                estadoSagaRepository.actualizar(estadoSaga);
                
                logger.info("Saga completado exitosamente: {}", sagaId);
                return new ResultadoSaga(true, "Saga completado exitosamente", null);

            } catch (Exception e) {
                logger.error("Error ejecutando saga: {} - {}", sagaId, e.getMessage(), e);
                return new ResultadoSaga(false, "Error ejecutando saga: " + e.getMessage(), e);
            }
        }, executorService);
    }

    /**
     * Compensa un saga fallido
     */
    private ResultadoSaga compensarSaga(String sagaId, EstadoSaga estadoSaga) {
        logger.info("Iniciando compensación para saga: {}", sagaId);
        
        try {
            // Ejecutar pasos de compensación en orden inverso
            List<String> pasosEjecutados = estadoSaga.getPasosEjecutados();
            
            for (int i = pasosEjecutados.size() - 1; i >= 0; i--) {
                String nombrePaso = pasosEjecutados.get(i);
                
                // Buscar el paso correspondiente
                PasoSaga paso = pasosSaga.stream()
                    .filter(p -> p.getNombre().equals(nombrePaso))
                    .findFirst()
                    .orElse(null);

                if (paso != null && paso instanceof PasoCompensacion) {
                    logger.info("Ejecutando compensación para paso: {}", nombrePaso);
                    
                    try {
                        ResultadoPaso resultadoCompensacion = ((PasoCompensacion) paso).compensar(estadoSaga.getEventoInicial());
                        
                        if (!resultadoCompensacion.esExitoso()) {
                            logger.error("Compensación falló para paso: {} - {}", nombrePaso, resultadoCompensacion.getMensajeError());
                        } else {
                            logger.info("Compensación exitosa para paso: {}", nombrePaso);
                        }

                    } catch (Exception e) {
                        logger.error("Error en compensación para paso: {} - {}", nombrePaso, e.getMessage(), e);
                    }
                }
            }

            // Marcar saga como compensado
            estadoSaga.marcarComoCompensado();
            estadoSagaRepository.actualizar(estadoSaga);
            
            logger.info("Compensación completada para saga: {}", sagaId);
            return new ResultadoSaga(false, "Saga compensado debido a fallos", null);

        } catch (Exception e) {
            logger.error("Error en compensación del saga: {} - {}", sagaId, e.getMessage(), e);
            return new ResultadoSaga(false, "Error en compensación: " + e.getMessage(), e);
        }
    }

    /**
     * Obtiene el estado de un saga
     */
    public EstadoSaga obtenerEstadoSaga(String sagaId) {
        return estadoSagaRepository.buscarPorId(sagaId);
    }

    /**
     * Reintenta un saga fallido
     */
    public CompletableFuture<ResultadoSaga> reintentarSaga(String sagaId) {
        logger.info("Reintentando saga: {}", sagaId);
        
        EstadoSaga estadoSaga = estadoSagaRepository.buscarPorId(sagaId);
        if (estadoSaga == null) {
            return CompletableFuture.completedFuture(
                new ResultadoSaga(false, "Saga no encontrado", null)
            );
        }

        if (estadoSaga.esCompletado()) {
            return CompletableFuture.completedFuture(
                new ResultadoSaga(true, "Saga ya completado", null)
            );
        }

        // Limpiar estado y reintentar
        estadoSaga.limpiarPasosEjecutados();
        estadoSagaRepository.actualizar(estadoSaga);
        
        return ejecutarSaga(sagaId, estadoSaga.getEventoInicial());
    }

    /**
     * Cancela un saga en progreso
     */
    public CompletableFuture<ResultadoSaga> cancelarSaga(String sagaId) {
        logger.info("Cancelando saga: {}", sagaId);
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                EstadoSaga estadoSaga = estadoSagaRepository.buscarPorId(sagaId);
                if (estadoSaga == null) {
                    return new ResultadoSaga(false, "Saga no encontrado", null);
                }

                if (estadoSaga.esCompletado()) {
                    return new ResultadoSaga(false, "No se puede cancelar un saga completado", null);
                }

                // Compensar saga
                ResultadoSaga resultado = compensarSaga(sagaId, estadoSaga);
                
                // Marcar como cancelado
                estadoSaga.marcarComoCancelado();
                estadoSagaRepository.actualizar(estadoSaga);
                
                logger.info("Saga cancelado: {}", sagaId);
                return new ResultadoSaga(true, "Saga cancelado exitosamente", null);

            } catch (Exception e) {
                logger.error("Error cancelando saga: {} - {}", sagaId, e.getMessage(), e);
                return new ResultadoSaga(false, "Error cancelando saga: " + e.getMessage(), e);
            }
        }, executorService);
    }

    /**
     * Obtiene estadísticas de sagas
     */
    public EstadisticasSaga obtenerEstadisticas() {
        return estadoSagaRepository.obtenerEstadisticas();
    }

    /**
     * Cierra el orquestador
     */
    public void cerrar() {
        executorService.shutdown();
        logger.info("SagaOrquestador cerrado");
    }
}
