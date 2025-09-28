package objetoValor

import (
	"regexp"
	"strings"
)

// Telefono representa un número de teléfono válido
type Telefono struct {
	valor string
}

var (
	patronTelefono = regexp.MustCompile(`^\+?[1-9]\d{1,14}$`)
)

// NuevoTelefono crea una nueva instancia de Telefono
func NuevoTelefono(telefono string) (*Telefono, error) {
	if telefono == "" {
		return nil, NewErrorValidacion("Teléfono no puede estar vacío")
	}

	// Limpiar el teléfono removiendo espacios, guiones y paréntesis
	telefonoLimpio := strings.ReplaceAll(telefono, " ", "")
	telefonoLimpio = strings.ReplaceAll(telefonoLimpio, "-", "")
	telefonoLimpio = strings.ReplaceAll(telefonoLimpio, "(", "")
	telefonoLimpio = strings.ReplaceAll(telefonoLimpio, ")", "")
	telefonoLimpio = strings.ReplaceAll(telefonoLimpio, ".", "")

	if !patronTelefono.MatchString(telefonoLimpio) {
		return nil, NewErrorValidacion("Formato de teléfono inválido")
	}

	return &Telefono{valor: telefonoLimpio}, nil
}

// ObtenerValor retorna el valor del teléfono
func (t *Telefono) ObtenerValor() string {
	return t.valor
}

// ObtenerCodigoPais retorna el código de país del teléfono
func (t *Telefono) ObtenerCodigoPais() string {
	if strings.HasPrefix(t.valor, "+") {
		// Buscar el código de país (1-3 dígitos después del +)
		for i := 1; i <= 3 && i < len(t.valor); i++ {
			if len(t.valor) > i+7 { // Mínimo 7 dígitos para el número local
				return t.valor[1 : i+1]
			}
		}
	}
	return ""
}

// ObtenerNumeroLocal retorna el número local sin código de país
func (t *Telefono) ObtenerNumeroLocal() string {
	codigoPais := t.ObtenerCodigoPais()
	if codigoPais != "" {
		return t.valor[len(codigoPais)+1:]
	}
	return t.valor
}

// EsInternacional verifica si es un número internacional
func (t *Telefono) EsInternacional() bool {
	return strings.HasPrefix(t.valor, "+")
}

// Formatear formatea el teléfono para mostrar
func (t *Telefono) Formatear() string {
	numero := t.valor
	if strings.HasPrefix(numero, "+") {
		numero = numero[1:]
	}

	// Formatear según la longitud
	switch len(numero) {
	case 10: // Número local de 10 dígitos
		return "(" + numero[:3] + ") " + numero[3:6] + "-" + numero[6:]
	case 11: // Número con código de área
		return "+" + numero[:1] + " (" + numero[1:4] + ") " + numero[4:7] + "-" + numero[7:]
	default:
		return "+" + numero
	}
}

// String implementa la interfaz Stringer
func (t *Telefono) String() string {
	return t.valor
}

// Equals verifica si dos teléfonos son iguales
func (t *Telefono) Equals(otro *Telefono) bool {
	if otro == nil {
		return false
	}
	return t.valor == otro.valor
}
