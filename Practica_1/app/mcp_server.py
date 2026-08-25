"""Servidor MCP con herramientas de analisis de ventas."""

from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from app.config import RUTA_ENV, es_host_local
from app.herramientas.punto_02 import (
    consultar_estadisticas_basicas,
    consultar_muestra_datos,
    consultar_resumen_datos,
)
from app.herramientas.punto_03 import (
    consultar_boletines_vales_por_mes,
    consultar_navegador_preferido,
    consultar_ventas_efectivo_contra_entrega,
    consultar_ventas_por_mes,
)
from app.herramientas.punto_04 import (
    consultar_segmentacion_edad,
    consultar_segmentacion_genero,
    consultar_impacto_boletines_vales,
)

from app.herramientas.punto_05 import (
    consultar_correlacion_venta_edad, 
    consultar_correlacion_genero_metodo_pago, 
    consultar_correlacion_boletin_vale, 
)


load_dotenv(RUTA_ENV)

MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))


if not es_host_local(MCP_HOST):
    raise ValueError(
        "MCP_HOST debe ser una direccion local mientras el servidor no tenga autenticacion."
    )

mcp = FastMCP(
    "Analisis de ventas online",
    instructions=(
        "Herramientas de solo lectura para obtener y analizar las ventas de 2021. "
        "No permite ejecutar SQL arbitrario ni modificar la base de datos."
    ),
    host=MCP_HOST,
    port=MCP_PORT,
)


# Punto 2: analisis exploratorio.
@mcp.tool()
def obtener_resumen_datos() -> dict:
    """Obtiene desde PostgreSQL las dimensiones, columnas, tipos y validaciones."""
    return consultar_resumen_datos()


@mcp.tool()
def obtener_estadisticas_basicas() -> dict:
    """Calcula media, mediana y moda de todas las variables cuantitativas."""
    return consultar_estadisticas_basicas()


@mcp.tool()
def obtener_muestra_datos(
    tabla: Literal["clientes", "compras"] = "clientes", limite: int = 5
) -> dict:
    """Obtiene entre 1 y 20 filas de muestra de la tabla clientes o compras."""
    return consultar_muestra_datos(tabla, limite)


# Punto 3: analisis de tendencias.
@mcp.tool()
def obtener_ventas_por_mes() -> dict:
    """Determina los meses de 2021 con mayores y menores ventas totales."""
    return consultar_ventas_por_mes()
 
 
@mcp.tool()
def obtener_navegador_preferido() -> dict:
    """Identifica el navegador/canal mas preferido y el menos popular."""
    return consultar_navegador_preferido()
 
 
@mcp.tool()
def obtener_ventas_efectivo_contra_entrega() -> dict:
    """Identifica el total de ventas pagadas en efectivo o contra entrega."""
    return consultar_ventas_efectivo_contra_entrega()
 
 
@mcp.tool()
def obtener_boletines_vales_por_mes() -> dict:
    """Identifica los meses donde se usaron mas boletines y mas vales."""
    return consultar_boletines_vales_por_mes()
 
# Punto 4: segmentacion de clientes.
@mcp.tool()
def obtener_segmentacion_edad() -> dict:
    """Agrupa a los clientes por edad y analiza patrones de compra."""
    return consultar_segmentacion_edad()

@mcp.tool()
def obtener_segmentacion_genero() -> dict:
    """Compara el comportamiento de compra entre géneros (Femenino y Masculino)."""
    return consultar_segmentacion_genero()

@mcp.tool()
def obtener_impacto_boletines_vales() -> dict:
    """Analiza los patrones de compra basados en si usaron vales o boletines."""
    return consultar_impacto_boletines_vales()

@mcp.tool()
def obtener_correlacion_venta_edad() -> dict:
    """Investiga si existe una relacion entre la venta total y la edad del cliente."""
    return consultar_correlacion_venta_edad()

@mcp.tool()
def obtener_correlacion_genero_metodo_pago() -> dict:
    """Examina si hay correlacion entre el genero del cliente y su metodo de pago preferido."""
    return consultar_correlacion_genero_metodo_pago()

@mcp.tool()
def obtener_correlacion_boletin_vale() -> dict:
    """Investiga si existe correlacion entre el uso de boletin y de vale."""
    return consultar_correlacion_boletin_vale()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
