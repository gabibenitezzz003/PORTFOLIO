package com.portfolio.arquitectura.eventos;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Clase base para todos los eventos de dominio
 * 
 * Implementa el patrón Event Sourcing y define la estructura
 * común para todos los eventos en el sistema distribuido.
 * 
 * @author Gabriel - Arquitecto de Software
 */
public abstract class EventoDominio {
    
    private final UUID id;
    private final String tipo;
    private final LocalDateTime timestamp;
    private final String version;
    private final String correlationId;
    private final String causationId;
    private final String aggregateId;
    private final String aggregateType;
    private final int versionAgregado;
    private final Object datos;

    protected EventoDominio(Builder<?> builder) {
        this.id = builder.id != null ? builder.id : UUID.randomUUID();
        this.tipo = builder.tipo;
        this.timestamp = builder.timestamp != null ? builder.timestamp : LocalDateTime.now();
        this.version = builder.version != null ? builder.version : "1.0";
        this.correlationId = builder.correlationId;
        this.causationId = builder.causationId;
        this.aggregateId = builder.aggregateId;
        this.aggregateType = builder.aggregateType;
        this.versionAgregado = builder.versionAgregado;
        this.datos = builder.datos;
    }

    // Getters
    public UUID getId() { return id; }
    public String getTipo() { return tipo; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public String getVersion() { return version; }
    public String getCorrelationId() { return correlationId; }
    public String getCausationId() { return causationId; }
    public String getAggregateId() { return aggregateId; }
    public String getAggregateType() { return aggregateType; }
    public int getVersionAgregado() { return versionAgregado; }
    public Object getDatos() { return datos; }

    /**
     * Builder abstracto para eventos de dominio
     */
    public abstract static class Builder<T extends Builder<T>> {
        protected UUID id;
        protected String tipo;
        protected LocalDateTime timestamp;
        protected String version;
        protected String correlationId;
        protected String causationId;
        protected String aggregateId;
        protected String aggregateType;
        protected int versionAgregado;
        protected Object datos;

        protected abstract T self();

        public T id(UUID id) {
            this.id = id;
            return self();
        }

        public T tipo(String tipo) {
            this.tipo = tipo;
            return self();
        }

        public T timestamp(LocalDateTime timestamp) {
            this.timestamp = timestamp;
            return self();
        }

        public T version(String version) {
            this.version = version;
            return self();
        }

        public T correlationId(String correlationId) {
            this.correlationId = correlationId;
            return self();
        }

        public T causationId(String causationId) {
            this.causationId = causationId;
            return self();
        }

        public T aggregateId(String aggregateId) {
            this.aggregateId = aggregateId;
            return self();
        }

        public T aggregateType(String aggregateType) {
            this.aggregateType = aggregateType;
            return self();
        }

        public T versionAgregado(int versionAgregado) {
            this.versionAgregado = versionAgregado;
            return self();
        }

        public T datos(Object datos) {
            this.datos = datos;
            return self();
        }
    }

    /**
     * Verifica si el evento es del tipo especificado
     */
    public boolean esDeTipo(String tipo) {
        return this.tipo.equals(tipo);
    }

    /**
     * Verifica si el evento pertenece al agregado especificado
     */
    public boolean perteneceAAgregado(String aggregateId) {
        return this.aggregateId.equals(aggregateId);
    }

    /**
     * Obtiene los datos del evento como el tipo especificado
     */
    @SuppressWarnings("unchecked")
    public <T> T obtenerDatos(Class<T> tipo) {
        if (datos != null && tipo.isAssignableFrom(datos.getClass())) {
            return (T) datos;
        }
        return null;
    }

    /**
     * Verifica si el evento tiene correlación
     */
    public boolean tieneCorrelacion() {
        return correlationId != null && !correlationId.trim().isEmpty();
    }

    /**
     * Verifica si el evento tiene causación
     */
    public boolean tieneCausacion() {
        return causationId != null && !causationId.trim().isEmpty();
    }

    @Override
    public String toString() {
        return String.format(
            "EventoDominio{id=%s, tipo='%s', timestamp=%s, aggregateId='%s', versionAgregado=%d}",
            id, tipo, timestamp, aggregateId, versionAgregado
        );
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        EventoDominio that = (EventoDominio) obj;
        return id.equals(that.id);
    }

    @Override
    public int hashCode() {
        return id.hashCode();
    }
}
