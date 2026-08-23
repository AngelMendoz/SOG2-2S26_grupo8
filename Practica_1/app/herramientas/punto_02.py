"""Funciones seguras que el servidor MCP expone al agente conversacional."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from app.analisis.punto_02 import ejecutar_analisis


VARIABLES_CUANTITATIVAS = [
    "edad",
    "venta_total",
    "n_compras",
    "monto_compra",
    "tiempo",
]

VARIABLES_CATEGORICAS_EXCLUIDAS = [
    "genero",
    "metodo_pago",
    "navegador",
    "boletin",
    "vale",
]


def _registros_json(datos: pd.DataFrame) -> list[dict[str, Any]]:
    """Convierte tipos de Pandas y NumPy a valores JSON nativos."""
    return json.loads(datos.to_json(orient="records", date_format="iso"))


def consultar_resumen_datos() -> dict[str, Any]:
    """Obtiene dimensiones, columnas, tipos y validaciones desde PostgreSQL."""
    resultado = ejecutar_analisis(directorio_resultados=None)
    return {
        "exito": True,
        "origen": resultado["resumen"]["origen"],
        "extraccion": resultado["resumen"]["extraccion"],
        "verificacion": resultado["resumen"]["verificacion"],
        "validaciones": _registros_json(resultado["validaciones"]),
        "nota": (
            "Los datos se obtuvieron de PostgreSQL en una transaccion "
            "REPEATABLE READ de solo lectura."
        ),
    }


def consultar_estadisticas_basicas() -> dict[str, Any]:
    """Calcula y contrasta media, mediana y moda para variables cuantitativas."""
    resultado = ejecutar_analisis(directorio_resultados=None)
    estadisticas = resultado["estadisticas"].copy()
    estadisticas[["media", "mediana"]] = estadisticas[
        ["media", "mediana"]
    ].round(6)
    contraste = resultado["contraste"][
        ["tabla", "variable", "todo_coincide"]
    ]
    return {
        "exito": True,
        "variables_cuantitativas": VARIABLES_CUANTITATIVAS,
        "variables_categoricas_excluidas": VARIABLES_CATEGORICAS_EXCLUIDAS,
        "estadisticas": _registros_json(estadisticas),
        "contraste_postgresql": _registros_json(contraste),
        "todo_coincide": bool(contraste["todo_coincide"].all()),
        "nota": (
            "Los identificadores y codigos categoricos no se promedian. "
            "La moda conserva todos los empates."
        ),
    }


def consultar_muestra_datos(tabla: str = "clientes", limite: int = 5) -> dict[str, Any]:
    """Devuelve una muestra acotada de clientes o compras, nunca SQL arbitrario."""
    if tabla not in {"clientes", "compras"}:
        raise ValueError("La tabla debe ser 'clientes' o 'compras'.")
    if not 1 <= limite <= 20:
        raise ValueError("El limite debe estar entre 1 y 20.")

    resultado = ejecutar_analisis(directorio_resultados=None)
    muestra = resultado[tabla].head(limite)
    return {
        "exito": True,
        "tabla": tabla,
        "filas_totales": len(resultado[tabla]),
        "filas_mostradas": len(muestra),
        "datos": _registros_json(muestra),
        "nota": "La respuesta es una muestra ordenada y no el conjunto completo.",
    }
