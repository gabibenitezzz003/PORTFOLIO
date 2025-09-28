package com.portfolio.arquitectura.eventos;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

/**
 * Evento de dominio: Orden Creada
 * 
 * Se publica cuando se crea una nueva orden en el sistema.
 * Este evento inicia el proceso de Saga para el procesamiento de la orden.
 * 
 * @author Gabriel - Arquitecto de Software
 */
public class OrdenCreadaEvento extends EventoDominio {

    private final DatosOrdenCreada datosOrden;

    private OrdenCreadaEvento(Builder builder) {
        super(builder);
        this.datosOrden = (DatosOrdenCreada) builder.datos;
    }

    public DatosOrdenCreada getDatosOrden() {
        return datosOrden;
    }

    /**
     * Datos específicos del evento Orden Creada
     */
    public static class DatosOrdenCreada {
        private final UUID ordenId;
        private final UUID clienteId;
        private final List<ItemOrden> items;
        private final BigDecimal total;
        private final String moneda;
        private final String direccionEnvio;
        private final String metodoPago;
        private final String estado;

        public DatosOrdenCreada(UUID ordenId, UUID clienteId, List<ItemOrden> items, 
                               BigDecimal total, String moneda, String direccionEnvio, 
                               String metodoPago, String estado) {
            this.ordenId = ordenId;
            this.clienteId = clienteId;
            this.items = items;
            this.total = total;
            this.moneda = moneda;
            this.direccionEnvio = direccionEnvio;
            this.metodoPago = metodoPago;
            this.estado = estado;
        }

        // Getters
        public UUID getOrdenId() { return ordenId; }
        public UUID getClienteId() { return clienteId; }
        public List<ItemOrden> getItems() { return items; }
        public BigDecimal getTotal() { return total; }
        public String getMoneda() { return moneda; }
        public String getDireccionEnvio() { return direccionEnvio; }
        public String getMetodoPago() { return metodoPago; }
        public String getEstado() { return estado; }
    }

    /**
     * Item de la orden
     */
    public static class ItemOrden {
        private final UUID productoId;
        private final String nombre;
        private final int cantidad;
        private final BigDecimal precioUnitario;
        private final BigDecimal subtotal;

        public ItemOrden(UUID productoId, String nombre, int cantidad, 
                        BigDecimal precioUnitario, BigDecimal subtotal) {
            this.productoId = productoId;
            this.nombre = nombre;
            this.cantidad = cantidad;
            this.precioUnitario = precioUnitario;
            this.subtotal = subtotal;
        }

        // Getters
        public UUID getProductoId() { return productoId; }
        public String getNombre() { return nombre; }
        public int getCantidad() { return cantidad; }
        public BigDecimal getPrecioUnitario() { return precioUnitario; }
        public BigDecimal getSubtotal() { return subtotal; }
    }

    /**
     * Builder para OrdenCreadaEvento
     */
    public static class Builder extends EventoDominio.Builder<Builder> {
        
        public Builder() {
            super();
            this.tipo = "OrdenCreada";
        }

        @Override
        protected Builder self() {
            return this;
        }

        public Builder ordenId(UUID ordenId) {
            this.aggregateId = ordenId.toString();
            return this;
        }

        public Builder clienteId(UUID clienteId) {
            this.correlationId = clienteId.toString();
            return this;
        }

        public Builder datosOrden(DatosOrdenCreada datosOrden) {
            this.datos = datosOrden;
            return this;
        }

        public OrdenCreadaEvento build() {
            return new OrdenCreadaEvento(this);
        }
    }

    /**
     * Factory method para crear el evento
     */
    public static Builder builder() {
        return new Builder();
    }

    /**
     * Factory method para crear el evento con datos básicos
     */
    public static OrdenCreadaEvento crear(UUID ordenId, UUID clienteId, 
                                         List<ItemOrden> items, BigDecimal total, 
                                         String direccionEnvio, String metodoPago) {
        DatosOrdenCreada datos = new DatosOrdenCreada(
            ordenId, clienteId, items, total, "USD", direccionEnvio, metodoPago, "PENDIENTE"
        );

        return builder()
            .ordenId(ordenId)
            .clienteId(clienteId)
            .datosOrden(datos)
            .aggregateType("Orden")
            .versionAgregado(1)
            .build();
    }
}
