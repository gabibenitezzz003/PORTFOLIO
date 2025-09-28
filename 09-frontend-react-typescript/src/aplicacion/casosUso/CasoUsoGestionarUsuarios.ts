import { Usuario, UsuarioProps, RolUsuario, EstadoUsuario } from '../../dominio/entidades/Usuario';
import { RepositorioUsuario } from '../../dominio/repositorios/RepositorioUsuario';
import { ServicioNotificaciones } from '../servicios/ServicioNotificaciones';
import { ServicioCache } from '../servicios/ServicioCache';
import { ErrorAplicacion } from '../excepciones/ErrorAplicacion';

/**
 * Caso de Uso para Gestionar Usuarios
 * 
 * Implementa la lógica de negocio para la gestión de usuarios,
 * incluyendo creación, actualización, eliminación y consulta.
 * 
 * @author Gabriel - Arquitecto de Software
 */
export class CasoUsoGestionarUsuarios {
  constructor(
    private repositorioUsuario: RepositorioUsuario,
    private servicioNotificaciones: ServicioNotificaciones,
    private servicioCache: ServicioCache
  ) {}

  /**
   * Crea un nuevo usuario
   */
  async crearUsuario(datosUsuario: Omit<UsuarioProps, 'id' | 'fechaCreacion' | 'fechaActualizacion'>): Promise<Usuario> {
    try {
      // Validar datos de entrada
      this.validarDatosUsuario(datosUsuario);

      // Verificar si el usuario ya existe
      const usuarioExistente = await this.repositorioUsuario.buscarPorCorreo(datosUsuario.correoElectronico);
      if (usuarioExistente) {
        throw new ErrorAplicacion('Ya existe un usuario con este correo electrónico');
      }

      const usuarioExistentePorNombre = await this.repositorioUsuario.buscarPorNombreUsuario(datosUsuario.nombreUsuario);
      if (usuarioExistentePorNombre) {
        throw new ErrorAplicacion('Ya existe un usuario con este nombre de usuario');
      }

      // Crear usuario
      const usuario = Usuario.crear(datosUsuario);

      // Validar usuario
      if (!usuario.esValido()) {
        const errores = usuario.validar();
        throw new ErrorAplicacion(`Datos de usuario inválidos: ${errores.join(', ')}`);
      }

      // Guardar usuario
      const usuarioGuardado = await this.repositorioUsuario.guardar(usuario);

      // Actualizar cache
      await this.servicioCache.establecer(`usuario:${usuarioGuardado.id}`, usuarioGuardado.aJSON(), 3600);

      // Enviar notificación
      await this.servicioNotificaciones.enviarNotificacion({
        tipo: 'usuario_creado',
        datos: {
          usuarioId: usuarioGuardado.id,
          nombre: usuarioGuardado.obtenerNombreCompleto(),
          correo: usuarioGuardado.correoElectronico
        }
      });

      return usuarioGuardado;

    } catch (error) {
      if (error instanceof ErrorAplicacion) {
        throw error;
      }
      throw new ErrorAplicacion(`Error creando usuario: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  }

  /**
   * Obtiene un usuario por ID
   */
  async obtenerUsuarioPorId(id: string): Promise<Usuario> {
    try {
      // Buscar en cache primero
      const usuarioCache = await this.servicioCache.obtener(`usuario:${id}`);
      if (usuarioCache) {
        return Usuario.desdeDatos(usuarioCache);
      }

      // Buscar en repositorio
      const usuario = await this.repositorioUsuario.buscarPorId(id);
      if (!usuario) {
        throw new ErrorAplicacion('Usuario no encontrado');
      }

      // Actualizar cache
      await this.servicioCache.establecer(`usuario:${id}`, usuario.aJSON(), 3600);

      return usuario;

    } catch (error) {
      if (error instanceof ErrorAplicacion) {
        throw error;
      }
      throw new ErrorAplicacion(`Error obteniendo usuario: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  }

  /**
   * Lista usuarios con filtros
   */
  async listarUsuarios(filtros: {
    rol?: RolUsuario;
    estado?: EstadoUsuario;
    busqueda?: string;
    pagina?: number;
    limite?: number;
    ordenarPor?: string;
    orden?: 'asc' | 'desc';
  } = {}): Promise<{
    usuarios: Usuario[];
    paginacion: {
      pagina: number;
      limite: number;
      total: number;
      totalPaginas: number;
    };
  }> {
    try {
      const {
        rol,
        estado,
        busqueda,
        pagina = 1,
        limite = 10,
        ordenarPor = 'fechaCreacion',
        orden = 'desc'
      } = filtros;

      // Construir filtros de búsqueda
      const filtrosBusqueda: any = {};
      if (rol) filtrosBusqueda.rol = rol;
      if (estado) filtrosBusqueda.estado = estado;
      if (busqueda) filtrosBusqueda.busqueda = busqueda;

      // Calcular offset
      const offset = (pagina - 1) * limite;

      // Buscar usuarios
      const usuarios = await this.repositorioUsuario.buscarConFiltros(
        filtrosBusqueda,
        offset,
        limite,
        ordenarPor,
        orden
      );

      // Obtener total
      const total = await this.repositorioUsuario.contarConFiltros(filtrosBusqueda);

      return {
        usuarios,
        paginacion: {
          pagina,
          limite,
          total,
          totalPaginas: Math.ceil(total / limite)
        }
      };

    } catch (error) {
      throw new ErrorAplicacion(`Error listando usuarios: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  }

  /**
   * Actualiza un usuario
   */
  async actualizarUsuario(id: string, datosActualizacion: Partial<Pick<UsuarioProps, 'nombre' | 'apellido' | 'telefono' | 'avatar' | 'preferencias'>>): Promise<Usuario> {
    try {
      // Buscar usuario existente
      const usuarioExistente = await this.repositorioUsuario.buscarPorId(id);
      if (!usuarioExistente) {
        throw new ErrorAplicacion('Usuario no encontrado');
      }

      // Actualizar datos
      if (datosActualizacion.nombre || datosActualizacion.apellido || datosActualizacion.telefono || datosActualizacion.avatar) {
        usuarioExistente.actualizarPerfil({
          nombre: datosActualizacion.nombre,
          apellido: datosActualizacion.apellido,
          telefono: datosActualizacion.telefono,
          avatar: datosActualizacion.avatar
        });
      }

      if (datosActualizacion.preferencias) {
        usuarioExistente.actualizarPreferencias(datosActualizacion.preferencias);
      }

      // Validar usuario actualizado
      if (!usuarioExistente.esValido()) {
        const errores = usuarioExistente.validar();
        throw new ErrorAplicacion(`Datos de usuario inválidos: ${errores.join(', ')}`);
      }

      // Guardar cambios
      const usuarioActualizado = await this.repositorioUsuario.actualizar(usuarioExistente);

      // Actualizar cache
      await this.servicioCache.establecer(`usuario:${id}`, usuarioActualizado.aJSON(), 3600);

      // Enviar notificación
      await this.servicioNotificaciones.enviarNotificacion({
        tipo: 'usuario_actualizado',
        datos: {
          usuarioId: id,
          nombre: usuarioActualizado.obtenerNombreCompleto()
        }
      });

      return usuarioActualizado;

    } catch (error) {
      if (error instanceof ErrorAplicacion) {
        throw error;
      }
      throw new ErrorAplicacion(`Error actualizando usuario: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  }

  /**
   * Cambia el rol de un usuario
   */
  async cambiarRolUsuario(id: string, nuevoRol: RolUsuario): Promise<Usuario> {
    try {
      const usuario = await this.repositorioUsuario.buscarPorId(id);
      if (!usuario) {
        throw new ErrorAplicacion('Usuario no encontrado');
      }

      usuario.cambiarRol(nuevoRol);
      const usuarioActualizado = await this.repositorioUsuario.actualizar(usuario);

      // Actualizar cache
      await this.servicioCache.establecer(`usuario:${id}`, usuarioActualizado.aJSON(), 3600);

      // Enviar notificación
      await this.servicioNotificaciones.enviarNotificacion({
        tipo: 'usuario_rol_cambiado',
        datos: {
          usuarioId: id,
          nombre: usuarioActualizado.obtenerNombreCompleto(),
          rolAnterior: usuario.rol,
          rolNuevo: nuevoRol
        }
      });

      return usuarioActualizado;

    } catch (error) {
      if (error instanceof ErrorAplicacion) {
        throw error;
      }
      throw new ErrorAplicacion(`Error cambiando rol de usuario: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  }

  /**
   * Cambia el estado de un usuario
   */
  async cambiarEstadoUsuario(id: string, nuevoEstado: EstadoUsuario): Promise<Usuario> {
    try {
      const usuario = await this.repositorioUsuario.buscarPorId(id);
      if (!usuario) {
        throw new ErrorAplicacion('Usuario no encontrado');
      }

      usuario.cambiarEstado(nuevoEstado);
      const usuarioActualizado = await this.repositorioUsuario.actualizar(usuario);

      // Actualizar cache
      await this.servicioCache.establecer(`usuario:${id}`, usuarioActualizado.aJSON(), 3600);

      // Enviar notificación
      await this.servicioNotificaciones.enviarNotificacion({
        tipo: 'usuario_estado_cambiado',
        datos: {
          usuarioId: id,
          nombre: usuarioActualizado.obtenerNombreCompleto(),
          estadoAnterior: usuario.estado,
          estadoNuevo: nuevoEstado
        }
      });

      return usuarioActualizado;

    } catch (error) {
      if (error instanceof ErrorAplicacion) {
        throw error;
      }
      throw new ErrorAplicacion(`Error cambiando estado de usuario: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  }

  /**
   * Elimina un usuario
   */
  async eliminarUsuario(id: string): Promise<void> {
    try {
      const usuario = await this.repositorioUsuario.buscarPorId(id);
      if (!usuario) {
        throw new ErrorAplicacion('Usuario no encontrado');
      }

      // Eliminar usuario
      await this.repositorioUsuario.eliminar(id);

      // Eliminar de cache
      await this.servicioCache.eliminar(`usuario:${id}`);

      // Enviar notificación
      await this.servicioNotificaciones.enviarNotificacion({
        tipo: 'usuario_eliminado',
        datos: {
          usuarioId: id,
          nombre: usuario.obtenerNombreCompleto()
        }
      });

    } catch (error) {
      if (error instanceof ErrorAplicacion) {
        throw error;
      }
      throw new ErrorAplicacion(`Error eliminando usuario: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  }

  /**
   * Obtiene estadísticas de usuarios
   */
  async obtenerEstadisticasUsuarios(): Promise<{
    total: number;
    porRol: Record<RolUsuario, number>;
    porEstado: Record<EstadoUsuario, number>;
    activosUltimoMes: number;
  }> {
    try {
      const estadisticas = await this.repositorioUsuario.obtenerEstadisticas();
      return estadisticas;

    } catch (error) {
      throw new ErrorAplicacion(`Error obteniendo estadísticas: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    }
  }

  /**
   * Valida los datos de usuario
   */
  private validarDatosUsuario(datos: any): void {
    if (!datos.nombreUsuario || datos.nombreUsuario.trim() === '') {
      throw new ErrorAplicacion('Nombre de usuario es requerido');
    }

    if (!datos.correoElectronico || !this.validarEmail(datos.correoElectronico)) {
      throw new ErrorAplicacion('Correo electrónico válido es requerido');
    }

    if (!datos.nombre || datos.nombre.trim() === '') {
      throw new ErrorAplicacion('Nombre es requerido');
    }

    if (!datos.apellido || datos.apellido.trim() === '') {
      throw new ErrorAplicacion('Apellido es requerido');
    }

    if (datos.telefono && !this.validarTelefono(datos.telefono)) {
      throw new ErrorAplicacion('Formato de teléfono inválido');
    }
  }

  private validarEmail(email: string): boolean {
    const patron = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return patron.test(email);
  }

  private validarTelefono(telefono: string): boolean {
    const patron = /^\+?[\d\s\-\(\)]+$/;
    return patron.test(telefono);
  }
}
