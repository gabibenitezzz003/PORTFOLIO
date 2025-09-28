# Multi-stage build para optimizar el tamaño de la imagen
FROM maven:3.9.5-openjdk-17-slim AS builder

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY pom.xml .
COPY microservicios/servicio-usuarios/pom.xml microservicios/servicio-usuarios/

# Descargar dependencias (se cachean si no cambian)
RUN mvn dependency:go-offline -f microservicios/servicio-usuarios/pom.xml

# Copiar código fuente
COPY microservicios/servicio-usuarios/src microservicios/servicio-usuarios/src

# Compilar la aplicación
RUN mvn clean package -f microservicios/servicio-usuarios/pom.xml -DskipTests

# Runtime stage
FROM openjdk:17-jre-slim

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de trabajo
WORKDIR /app

# Copiar JAR desde builder
COPY --from=builder /app/microservicios/servicio-usuarios/target/servicio-usuarios-*.jar app.jar

# Cambiar propietario
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

# Comando por defecto
ENTRYPOINT ["java", "-jar", "app.jar"]
