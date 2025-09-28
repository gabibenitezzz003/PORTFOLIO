package entidad

import (
	"time"
	"gorm.io/gorm"
)

// EstadoUsuario define los estados de un usuario
type EstadoUsuario string

const (
	EstadoActivo       EstadoUsuario = "activo"
	EstadoInactivo     EstadoUsuario = "inactivo"
	EstadoSuspendido   EstadoUsuario = "suspendido"
	EstadoPendiente    EstadoUsuario = "pendiente"
)

// RolUsuario define los roles de un usuario
type RolUsuario string

const (
	RolAdministrador  RolUsuario = "administrador"
	RolModerador      RolUsuario = "moderador"
	RolUsuario        RolUsuario = "usuario"
	RolInvitado       RolUsuario = "invitado"
)

// Usuario representa un usuario en el sistema
type Usuario struct {
	ID                uint           `json:"id" gorm:"primaryKey"`
	NombreUsuario     string         `json:"nombre_usuario" gorm:"uniqueIndex;not null;size:50"`
	CorreoElectronico string         `json:"correo_electronico" gorm:"uniqueIndex;not null;size:255"`
	Nombre            string         `json:"nombre" gorm:"not null;size:100"`
	Apellido          string         `json:"apellido" gorm:"not null;size:100"`
	Telefono          string         `json:"telefono" gorm:"size:20"`
	Estado            EstadoUsuario  `json:"estado" gorm:"not null;size:50;default:'activo'"`
	Rol               RolUsuario     `json:"rol" gorm:"not null;size:50;default:'usuario'"`
	CorreoVerificado  bool           `json:"correo_verificado" gorm:"default:false"`
	TelefonoVerificado bool          `json:"telefono_verificado" gorm:"default:false"`
	UltimoAcceso      *time.Time     `json:"ultimo_acceso"`
	FechaCreacion     time.Time      `json:"fecha_creacion" gorm:"autoCreateTime"`
	FechaActualizacion time.Time     `json:"fecha_actualizacion" gorm:"autoUpdateTime"`
	FechaEliminacion  gorm.DeletedAt `json:"fecha_eliminacion" gorm:"index"`
	
	// Relaciones
	Notificaciones    []Notificacion `json:"notificaciones" gorm:"foreignKey:UsuarioID"`
	Canales           []Canal        `json:"canales" gorm:"many2many:usuario_canales;"`
}

// NuevoUsuario crea una nueva instancia de Usuario
func NuevoUsuario(nombreUsuario, correoElectronico, nombre, apellido string) *Usuario {
	return &Usuario{
		NombreUsuario:     nombreUsuario,
		CorreoElectronico: correoElectronico,
		Nombre:            nombre,
		Apellido:          apellido,
		Estado:            EstadoActivo,
		Rol:               RolUsuario,
		CorreoVerificado:  false,
		TelefonoVerificado: false,
	}
}

// ObtenerNombreCompleto retorna el nombre completo del usuario
func (u *Usuario) ObtenerNombreCompleto() string {
	return u.Nombre + " " + u.Apellido
}

// EstaActivo verifica si el usuario está activo
func (u *Usuario) EstaActivo() bool {
	return u.Estado == EstadoActivo
}

// EsAdministrador verifica si el usuario es administrador
func (u *Usuario) EsAdministrador() bool {
	return u.Rol == RolAdministrador
}

// EsModerador verifica si el usuario es moderador
func (u *Usuario) EsModerador() bool {
	return u.Rol == RolModerador
}

// ActualizarUltimoAcceso actualiza la fecha del último acceso
func (u *Usuario) ActualizarUltimoAcceso() {
	ahora := time.Now()
	u.UltimoAcceso = &ahora
}

// VerificarCorreo marca el correo como verificado
func (u *Usuario) VerificarCorreo() {
	u.CorreoVerificado = true
}

// VerificarTelefono marca el teléfono como verificado
func (u *Usuario) VerificarTelefono() {
	u.TelefonoVerificado = true
}

// Activar activa el usuario
func (u *Usuario) Activar() {
	u.Estado = EstadoActivo
}

// Desactivar desactiva el usuario
func (u *Usuario) Desactivar() {
	u.Estado = EstadoInactivo
}

// Suspender suspende el usuario
func (u *Usuario) Suspender() {
	u.Estado = EstadoSuspendido
}

// CambiarRol cambia el rol del usuario
func (u *Usuario) CambiarRol(nuevoRol RolUsuario) {
	u.Rol = nuevoRol
}

// Validar valida el usuario
func (u *Usuario) Validar() error {
	if u.NombreUsuario == "" {
		return NewErrorValidacion("Nombre de usuario es requerido")
	}
	if u.CorreoElectronico == "" {
		return NewErrorValidacion("Correo electrónico es requerido")
	}
	if u.Nombre == "" {
		return NewErrorValidacion("Nombre es requerido")
	}
	if u.Apellido == "" {
		return NewErrorValidacion("Apellido es requerido")
	}
	return nil
}
