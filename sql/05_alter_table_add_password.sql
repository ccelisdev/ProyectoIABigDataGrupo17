USE proyecto_rag;

-- Migración: añadir columna password a usuarios
-- Fecha: 2026-04-03
-- Motivo: Securizar credenciales de usuario (hash bcrypt)

ALTER TABLE usuarios
ADD COLUMN password VARCHAR(255) NOT NULL AFTER email;
