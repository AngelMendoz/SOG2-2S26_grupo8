"""Servidor MCP con herramientas de analisis de ventas verificadas."""

from __future__ import annotations

import os
from ipaddress import ip_address
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from herramientas_ventas import (
    consultar_estadisticas_basicas,
    consultar_muestra_datos,
    consultar_resumen_datos,
)


DIRECTORIO_ACTUAL = Path(__file__).resolve().parent
load_dotenv(DIRECTORIO_ACTUAL.parent / ".env")

MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))


def _es_host_local(host: str) -> bool:
    if host.lower() == "localhost":
        return True
    try:
        return ip_address(host).is_loopback
    except ValueError:
        return False


if not _es_host_local(MCP_HOST):
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


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
