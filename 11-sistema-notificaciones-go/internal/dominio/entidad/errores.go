package entidad

import "errors"

// ErrorValidacion representa un error de validación
type ErrorValidacion struct {
	Mensaje string
}

func (e *ErrorValidacion) Error() string {
	return e.Mensaje
}

// NewErrorValidacion crea un nuevo error de validación
func NewErrorValidacion(mensaje string) *ErrorValidacion {
	return &ErrorValidacion{Mensaje: mensaje}
}

// ErrorDominio representa un error de dominio
type ErrorDominio struct {
	Mensaje string
}

func (e *ErrorDominio) Error() string {
	return e.Mensaje
}

// NewErrorDominio crea un nuevo error de dominio
func NewErrorDominio(mensaje string) *ErrorDominio {
	return &ErrorDominio{Mensaje: mensaje}
}

// Errores comunes del dominio
var (
	ErrUsuarioNoEncontrado     = errors.New("usuario no encontrado")
	ErrNotificacionNoEncontrada = errors.New("notificación no encontrada")
	ErrCanalNoEncontrado       = errors.New("canal no encontrado")
	ErrUsuarioInactivo         = errors.New("usuario inactivo")
	ErrCanalInactivo           = errors.New("canal inactivo")
	ErrNotificacionYaEnviada   = errors.New("notificación ya enviada")
	ErrNotificacionCancelada   = errors.New("notificación cancelada")
	ErrMaxIntentosExcedidos    = errors.New("máximo de intentos excedido")
)
