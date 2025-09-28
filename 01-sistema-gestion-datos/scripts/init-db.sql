-- Script de inicialización de base de datos
-- Crear extensiones y configuraciones iniciales

-- Crear extensión para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear extensión para funciones de texto
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Configurar timezone
SET timezone = 'America/Argentina/Buenos_Aires';

-- Crear esquema adicional si es necesario
-- CREATE SCHEMA IF NOT EXISTS auditoria;

-- Configurar parámetros de PostgreSQL
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Crear índices adicionales si es necesario
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_usuarios_email_lower 
-- ON usuarios (LOWER(email));

-- Crear vistas si es necesario
-- CREATE OR REPLACE VIEW vista_usuarios_activos AS
-- SELECT id, email, nombre_usuario, nombre_completo, fecha_creacion
-- FROM usuarios
-- WHERE esta_activo = true;

-- Insertar datos de prueba (opcional)
-- INSERT INTO usuarios (email, nombre_usuario, hash_contraseña, nombre_completo, esta_activo)
-- VALUES 
-- ('admin@sistema.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2', 'Administrador', true),
-- ('usuario@sistema.com', 'usuario', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2', 'Usuario Prueba', true)
-- ON CONFLICT (email) DO NOTHING;
