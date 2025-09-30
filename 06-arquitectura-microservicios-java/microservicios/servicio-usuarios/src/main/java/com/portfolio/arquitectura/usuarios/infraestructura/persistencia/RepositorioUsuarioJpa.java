package com.portfolio.arquitectura.usuarios.infraestructura.persistencia;

import com.portfolio.arquitectura.usuarios.dominio.entidad.Usuario;
import com.portfolio.arquitectura.usuarios.dominio.entidad.EstadoUsuario;
import com.portfolio.arquitectura.usuarios.dominio.entidad.RolUsuario;
import com.portfolio.arquitectura.usuarios.dominio.objetoValor.CorreoElectronico;
import com.portfolio.arquitectura.usuarios.dominio.repositorio.RepositorioUsuario;
import com.portfolio.arquitectura.usuarios.infraestructura.persistencia.entidad.UsuarioEntidad;
import com.portfolio.arquitectura.usuarios.infraestructura.persistencia.mapeador.UsuarioMapeador;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Implementación JPA del Repositorio de Usuario
 * 
 * @author Gabriel - Arquitecto de Software
 */
@Repository
public class RepositorioUsuarioJpa implements RepositorioUsuario {

    private final UsuarioJpaRepository usuarioJpaRepository;
    private final UsuarioMapeador usuarioMapeador;

    public RepositorioUsuarioJpa(UsuarioJpaRepository usuarioJpaRepository, UsuarioMapeador usuarioMapeador) {
        this.usuarioJpaRepository = usuarioJpaRepository;
        this.usuarioMapeador = usuarioMapeador;
    }

    @Override
    public Usuario guardar(Usuario usuario) {
        UsuarioEntidad entidad = usuarioMapeador.aEntidad(usuario);
        UsuarioEntidad entidadGuardada = usuarioJpaRepository.save(entidad);
        return usuarioMapeador.aDominio(entidadGuardada);
    }

    @Override
    public Optional<Usuario> buscarPorId(UUID id) {
        return usuarioJpaRepository.findById(id)
                .map(usuarioMapeador::aDominio);
    }

    @Override
    public Optional<Usuario> buscarPorCorreo(CorreoElectronico correo) {
        return usuarioJpaRepository.findByCorreoElectronico(correo.getValor())
                .map(usuarioMapeador::aDominio);
    }

    @Override
    public Optional<Usuario> buscarPorNombreUsuario(String nombreUsuario) {
        return usuarioJpaRepository.findByNombreUsuario(nombreUsuario)
                .map(usuarioMapeador::aDominio);
    }

    @Override
    public boolean existePorCorreo(CorreoElectronico correo) {
        return usuarioJpaRepository.existsByCorreoElectronico(correo.getValor());
    }

    @Override
    public boolean existePorNombreUsuario(String nombreUsuario) {
        return usuarioJpaRepository.existsByNombreUsuario(nombreUsuario);
    }

    @Override
    public List<Usuario> buscarPorEstado(EstadoUsuario estado) {
        return usuarioJpaRepository.findByEstado(estado)
                .stream()
                .map(usuarioMapeador::aDominio)
                .toList();
    }

    @Override
    public List<Usuario> buscarPorRol(RolUsuario rol) {
        return usuarioJpaRepository.findByRol(rol)
                .stream()
                .map(usuarioMapeador::aDominio)
                .toList();
    }

    @Override
    public List<Usuario> buscarTodos(int pagina, int tamano) {
        Pageable pageable = PageRequest.of(pagina, tamano);
        Page<UsuarioEntidad> paginaEntidades = usuarioJpaRepository.findAll(pageable);
        return paginaEntidades.getContent()
                .stream()
                .map(usuarioMapeador::aDominio)
                .toList();
    }

    @Override
    public long contar() {
        return usuarioJpaRepository.count();
    }

    @Override
    public long contarPorEstado(EstadoUsuario estado) {
        return usuarioJpaRepository.countByEstado(estado);
    }

    @Override
    public long contarPorRol(RolUsuario rol) {
        return usuarioJpaRepository.countByRol(rol);
    }

    @Override
    public void eliminarPorId(UUID id) {
        usuarioJpaRepository.deleteById(id);
    }

    @Override
    public List<Usuario> buscarPorNombreConteniendoIgnoreCaseOrApellidoConteniendoIgnoreCase(String nombre, String apellido) {
        return usuarioJpaRepository.findByNombreContainingIgnoreCaseOrApellidoContainingIgnoreCase(nombre, apellido)
                .stream()
                .map(usuarioMapeador::aDominio)
                .toList();
    }

    @Override
    public List<Usuario> buscarUsuariosActivos(int pagina, int tamano) {
        Pageable pageable = PageRequest.of(pagina, tamano);
        return usuarioJpaRepository.findByEstado(EstadoUsuario.ACTIVO, pageable)
                .stream()
                .map(usuarioMapeador::aDominio)
                .toList();
    }

    @Override
    public List<Usuario> buscarPorFechaCreacionEntre(LocalDateTime fechaInicio, LocalDateTime fechaFin) {
        return usuarioJpaRepository.findByFechaCreacionBetween(fechaInicio, fechaFin)
                .stream()
                .map(usuarioMapeador::aDominio)
                .toList();
    }

    /**
     * Interfaz JPA Repository
     */
    public interface UsuarioJpaRepository extends JpaRepository<UsuarioEntidad, UUID> {
        Optional<UsuarioEntidad> findByCorreoElectronico(String correoElectronico);
        Optional<UsuarioEntidad> findByNombreUsuario(String nombreUsuario);
        boolean existsByCorreoElectronico(String correoElectronico);
        boolean existsByNombreUsuario(String nombreUsuario);
        List<UsuarioEntidad> findByEstado(EstadoUsuario estado);
        List<UsuarioEntidad> findByRol(RolUsuario rol);
        long countByEstado(EstadoUsuario estado);
        long countByRol(RolUsuario rol);
        List<UsuarioEntidad> findByNombreContainingIgnoreCaseOrApellidoContainingIgnoreCase(String nombre, String apellido);
        List<UsuarioEntidad> findByEstado(EstadoUsuario estado, Pageable pageable);
        List<UsuarioEntidad> findByFechaCreacionBetween(LocalDateTime fechaInicio, LocalDateTime fechaFin);
    }
}
