-- Ejecutar con la conexion del usuario odoo (NO con rpa_robot: no puede leer res_partner ni product_template).
-- 1) Resumen de cada ejecución del robot (lote = fecha y hora de la corrida)
SELECT 'clientes' AS tabla, x_lote AS lote, x_estado AS estado, count(*) AS filas
FROM x_rpa_cliente GROUP BY x_lote, x_estado
UNION ALL
SELECT 'productos', x_lote, x_estado, count(*)
FROM x_rpa_producto GROUP BY x_lote, x_estado
ORDER BY lote DESC, tabla, estado;

-- 2) Clientes de la última corrida y el contacto que se creó en Odoo
SELECT c.x_name AS nombre, c.x_archivo_origen AS archivo, c.x_estado AS estado,
       p.id AS id_contacto, p.email, p.city AS ciudad
FROM x_rpa_cliente c
LEFT JOIN res_partner p ON p.id = c.x_registro_odoo
WHERE c.x_lote = (SELECT max(x_lote) FROM x_rpa_cliente)
ORDER BY c.id;

-- 3) Productos de la última corrida: precio, si está publicado y existencia real
SELECT r.x_name AS producto, r.x_archivo_origen AS archivo, r.x_estado AS estado,
       t.list_price AS precio, t.is_published AS publicado_en_web,
       (SELECT coalesce(sum(q.quantity), 0)
          FROM stock_quant q
          JOIN product_product pp ON pp.id = q.product_id
          JOIN stock_location l ON l.id = q.location_id AND l.usage = 'internal'
         WHERE pp.product_tmpl_id = t.id) AS cantidad_a_la_mano
FROM x_rpa_producto r
LEFT JOIN product_template t ON t.id = r.x_registro_odoo
WHERE r.x_lote = (SELECT max(x_lote) FROM x_rpa_producto)
ORDER BY r.id;

-- 4) Filas con error o avisos (para explicar qué pasó)
SELECT 'cliente' AS tipo, x_name, x_estado, x_mensaje FROM x_rpa_cliente WHERE x_estado <> 'Procesado'
UNION ALL
SELECT 'producto', x_name, x_estado, x_mensaje FROM x_rpa_producto WHERE x_estado <> 'Procesado';
