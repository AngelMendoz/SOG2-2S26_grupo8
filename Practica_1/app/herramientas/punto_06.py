"""Funciones que el servidor MCP y el agente exponen para el punto 6."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import Image

from app.analisis.punto_06 import HALLAZGOS
from app.config import RUTA_RESULTADOS_PUNTO_06


def consultar_hallazgos_disponibles() -> dict[str, Any]:
    """Lista los graficos disponibles que resumen los hallazgos mas importantes
    del analisis (punto 6)."""
    return {
        "exito": True,
        "hallazgos": [
            {"clave": clave, **datos} for clave, datos in HALLAZGOS.items()
        ],
        "nota": (
            "Cada hallazgo tiene un grafico asociado. Para verlo, pide el "
            "grafico indicando su clave."
        ),
    }


def consultar_grafico_hallazgo(clave: str) -> Image:
    """Devuelve como imagen PNG el grafico de un hallazgo especifico (punto 6)."""
    if clave not in HALLAZGOS:
        raise ValueError("La clave debe ser una de: " + ", ".join(sorted(HALLAZGOS)))

    ruta_imagen = RUTA_RESULTADOS_PUNTO_06 / HALLAZGOS[clave]["archivo"]
    if not ruta_imagen.is_file():
        raise FileNotFoundError(
            f"El grafico de '{clave}' aun no se genero. Ejecute "
            "app.analisis.punto_06.ejecutar_visualizacion_hallazgos primero."
        )
    return Image(path=ruta_imagen)
