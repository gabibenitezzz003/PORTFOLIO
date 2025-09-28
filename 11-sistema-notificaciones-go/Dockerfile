# Build stage
FROM golang:1.21-alpine AS builder

# Instalar dependencias del sistema
RUN apk add --no-cache git ca-certificates tzdata

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY go.mod go.sum ./

# Descargar dependencias
RUN go mod download

# Copiar código fuente
COPY . .

# Build de la aplicación
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main cmd/servidor/main.go

# Runtime stage
FROM alpine:latest

# Instalar dependencias del sistema
RUN apk --no-cache add ca-certificates tzdata

# Crear usuario no-root
RUN adduser -D -s /bin/sh appuser

# Crear directorio de trabajo
WORKDIR /app

# Copiar binario desde builder
COPY --from=builder /app/main .

# Cambiar propietario
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/api/v1/health || exit 1

# Comando por defecto
CMD ["./main"]
