package objetoValor

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

// Errores comunes de objetos valor
var (
	ErrCorreoInvalido     = errors.New("correo electrónico inválido")
	ErrTelefonoInvalido   = errors.New("teléfono inválido")
	ErrMensajeVacio       = errors.New("mensaje no puede estar vacío")
	ErrTituloVacio        = errors.New("título no puede estar vacío")
)
