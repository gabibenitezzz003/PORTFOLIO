package main

import (
	"log"
	"sistema-notificaciones-go/internal/infraestructura/configuracion"
	"sistema-notificaciones-go/internal/presentacion/controlador"
	"sistema-notificaciones-go/internal/presentacion/middleware"
	"sistema-notificaciones-go/pkg/logger"

	"github.com/gin-gonic/gin"
)

// @title Sistema de Notificaciones API
// @version 1.0
// @description API para sistema de notificaciones en tiempo real
// @host localhost:8080
// @BasePath /api/v1
func main() {
	// Configurar logger
	logger := logger.NuevoLogger()
	logger.Info("Iniciando Sistema de Notificaciones")

	// Cargar configuración
	config, err := configuracion.CargarConfiguracion()
	if err != nil {
		logger.Fatal("Error cargando configuración", "error", err)
	}

	// Configurar Gin
	if config.Modo == "produccion" {
		gin.SetMode(gin.ReleaseMode)
	}

	// Crear router
	router := gin.New()

	// Aplicar middleware global
	router.Use(middleware.Logger(logger))
	router.Use(middleware.Recovery(logger))
	router.Use(middleware.CORS())

	// Configurar rutas
	configurarRutas(router, config, logger)

	// Iniciar servidor
	puerto := config.Puerto
	if puerto == "" {
		puerto = "8080"
	}

	logger.Info("Servidor iniciado", "puerto", puerto)
	if err := router.Run(":" + puerto); err != nil {
		log.Fatal("Error iniciando servidor:", err)
	}
}

func configurarRutas(router *gin.Engine, config *configuracion.Configuracion, logger *logger.Logger) {
	// Grupo de API v1
	v1 := router.Group("/api/v1")

	// Health check
	v1.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"estado": "funcionando",
			"servicio": "sistema-notificaciones-go",
		})
	})

	// Configurar controladores
	controladorNotificacion := controlador.NuevoControladorNotificacion(config, logger)
	controladorWebSocket := controlador.NuevoControladorWebSocket(config, logger)

	// Rutas de notificaciones
	notificaciones := v1.Group("/notificaciones")
	{
		notificaciones.POST("", controladorNotificacion.EnviarNotificacion)
		notificaciones.GET("", controladorNotificacion.ObtenerNotificaciones)
		notificaciones.GET("/:id", controladorNotificacion.ObtenerNotificacionPorID)
		notificaciones.PUT("/:id/marcar-leida", controladorNotificacion.MarcarComoLeida)
		notificaciones.DELETE("/:id", controladorNotificacion.EliminarNotificacion)
	}

	// WebSocket para notificaciones en tiempo real
	v1.GET("/ws", controladorWebSocket.ManejarWebSocket)
}
