-- ============================================================
-- Práctica 1 — SOG2 2S26 Grupo 8
-- Script de creación de base de datos
-- ============================================================
-- Ejecutar como superusuario si es necesario:
-- CREATE DATABASE ventas_online;

-- ============================================================
-- TABLA: clientes
-- Contiene el perfil agregado anual de cada cliente.
-- Campos: id, edad, género y métricas acumuladas del año.
-- ============================================================
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente   INTEGER       PRIMARY KEY,
    edad         SMALLINT      NOT NULL CHECK (edad BETWEEN 0 AND 150),
    genero       SMALLINT      NOT NULL CHECK (genero IN (0, 1)),
                 -- 0: Masculino, 1: Femenino
    venta_total  NUMERIC(12,4) NOT NULL CHECK (venta_total >= 0),
                 -- Total acumulado de ventas del año (mínimo 4 decimales por ser monetario)
    n_compras    INTEGER       NOT NULL CHECK (n_compras > 0)
);

COMMENT ON TABLE  clientes              IS 'Perfil agregado del cliente en el año 2021';
COMMENT ON COLUMN clientes.id_cliente   IS 'Identificador único del cliente';
COMMENT ON COLUMN clientes.edad         IS 'Edad del cliente en años';
COMMENT ON COLUMN clientes.genero       IS '0 = Masculino, 1 = Femenino';
COMMENT ON COLUMN clientes.venta_total  IS 'Total acumulado de ventas del cliente en el año (monetario, 4 decimales)';
COMMENT ON COLUMN clientes.n_compras    IS 'Número total de compras realizadas en el año';

-- ============================================================
-- TABLA: compras
-- Detalle de una compra puntual asociada a un cliente.
-- ============================================================
CREATE TABLE IF NOT EXISTS compras (
    id_compra     SERIAL        PRIMARY KEY,
    id_cliente    INTEGER       NOT NULL REFERENCES clientes(id_cliente)
                                ON DELETE CASCADE
                                ON UPDATE CASCADE,
    fecha_compra  DATE          NOT NULL,
    monto_compra  NUMERIC(12,4) NOT NULL CHECK (monto_compra >= 0),
                  -- Monto de la compra individual (monetario, 4 decimales)
    metodo_pago   SMALLINT      NOT NULL CHECK (metodo_pago IN (0, 1, 2)),
                  -- 0: Efectivo / Contra entrega (aclaración del auxiliar)
                  -- 1: Tarjeta de Crédito
                  -- 2: Tarjeta de Débito
    tiempo        INTEGER       NOT NULL CHECK (tiempo > 0),
                  -- Tiempo de navegación en segundos
    navegador     SMALLINT      NOT NULL CHECK (navegador BETWEEN 0 AND 4),
                  -- 0: Tienda Física
                  -- 1: Navegador 1
                  -- 2: Navegador 2
                  -- 3: Navegador 3
                  -- 4: Navegador 4
    boletin       BOOLEAN       NOT NULL DEFAULT FALSE,
                  -- TRUE si la venta fue realizada con un boletín
    vale          BOOLEAN       NOT NULL DEFAULT FALSE
                  -- TRUE si la venta fue realizada con un vale
);

COMMENT ON TABLE  compras               IS 'Detalle de compra individual asociada a un cliente';
COMMENT ON COLUMN compras.id_compra     IS 'Identificador auto-incremental de la compra';
COMMENT ON COLUMN compras.id_cliente    IS 'Referencia al cliente (FK → clientes.id_cliente)';
COMMENT ON COLUMN compras.fecha_compra  IS 'Fecha en que se realizó la compra';
COMMENT ON COLUMN compras.monto_compra  IS 'Monto de la compra individual (monetario, 4 decimales)';
COMMENT ON COLUMN compras.metodo_pago   IS '0 = Efectivo/Contra entrega, 1 = Tarjeta Crédito, 2 = Tarjeta Débito';
COMMENT ON COLUMN compras.tiempo        IS 'Tiempo de navegación en segundos (rango observado: 180-1443)';
COMMENT ON COLUMN compras.navegador     IS '0 = Tienda Física, 1-4 = Navegadores web';
COMMENT ON COLUMN compras.boletin       IS 'Si la compra utilizó boletín (TRUE/FALSE)';
COMMENT ON COLUMN compras.vale          IS 'Si la compra utilizó vale (TRUE/FALSE)';

-- ============================================================
-- ÍNDICES
-- Mejoran consultas frecuentes del análisis
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_compras_fecha
    ON compras(fecha_compra);

CREATE INDEX IF NOT EXISTS idx_compras_cliente
    ON compras(id_cliente);

CREATE INDEX IF NOT EXISTS idx_compras_metodo_pago
    ON compras(metodo_pago);

CREATE INDEX IF NOT EXISTS idx_compras_navegador
    ON compras(navegador);

-- ============================================================
-- ROL DE SOLO LECTURA (opcional, recomendado para el MCP Server)
-- Descomentar y ajustar credenciales antes de ejecutar
-- ============================================================
-- CREATE ROLE mcp_readonly WITH LOGIN PASSWORD 'contraseña_segura';
-- GRANT CONNECT ON DATABASE ventas_online TO mcp_readonly;
-- GRANT USAGE ON SCHEMA public TO mcp_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;
