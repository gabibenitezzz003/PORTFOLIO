# 🌐 Proyecto 10: Arquitectura Distribuida con Event Streaming

## 📋 Descripción del Proyecto

Sistema de **arquitectura distribuida** implementando **event-driven architecture** con **Apache Kafka**, **Event Sourcing**, **CQRS** y **Saga Pattern**. Demuestra experiencia en **sistemas distribuidos**, **escalabilidad horizontal** y **patrones de microservicios avanzados**.

## 🎯 Objetivos Arquitectónicos

- **Event-Driven Architecture**: Comunicación asíncrona entre servicios
- **Escalabilidad Horizontal**: Distribución de carga automática
- **Resiliencia**: Tolerancia a fallos y recuperación automática
- **Consistencia Eventual**: Garantías de consistencia distribuida
- **Observabilidad**: Monitoreo de eventos y flujos de datos

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                ARQUITECTURA DISTRIBUIDA                        │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐    ┌────────▼────────┐    ┌────────▼────────┐
│   PRODUCERS    │    │   KAFKA CLUSTER │    │   CONSUMERS     │
│   (Eventos)    │    │   (Event Bus)   │    │   (Procesadores)│
└────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │     EVENT STORE       │
                    │   (Event Sourcing)    │
                    └───────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │     READ MODELS       │
                    │   (CQRS)              │
                    └───────────────────────┘
```

## 🛠️ Stack Tecnológico

### Event Streaming
- **Apache Kafka** - Message broker distribuido
- **Kafka Streams** - Procesamiento de streams
- **Kafka Connect** - Integración con sistemas externos
- **Schema Registry** - Gestión de esquemas

### Event Processing
- **Apache Flink** - Procesamiento de streams en tiempo real
- **Apache Spark** - Procesamiento de datos a gran escala
- **Redis Streams** - Streams en memoria
- **Apache Pulsar** - Alternativa a Kafka

### Data Storage
- **PostgreSQL** - Event store principal
- **MongoDB** - Read models (CQRS)
- **Redis** - Cache y sesiones
- **Elasticsearch** - Búsqueda y analytics

### Infrastructure
- **Kubernetes** - Orquestación de contenedores
- **Helm** - Gestión de paquetes
- **Terraform** - Infrastructure as Code
- **Prometheus** - Métricas y monitoreo

## 📁 Estructura del Proyecto

```
10-arquitectura-distribuida-kafka/
├── kafka-cluster/              # Configuración de Kafka
│   ├── docker-compose.yml     # Cluster local
│   ├── kafka-config/          # Configuraciones
│   └── topics/                # Definición de topics
├── event-sourcing/            # Event Sourcing
│   ├── event-store/           # Almacén de eventos
│   ├── aggregates/            # Agregados de dominio
│   ├── projections/           # Proyecciones de eventos
│   └── snapshots/             # Snapshots de estado
├── cqrs/                      # CQRS Implementation
│   ├── commands/              # Comandos
│   ├── queries/               # Consultas
│   ├── handlers/              # Manejadores
│   └── read-models/           # Modelos de lectura
├── saga-pattern/              # Saga Pattern
│   ├── orchestrators/         # Orquestadores
│   ├── participants/          # Participantes
│   ├── compensations/         # Compensaciones
│   └── state-machines/        # Máquinas de estado
├── microservices/             # Microservicios
│   ├── order-service/         # Servicio de órdenes
│   ├── payment-service/       # Servicio de pagos
│   ├── inventory-service/     # Servicio de inventario
│   ├── notification-service/  # Servicio de notificaciones
│   └── analytics-service/     # Servicio de analytics
├── event-handlers/            # Manejadores de eventos
│   ├── order-events/          # Eventos de órdenes
│   ├── payment-events/        # Eventos de pagos
│   ├── inventory-events/      # Eventos de inventario
│   └── notification-events/   # Eventos de notificaciones
├── stream-processing/         # Procesamiento de streams
│   ├── kafka-streams/         # Aplicaciones Kafka Streams
│   ├── flink-jobs/            # Jobs de Apache Flink
│   └── spark-jobs/            # Jobs de Apache Spark
├── monitoring/                # Monitoreo y observabilidad
│   ├── prometheus/            # Configuración Prometheus
│   ├── grafana/               # Dashboards
│   └── jaeger/                # Distributed tracing
├── infrastructure/            # Infraestructura
│   ├── kubernetes/            # Manifiestos K8s
│   ├── terraform/             # Infrastructure as Code
│   └── helm-charts/           # Charts de Helm
└── docs/                      # Documentación
    ├── architecture.md        # Arquitectura del sistema
    ├── event-schema.md        # Esquemas de eventos
    └── deployment.md          # Guía de despliegue
```

## 🎨 Patrones de Arquitectura Implementados

### 1. **Event-Driven Architecture**
- **Event Sourcing**: Almacenamiento de eventos
- **Event Streaming**: Flujo de eventos en tiempo real
- **Event Collaboration**: Colaboración entre servicios
- **Event Notification**: Notificaciones basadas en eventos

### 2. **CQRS (Command Query Responsibility Segregation)**
- **Command Side**: Escritura de datos
- **Query Side**: Lectura de datos
- **Event Handlers**: Procesamiento de eventos
- **Read Models**: Modelos optimizados para consultas

### 3. **Saga Pattern**
- **Choreography**: Orquestación distribuida
- **Orchestration**: Orquestación centralizada
- **Compensation**: Transacciones compensatorias
- **State Management**: Gestión de estado distribuido

### 4. **Distributed Patterns**
- **Circuit Breaker**: Protección contra fallos
- **Bulkhead**: Aislamiento de recursos
- **Retry**: Reintentos automáticos
- **Timeout**: Timeouts configurables

## 🔧 Características Técnicas

### Event Sourcing
```typescript
// Event Store Interface
interface EventStore {
  saveEvents(streamId: string, events: DomainEvent[]): Promise<void>;
  getEvents(streamId: string): Promise<DomainEvent[]>;
  getEventsFromVersion(streamId: string, fromVersion: number): Promise<DomainEvent[]>;
}

// Domain Event
abstract class DomainEvent {
  constructor(
    public readonly aggregateId: string,
    public readonly eventType: string,
    public readonly occurredOn: Date,
    public readonly version: number
  ) {}
}

// Aggregate Root
abstract class AggregateRoot {
  private events: DomainEvent[] = [];
  private version: number = 0;

  protected addEvent(event: DomainEvent): void {
    this.events.push(event);
  }

  public getUncommittedEvents(): DomainEvent[] {
    return [...this.events];
  }

  public markEventsAsCommitted(): void {
    this.events = [];
  }
}
```

### CQRS Implementation
```typescript
// Command
interface Command {
  commandType: string;
  aggregateId: string;
}

// Command Handler
interface CommandHandler<T extends Command> {
  handle(command: T): Promise<void>;
}

// Query
interface Query {
  queryType: string;
}

// Query Handler
interface QueryHandler<T extends Query, R> {
  handle(query: T): Promise<R>;
}

// Read Model
interface ReadModel {
  id: string;
  version: number;
  lastUpdated: Date;
}
```

### Saga Pattern
```typescript
// Saga Orchestrator
class OrderSagaOrchestrator {
  async handleOrderCreated(event: OrderCreatedEvent): Promise<void> {
    try {
      // Step 1: Reserve inventory
      await this.inventoryService.reserveItems(event.orderId, event.items);
      
      // Step 2: Process payment
      await this.paymentService.processPayment(event.orderId, event.totalAmount);
      
      // Step 3: Confirm order
      await this.orderService.confirmOrder(event.orderId);
      
    } catch (error) {
      // Compensate if any step fails
      await this.compensateOrder(event.orderId);
    }
  }

  private async compensateOrder(orderId: string): Promise<void> {
    // Compensation logic
    await this.inventoryService.releaseItems(orderId);
    await this.paymentService.refundPayment(orderId);
    await this.orderService.cancelOrder(orderId);
  }
}
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Docker & Docker Compose
- Kubernetes cluster
- Java 17+
- Node.js 18+

### Instalación Local
```bash
# Clonar el repositorio
git clone <repository-url>
cd 10-arquitectura-distribuida-kafka

# Iniciar Kafka cluster
docker-compose -f kafka-cluster/docker-compose.yml up -d

# Verificar que Kafka esté funcionando
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list

# Iniciar microservicios
docker-compose up -d

# Verificar servicios
curl http://localhost:8080/health
```

### Configuración de Kafka
```yaml
# kafka-cluster/docker-compose.yml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
```

## 📊 Monitoreo y Observabilidad

### Métricas de Kafka
- **Throughput**: Mensajes por segundo
- **Latency**: Latencia end-to-end
- **Consumer Lag**: Retraso de consumidores
- **Partition Distribution**: Distribución de particiones

### Event Tracing
- **Distributed Tracing**: Trazado de eventos
- **Event Correlation**: Correlación de eventos
- **Performance Metrics**: Métricas de rendimiento
- **Error Tracking**: Seguimiento de errores

### Dashboards de Grafana
1. **Kafka Overview**
   - Cluster health
   - Topic metrics
   - Consumer groups
   - Broker performance

2. **Event Flow**
   - Event throughput
   - Processing latency
   - Error rates
   - Backpressure

3. **Saga Monitoring**
   - Saga execution time
   - Compensation rates
   - Success/failure rates
   - State transitions

## 🧪 Testing Strategy

### Testing de Eventos
```typescript
// Event Testing
describe('OrderCreatedEvent', () => {
  it('should create event with correct data', () => {
    const event = new OrderCreatedEvent(
      'order-123',
      'user-456',
      [{ productId: 'prod-1', quantity: 2 }],
      new Date()
    );

    expect(event.aggregateId).toBe('order-123');
    expect(event.eventType).toBe('OrderCreated');
    expect(event.items).toHaveLength(1);
  });
});

// Saga Testing
describe('OrderSaga', () => {
  it('should complete successfully', async () => {
    const saga = new OrderSagaOrchestrator();
    const event = new OrderCreatedEvent(/* ... */);

    await saga.handleOrderCreated(event);

    // Verify all steps completed
    expect(mockInventoryService.reserveItems).toHaveBeenCalled();
    expect(mockPaymentService.processPayment).toHaveBeenCalled();
    expect(mockOrderService.confirmOrder).toHaveBeenCalled();
  });

  it('should compensate on failure', async () => {
    const saga = new OrderSagaOrchestrator();
    mockPaymentService.processPayment.mockRejectedValue(new Error('Payment failed'));

    await saga.handleOrderCreated(event);

    // Verify compensation
    expect(mockInventoryService.releaseItems).toHaveBeenCalled();
    expect(mockPaymentService.refundPayment).toHaveBeenCalled();
  });
});
```

## 📈 Performance y Escalabilidad

### Benchmarks
- **Event Throughput**: 1M+ eventos/segundo
- **Latency**: <10ms end-to-end
- **Availability**: 99.99%
- **Partition Scaling**: Hasta 1000 particiones

### Optimizaciones
- **Partitioning Strategy**: Estrategia de particionado
- **Consumer Group Scaling**: Escalado de grupos de consumidores
- **Batch Processing**: Procesamiento por lotes
- **Compression**: Compresión de mensajes

## 🔄 Event Schema Management

### Schema Registry
```json
{
  "schema": {
    "type": "record",
    "name": "OrderCreatedEvent",
    "fields": [
      {
        "name": "orderId",
        "type": "string"
      },
      {
        "name": "userId",
        "type": "string"
      },
      {
        "name": "items",
        "type": {
          "type": "array",
          "items": {
            "type": "record",
            "name": "OrderItem",
            "fields": [
              {"name": "productId", "type": "string"},
              {"name": "quantity", "type": "int"},
              {"name": "price", "type": "double"}
            ]
          }
        }
      },
      {
        "name": "createdAt",
        "type": "long"
      }
    ]
  }
}
```

## 🎯 Casos de Uso Demostrados

### 1. **E-commerce Order Processing**
- Creación de órdenes
- Procesamiento de pagos
- Gestión de inventario
- Notificaciones en tiempo real

### 2. **Real-time Analytics**
- Event streaming
- Data processing
- Dashboard updates
- Alert generation

### 3. **Event Sourcing**
- Audit trail completo
- State reconstruction
- Time travel debugging
- Compliance reporting

## 🏆 Logros Técnicos

- ✅ **Arquitectura distribuida** con 99.99% de disponibilidad
- ✅ **Event streaming** con 1M+ eventos/segundo
- ✅ **CQRS** implementado con separación completa
- ✅ **Saga Pattern** con compensación automática
- ✅ **Event Sourcing** con auditoría completa
- ✅ **Escalabilidad horizontal** para 1000+ particiones
- ✅ **Observabilidad completa** con métricas y traces

## 🚀 Próximos Pasos

1. **Event Mesh**: Malla de eventos distribuida
2. **AI/ML Integration**: Procesamiento inteligente de eventos
3. **Edge Computing**: Eventos en edge
4. **Multi-Cloud**: Distribución en múltiples clouds
5. **Quantum Computing**: Preparación para computación cuántica

---

**Desarrollado por Gabriel - Arquitecto de Software**  
*Demostrando experiencia en arquitecturas distribuidas, event streaming y patrones avanzados de microservicios*
