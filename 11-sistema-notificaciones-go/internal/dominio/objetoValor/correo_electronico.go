package objetoValor

import (
	"regexp"
	"strings"
)

// CorreoElectronico representa un correo electrónico válido
type CorreoElectronico struct {
	valor string
}

var (
	patronCorreo = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
)

// NuevoCorreoElectronico crea una nueva instancia de CorreoElectronico
func NuevoCorreoElectronico(correo string) (*CorreoElectronico, error) {
	if correo == "" {
		return nil, NewErrorValidacion("Correo electrónico no puede estar vacío")
	}

	correoLimpio := strings.TrimSpace(strings.ToLower(correo))

	if !patronCorreo.MatchString(correoLimpio) {
		return nil, NewErrorValidacion("Formato de correo electrónico inválido")
	}

	return &CorreoElectronico{valor: correoLimpio}, nil
}

// ObtenerValor retorna el valor del correo electrónico
func (c *CorreoElectronico) ObtenerValor() string {
	return c.valor
}

// ObtenerDominio retorna el dominio del correo electrónico
func (c *CorreoElectronico) ObtenerDominio() string {
	partes := strings.Split(c.valor, "@")
	if len(partes) != 2 {
		return ""
	}
	return partes[1]
}

// ObtenerParteLocal retorna la parte local del correo electrónico
func (c *CorreoElectronico) ObtenerParteLocal() string {
	partes := strings.Split(c.valor, "@")
	if len(partes) != 2 {
		return c.valor
	}
	return partes[0]
}

// EsDelDominio verifica si el correo es de un dominio específico
func (c *CorreoElectronico) EsDelDominio(dominio string) bool {
	return strings.HasSuffix(c.valor, "@"+strings.ToLower(dominio))
}

// EsCorreoCorporativo verifica si es un correo corporativo
func (c *CorreoElectronico) EsCorreoCorporativo() bool {
	dominiosPersonales := []string{
		"gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
		"live.com", "msn.com", "aol.com", "icloud.com",
	}

	for _, dominio := range dominiosPersonales {
		if c.EsDelDominio(dominio) {
			return false
		}
	}

	return true
}

// String implementa la interfaz Stringer
func (c *CorreoElectronico) String() string {
	return c.valor
}

// Equals verifica si dos correos electrónicos son iguales
func (c *CorreoElectronico) Equals(otro *CorreoElectronico) bool {
	if otro == nil {
		return false
	}
	return c.valor == otro.valor
}
