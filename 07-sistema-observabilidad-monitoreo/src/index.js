const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const { configurarTracing } = require('./infraestructura/tracing/configuradorTracing');
const { configurarMetricas } = require('./infraestructura/metricas/configuradorMetricas');
const { configurarLogger } = require('./infraestructura/logging/configuradorLogger');
const { configurarRedis } = require('./infraestructura/cache/configuradorRedis');
const { configurarElasticsearch } = require('./infraestructura/busqueda/configuradorElasticsearch');

const rutasMetricas = require('./presentacion/rutas/rutasMetricas');
const rutasLogs = require('./presentacion/rutas/rutasLogs');
const rutasTrazas = require('./presentacion/rutas/rutasTrazas');
const rutasAlertas = require('./presentacion/rutas/rutasAlertas');
const rutasDashboards = require('./presentacion/rutas/rutasDashboards');
const rutasHealth = require('./presentacion/rutas/rutasHealth');

const middlewareError = require('./presentacion/middleware/middlewareError');
const middlewareAutenticacion = require('./presentacion/middleware/middlewareAutenticacion');
const middlewareValidacion = require('./presentacion/middleware/middlewareValidacion');

const logger = require('./infraestructura/logging/logger');

class AplicacionObservabilidad {
    constructor() {
        this.app = express();
        this.puerto = process.env.PUERTO || 3000;
        this.configurarAplicacion();
    }

    async configurarAplicacion() {
        try {
            // Configurar tracing
            await configurarTracing();
            logger.info('Tracing configurado correctamente');

            // Configurar métricas
            configurarMetricas();
            logger.info('Métricas configuradas correctamente');

            // Configurar logger
            configurarLogger();
            logger.info('Logger configurado correctamente');

            // Configurar Redis
            await configurarRedis();
            logger.info('Redis configurado correctamente');

            // Configurar Elasticsearch
            await configurarElasticsearch();
            logger.info('Elasticsearch configurado correctamente');

            // Configurar middleware
            this.configurarMiddleware();

            // Configurar rutas
            this.configurarRutas();

            // Configurar manejo de errores
            this.configurarManejoErrores();

            logger.info('Aplicación de observabilidad configurada correctamente');
        } catch (error) {
            logger.error('Error configurando la aplicación:', error);
            process.exit(1);
        }
    }

    configurarMiddleware() {
        // Middleware de seguridad
        this.app.use(helmet({
            contentSecurityPolicy: {
                directives: {
                    defaultSrc: ["'self'"],
                    styleSrc: ["'self'", "'unsafe-inline'"],
                    scriptSrc: ["'self'"],
                    imgSrc: ["'self'", "data:", "https:"],
                },
            },
        }));

        // CORS
        this.app.use(cors({
            origin: process.env.ORIGENES_PERMITIDOS?.split(',') || ['http://localhost:3000'],
            credentials: true,
        }));

        // Compresión
        this.app.use(compression());

        // Rate limiting
        const limiter = rateLimit({
            windowMs: 15 * 60 * 1000, // 15 minutos
            max: 1000, // máximo 1000 requests por ventana
            message: {
                error: 'Demasiadas solicitudes desde esta IP',
                codigo: 'RATE_LIMIT_EXCEEDED'
            }
        });
        this.app.use(limiter);

        // Logging de requests
        this.app.use(morgan('combined', {
            stream: {
                write: (mensaje) => logger.info(mensaje.trim())
            }
        }));

        // Parseo de JSON
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

        // Middleware de autenticación
        this.app.use('/api', middlewareAutenticacion);

        // Middleware de validación
        this.app.use('/api', middlewareValidacion);
    }

    configurarRutas() {
        // Rutas de health check
        this.app.use('/health', rutasHealth);

        // Rutas de API
        this.app.use('/api/metricas', rutasMetricas);
        this.app.use('/api/logs', rutasLogs);
        this.app.use('/api/trazas', rutasTrazas);
        this.app.use('/api/alertas', rutasAlertas);
        this.app.use('/api/dashboards', rutasDashboards);

        // Ruta raíz
        this.app.get('/', (req, res) => {
            res.json({
                servicio: 'Sistema de Observabilidad y Monitoreo',
                version: '1.0.0',
                estado: 'funcionando',
                timestamp: new Date().toISOString(),
                endpoints: {
                    health: '/health',
                    metricas: '/api/metricas',
                    logs: '/api/logs',
                    trazas: '/api/trazas',
                    alertas: '/api/alertas',
                    dashboards: '/api/dashboards'
                }
            });
        });

        // Ruta 404
        this.app.use('*', (req, res) => {
            res.status(404).json({
                error: 'Endpoint no encontrado',
                codigo: 'ENDPOINT_NOT_FOUND',
                timestamp: new Date().toISOString()
            });
        });
    }

    configurarManejoErrores() {
        this.app.use(middlewareError);
    }

    iniciar() {
        this.app.listen(this.puerto, () => {
            logger.info(`🚀 Servidor de observabilidad iniciado en puerto ${this.puerto}`);
            logger.info(`📊 Métricas disponibles en: http://localhost:${this.puerto}/api/metricas`);
            logger.info(`📝 Logs disponibles en: http://localhost:${this.puerto}/api/logs`);
            logger.info(`🔍 Trazas disponibles en: http://localhost:${this.puerto}/api/trazas`);
            logger.info(`🚨 Alertas disponibles en: http://localhost:${this.puerto}/api/alertas`);
            logger.info(`📈 Dashboards disponibles en: http://localhost:${this.puerto}/api/dashboards`);
        });
    }
}

// Inicializar aplicación
const aplicacion = new AplicacionObservabilidad();
aplicacion.iniciar();

// Manejo de señales para shutdown graceful
process.on('SIGTERM', () => {
    logger.info('Recibida señal SIGTERM, cerrando servidor...');
    process.exit(0);
});

process.on('SIGINT', () => {
    logger.info('Recibida señal SIGINT, cerrando servidor...');
    process.exit(0);
});

module.exports = aplicacion;
