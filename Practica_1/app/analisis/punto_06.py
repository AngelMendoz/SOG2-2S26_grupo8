"""Visualizacion de los hallazgos mas importantes del analisis (Punto 6)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.analisis.punto_02 import (
    _graficar_barras,
    distribucion_ventas_por_mes,
    distribucion_ventas_por_navegador,
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

RANGOS_EDAD_BINS = [17, 25, 35, 45, 55, 65, 120]
RANGOS_EDAD_ETIQUETAS = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]


def _ventas_por_edad(
    clientes: pd.DataFrame, directorio_resultados: str | Path | None
) -> pd.DataFrame:
    """Ventas totales por rango de edad, con valor y % anotados sobre cada barra."""
    df = clientes.copy()
    df["rango_edad"] = pd.cut(
        df["edad"], bins=RANGOS_EDAD_BINS, labels=RANGOS_EDAD_ETIQUETAS
    )
    resumen = (
        df.groupby("rango_edad", observed=False)
        .agg(
            total_clientes=("id_cliente", "count"),
            ventas_totales=("venta_total", "sum"),
        )
        .reset_index()
    )
    _graficar_barras(
        resumen,
        x="rango_edad",
        y="ventas_totales",
        titulo="Ventas Totales por Rango de Edad",
        etiqueta_x="Rango de Edad",
        etiqueta_y="Ventas Totales ($)",
        nombre_archivo=HALLAZGOS["ventas_por_edad"]["archivo"],
        directorio_resultados=directorio_resultados,
        paleta="viridis",
        n_registros=len(clientes),
        unidad_fuente="clientes",
    )
    return resumen


def _ventas_por_genero(
    clientes: pd.DataFrame, directorio_resultados: str | Path | None
) -> pd.DataFrame:
    """Ventas totales por genero, con valor y % anotados sobre cada barra."""
    df = clientes.copy()
    df["genero_desc"] = df["genero"].map({1: "Femenino", 0: "Masculino"})
    resumen = (
        df.groupby("genero_desc")
        .agg(
            total_clientes=("id_cliente", "count"),
            ventas_totales=("venta_total", "sum"),
        )
        .reset_index()
    )
    _graficar_barras(
        resumen,
        x="genero_desc",
        y="ventas_totales",
        titulo="Ventas Totales por Genero",
        etiqueta_x="Genero",
        etiqueta_y="Ventas Totales ($)",
        nombre_archivo=HALLAZGOS["ventas_por_genero"]["archivo"],
        directorio_resultados=directorio_resultados,
        paleta="Set2",
        n_registros=len(clientes),
        unidad_fuente="clientes",
    )
    return resumen


def _monto_por_boletin_vale(
    compras: pd.DataFrame, directorio_resultados: str | Path | None
) -> pd.DataFrame:
    """Monto total por uso combinado de boletin y vale, con valor y % anotados."""
    df = compras.copy()
    df["tipo_compra"] = "Normal"
    df.loc[(df["boletin"] == True) & (df["vale"] == False), "tipo_compra"] = (
        "Solo Boletin"
    )
    df.loc[(df["boletin"] == False) & (df["vale"] == True), "tipo_compra"] = (
        "Solo Vale"
    )
    df.loc[(df["boletin"] == True) & (df["vale"] == True), "tipo_compra"] = (
        "Boletin y Vale"
    )
    resumen = (
        df.groupby("tipo_compra")
        .agg(
            cantidad_compras=("id_compra", "count"),
            monto_total=("monto_compra", "sum"),
        )
        .reset_index()
        .sort_values("monto_total", ascending=False)
        .reset_index(drop=True)
    )
    _graficar_barras(
        resumen,
        x="tipo_compra",
        y="monto_total",
        titulo="Monto Total de Compras por Uso de Boletin/Vale",
        etiqueta_x="Clasificacion",
        etiqueta_y="Monto Total ($)",
        nombre_archivo=HALLAZGOS["boletin_vale"]["archivo"],
        directorio_resultados=directorio_resultados,
        paleta="cubehelix",
        n_registros=len(compras),
    )
    return resumen


def ejecutar_visualizacion_hallazgos(
    clientes: pd.DataFrame,
    compras: pd.DataFrame,
    directorio_resultados: str | Path | None = RUTA_RESULTADOS_PUNTO_06,
) -> dict[str, Any]:
    """Genera los 7 graficos que representan los hallazgos mas importantes del
    analisis (punto 6).

    Los graficos de barras y de linea (mes, navegador, edad, genero,
    boletin/vale) llevan el valor exacto y el porcentaje del total anotados
    sobre cada barra o punto, mas una nota de fuente al pie, siguiendo el
    estandar de graficos precisos pedido en el curso. Los dos graficos de
    correlacion reutilizan las funciones del punto 5 tal cual, ya que ya
    muestran sus valores exactos por naturaleza (conteos en el mapa de calor,
    coeficiente r en el titulo del grafico de dispersion).
    """
    distribucion_ventas_por_mes(compras, directorio_resultados=directorio_resultados)
    distribucion_ventas_por_navegador(
        compras, directorio_resultados=directorio_resultados
    )
    _ventas_por_edad(clientes, directorio_resultados)
    _ventas_por_genero(clientes, directorio_resultados)
    _monto_por_boletin_vale(compras, directorio_resultados)
    correlacion_venta_edad(clientes, directorio_resultados=directorio_resultados)
    correlacion_genero_metodo_pago(
        clientes, compras, directorio_resultados=directorio_resultados
    )
    return HALLAZGOS
