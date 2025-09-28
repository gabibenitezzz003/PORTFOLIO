const CasoUsoGestionarMetricas = require('../../aplicacion/casosUso/CasoUsoGestionarMetricas');
const { RespuestaApi } = require('../dto/RespuestaApi');
const { ErrorAplicacion } = require('../../aplicacion/excepciones/ErroresAplicacion');
const { ErrorDominio } = require('../../dominio/excepciones/ErroresDominio');
const logger = require('../../infraestructura/logging/logger');

/**
 * Controlador REST para la gestión de métricas
 * 
 * @author Gabriel - Arquitecto de Software
 */
class ControladorMetricas {
    constructor(casoUsoGestionarMetricas) {
        this.casoUsoGestionarMetricas = casoUsoGestionarMetricas;
    }

    /**
     * Crea una nueva métrica
     */
    async crearMetrica(req, res) {
        try {
            logger.info('Creando nueva métrica', { datos: req.body });

            const metrica = await this.casoUsoGestionarMetricas.crearMetrica(req.body);

            const respuesta = new RespuestaApi({
                exito: true,
                mensaje: 'Métrica creada correctamente',
                datos: metrica.aJSON()
            });

            res.status(201).json(respuesta);

        } catch (error) {
            logger.error('Error creando métrica:', error);

            if (error instanceof ErrorDominio) {
                const respuesta = new RespuestaApi({
                    exito: false,
                    mensaje: error.message,
                    error: {
                        codigo: 'ERROR_DOMINIO',
                        tipo: 'ErrorDominio'
                    }
                });
                return res.status(400).json(respuesta);
            }

            const respuesta = new RespuestaApi({
                exito: false,
                mensaje: 'Error interno del servidor',
                error: {
                    codigo: 'ERROR_INTERNO',
                    tipo: 'ErrorInterno'
                }
            });

            res.status(500).json(respuesta);
        }
    }

    /**
     * Obtiene una métrica por ID
     */
    async obtenerMetricaPorId(req, res) {
        try {
            const { id } = req.params;
            logger.info('Obteniendo métrica por ID', { id });

            const metrica = await this.casoUsoGestionarMetricas.obtenerMetricaPorId(id);

            const respuesta = new RespuestaApi({
                exito: true,
                mensaje: 'Métrica obtenida correctamente',
                datos: metrica.aJSON()
            });

            res.json(respuesta);

        } catch (error) {
            logger.error('Error obteniendo métrica:', error);

            if (error instanceof ErrorDominio) {
                const respuesta = new RespuestaApi({
                    exito: false,
                    mensaje: error.message,
                    error: {
                        codigo: 'METRICA_NO_ENCONTRADA',
                        tipo: 'ErrorDominio'
                    }
                });
                return res.status(404).json(respuesta);
            }

            const respuesta = new RespuestaApi({
                exito: false,
                mensaje: 'Error interno del servidor',
                error: {
                    codigo: 'ERROR_INTERNO',
                    tipo: 'ErrorInterno'
                }
            });

            res.status(500).json(respuesta);
        }
    }

    /**
     * Lista métricas con filtros
     */
    async listarMetricas(req, res) {
        try {
            const filtros = req.query;
            logger.info('Listando métricas', { filtros });

            const resultado = await this.casoUsoGestionarMetricas.listarMetricas(filtros);

            const respuesta = new RespuestaApi({
                exito: true,
                mensaje: 'Métricas obtenidas correctamente',
                datos: resultado
            });

            res.json(respuesta);

        } catch (error) {
            logger.error('Error listando métricas:', error);

            const respuesta = new RespuestaApi({
                exito: false,
                mensaje: 'Error interno del servidor',
                error: {
                    codigo: 'ERROR_INTERNO',
                    tipo: 'ErrorInterno'
                }
            });

            res.status(500).json(respuesta);
        }
    }

    /**
     * Actualiza una métrica
     */
    async actualizarMetrica(req, res) {
        try {
            const { id } = req.params;
            const datosActualizacion = req.body;
            logger.info('Actualizando métrica', { id, datosActualizacion });

            const metrica = await this.casoUsoGestionarMetricas.actualizarMetrica(id, datosActualizacion);

            const respuesta = new RespuestaApi({
                exito: true,
                mensaje: 'Métrica actualizada correctamente',
                datos: metrica.aJSON()
            });

            res.json(respuesta);

        } catch (error) {
            logger.error('Error actualizando métrica:', error);

            if (error instanceof ErrorDominio) {
                const respuesta = new RespuestaApi({
                    exito: false,
                    mensaje: error.message,
                    error: {
                        codigo: 'ERROR_DOMINIO',
                        tipo: 'ErrorDominio'
                    }
                });
                return res.status(400).json(respuesta);
            }

            const respuesta = new RespuestaApi({
                exito: false,
                mensaje: 'Error interno del servidor',
                error: {
                    codigo: 'ERROR_INTERNO',
                    tipo: 'ErrorInterno'
                }
            });

            res.status(500).json(respuesta);
        }
    }

    /**
     * Actualiza el valor de una métrica
     */
    async actualizarValorMetrica(req, res) {
        try {
            const { id } = req.params;
            const { valor } = req.body;
            logger.info('Actualizando valor de métrica', { id, valor });

            const metrica = await this.casoUsoGestionarMetricas.actualizarValorMetrica(id, valor);

            const respuesta = new RespuestaApi({
                exito: true,
                mensaje: 'Valor de métrica actualizado correctamente',
                datos: metrica.aJSON()
            });

            res.json(respuesta);

        } catch (error) {
            logger.error('Error actualizando valor de métrica:', error);

            if (error instanceof ErrorDominio) {
                const respuesta = new RespuestaApi({
                    exito: false,
                    mensaje: error.message,
                    error: {
                        codigo: 'ERROR_DOMINIO',
                        tipo: 'ErrorDominio'
                    }
                });
                return res.status(400).json(respuesta);
            }

            const respuesta = new RespuestaApi({
                exito: false,
                mensaje: 'Error interno del servidor',
                error: {
                    codigo: 'ERROR_INTERNO',
                    tipo: 'ErrorInterno'
                }
            });

            res.status(500).json(respuesta);
        }
    }

    /**
     * Elimina una métrica
     */
    async eliminarMetrica(req, res) {
        try {
            const { id } = req.params;
            logger.info('Eliminando métrica', { id });

            const resultado = await this.casoUsoGestionarMetricas.eliminarMetrica(id);

            const respuesta = new RespuestaApi({
                exito: true,
                mensaje: resultado.mensaje,
                datos: null
            });

            res.json(respuesta);

        } catch (error) {
            logger.error('Error eliminando métrica:', error);

            if (error instanceof ErrorDominio) {
                const respuesta = new RespuestaApi({
                    exito: false,
                    mensaje: error.message,
                    error: {
                        codigo: 'METRICA_NO_ENCONTRADA',
                        tipo: 'ErrorDominio'
                    }
                });
                return res.status(404).json(respuesta);
            }

            const respuesta = new RespuestaApi({
                exito: false,
                mensaje: 'Error interno del servidor',
                error: {
                    codigo: 'ERROR_INTERNO',
                    tipo: 'ErrorInterno'
                }
            });

            res.status(500).json(respuesta);
        }
    }

    /**
     * Obtiene métricas en formato Prometheus
     */
    async obtenerMetricasPrometheus(req, res) {
        try {
            const filtros = req.query;
            logger.info('Obteniendo métricas Prometheus', { filtros });

            const prometheusFormat = await this.casoUsoGestionarMetricas.obtenerMetricasPrometheus(filtros);

            res.set('Content-Type', 'text/plain; version=0.0.4; charset=utf-8');
            res.send(prometheusFormat);

        } catch (error) {
            logger.error('Error obteniendo métricas Prometheus:', error);

            const respuesta = new RespuestaApi({
                exito: false,
                mensaje: 'Error interno del servidor',
                error: {
                    codigo: 'ERROR_INTERNO',
                    tipo: 'ErrorInterno'
                }
            });

            res.status(500).json(respuesta);
        }
    }

    /**
     * Obtiene estadísticas de métricas
     */
    async obtenerEstadisticasMetricas(req, res) {
        try {
            logger.info('Obteniendo estadísticas de métricas');

            const estadisticas = await this.casoUsoGestionarMetricas.obtenerEstadisticasMetricas();

            const respuesta = new RespuestaApi({
                exito: true,
                mensaje: 'Estadísticas obtenidas correctamente',
                datos: estadisticas
            });

            res.json(respuesta);

        } catch (error) {
            logger.error('Error obteniendo estadísticas:', error);

            const respuesta = new RespuestaApi({
                exito: false,
                mensaje: 'Error interno del servidor',
                error: {
                    codigo: 'ERROR_INTERNO',
                    tipo: 'ErrorInterno'
                }
            });

            res.status(500).json(respuesta);
        }
    }
}

module.exports = ControladorMetricas;
