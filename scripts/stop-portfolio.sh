#!/bin/bash

# Script para detener el Portfolio Completo
# Portfolio de Gabriel para GreenCode Software

echo "🛑 Deteniendo Portfolio Completo - Gabriel"
echo "=========================================="

# Detener servicios
echo "🐳 Deteniendo servicios con Docker Compose..."
docker-compose down

# Limpiar contenedores huérfanos
echo "🧹 Limpiando contenedores huérfanos..."
docker-compose down --remove-orphans

# Mostrar estado
echo "📊 Estado actual de los servicios:"
docker-compose ps

echo ""
echo "✅ Portfolio detenido exitosamente!"
echo ""
echo "💡 Para limpiar completamente (eliminar volúmenes):"
echo "   docker-compose down -v"
echo ""
echo "💡 Para limpiar imágenes no utilizadas:"
echo "   docker system prune -a"
echo ""
echo "¡Hasta la próxima! 👋"
