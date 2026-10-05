-- Ejecutar como usuario odoo (conexion geren2_proyecto / dbquetzalmart).
-- La clave real NO se sube al repositorio: se deja el marcador.
CREATE ROLE rpa_robot LOGIN PASSWORD 'CAMBIA_ESTA_CLAVE';
GRANT CONNECT ON DATABASE dbquetzalmart TO rpa_robot;
GRANT USAGE ON SCHEMA public TO rpa_robot;
GRANT SELECT, INSERT ON x_rpa_cliente, x_rpa_producto TO rpa_robot;
GRANT USAGE ON SEQUENCE x_rpa_cliente_id_seq, x_rpa_producto_id_seq TO rpa_robot;
