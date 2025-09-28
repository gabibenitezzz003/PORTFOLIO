const { v4: uuidv4 } = require('uuid');

/**
 * Entidad Métrica - Capa de Dominio
 * 
 * Representa una métrica en el sistema de observabilidad.
 * Implementa los principios de DDD con agregados bien definidos.
 * 
 * @author Gabriel - Arquitecto de Software
 */
class Metrica {
    constructor(datos) {
        this.id = datos.id || uuidv4();
        this.nombre = datos.nombre;
        this.tipo = datos.tipo; // counter, gauge, histogram, summary
        this.valor = datos.valor;
        this.etiquetas = datos.etiquetas || {};
        this.timestamp = datos.timestamp || new Date();
        this.servicio = datos.servicio;
        this.version = datos.version || '1.0.0';
        this.descripcion = datos.descripcion;
        this.unidad = datos.unidad;
        this.agregacion = datos.agregacion || 'sum';
        this.retencion = datos.retencion || 30; // días
        this.activa = datos.activa !== undefined ? datos.activa : true;
        this.fechaCreacion = datos.fechaCreacion || new Date();
        this.fechaActualizacion = datos.fechaActualizacion || new Date();
    }

    /**
     * Valida la métrica
     */
    validar() {
        const errores = [];

        if (!this.nombre || this.nombre.trim() === '') {
            errores.push('Nombre es requerido');
        }

        if (!this.tipo || !['counter', 'gauge', 'histogram', 'summary'].includes(this.tipo)) {
            errores.push('Tipo debe ser counter, gauge, histogram o summary');
        }

        if (typeof this.valor !== 'number' || isNaN(this.valor)) {
            errores.push('Valor debe ser un número válido');
        }

        if (!this.servicio || this.servicio.trim() === '') {
            errores.push('Servicio es requerido');
        }

        if (this.retencion < 1 || this.retencion > 365) {
            errores.push('Retención debe estar entre 1 y 365 días');
        }

        return errores;
    }

    /**
     * Verifica si la métrica es válida
     */
    esValida() {
        return this.validar().length === 0;
    }

    /**
     * Actualiza el valor de la métrica
     */
    actualizarValor(nuevoValor) {
        if (typeof nuevoValor !== 'number' || isNaN(nuevoValor)) {
            throw new Error('Valor debe ser un número válido');
        }

        this.valor = nuevoValor;
        this.fechaActualizacion = new Date();
    }

    /**
     * Agrega una etiqueta
     */
    agregarEtiqueta(clave, valor) {
        if (!clave || !valor) {
            throw new Error('Clave y valor son requeridos');
        }

        this.etiquetas[clave] = valor;
        this.fechaActualizacion = new Date();
    }

    /**
     * Remueve una etiqueta
     */
    removerEtiqueta(clave) {
        if (this.etiquetas[clave]) {
            delete this.etiquetas[clave];
            this.fechaActualizacion = new Date();
        }
    }

    /**
     * Verifica si la métrica está activa
     */
    estaActiva() {
        return this.activa;
    }

    /**
     * Activa la métrica
     */
    activar() {
        this.activa = true;
        this.fechaActualizacion = new Date();
    }

    /**
     * Desactiva la métrica
     */
    desactivar() {
        this.activa = false;
        this.fechaActualizacion = new Date();
    }

    /**
     * Verifica si la métrica ha expirado
     */
    haExpirado() {
        const diasDiferencia = (new Date() - this.timestamp) / (1000 * 60 * 60 * 24);
        return diasDiferencia > this.retencion;
    }

    /**
     * Obtiene el valor formateado según el tipo
     */
    obtenerValorFormateado() {
        switch (this.tipo) {
            case 'counter':
                return Math.floor(this.valor);
            case 'gauge':
                return parseFloat(this.valor.toFixed(2));
            case 'histogram':
                return {
                    count: Math.floor(this.valor),
                    sum: this.valor,
                    buckets: this.etiquetas.buckets || []
                };
            case 'summary':
                return {
                    count: Math.floor(this.valor),
                    sum: this.valor,
                    quantiles: this.etiquetas.quantiles || {}
                };
            default:
                return this.valor;
        }
    }

    /**
     * Convierte la métrica a formato Prometheus
     */
    aFormatoPrometheus() {
        const etiquetas = Object.entries(this.etiquetas)
            .map(([clave, valor]) => `${clave}="${valor}"`)
            .join(',');

        const etiquetasStr = etiquetas ? `{${etiquetas}}` : '';
        const valorFormateado = this.obtenerValorFormateado();

        return `# HELP ${this.nombre} ${this.descripcion || ''}\n# TYPE ${this.nombre} ${this.tipo}\n${this.nombre}${etiquetasStr} ${valorFormateado}`;
    }

    /**
     * Convierte la métrica a JSON
     */
    aJSON() {
        return {
            id: this.id,
            nombre: this.nombre,
            tipo: this.tipo,
            valor: this.valor,
            etiquetas: this.etiquetas,
            timestamp: this.timestamp,
            servicio: this.servicio,
            version: this.version,
            descripcion: this.descripcion,
            unidad: this.unidad,
            agregacion: this.agregacion,
            retencion: this.retencion,
            activa: this.activa,
            fechaCreacion: this.fechaCreacion,
            fechaActualizacion: this.fechaActualizacion
        };
    }

    /**
     * Crea una métrica desde JSON
     */
    static desdeJSON(datos) {
        return new Metrica(datos);
    }

    /**
     * Crea una métrica de contador
     */
    static crearContador(nombre, valor, servicio, etiquetas = {}) {
        return new Metrica({
            nombre,
            tipo: 'counter',
            valor,
            servicio,
            etiquetas,
            descripcion: `Contador: ${nombre}`,
            agregacion: 'sum'
        });
    }

    /**
     * Crea una métrica de gauge
     */
    static crearGauge(nombre, valor, servicio, etiquetas = {}) {
        return new Metrica({
            nombre,
            tipo: 'gauge',
            valor,
            servicio,
            etiquetas,
            descripcion: `Gauge: ${nombre}`,
            agregacion: 'last'
        });
    }

    /**
     * Crea una métrica de histograma
     */
    static crearHistograma(nombre, valor, servicio, buckets = [], etiquetas = {}) {
        return new Metrica({
            nombre,
            tipo: 'histogram',
            valor,
            servicio,
            etiquetas: { ...etiquetas, buckets },
            descripcion: `Histograma: ${nombre}`,
            agregacion: 'histogram'
        });
    }
}

module.exports = Metrica;
