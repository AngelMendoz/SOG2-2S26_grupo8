-- Diagnostico: ¿el usuario del robot quedo restringido?
-- Se puede ejecutar con CUALQUIER conexion (odoo o rpa_robot).

-- 1) ¿Con que usuario estoy conectado? Para la prueba 02 debe decir rpa_robot.
SELECT current_user;

-- 2) Permisos reales de rpa_robot (resultado esperado: t, t, f, f).
SELECT has_table_privilege('rpa_robot', 'x_rpa_cliente', 'SELECT')  AS lee_x_rpa_cliente,
       has_table_privilege('rpa_robot', 'x_rpa_cliente', 'INSERT')  AS inserta_x_rpa_cliente,
       has_table_privilege('rpa_robot', 'res_partner',   'SELECT')  AS lee_res_partner,
       has_table_privilege('rpa_robot', 'res_partner',   'INSERT')  AS inserta_res_partner;

-- 3) Si lee_res_partner sale t, revisar si se le dio permiso a PUBLIC o al robot:
SELECT grantee, privilege_type
FROM information_schema.role_table_grants
WHERE table_name = 'res_partner' AND grantee IN ('PUBLIC', 'rpa_robot');
