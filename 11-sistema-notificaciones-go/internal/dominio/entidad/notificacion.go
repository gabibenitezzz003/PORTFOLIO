package entidad

import (
	"time"
	"gorm.io/gorm"
)

// TipoNotificacion define los tipos de notificación
type TipoNotificacion string

const (
	TipoEmail        TipoNotificacion = "email"
	TipoSMS          TipoNotificacion = "sms"
	TipoPush         TipoNotificacion = "push"
	TipoWebSocket    TipoNotificacion = "websocket"
	TipoInApp        TipoNotificacion = "in_app"
)

// EstadoNotificacion define los estados de una notificación
type EstadoNotificacion string

const (
	EstadoPendiente    EstadoNotificacion = "pendiente"
	EstadoEnviada      EstadoNotificacion = "enviada"
	EstadoEntregada    EstadoNotificacion = "entregada"
	EstadoLeida        EstadoNotificacion = "leida"
	EstadoFallida      EstadoNotificacion = "fallida"
	EstadoCancelada    EstadoNotificacion = "cancelada"
)

// PrioridadNotificacion define la prioridad de una notificación
type PrioridadNotificacion string

const (
	PrioridadBaja      PrioridadNotificacion = "baja"
	PrioridadNormal    PrioridadNotificacion = "normal"
	PrioridadAlta      PrioridadNotificacion = "alta"
	PrioridadCritica   PrioridadNotificacion = "critica"
)

// Notificacion representa una notificación en el sistema
type Notificacion struct {
	ID                uint                   `json:"id" gorm:"primaryKey"`
	UsuarioID         uint                   `json:"usuario_id" gorm:"not null;index"`
	Usuario           Usuario                `json:"usuario" gorm:"foreignKey:UsuarioID"`
	Titulo            string                 `json:"titulo" gorm:"not null;size:255"`
	Mensaje           string                 `json:"mensaje" gorm:"not null;type:text"`
	Tipo              TipoNotificacion       `json:"tipo" gorm:"not null;size:50"`
	Estado            EstadoNotificacion     `json:"estado" gorm:"not null;size:50;default:'pendiente'"`
	Prioridad         PrioridadNotificacion  `json:"prioridad" gorm:"not null;size:50;default:'normal'"`
	CanalID           uint                   `json:"canal_id" gorm:"index"`
	Canal             Canal                  `json:"canal" gorm:"foreignKey:CanalID"`
	Metadatos         map[string]interface{} `json:"metadatos" gorm:"type:jsonb"`
	FechaProgramada   *time.Time             `json:"fecha_programada"`
	FechaEnviada      *time.Time             `json:"fecha_enviada"`
	FechaLeida        *time.Time             `json:"fecha_leida"`
	IntentosEnvio     int                    `json:"intentos_envio" gorm:"default:0"`
	MaxIntentos       int                    `json:"max_intentos" gorm:"default:3"`
	FechaCreacion     time.Time              `json:"fecha_creacion" gorm:"autoCreateTime"`
	FechaActualizacion time.Time             `json:"fecha_actualizacion" gorm:"autoUpdateTime"`
	FechaEliminacion  gorm.DeletedAt         `json:"fecha_eliminacion" gorm:"index"`
}

// NuevaNotificacion crea una nueva instancia de Notificacion
func NuevaNotificacion(usuarioID uint, titulo, mensaje string, tipo TipoNotificacion) *Notificacion {
	return &Notificacion{
		UsuarioID: usuarioID,
		Titulo:    titulo,
		Mensaje:   mensaje,
		Tipo:      tipo,
		Estado:    EstadoPendiente,
		Prioridad: PrioridadNormal,
		MaxIntentos: 3,
	}
}

// MarcarComoEnviada marca la notificación como enviada
func (n *Notificacion) MarcarComoEnviada() {
	n.Estado = EstadoEnviada
	ahora := time.Now()
	n.FechaEnviada = &ahora
}

// MarcarComoEntregada marca la notificación como entregada
func (n *Notificacion) MarcarComoEntregada() {
	n.Estado = EstadoEntregada
}

// MarcarComoLeida marca la notificación como leída
func (n *Notificacion) MarcarComoLeida() {
	n.Estado = EstadoLeida
	ahora := time.Now()
	n.FechaLeida = &ahora
}

// MarcarComoFallida marca la notificación como fallida
func (n *Notificacion) MarcarComoFallida() {
	n.Estado = EstadoFallida
}

// IncrementarIntentos incrementa el contador de intentos
func (n *Notificacion) IncrementarIntentos() {
	n.IntentosEnvio++
}

// PuedeReintentar verifica si la notificación puede ser reintentada
func (n *Notificacion) PuedeReintentar() bool {
	return n.IntentosEnvio < n.MaxIntentos && n.Estado == EstadoFallida
}

// EsUrgente verifica si la notificación es urgente
func (n *Notificacion) EsUrgente() bool {
	return n.Prioridad == PrioridadAlta || n.Prioridad == PrioridadCritica
}

// EstaProgramada verifica si la notificación está programada para el futuro
func (n *Notificacion) EstaProgramada() bool {
	return n.FechaProgramada != nil && n.FechaProgramada.After(time.Now())
}

// ObtenerMetadato obtiene un metadato específico
func (n *Notificacion) ObtenerMetadato(clave string) (interface{}, bool) {
	if n.Metadatos == nil {
		return nil, false
	}
	valor, existe := n.Metadatos[clave]
	return valor, existe
}

// EstablecerMetadato establece un metadato
func (n *Notificacion) EstablecerMetadato(clave string, valor interface{}) {
	if n.Metadatos == nil {
		n.Metadatos = make(map[string]interface{})
	}
	n.Metadatos[clave] = valor
}

// Validar valida la notificación
func (n *Notificacion) Validar() error {
	if n.UsuarioID == 0 {
		return NewErrorValidacion("UsuarioID es requerido")
	}
	if n.Titulo == "" {
		return NewErrorValidacion("Título es requerido")
	}
	if n.Mensaje == "" {
		return NewErrorValidacion("Mensaje es requerido")
	}
	if n.Tipo == "" {
		return NewErrorValidacion("Tipo es requerido")
	}
	return nil
}
