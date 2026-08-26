"""Funciones que el servidor MCP expone al agente conversacional."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
from mcp.server.fastmcp import Image

from app.analisis.punto_02 import (
    distribucion_ventas_por_boletin,
    distribucion_ventas_por_mes,
    distribucion_ventas_por_metodo_pago,
    distribucion_ventas_por_navegador,
    distribucion_ventas_por_vale,
    ejecutar_analisis,
)
from app.config import RUTA_RESULTADOS_PUNTO_02

NOMBRES_ARCHIVO_DISTRIBUCION = {
    "mes": "distribucion_ventas_mes.png",
    "metodo_pago": "distribucion_ventas_metodo_pago.png",
    "navegador": "distribucion_ventas_navegador.png",
    "boletin": "distribucion_ventas_boletin.png",
    "vale": "distribucion_ventas_vale.png",
}


DIMENSIONES_DISTRIBUCION = {
    "mes": distribucion_ventas_por_mes,
    "metodo_pago": distribucion_ventas_por_metodo_pago,
    "navegador": distribucion_ventas_por_navegador,
    "boletin": distribucion_ventas_por_boletin,
    "vale": distribucion_ventas_por_vale,
}

VARIABLES_CUANTITATIVAS = [
    "edad",
    "venta_total",
    "n_compras",
    "monto_compra",
    "tiempo",
]

VARIABLES_CATEGORICAS_CODIFICADAS = [
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
    """Calcula y contrasta las medidas de las diez variables solicitadas."""
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
        "variables_analizadas": (
            VARIABLES_CUANTITATIVAS + VARIABLES_CATEGORICAS_CODIFICADAS
        ),
        "variables_cuantitativas": VARIABLES_CUANTITATIVAS,
        "variables_categoricas_codificadas": VARIABLES_CATEGORICAS_CODIFICADAS,
        "estadisticas": _registros_json(estadisticas),
        "contraste_postgresql": _registros_json(contraste),
        "todo_coincide": bool(contraste["todo_coincide"].all()),
        "nota": (
            "Los identificadores se excluyen. Para cumplir la rubrica se calculan "
            "las tres medidas sobre los codigos categoricos, pero estos se interpretan "
            "principalmente mediante la moda y sus proporciones. La moda conserva "
            "todos los empates."
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


def consultar_distribucion_ventas(dimension: str) -> dict[str, Any]:
    """Obtiene la distribucion de compras y montos segun mes, metodo de pago,
    navegador, boletin o vale (punto 2.c)."""
    if dimension not in DIMENSIONES_DISTRIBUCION:
        raise ValueError(
            "La dimension debe ser una de: "
            + ", ".join(sorted(DIMENSIONES_DISTRIBUCION))
        )

    resultado = ejecutar_analisis(directorio_resultados=None)
    funcion = DIMENSIONES_DISTRIBUCION[dimension]
    distribucion = funcion(resultado["compras"], graficar=False)

    return {
        "exito": True,
        "dimension": dimension,
        "datos": _registros_json(distribucion),
        "nota": (
            "La distribucion se calculo sobre las compras obtenidas de PostgreSQL. "
            "El grafico correspondiente se genera por separado y no se envia en esta respuesta."
        ),
    }


def consultar_grafico_distribucion_ventas(dimension: str) -> Image:
    """Genera y devuelve como imagen PNG el grafico de distribucion de ventas
    para una dimension especifica (punto 2.c)."""
    if dimension not in DIMENSIONES_DISTRIBUCION:
        raise ValueError(
            "La dimension debe ser una de: "
            + ", ".join(sorted(DIMENSIONES_DISTRIBUCION))
        )

    resultado = ejecutar_analisis(directorio_resultados=None)
    funcion = DIMENSIONES_DISTRIBUCION[dimension]
    funcion(
        resultado["compras"],
        directorio_resultados=RUTA_RESULTADOS_PUNTO_02,
        graficar=True,
        mostrar=False,
    )
    ruta_imagen = RUTA_RESULTADOS_PUNTO_02 / NOMBRES_ARCHIVO_DISTRIBUCION[dimension]
    return Image(path=ruta_imagen)
