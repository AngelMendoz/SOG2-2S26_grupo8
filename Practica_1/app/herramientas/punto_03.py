"""Funciones que el servidor MCP expone al agente conversacional para tendencias (Punto 3)."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from app.analisis.punto_02 import crear_motor, obtener_datos
from app.analisis.punto_03 import (
    boletines_vales_por_mes,
    navegador_preferido,
    ventas_efectivo_contra_entrega,
    ventas_por_mes,
)
from app.config import RUTA_ENV


def _registros_json(datos: pd.DataFrame) -> list[dict[str, Any]]:
    """Convierte tipos de Pandas y NumPy a valores JSON nativos."""
    return json.loads(datos.to_json(orient="records", date_format="iso"))


def _obtener_compras_frescas() -> pd.DataFrame:
    """Conecta a BD y extrae solo la tabla compras (suficiente para tendencias)."""
    motor = crear_motor(RUTA_ENV)
    _clientes, compras, _control = obtener_datos(motor)
    return compras


def consultar_ventas_por_mes() -> dict[str, Any]:
    """3.a Determina los meses con mayores y menores ventas totales."""
    compras = _obtener_compras_frescas()
    resultado = ventas_por_mes(compras, graficar=False)

    tabla = resultado["tabla_mensual"].copy()
    tabla[["total_ventas", "venta_promedio"]] = tabla[
        ["total_ventas", "venta_promedio"]
    ].round(6)

    return {
        "exito": True,
        "analisis": "Ventas totales por mes (2021)",
        "tabla_mensual": _registros_json(tabla),
        "mes_mayor_venta": resultado["mes_mayor_venta"],
        "mes_mayor_venta_total": round(resultado["mes_mayor_venta_total"], 6),
        "mes_menor_venta": resultado["mes_menor_venta"],
        "mes_menor_venta_total": round(resultado["mes_menor_venta_total"], 6),
        "nota": (
            "El total de ventas se calcula sumando monto_compra agrupado "
            "por el mes de fecha_compra."
        ),
    }


def consultar_navegador_preferido() -> dict[str, Any]:
    """3.b Identifica el navegador (canal) mas preferido y el menos popular."""
    compras = _obtener_compras_frescas()
    resultado = navegador_preferido(compras, graficar=False)

    return {
        "exito": True,
        "analisis": "Navegador / canal mas y menos utilizado",
        "tabla_navegadores": _registros_json(resultado["tabla_navegadores"]),
        "navegador_mas_preferido": resultado["navegador_mas_preferido"],
        "navegador_mas_preferido_compras": resultado["navegador_mas_preferido_compras"],
        "navegador_menos_popular": resultado["navegador_menos_popular"],
        "navegador_menos_popular_compras": resultado["navegador_menos_popular_compras"],
        "nota": "Navegador 0 corresponde a la tienda fisica; 1-4 son canales web.",
    }


def consultar_ventas_efectivo_contra_entrega() -> dict[str, Any]:
    """3.c Identifica el total de ventas pagadas en efectivo o contra entrega."""
    compras = _obtener_compras_frescas()
    resultado = ventas_efectivo_contra_entrega(compras, graficar=False)

    tabla = resultado["tabla_metodo_pago"].copy()
    tabla["total_ventas"] = tabla["total_ventas"].round(6)

    return {
        "exito": True,
        "analisis": "Ventas por metodo de pago, con foco en efectivo / contra entrega",
        "tabla_metodo_pago": _registros_json(tabla),
        "total_efectivo_contra_entrega": round(resultado["total_efectivo_contra_entrega"], 6),
        "n_compras_efectivo_contra_entrega": resultado["n_compras_efectivo_contra_entrega"],
        "porcentaje_del_total": round(resultado["porcentaje_del_total"], 6),
        "nota": (
            "metodo_pago = 0 agrupa efectivo y pago contra entrega, segun "
            "la aclaracion del enunciado."
        ),
    }


def consultar_boletines_vales_por_mes() -> dict[str, Any]:
    """3.d Identifica los meses donde se usaron mas boletines y mas vales."""
    compras = _obtener_compras_frescas()
    resultado = boletines_vales_por_mes(compras, graficar=False)

    return {
        "exito": True,
        "analisis": "Uso de boletines y vales por mes (2021)",
        "tabla_mensual": _registros_json(resultado["tabla_mensual"]),
        "mes_mas_boletines": resultado["mes_mas_boletines"],
        "mes_mas_boletines_cantidad": resultado["mes_mas_boletines_cantidad"],
        "mes_mas_vales": resultado["mes_mas_vales"],
        "mes_mas_vales_cantidad": resultado["mes_mas_vales_cantidad"],
        "nota": (
            "Se cuentan por separado las compras con boletin=TRUE y vale=TRUE, "
            "agrupadas por mes."
        ),
    }