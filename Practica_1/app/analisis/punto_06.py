"""Visualizacion de los hallazgos mas importantes del analisis (Punto 6)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.analisis.punto_02 import (
    distribucion_ventas_por_mes,
    distribucion_ventas_por_navegador,
)
from app.analisis.punto_04 import (
    comportamiento_por_genero,
    impacto_boletines_vales,
    segmentar_por_edad,
)
from app.analisis.punto_05 import (
    correlacion_genero_metodo_pago,
    correlacion_venta_edad,
)
from app.config import RUTA_RESULTADOS_PUNTO_06

HALLAZGOS = {
    "ventas_por_mes": {
        "titulo": "Ventas totales por mes",
        "descripcion": "Muestra la estacionalidad de las ventas a lo largo de 2021.",
        "tipo_grafico": "linea",
        "archivo": "distribucion_ventas_mes.png",
    },
    "navegador_mas_usado": {
        "titulo": "Ventas por navegador",
        "descripcion": (
            "Identifica el canal de venta (tienda fisica o navegador) mas y "
            "menos utilizado."
        ),
        "tipo_grafico": "barras",
        "archivo": "distribucion_ventas_navegador.png",
    },
    "ventas_por_edad": {
        "titulo": "Ventas totales por rango de edad",
        "descripcion": "Compara el aporte de cada grupo etario a las ventas totales.",
        "tipo_grafico": "barras",
        "archivo": "ventas_por_edad.png",
    },
    "ventas_por_genero": {
        "titulo": "Ventas totales por genero",
        "descripcion": "Compara el comportamiento de compra entre generos.",
        "tipo_grafico": "barras",
        "archivo": "ventas_por_genero.png",
    },
    "boletin_vale": {
        "titulo": "Monto total por uso de boletin y vale",
        "descripcion": (
            "Muestra el impacto combinado de boletines y vales en el monto de compra."
        ),
        "tipo_grafico": "barras",
        "archivo": "monto_por_boletin_vale.png",
    },
    "venta_vs_edad": {
        "titulo": "Correlacion entre venta total y edad",
        "descripcion": (
            "Dispersion con linea de tendencia entre la edad del cliente y su "
            "venta total."
        ),
        "tipo_grafico": "dispersion",
        "archivo": "correlacion_venta_edad.png",
    },
    "genero_vs_metodo_pago": {
        "titulo": "Correlacion entre genero y metodo de pago",
        "descripcion": (
            "Mapa de calor de la tabla de contingencia entre genero y metodo "
            "de pago preferido."
        ),
        "tipo_grafico": "mapa_de_calor",
        "archivo": "correlacion_genero_metodo_pago.png",
    },
}


def ejecutar_visualizacion_hallazgos(
    clientes: pd.DataFrame,
    compras: pd.DataFrame,
    directorio_resultados: str | Path | None = RUTA_RESULTADOS_PUNTO_06,
) -> dict[str, Any]:
    """Genera los 7 graficos que representan los hallazgos mas importantes del
    analisis (punto 6), reutilizando las funciones de los puntos 2, 4 y 5."""
    distribucion_ventas_por_mes(compras, directorio_resultados=directorio_resultados)
    distribucion_ventas_por_navegador(
        compras, directorio_resultados=directorio_resultados
    )
    segmentar_por_edad(clientes, directorio_resultados=directorio_resultados)
    comportamiento_por_genero(clientes, directorio_resultados=directorio_resultados)
    impacto_boletines_vales(compras, directorio_resultados=directorio_resultados)
    correlacion_venta_edad(clientes, directorio_resultados=directorio_resultados)
    correlacion_genero_metodo_pago(
        clientes, compras, directorio_resultados=directorio_resultados
    )
    return HALLAZGOS
