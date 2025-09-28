package com.portfolio.arquitectura.users.domain.repository;

import com.portfolio.arquitectura.users.domain.entity.User;
import com.portfolio.arquitectura.users.domain.entity.UserRole;
import com.portfolio.arquitectura.users.domain.entity.UserStatus;
import com.portfolio.arquitectura.users.domain.valueobject.Email;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository Interface para Usuario - Domain Layer
 * 
 * Define el contrato para la persistencia de usuarios.
 * Implementa el patrón Repository para desacoplar la lógica de negocio
 * de la implementación de persistencia.
 * 
 * @author Gabriel - Arquitecto de Software
 */
public interface UserRepository {

    /**
     * Guarda un usuario en el repositorio
     * 
     * @param user Usuario a guardar
     * @return Usuario guardado con ID generado
     */
    User save(User user);

    /**
     * Busca un usuario por ID
     * 
     * @param id ID del usuario
     * @return Optional con el usuario si existe
     */
    Optional<User> findById(UUID id);

    /**
     * Busca un usuario por email
     * 
     * @param email Email del usuario
     * @return Optional con el usuario si existe
     */
    Optional<User> findByEmail(Email email);

    /**
     * Busca un usuario por username
     * 
     * @param username Username del usuario
     * @return Optional con el usuario si existe
     */
    Optional<User> findByUsername(String username);

    /**
     * Verifica si existe un usuario con el email dado
     * 
     * @param email Email a verificar
     * @return true si existe un usuario con ese email
     */
    boolean existsByEmail(Email email);

    /**
     * Verifica si existe un usuario con el username dado
     * 
     * @param username Username a verificar
     * @return true si existe un usuario con ese username
     */
    boolean existsByUsername(String username);

    /**
     * Busca usuarios por estado
     * 
     * @param status Estado del usuario
     * @return Lista de usuarios con el estado especificado
     */
    List<User> findByStatus(UserStatus status);

    /**
     * Busca usuarios por rol
     * 
     * @param role Rol del usuario
     * @return Lista de usuarios con el rol especificado
     */
    List<User> findByRole(UserRole role);

    /**
     * Busca usuarios con paginación
     * 
     * @param page Número de página (0-based)
     * @param size Tamaño de la página
     * @return Lista paginada de usuarios
     */
    List<User> findAll(int page, int size);

    /**
     * Cuenta el total de usuarios
     * 
     * @return Número total de usuarios
     */
    long count();

    /**
     * Cuenta usuarios por estado
     * 
     * @param status Estado del usuario
     * @return Número de usuarios con el estado especificado
     */
    long countByStatus(UserStatus status);

    /**
     * Cuenta usuarios por rol
     * 
     * @param role Rol del usuario
     * @return Número de usuarios con el rol especificado
     */
    long countByRole(UserRole role);

    /**
     * Elimina un usuario por ID
     * 
     * @param id ID del usuario a eliminar
     */
    void deleteById(UUID id);

    /**
     * Busca usuarios por nombre (búsqueda parcial)
     * 
     * @param firstName Nombre a buscar
     * @param lastName Apellido a buscar
     * @return Lista de usuarios que coinciden
     */
    List<User> findByFirstNameContainingIgnoreCaseOrLastNameContainingIgnoreCase(
            String firstName, String lastName);

    /**
     * Busca usuarios activos con paginación
     * 
     * @param page Número de página (0-based)
     * @param size Tamaño de la página
     * @return Lista paginada de usuarios activos
     */
    List<User> findActiveUsers(int page, int size);

    /**
     * Busca usuarios por rango de fechas de creación
     * 
     * @param startDate Fecha de inicio
     * @param endDate Fecha de fin
     * @return Lista de usuarios creados en el rango
     */
    List<User> findByCreatedAtBetween(java.time.LocalDateTime startDate, 
                                     java.time.LocalDateTime endDate);
}
