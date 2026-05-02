USE proyecto_rag;

-- =========================
-- ROLES DEL SISTEMA
-- =========================
INSERT INTO roles (nombre, descripcion) VALUES
('admin', 'Administrador del sistema'),
('empleado', 'Empleado estándar'),
('compliance', 'Acceso a normativa interna');

-- =========================
-- USUARIOS DE PRUEBA (LOGIN)
-- =========================
INSERT INTO usuarios (email, password, rol_id) VALUES
('empleado@grupo17.com', 'empleado123', 1),
('compliance@grupo17.com', 'compliance123', 2),
('admin@grupo17.com', 'admin123', 3);
