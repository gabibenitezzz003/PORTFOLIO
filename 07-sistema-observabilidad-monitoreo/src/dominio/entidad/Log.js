const { v4: uuidv4 } = require('uuid');

/**
 * Entidad Log - Capa de Dominio
 * 
 * Representa un log en el sistema de observabilidad.
 * Implementa los principios de DDD con agregados bien definidos.
 * 
 * @author Gabriel - Arquitecto de Software
 */
class Log {
    constructor(datos) {
        this.id = datos.id || uuidv4();
        this.nivel = datos.nivel; // debug, info, warn, error, fatal
        this.mensaje = datos.mensaje;
        this.servicio = datos.servicio;
        this.version = datos.version || '1.0.0';
        this.timestamp = datos.timestamp || new Date();
        this.threadId = datos.threadId;
        this.correlationId = datos.correlationId;
        this.userId = datos.userId;
        this.sessionId = datos.sessionId;
        this.requestId = datos.requestId;
        this.tags = datos.tags || [];
        this.metadata = datos.metadata || {};
        this.stackTrace = datos.stackTrace;
        this.source = datos.source;
        this.environment = datos.environment || 'development';
        this.hostname = datos.hostname;
        this.pid = datos.pid;
        this.fechaCreacion = datos.fechaCreacion || new Date();
    }

    /**
     * Valida el log
     */
    validar() {
        const errores = [];

        if (!this.nivel || !['debug', 'info', 'warn', 'error', 'fatal'].includes(this.nivel)) {
            errores.push('Nivel debe ser debug, info, warn, error o fatal');
        }

        if (!this.mensaje || this.mensaje.trim() === '') {
            errores.push('Mensaje es requerido');
        }

        if (!this.servicio || this.servicio.trim() === '') {
            errores.push('Servicio es requerido');
        }

        if (!this.timestamp || !(this.timestamp instanceof Date)) {
            errores.push('Timestamp debe ser una fecha válida');
        }

        return errores;
    }

    /**
     * Verifica si el log es válido
     */
    esValido() {
        return this.validar().length === 0;
    }

    /**
     * Verifica si es un log de error
     */
    esError() {
        return ['error', 'fatal'].includes(this.nivel);
    }

    /**
     * Verifica si es un log crítico
     */
    esCritico() {
        return this.nivel === 'fatal';
    }

    /**
     * Agrega un tag
     */
    agregarTag(tag) {
        if (!this.tags.includes(tag)) {
            this.tags.push(tag);
        }
    }

    /**
     * Remueve un tag
     */
    removerTag(tag) {
        const indice = this.tags.indexOf(tag);
        if (indice > -1) {
            this.tags.splice(indice, 1);
        }
    }

    /**
     * Agrega metadata
     */
    agregarMetadata(clave, valor) {
        this.metadata[clave] = valor;
    }

    /**
     * Obtiene metadata
     */
    obtenerMetadata(clave) {
        return this.metadata[clave];
    }

    /**
     * Establece el stack trace para errores
     */
    establecerStackTrace(stackTrace) {
        if (this.esError()) {
            this.stackTrace = stackTrace;
        }
    }

    /**
     * Obtiene el nivel de prioridad numérico
     */
    obtenerPrioridadNumerica() {
        const prioridades = {
            debug: 0,
            info: 1,
            warn: 2,
            error: 3,
            fatal: 4
        };
        return prioridades[this.nivel] || 0;
    }

    /**
     * Verifica si el log es más prioritario que otro
     */
    esMasPrioritarioQue(otroLog) {
        return this.obtenerPrioridadNumerica() > otroLog.obtenerPrioridadNumerica();
    }

    /**
     * Formatea el log para visualización
     */
    formatear() {
        const timestamp = this.timestamp.toISOString();
        const nivel = this.nivel.toUpperCase().padEnd(5);
        const servicio = this.servicio.padEnd(15);
        const mensaje = this.mensaje;

        let logFormateado = `[${timestamp}] ${nivel} ${servicio} ${mensaje}`;

        if (this.correlationId) {
            logFormateado += ` [correlationId: ${this.correlationId}]`;
        }

        if (this.userId) {
            logFormateado += ` [userId: ${this.userId}]`;
        }

        if (this.tags.length > 0) {
            logFormateado += ` [tags: ${this.tags.join(', ')}]`;
        }

        if (this.stackTrace) {
            logFormateado += `\n${this.stackTrace}`;
        }

        return logFormateado;
    }

    /**
     * Convierte el log a formato JSON estructurado
     */
    aJSON() {
        return {
            id: this.id,
            nivel: this.nivel,
            mensaje: this.mensaje,
            servicio: this.servicio,
            version: this.version,
            timestamp: this.timestamp,
            threadId: this.threadId,
            correlationId: this.correlationId,
            userId: this.userId,
            sessionId: this.sessionId,
            requestId: this.requestId,
            tags: this.tags,
            metadata: this.metadata,
            stackTrace: this.stackTrace,
            source: this.source,
            environment: this.environment,
            hostname: this.hostname,
            pid: this.pid,
            fechaCreacion: this.fechaCreacion
        };
    }

    /**
     * Crea un log desde JSON
     */
    static desdeJSON(datos) {
        return new Log(datos);
    }

    /**
     * Crea un log de información
     */
    static crearInfo(mensaje, servicio, metadata = {}) {
        return new Log({
            nivel: 'info',
            mensaje,
            servicio,
            metadata
        });
    }

    /**
     * Crea un log de error
     */
    static crearError(mensaje, servicio, error = null, metadata = {}) {
        const log = new Log({
            nivel: 'error',
            mensaje,
            servicio,
            metadata
        });

        if (error && error.stack) {
            log.establecerStackTrace(error.stack);
        }

        return log;
    }

    /**
     * Crea un log de warning
     */
    static crearWarning(mensaje, servicio, metadata = {}) {
        return new Log({
            nivel: 'warn',
            mensaje,
            servicio,
            metadata
        });
    }

    /**
     * Crea un log de debug
     */
    static crearDebug(mensaje, servicio, metadata = {}) {
        return new Log({
            nivel: 'debug',
            mensaje,
            servicio,
            metadata
        });
    }

    /**
     * Crea un log fatal
     */
    static crearFatal(mensaje, servicio, error = null, metadata = {}) {
        const log = new Log({
            nivel: 'fatal',
            mensaje,
            servicio,
            metadata
        });

        if (error && error.stack) {
            log.establecerStackTrace(error.stack);
        }

        return log;
    }
}

module.exports = Log;
