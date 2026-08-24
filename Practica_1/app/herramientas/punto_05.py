"""Funciones que el servidor MCP expone al agente conversacional para correlación."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from app.analisis.punto_02 import crear_motor, obtener_datos
from app.analisis.punto_05 import (
    correlacion_venta_edad,
    correlacion_genero_metodo_pago,
    correlacion_boletin_vale,
)
from app.config import RUTA_ENV


def _registros_json(datos: pd.DataFrame) -> list[dict[str, Any]]:
    """Convierte tipos de Pandas y NumPy a valores JSON nativos."""
    return json.loads(datos.to_json(orient="records", date_format="iso"))


def _tabla_contingencia_a_registros(tabla: pd.DataFrame) -> list[dict[str, Any]]:
    """Convierte una tabla de contingencia (con índice) a una lista de registros JSON."""
    return _registros_json(tabla.reset_index())


def _obtener_datos_frescos():
    """Conecta a BD y extrae clientes y compras."""
    motor = crear_motor(RUTA_ENV)
    clientes, compras, _ = obtener_datos(motor)
    return clientes, compras


def consultar_correlacion_venta_edad() -> dict[str, Any]:
    """Investiga si existe una relacion entre el total de la venta y la edad del cliente."""
    clientes, _ = _obtener_datos_frescos()
    resultado = correlacion_venta_edad(clientes, graficar=False)

    return {
        "exito": True,
        "analisis": "Correlacion Venta Total vs Edad",
        "pearson_r": resultado["pearson_r"],
        "pearson_p_valor": resultado["pearson_p_valor"],
        "spearman_r": resultado["spearman_r"],
        "spearman_p_valor": resultado["spearman_p_valor"],
        "interpretacion": resultado["interpretacion"],
        "significativo": resultado["significativo"],
        "nota": "Pearson mide relacion lineal; Spearman detecta relaciones no lineales monotonas.",
    }


def consultar_correlacion_genero_metodo_pago() -> dict[str, Any]:
    """Examina si hay una correlacion entre el genero del cliente y el metodo de pago preferido."""
    clientes, compras = _obtener_datos_frescos()
    resultado = correlacion_genero_metodo_pago(clientes, compras, graficar=False)

    return {
        "exito": True,
        "analisis": "Correlacion Genero vs Metodo de Pago",
        "tabla_contingencia": _tabla_contingencia_a_registros(resultado["tabla_contingencia"]),
        "chi2": resultado["chi2"],
        "p_valor": resultado["p_valor"],
        "grados_libertad": resultado["grados_libertad"],
        "cramers_v": resultado["cramers_v"],
        "interpretacion": resultado["interpretacion"],
        "significativo": resultado["significativo"],
        "nota": "El metodo de pago preferido es el mas frecuente por cliente (moda de sus compras).",
    }


def consultar_correlacion_boletin_vale() -> dict[str, Any]:
    """Investiga si existe una correlacion entre los clientes que utilizan boletines y vales."""
    _, compras = _obtener_datos_frescos()
    resultado = correlacion_boletin_vale(compras, graficar=False)

    return {
        "exito": True,
        "analisis": "Correlacion Boletin vs Vale",
        "tabla_contingencia": _tabla_contingencia_a_registros(resultado["tabla_contingencia"]),
        "chi2": resultado["chi2"],
        "p_valor": resultado["p_valor"],
        "grados_libertad": resultado["grados_libertad"],
        "phi": resultado["phi"],
        "interpretacion": resultado["interpretacion"],
        "significativo": resultado["significativo"],
        "nota": "Phi equivale a Pearson aplicado sobre boletin y vale codificados como 0/1.",
    }