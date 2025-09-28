package com.portfolio.arquitectura.users.application.usecase;

import com.portfolio.arquitectura.users.domain.entity.User;
import com.portfolio.arquitectura.users.domain.entity.UserRole;
import com.portfolio.arquitectura.users.domain.entity.UserStatus;
import com.portfolio.arquitectura.users.domain.repository.UserRepository;
import com.portfolio.arquitectura.users.domain.valueobject.Email;
import com.portfolio.arquitectura.users.application.dto.CreateUserRequest;
import com.portfolio.arquitectura.users.application.dto.UserResponse;
import com.portfolio.arquitectura.users.application.mapper.UserMapper;
import com.portfolio.arquitectura.users.application.exception.UserAlreadyExistsException;
import com.portfolio.arquitectura.users.application.exception.InvalidUserDataException;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Use Case para crear un nuevo usuario
 * 
 * Implementa la lógica de negocio para la creación de usuarios,
 * incluyendo validaciones, encriptación de contraseña y notificaciones.
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class CreateUserUseCase {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final UserMapper userMapper;
    private final UserEventPublisher userEventPublisher;

    /**
     * Crea un nuevo usuario en el sistema
     * 
     * @param request Datos del usuario a crear
     * @return Usuario creado
     * @throws UserAlreadyExistsException si el usuario ya existe
     * @throws InvalidUserDataException si los datos son inválidos
     */
    public UserResponse execute(CreateUserRequest request) {
        log.info("Iniciando creación de usuario con email: {}", request.getEmail());

        // Validar datos de entrada
        validateRequest(request);

        // Crear email value object
        Email email = Email.of(request.getEmail());

        // Verificar si el usuario ya existe
        if (userRepository.existsByEmail(email)) {
            log.warn("Intento de crear usuario con email existente: {}", request.getEmail());
            throw new UserAlreadyExistsException("Ya existe un usuario con el email: " + request.getEmail());
        }

        if (userRepository.existsByUsername(request.getUsername())) {
            log.warn("Intento de crear usuario con username existente: {}", request.getUsername());
            throw new UserAlreadyExistsException("Ya existe un usuario con el username: " + request.getUsername());
        }

        // Crear entidad usuario
        User user = User.builder()
                .email(email.getValue())
                .username(request.getUsername())
                .password(passwordEncoder.encode(request.getPassword()))
                .firstName(request.getFirstName())
                .lastName(request.getLastName())
                .phoneNumber(request.getPhoneNumber())
                .status(UserStatus.PENDING_VERIFICATION)
                .role(determineUserRole(request))
                .emailVerified(false)
                .build();

        // Guardar usuario
        User savedUser = userRepository.save(user);
        log.info("Usuario creado exitosamente con ID: {}", savedUser.getId());

        // Publicar evento de usuario creado
        userEventPublisher.publishUserCreated(savedUser);

        // Enviar email de verificación
        userEventPublisher.publishEmailVerificationRequested(savedUser);

        return userMapper.toResponse(savedUser);
    }

    /**
     * Valida los datos de entrada
     */
    private void validateRequest(CreateUserRequest request) {
        if (request == null) {
            throw new InvalidUserDataException("Request no puede ser nulo");
        }

        if (request.getEmail() == null || request.getEmail().trim().isEmpty()) {
            throw new InvalidUserDataException("Email es requerido");
        }

        if (request.getUsername() == null || request.getUsername().trim().isEmpty()) {
            throw new InvalidUserDataException("Username es requerido");
        }

        if (request.getPassword() == null || request.getPassword().length() < 8) {
            throw new InvalidUserDataException("Password debe tener al menos 8 caracteres");
        }

        if (request.getFirstName() == null || request.getFirstName().trim().isEmpty()) {
            throw new InvalidUserDataException("Nombre es requerido");
        }

        if (request.getLastName() == null || request.getLastName().trim().isEmpty()) {
            throw new InvalidUserDataException("Apellido es requerido");
        }

        // Validar formato de username
        if (!request.getUsername().matches("^[a-zA-Z0-9_]{3,20}$")) {
            throw new InvalidUserDataException("Username debe contener solo letras, números y guiones bajos, entre 3 y 20 caracteres");
        }
    }

    /**
     * Determina el rol del usuario basado en el contexto
     */
    private UserRole determineUserRole(CreateUserRequest request) {
        // Por defecto, todos los usuarios son CUSTOMER
        // En un sistema real, esto podría basarse en:
        // - Código de invitación
        // - Dominio de email
        // - Configuración del sistema
        return UserRole.CUSTOMER;
    }
}
