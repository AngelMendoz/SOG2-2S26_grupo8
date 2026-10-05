-- Ejecutar CONECTADO COMO rpa_robot (no como odoo).
-- 1) Devuelve un numero (0 mientras el robot no haya cargado nada).
-- 2) Debe fallar con: permission denied for table res_partner
SELECT count(*) FROM x_rpa_cliente;
SELECT count(*) FROM res_partner;
