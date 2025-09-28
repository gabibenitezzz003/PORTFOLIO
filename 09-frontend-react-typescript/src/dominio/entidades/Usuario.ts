/**
 * Entidad Usuario - Capa de Dominio
 * 
 * Representa un usuario en el sistema frontend.
 * Implementa los principios de DDD con agregados bien definidos.
 * 
 * @author Gabriel - Arquitecto de Software
 */

export interface UsuarioProps {
  id: string;
  nombreUsuario: string;
  correoElectronico: string;
  nombre: string;
  apellido: string;
  telefono?: string;
  avatar?: string;
  rol: RolUsuario;
  estado: EstadoUsuario;
  preferencias: PreferenciasUsuario;
  fechaCreacion: Date;
  fechaActualizacion: Date;
  ultimoAcceso?: Date;
}

export enum RolUsuario {
  ADMINISTRADOR = 'administrador',
  USUARIO = 'usuario',
  MODERADOR = 'moderador',
  INVITADO = 'invitado'
}

export enum EstadoUsuario {
  ACTIVO = 'activo',
  INACTIVO = 'inactivo',
  SUSPENDIDO = 'suspendido',
  PENDIENTE_VERIFICACION = 'pendiente_verificacion'
}

export interface PreferenciasUsuario {
  tema: 'claro' | 'oscuro' | 'sistema';
  idioma: string;
  zonaHoraria: string;
  notificaciones: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  privacidad: {
    perfilPublico: boolean;
    mostrarEmail: boolean;
    mostrarTelefono: boolean;
  };
}

export class Usuario {
  private constructor(private props: UsuarioProps) {}

  /**
   * Factory method para crear un usuario
   */
  static crear(props: Omit<UsuarioProps, 'fechaCreacion' | 'fechaActualizacion'>): Usuario {
    const ahora = new Date();
    return new Usuario({
      ...props,
      fechaCreacion: ahora,
      fechaActualizacion: ahora
    });
  }

  /**
   * Factory method para crear desde datos existentes
   */
  static desdeDatos(props: UsuarioProps): Usuario {
    return new Usuario(props);
  }

  /**
   * Getters
   */
  get id(): string {
    return this.props.id;
  }

  get nombreUsuario(): string {
    return this.props.nombreUsuario;
  }

  get correoElectronico(): string {
    return this.props.correoElectronico;
  }

  get nombre(): string {
    return this.props.nombre;
  }

  get apellido(): string {
    return this.props.apellido;
  }

  get telefono(): string | undefined {
    return this.props.telefono;
  }

  get avatar(): string | undefined {
    return this.props.avatar;
  }

  get rol(): RolUsuario {
    return this.props.rol;
  }

  get estado(): EstadoUsuario {
    return this.props.estado;
  }

  get preferencias(): PreferenciasUsuario {
    return this.props.preferencias;
  }

  get fechaCreacion(): Date {
    return this.props.fechaCreacion;
  }

  get fechaActualizacion(): Date {
    return this.props.fechaActualizacion;
  }

  get ultimoAcceso(): Date | undefined {
    return this.props.ultimoAcceso;
  }

  /**
   * Métodos de negocio
   */
  obtenerNombreCompleto(): string {
    return `${this.props.nombre} ${this.props.apellido}`;
  }

  obtenerIniciales(): string {
    return `${this.props.nombre.charAt(0)}${this.props.apellido.charAt(0)}`.toUpperCase();
  }

  estaActivo(): boolean {
    return this.props.estado === EstadoUsuario.ACTIVO;
  }

  esAdministrador(): boolean {
    return this.props.rol === RolUsuario.ADMINISTRADOR;
  }

  esModerador(): boolean {
    return this.props.rol === RolUsuario.MODERADOR;
  }

  tienePermiso(permiso: string): boolean {
    switch (this.props.rol) {
      case RolUsuario.ADMINISTRADOR:
        return true;
      case RolUsuario.MODERADOR:
        return ['leer', 'escribir', 'moderar'].includes(permiso);
      case RolUsuario.USUARIO:
        return ['leer', 'escribir'].includes(permiso);
      case RolUsuario.INVITADO:
        return permiso === 'leer';
      default:
        return false;
    }
  }

  actualizarPerfil(datos: Partial<Pick<UsuarioProps, 'nombre' | 'apellido' | 'telefono' | 'avatar'>>): void {
    this.props = {
      ...this.props,
      ...datos,
      fechaActualizacion: new Date()
    };
  }

  actualizarPreferencias(preferencias: Partial<PreferenciasUsuario>): void {
    this.props.preferencias = {
      ...this.props.preferencias,
      ...preferencias
    };
    this.props.fechaActualizacion = new Date();
  }

  actualizarUltimoAcceso(): void {
    this.props.ultimoAcceso = new Date();
    this.props.fechaActualizacion = new Date();
  }

  cambiarEstado(nuevoEstado: EstadoUsuario): void {
    this.props.estado = nuevoEstado;
    this.props.fechaActualizacion = new Date();
  }

  cambiarRol(nuevoRol: RolUsuario): void {
    this.props.rol = nuevoRol;
    this.props.fechaActualizacion = new Date();
  }

  /**
   * Validaciones
   */
  validar(): string[] {
    const errores: string[] = [];

    if (!this.props.id || this.props.id.trim() === '') {
      errores.push('ID es requerido');
    }

    if (!this.props.nombreUsuario || this.props.nombreUsuario.trim() === '') {
      errores.push('Nombre de usuario es requerido');
    }

    if (!this.props.correoElectronico || !this.validarEmail(this.props.correoElectronico)) {
      errores.push('Correo electrónico válido es requerido');
    }

    if (!this.props.nombre || this.props.nombre.trim() === '') {
      errores.push('Nombre es requerido');
    }

    if (!this.props.apellido || this.props.apellido.trim() === '') {
      errores.push('Apellido es requerido');
    }

    if (this.props.telefono && !this.validarTelefono(this.props.telefono)) {
      errores.push('Formato de teléfono inválido');
    }

    return errores;
  }

  esValido(): boolean {
    return this.validar().length === 0;
  }

  private validarEmail(email: string): boolean {
    const patron = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return patron.test(email);
  }

  private validarTelefono(telefono: string): boolean {
    const patron = /^\+?[\d\s\-\(\)]+$/;
    return patron.test(telefono);
  }

  /**
   * Serialización
   */
  aJSON(): UsuarioProps {
    return { ...this.props };
  }

  /**
   * Métodos estáticos de utilidad
   */
  static compararPorNombre(a: Usuario, b: Usuario): number {
    return a.obtenerNombreCompleto().localeCompare(b.obtenerNombreCompleto());
  }

  static compararPorFechaCreacion(a: Usuario, b: Usuario): number {
    return b.fechaCreacion.getTime() - a.fechaCreacion.getTime();
  }

  static filtrarPorRol(usuarios: Usuario[], rol: RolUsuario): Usuario[] {
    return usuarios.filter(usuario => usuario.rol === rol);
  }

  static filtrarActivos(usuarios: Usuario[]): Usuario[] {
    return usuarios.filter(usuario => usuario.estaActivo());
  }
}
