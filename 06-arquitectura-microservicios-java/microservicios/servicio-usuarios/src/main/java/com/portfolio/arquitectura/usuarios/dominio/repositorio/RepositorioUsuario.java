package com.portfolio.arquitectura.usuarios.dominio.repositorio;

import com.portfolio.arquitectura.usuarios.dominio.entidad.Usuario;
import com.portfolio.arquitectura.usuarios.dominio.entidad.RolUsuario;
import com.portfolio.arquitectura.usuarios.dominio.entidad.EstadoUsuario;
import com.portfolio.arquitectura.usuarios.dominio.objetoValor.CorreoElectronico;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Interfaz del Repositorio de Usuario - Capa de Dominio
 * 
 * Define el contrato para la persistencia de usuarios.
 * Implementa el patrón Repository para desacoplar la lógica de negocio
 * de la implementación de persistencia.
 * 
 * @author Gabriel - Arquitecto de Software
 */
public interface RepositorioUsuario {

    /**
     * Guarda un usuario en el repositorio
     * 
     * @param usuario Usuario a guardar
     * @return Usuario guardado con ID generado
     */
    Usuario guardar(Usuario usuario);

    /**
     * Busca un usuario por ID
     * 
     * @param id ID del usuario
     * @return Optional con el usuario si existe
     */
    Optional<Usuario> buscarPorId(UUID id);

    /**
     * Busca un usuario por correo electrónico
     * 
     * @param correo Correo electrónico del usuario
     * @return Optional con el usuario si existe
     */
    Optional<Usuario> buscarPorCorreo(CorreoElectronico correo);

    /**
     * Busca un usuario por nombre de usuario
     * 
     * @param nombreUsuario Nombre de usuario
     * @return Optional con el usuario si existe
     */
    Optional<Usuario> buscarPorNombreUsuario(String nombreUsuario);

    /**
     * Verifica si existe un usuario con el correo dado
     * 
     * @param correo Correo electrónico a verificar
     * @return true si existe un usuario con ese correo
     */
    boolean existePorCorreo(CorreoElectronico correo);

    /**
     * Verifica si existe un usuario con el nombre de usuario dado
     * 
     * @param nombreUsuario Nombre de usuario a verificar
     * @return true si existe un usuario con ese nombre de usuario
     */
    boolean existePorNombreUsuario(String nombreUsuario);

    /**
     * Busca usuarios por estado
     * 
     * @param estado Estado del usuario
     * @return Lista de usuarios con el estado especificado
     */
    List<Usuario> buscarPorEstado(EstadoUsuario estado);

    /**
     * Busca usuarios por rol
     * 
     * @param rol Rol del usuario
     * @return Lista de usuarios con el rol especificado
     */
    List<Usuario> buscarPorRol(RolUsuario rol);

    /**
     * Busca usuarios con paginación
     * 
     * @param pagina Número de página (0-based)
     * @param tamano Tamaño de la página
     * @return Lista paginada de usuarios
     */
    List<Usuario> buscarTodos(int pagina, int tamano);

    /**
     * Cuenta el total de usuarios
     * 
     * @return Número total de usuarios
     */
    long contar();

    /**
     * Cuenta usuarios por estado
     * 
     * @param estado Estado del usuario
     * @return Número de usuarios con el estado especificado
     */
    long contarPorEstado(EstadoUsuario estado);

    /**
     * Cuenta usuarios por rol
     * 
     * @param rol Rol del usuario
     * @return Número de usuarios con el rol especificado
     */
    long contarPorRol(RolUsuario rol);

    /**
     * Elimina un usuario por ID
     * 
     * @param id ID del usuario a eliminar
     */
    void eliminarPorId(UUID id);

    /**
     * Busca usuarios por nombre (búsqueda parcial)
     * 
     * @param nombre Nombre a buscar
     * @param apellido Apellido a buscar
     * @return Lista de usuarios que coinciden
     */
    List<Usuario> buscarPorNombreConteniendoIgnoreCaseOrApellidoConteniendoIgnoreCase(
            String nombre, String apellido);

    /**
     * Busca usuarios activos con paginación
     * 
     * @param pagina Número de página (0-based)
     * @param tamano Tamaño de la página
     * @return Lista paginada de usuarios activos
     */
    List<Usuario> buscarUsuariosActivos(int pagina, int tamano);

    /**
     * Busca usuarios por rango de fechas de creación
     * 
     * @param fechaInicio Fecha de inicio
     * @param fechaFin Fecha de fin
     * @return Lista de usuarios creados en el rango
     */
    List<Usuario> buscarPorFechaCreacionEntre(java.time.LocalDateTime fechaInicio, 
                                             java.time.LocalDateTime fechaFin);
}
