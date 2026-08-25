"""Analisis de tendencias (Punto 3).

a. Meses con mayores y menores ventas.
b. Navegador (canal) mas preferido y menos popular.
c. Total de ventas pagadas en efectivo / contra entrega.
d. Meses donde se usaron mas boletines y vales.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

NAVEGADOR_DESC = {
    0: "Tienda Fisica",
    1: "Navegador 1",
    2: "Navegador 2",
    3: "Navegador 3",
    4: "Navegador 4",
}

METODO_PAGO_DESC = {
    0: "Efectivo / Contra entrega",
    1: "Tarjeta de Credito",
    2: "Tarjeta de Debito",
}


def ventas_por_mes(
    compras: pd.DataFrame, directorio_resultados: Path = None, graficar: bool = True
) -> dict:
    """3.a Determina los meses con mayores y menores ventas (segun monto_compra)."""
    df = compras.copy()
    df["mes"] = df["fecha_compra"].dt.month
    resumen = (
        df.groupby("mes")["monto_compra"]
        .agg(total_ventas="sum", n_compras="count", venta_promedio="mean")
        .reset_index()
    )
    resumen["mes_nombre"] = resumen["mes"].map(MESES_ES)
    resumen = resumen.sort_values("mes").reset_index(drop=True)

    fila_max = resumen.loc[resumen["total_ventas"].idxmax()]
    fila_min = resumen.loc[resumen["total_ventas"].idxmin()]

    resultado = {
        "tabla_mensual": resumen,
        "mes_mayor_venta": fila_max["mes_nombre"],
        "mes_mayor_venta_total": float(fila_max["total_ventas"]),
        "mes_menor_venta": fila_min["mes_nombre"],
        "mes_menor_venta_total": float(fila_min["total_ventas"]),
    }

    if graficar:
        plt.figure(figsize=(10, 5))
        plt.bar(resumen["mes_nombre"], resumen["total_ventas"], color="steelblue")
        plt.title("Ventas totales por mes (2021)")
        plt.xlabel("Mes")
        plt.ylabel("Venta total ($)")
        plt.xticks(rotation=45)
        if directorio_resultados:
            directorio_resultados.mkdir(parents=True, exist_ok=True)
            plt.savefig(directorio_resultados / "ventas_por_mes.png", bbox_inches="tight")
        plt.show()

    return resultado


def navegador_preferido(
    compras: pd.DataFrame, directorio_resultados: Path = None, graficar: bool = True
) -> dict:
    """3.b Identifica el navegador/canal mas preferido y el menos popular."""
    conteo = compras["navegador"].value_counts().reset_index()
    conteo.columns = ["navegador", "n_compras"]
    conteo["navegador_desc"] = conteo["navegador"].map(NAVEGADOR_DESC)
    conteo = conteo.sort_values("n_compras", ascending=False).reset_index(drop=True)

    fila_max = conteo.iloc[0]
    fila_min = conteo.iloc[-1]

    resultado = {
        "tabla_navegadores": conteo,
        "navegador_mas_preferido": fila_max["navegador_desc"],
        "navegador_mas_preferido_compras": int(fila_max["n_compras"]),
        "navegador_menos_popular": fila_min["navegador_desc"],
        "navegador_menos_popular_compras": int(fila_min["n_compras"]),
    }

    if graficar:
        plt.figure(figsize=(8, 5))
        plt.bar(conteo["navegador_desc"], conteo["n_compras"], color="darkorange")
        plt.title("Compras por navegador / canal")
        plt.xlabel("Navegador")
        plt.ylabel("Numero de compras")
        plt.xticks(rotation=30)
        if directorio_resultados:
            directorio_resultados.mkdir(parents=True, exist_ok=True)
            plt.savefig(directorio_resultados / "navegador_preferido.png", bbox_inches="tight")
        plt.show()

    return resultado


def ventas_efectivo_contra_entrega(
    compras: pd.DataFrame, directorio_resultados: Path = None, graficar: bool = True
) -> dict:
    """3.c Identifica el total de ventas pagadas en efectivo / contra entrega (metodo_pago = 0)."""
    df = compras.copy()
    df["metodo_desc"] = df["metodo_pago"].map(METODO_PAGO_DESC)
    resumen = (
        df.groupby("metodo_desc")["monto_compra"]
        .agg(total_ventas="sum", n_compras="count")
        .reset_index()
        .sort_values("total_ventas", ascending=False)
        .reset_index(drop=True)
    )

    compras_efectivo = df.loc[df["metodo_pago"] == 0]
    total_efectivo = float(compras_efectivo["monto_compra"].sum())
    n_compras_efectivo = int(len(compras_efectivo))
    total_general = float(df["monto_compra"].sum())
    porcentaje_efectivo = (total_efectivo / total_general * 100) if total_general else 0.0

    resultado = {
        "tabla_metodo_pago": resumen,
        "total_efectivo_contra_entrega": total_efectivo,
        "n_compras_efectivo_contra_entrega": n_compras_efectivo,
        "porcentaje_del_total": float(porcentaje_efectivo),
    }

    if graficar:
        plt.figure(figsize=(7, 5))
        plt.bar(resumen["metodo_desc"], resumen["total_ventas"], color="seagreen")
        plt.title("Ventas totales por metodo de pago")
        plt.xlabel("Metodo de pago")
        plt.ylabel("Venta total ($)")
        plt.xticks(rotation=15)
        if directorio_resultados:
            directorio_resultados.mkdir(parents=True, exist_ok=True)
            plt.savefig(directorio_resultados / "ventas_metodo_pago.png", bbox_inches="tight")
        plt.show()

    return resultado


def boletines_vales_por_mes(
    compras: pd.DataFrame, directorio_resultados: Path = None, graficar: bool = True
) -> dict:
    """3.d Identifica los meses donde se usaron mas boletines y mas vales."""
    df = compras.copy()
    df["mes"] = df["fecha_compra"].dt.month
    resumen = (
        df.groupby("mes")
        .agg(n_boletines=("boletin", "sum"), n_vales=("vale", "sum"))
        .reset_index()
    )
    resumen["mes_nombre"] = resumen["mes"].map(MESES_ES)
    resumen["n_boletines"] = resumen["n_boletines"].astype(int)
    resumen["n_vales"] = resumen["n_vales"].astype(int)
    resumen = resumen.sort_values("mes").reset_index(drop=True)

    fila_max_boletin = resumen.loc[resumen["n_boletines"].idxmax()]
    fila_max_vale = resumen.loc[resumen["n_vales"].idxmax()]

    resultado = {
        "tabla_mensual": resumen,
        "mes_mas_boletines": fila_max_boletin["mes_nombre"],
        "mes_mas_boletines_cantidad": int(fila_max_boletin["n_boletines"]),
        "mes_mas_vales": fila_max_vale["mes_nombre"],
        "mes_mas_vales_cantidad": int(fila_max_vale["n_vales"]),
    }

    if graficar:
        plt.figure(figsize=(10, 5))
        ancho = 0.35
        posiciones = range(len(resumen))
        plt.bar(
            [p - ancho / 2 for p in posiciones], resumen["n_boletines"],
            width=ancho, label="Boletines", color="mediumpurple",
        )
        plt.bar(
            [p + ancho / 2 for p in posiciones], resumen["n_vales"],
            width=ancho, label="Vales", color="gold",
        )
        plt.xticks(list(posiciones), resumen["mes_nombre"], rotation=45)
        plt.title("Uso de boletines y vales por mes")
        plt.xlabel("Mes")
        plt.ylabel("Cantidad de compras")
        plt.legend()
        if directorio_resultados:
            directorio_resultados.mkdir(parents=True, exist_ok=True)
            plt.savefig(directorio_resultados / "boletines_vales_por_mes.png", bbox_inches="tight")
        plt.show()

    return resultado


def ejecutar_tendencias(compras: pd.DataFrame, directorio_resultados: Path = None) -> None:
    """Funcion maestra: ejecuta todo el punto 3 e imprime los resultados en consola."""
    print("--- 3.a Ventas por mes ---")
    res_meses = ventas_por_mes(compras, directorio_resultados)
    print(res_meses["tabla_mensual"].to_string(index=False))
    print(f"Mayor venta: {res_meses['mes_mayor_venta']} (${res_meses['mes_mayor_venta_total']:.2f})")
    print(f"Menor venta: {res_meses['mes_menor_venta']} (${res_meses['mes_menor_venta_total']:.2f})")

    print("\n--- 3.b Navegador preferido ---")
    res_nav = navegador_preferido(compras, directorio_resultados)
    print(res_nav["tabla_navegadores"].to_string(index=False))
    print(f"Mas preferido: {res_nav['navegador_mas_preferido']}")
    print(f"Menos popular: {res_nav['navegador_menos_popular']}")

    print("\n--- 3.c Ventas en efectivo / contra entrega ---")
    res_efec = ventas_efectivo_contra_entrega(compras, directorio_resultados)
    print(res_efec["tabla_metodo_pago"].to_string(index=False))
    print(
        f"Total efectivo/contra entrega: ${res_efec['total_efectivo_contra_entrega']:.2f} "
        f"({res_efec['porcentaje_del_total']:.2f}% del total)"
    )

    print("\n--- 3.d Boletines y vales por mes ---")
    res_bv = boletines_vales_por_mes(compras, directorio_resultados)
    print(res_bv["tabla_mensual"].to_string(index=False))
    print(f"Mes con mas boletines: {res_bv['mes_mas_boletines']} ({res_bv['mes_mas_boletines_cantidad']})")
    print(f"Mes con mas vales: {res_bv['mes_mas_vales']} ({res_bv['mes_mas_vales_cantidad']})")