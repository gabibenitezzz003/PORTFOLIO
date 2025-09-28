package entidad

import (
	"time"
	"gorm.io/gorm"
)

// TipoCanal define los tipos de canal
type TipoCanal string

const (
	TipoCanalGeneral     TipoCanal = "general"
	TipoCanalMarketing   TipoCanal = "marketing"
	TipoCanalSistema     TipoCanal = "sistema"
	TipoCanalPromociones TipoCanal = "promociones"
	TipoCanalSeguridad   TipoCanal = "seguridad"
)

// EstadoCanal define los estados de un canal
type EstadoCanal string

const (
	EstadoCanalActivo   EstadoCanal = "activo"
	EstadoCanalInactivo EstadoCanal = "inactivo"
	EstadoCanalPausado  EstadoCanal = "pausado"
)

// Canal representa un canal de notificaciones
type Canal struct {
	ID                uint           `json:"id" gorm:"primaryKey"`
	Nombre            string         `json:"nombre" gorm:"not null;size:100"`
	Descripcion       string         `json:"descripcion" gorm:"size:500"`
	Tipo              TipoCanal      `json:"tipo" gorm:"not null;size:50"`
	Estado            EstadoCanal    `json:"estado" gorm:"not null;size:50;default:'activo'"`
	Configuracion     map[string]interface{} `json:"configuracion" gorm:"type:jsonb"`
	FechaCreacion     time.Time      `json:"fecha_creacion" gorm:"autoCreateTime"`
	FechaActualizacion time.Time     `json:"fecha_actualizacion" gorm:"autoUpdateTime"`
	FechaEliminacion  gorm.DeletedAt `json:"fecha_eliminacion" gorm:"index"`
	
	// Relaciones
	Usuarios          []Usuario      `json:"usuarios" gorm:"many2many:usuario_canales;"`
	Notificaciones    []Notificacion `json:"notificaciones" gorm:"foreignKey:CanalID"`
}

// NuevoCanal crea una nueva instancia de Canal
func NuevoCanal(nombre, descripcion string, tipo TipoCanal) *Canal {
	return &Canal{
		Nombre:        nombre,
		Descripcion:   descripcion,
		Tipo:          tipo,
		Estado:        EstadoCanalActivo,
		Configuracion: make(map[string]interface{}),
	}
}

// EstaActivo verifica si el canal está activo
func (c *Canal) EstaActivo() bool {
	return c.Estado == EstadoCanalActivo
}

// Activar activa el canal
func (c *Canal) Activar() {
	c.Estado = EstadoCanalActivo
}

// Desactivar desactiva el canal
func (c *Canal) Desactivar() {
	c.Estado = EstadoCanalInactivo
}

// Pausar pausa el canal
func (c *Canal) Pausar() {
	c.Estado = EstadoCanalPausado
}

// ObtenerConfiguracion obtiene una configuración específica
func (c *Canal) ObtenerConfiguracion(clave string) (interface{}, bool) {
	if c.Configuracion == nil {
		return nil, false
	}
	valor, existe := c.Configuracion[clave]
	return valor, existe
}

// EstablecerConfiguracion establece una configuración
func (c *Canal) EstablecerConfiguracion(clave string, valor interface{}) {
	if c.Configuracion == nil {
		c.Configuracion = make(map[string]interface{})
	}
	c.Configuracion[clave] = valor
}

// Validar valida el canal
func (c *Canal) Validar() error {
	if c.Nombre == "" {
		return NewErrorValidacion("Nombre es requerido")
	}
	if c.Tipo == "" {
		return NewErrorValidacion("Tipo es requerido")
	}
	return nil
}
