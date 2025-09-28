const Metrica = require('../../dominio/entidad/Metrica');
const { ErrorDominio } = require('../../dominio/excepciones/ErroresDominio');

/**
 * Caso de Uso para Gestionar Métricas
 * 
 * Implementa la lógica de negocio para la gestión de métricas,
 * incluyendo creación, actualización y consulta de métricas.
 * 
 * @author Gabriel - Arquitecto de Software
 */
class CasoUsoGestionarMetricas {
    constructor(repositorioMetricas, servicioCache, servicioNotificaciones) {
        this.repositorioMetricas = repositorioMetricas;
        this.servicioCache = servicioCache;
        this.servicioNotificaciones = servicioNotificaciones;
    }

    /**
     * Crea una nueva métrica
     */
    async crearMetrica(datosMetrica) {
        try {
            // Crear entidad métrica
            const metrica = new Metrica(datosMetrica);

            // Validar métrica
            if (!metrica.esValida()) {
                const errores = metrica.validar();
                throw new ErrorDominio(`Métrica inválida: ${errores.join(', ')}`);
            }

            // Verificar si ya existe una métrica con el mismo nombre y servicio
            const metricaExistente = await this.repositorioMetricas.buscarPorNombreYServicio(
                metrica.nombre, 
                metrica.servicio
            );

            if (metricaExistente) {
                throw new ErrorDominio('Ya existe una métrica con el mismo nombre y servicio');
            }

            // Guardar métrica
            const metricaGuardada = await this.repositorioMetricas.guardar(metrica);

            // Actualizar cache
            await this.servicioCache.establecer(
                `metrica:${metricaGuardada.id}`,
                metricaGuardada.aJSON(),
                3600 // 1 hora
            );

            // Notificar creación
            await this.servicioNotificaciones.enviarNotificacion({
                tipo: 'metrica_creada',
                datos: {
                    metricaId: metricaGuardada.id,
                    nombre: metricaGuardada.nombre,
                    servicio: metricaGuardada.servicio
                }
            });

            return metricaGuardada;

        } catch (error) {
            if (error instanceof ErrorDominio) {
                throw error;
            }
            throw new Error(`Error creando métrica: ${error.message}`);
        }
    }

    /**
     * Actualiza una métrica existente
     */
    async actualizarMetrica(id, datosActualizacion) {
        try {
            // Buscar métrica existente
            const metricaExistente = await this.repositorioMetricas.buscarPorId(id);
            if (!metricaExistente) {
                throw new ErrorDominio('Métrica no encontrada');
            }

            // Actualizar datos
            Object.keys(datosActualizacion).forEach(clave => {
                if (datosActualizacion[clave] !== undefined) {
                    metricaExistente[clave] = datosActualizacion[clave];
                }
            });

            // Actualizar timestamp
            metricaExistente.fechaActualizacion = new Date();

            // Validar métrica actualizada
            if (!metricaExistente.esValida()) {
                const errores = metricaExistente.validar();
                throw new ErrorDominio(`Métrica inválida: ${errores.join(', ')}`);
            }

            // Guardar cambios
            const metricaActualizada = await this.repositorioMetricas.actualizar(metricaExistente);

            // Actualizar cache
            await this.servicioCache.establecer(
                `metrica:${metricaActualizada.id}`,
                metricaActualizada.aJSON(),
                3600
            );

            // Notificar actualización
            await this.servicioNotificaciones.enviarNotificacion({
                tipo: 'metrica_actualizada',
                datos: {
                    metricaId: metricaActualizada.id,
                    nombre: metricaActualizada.nombre,
                    servicio: metricaActualizada.servicio
                }
            });

            return metricaActualizada;

        } catch (error) {
            if (error instanceof ErrorDominio) {
                throw error;
            }
            throw new Error(`Error actualizando métrica: ${error.message}`);
        }
    }

    /**
     * Obtiene una métrica por ID
     */
    async obtenerMetricaPorId(id) {
        try {
            // Buscar en cache primero
            const metricaCache = await this.servicioCache.obtener(`metrica:${id}`);
            if (metricaCache) {
                return Metrica.desdeJSON(metricaCache);
            }

            // Buscar en repositorio
            const metrica = await this.repositorioMetricas.buscarPorId(id);
            if (!metrica) {
                throw new ErrorDominio('Métrica no encontrada');
            }

            // Actualizar cache
            await this.servicioCache.establecer(
                `metrica:${id}`,
                metrica.aJSON(),
                3600
            );

            return metrica;

        } catch (error) {
            if (error instanceof ErrorDominio) {
                throw error;
            }
            throw new Error(`Error obteniendo métrica: ${error.message}`);
        }
    }

    /**
     * Lista métricas con filtros
     */
    async listarMetricas(filtros = {}) {
        try {
            const {
                servicio,
                tipo,
                activa,
                pagina = 1,
                limite = 10,
                ordenarPor = 'fechaCreacion',
                orden = 'desc'
            } = filtros;

            // Construir filtros de búsqueda
            const filtrosBusqueda = {};
            if (servicio) filtrosBusqueda.servicio = servicio;
            if (tipo) filtrosBusqueda.tipo = tipo;
            if (activa !== undefined) filtrosBusqueda.activa = activa;

            // Calcular offset
            const offset = (pagina - 1) * limite;

            // Buscar métricas
            const metricas = await this.repositorioMetricas.buscarConFiltros(
                filtrosBusqueda,
                offset,
                limite,
                ordenarPor,
                orden
            );

            // Obtener total
            const total = await this.repositorioMetricas.contarConFiltros(filtrosBusqueda);

            return {
                metricas,
                paginacion: {
                    pagina,
                    limite,
                    total,
                    totalPaginas: Math.ceil(total / limite)
                }
            };

        } catch (error) {
            throw new Error(`Error listando métricas: ${error.message}`);
        }
    }

    /**
     * Actualiza el valor de una métrica
     */
    async actualizarValorMetrica(id, nuevoValor) {
        try {
            // Buscar métrica
            const metrica = await this.repositorioMetricas.buscarPorId(id);
            if (!metrica) {
                throw new ErrorDominio('Métrica no encontrada');
            }

            // Actualizar valor
            metrica.actualizarValor(nuevoValor);

            // Guardar cambios
            const metricaActualizada = await this.repositorioMetricas.actualizar(metrica);

            // Actualizar cache
            await this.servicioCache.establecer(
                `metrica:${id}`,
                metricaActualizada.aJSON(),
                3600
            );

            // Notificar actualización de valor
            await this.servicioNotificaciones.enviarNotificacion({
                tipo: 'metrica_valor_actualizado',
                datos: {
                    metricaId: id,
                    nombre: metricaActualizada.nombre,
                    valorAnterior: metrica.valor,
                    valorNuevo: nuevoValor
                }
            });

            return metricaActualizada;

        } catch (error) {
            if (error instanceof ErrorDominio) {
                throw error;
            }
            throw new Error(`Error actualizando valor de métrica: ${error.message}`);
        }
    }

    /**
     * Elimina una métrica
     */
    async eliminarMetrica(id) {
        try {
            // Verificar que existe
            const metrica = await this.repositorioMetricas.buscarPorId(id);
            if (!metrica) {
                throw new ErrorDominio('Métrica no encontrada');
            }

            // Eliminar métrica
            await this.repositorioMetricas.eliminar(id);

            // Eliminar de cache
            await this.servicioCache.eliminar(`metrica:${id}`);

            // Notificar eliminación
            await this.servicioNotificaciones.enviarNotificacion({
                tipo: 'metrica_eliminada',
                datos: {
                    metricaId: id,
                    nombre: metrica.nombre,
                    servicio: metrica.servicio
                }
            });

            return { mensaje: 'Métrica eliminada correctamente' };

        } catch (error) {
            if (error instanceof ErrorDominio) {
                throw error;
            }
            throw new Error(`Error eliminando métrica: ${error.message}`);
        }
    }

    /**
     * Obtiene métricas en formato Prometheus
     */
    async obtenerMetricasPrometheus(filtros = {}) {
        try {
            const { servicio, tipo } = filtros;
            
            const filtrosBusqueda = {};
            if (servicio) filtrosBusqueda.servicio = servicio;
            if (tipo) filtrosBusqueda.tipo = tipo;
            filtrosBusqueda.activa = true;

            const metricas = await this.repositorioMetricas.buscarConFiltros(filtrosBusqueda);

            // Convertir a formato Prometheus
            const prometheusFormat = metricas
                .map(metrica => metrica.aFormatoPrometheus())
                .join('\n');

            return prometheusFormat;

        } catch (error) {
            throw new Error(`Error obteniendo métricas Prometheus: ${error.message}`);
        }
    }

    /**
     * Obtiene estadísticas de métricas
     */
    async obtenerEstadisticasMetricas() {
        try {
            const estadisticas = await this.repositorioMetricas.obtenerEstadisticas();
            return estadisticas;

        } catch (error) {
            throw new Error(`Error obteniendo estadísticas: ${error.message}`);
        }
    }
}

module.exports = CasoUsoGestionarMetricas;
