from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


RAIZ_PRACTICA = Path(__file__).resolve().parents[1]

from app.analisis.punto_02 import (
    ENV_PREDETERMINADO,
    VARIABLES_NUMERICAS,
    _normalizar_tipos,
    calcular_estadisticas_basicas,
    contrastar_estadisticas,
    ejecutar_analisis,
    validar_integridad,
)


def datos_de_prueba() -> tuple[pd.DataFrame, pd.DataFrame]:
    clientes = pd.DataFrame(
        {
            "id_cliente": [1, 2, 3, 4],
            "edad": [18, 18, 20, 20],
            "genero": [0, 1, 0, 1],
            "venta_total": [10.0, 10.0, 20.0, 30.0],
            "n_compras": [1, 1, 2, 3],
        }
    )
    compras = pd.DataFrame(
        {
            "id_compra": [1, 2, 3, 4],
            "id_cliente": [1, 2, 3, 4],
            "fecha_compra": pd.to_datetime(
                ["2021-01-01", "2021-02-01", "2021-03-01", "2021-04-01"]
            ),
            "monto_compra": [5.5, 5.5, 7.0, 8.0],
            "metodo_pago": [0, 1, 2, 1],
            "tiempo": [100, 200, 200, 300],
            "navegador": [0, 1, 2, 3],
            "boletin": [False, True, False, True],
            "vale": [False, False, True, True],
        }
    )
    return clientes, compras


def test_calcula_media_mediana_y_todas_las_modas() -> None:
    clientes, compras = datos_de_prueba()

    estadisticas = calcular_estadisticas_basicas(clientes, compras).set_index("variable")

    assert estadisticas.loc["edad", "media"] == 19
    assert estadisticas.loc["edad", "mediana"] == 19
    assert estadisticas.loc["edad", "moda"] == "18, 20"
    assert estadisticas.loc["edad", "cantidad_modas"] == 2
    assert estadisticas.loc["monto_compra", "moda"] == "5.5"
    assert estadisticas.loc["tiempo", "frecuencia_moda"] == 2
    assert estadisticas.loc["genero", "media"] == 0.5
    assert estadisticas.loc["genero", "mediana"] == 0.5
    assert estadisticas.loc["genero", "moda"] == "0, 1"
    assert estadisticas.loc["metodo_pago", "moda"] == "1"
    assert estadisticas.loc["navegador", "moda"] == "0, 1, 2, 3"
    assert estadisticas.loc["boletin", "media"] == 0.5
    assert estadisticas.loc["boletin", "moda"] == "0, 1"
    assert estadisticas.loc["vale", "mediana"] == 0.5


def test_incluye_todas_las_variables_solicitadas_y_excluye_identificadores() -> None:
    columnas = {item["columna"] for item in VARIABLES_NUMERICAS}

    assert columnas == {
        "edad",
        "genero",
        "venta_total",
        "n_compras",
        "monto_compra",
        "metodo_pago",
        "tiempo",
        "navegador",
        "boletin",
        "vale",
    }
    assert columnas.isdisjoint({"id_cliente", "id_compra"})


def test_valida_integridad_de_datos_correctos() -> None:
    clientes, compras = datos_de_prueba()

    validaciones = validar_integridad(clientes, compras)

    assert validaciones["cumple"].all()


def test_detecta_una_compra_huerfana() -> None:
    clientes, compras = datos_de_prueba()
    compras.loc[0, "id_cliente"] = 99

    validaciones = validar_integridad(clientes, compras)
    resultado = validaciones.set_index("validacion")

    assert not bool(resultado.loc["sin compras huerfanas", "cumple"])


def test_normalizacion_no_oculta_booleanos_nulos() -> None:
    clientes, compras = datos_de_prueba()
    compras["boletin"] = compras["boletin"].astype(object)
    compras.loc[0, "boletin"] = None

    _, compras_normalizadas = _normalizar_tipos(clientes, compras)
    validaciones = validar_integridad(clientes, compras_normalizadas).set_index(
        "validacion"
    )

    assert pd.isna(compras_normalizadas.loc[0, "boletin"])
    assert not bool(validaciones.loc["sin nulos en compras", "cumple"])


def test_contraste_detecta_diferencias() -> None:
    clientes, compras = datos_de_prueba()
    pandas_df = calcular_estadisticas_basicas(clientes, compras)
    sql_df = pandas_df.rename(
        columns={
            "cantidad": "cantidad_sql",
            "nulos": "nulos_sql",
            "media": "media_sql",
            "mediana": "mediana_sql",
            "moda": "moda_sql",
            "frecuencia_moda": "frecuencia_moda_sql",
        }
    )[
        [
            "tabla",
            "variable",
            "cantidad_sql",
            "nulos_sql",
            "media_sql",
            "mediana_sql",
            "moda_sql",
            "frecuencia_moda_sql",
        ]
    ]
    sql_df.loc[sql_df["variable"] == "edad", "media_sql"] = 999

    contraste = contrastar_estadisticas(pandas_df, sql_df).set_index("variable")

    assert not bool(contraste.loc["edad", "todo_coincide"])
    assert contraste.drop(index="edad")["todo_coincide"].all()


def test_resultados_de_referencia_del_csv_oficial() -> None:
    ruta_csv = RAIZ_PRACTICA / "Enunciado" / "Venta_online_c.csv"
    datos = pd.read_csv(ruta_csv, sep=";")
    clientes = datos[
        ["Id_cliente", "Edad", "Genero", "Venta_total", "N_Compras"]
    ].rename(
        columns={
            "Id_cliente": "id_cliente",
            "Edad": "edad",
            "Genero": "genero",
            "Venta_total": "venta_total",
            "N_Compras": "n_compras",
        }
    )
    compras = datos[
        ["MontoCompra", "MetodoPago", "Tiempo", "Navegador", "Boletin", "Vale"]
    ].rename(
        columns={
            "MontoCompra": "monto_compra",
            "MetodoPago": "metodo_pago",
            "Tiempo": "tiempo",
            "Navegador": "navegador",
            "Boletin": "boletin",
            "Vale": "vale",
        }
    )

    estadisticas = calcular_estadisticas_basicas(clientes, compras).set_index("variable")

    assert len(datos) == 6500
    assert estadisticas.loc["edad", "media"] == pytest.approx(36.3052307692)
    assert estadisticas.loc["edad", "mediana"] == 36
    assert estadisticas.loc["edad", "moda"] == "18"
    assert estadisticas.loc["genero", "media"] == pytest.approx(0.4812307692)
    assert estadisticas.loc["genero", "mediana"] == 0
    assert estadisticas.loc["genero", "moda"] == "0"
    assert estadisticas.loc["venta_total", "media"] == pytest.approx(206.2424307692)
    assert estadisticas.loc["venta_total", "mediana"] == pytest.approx(137.35)
    assert estadisticas.loc["venta_total", "moda"] == "98"
    assert estadisticas.loc["n_compras", "moda"] == "2"
    assert estadisticas.loc["monto_compra", "moda"] == "37.145"
    assert estadisticas.loc["metodo_pago", "moda"] == "1"
    assert estadisticas.loc["tiempo", "moda"] == "852"
    assert estadisticas.loc["navegador", "moda"] == "0"
    assert estadisticas.loc["boletin", "media"] == pytest.approx(2921 / 6500)
    assert estadisticas.loc["boletin", "moda"] == "0"
    assert estadisticas.loc["vale", "media"] == pytest.approx(1254 / 6500)
    assert estadisticas.loc["vale", "moda"] == "0"


@pytest.mark.integration
def test_pipeline_completo_con_base_de_datos(tmp_path: Path) -> None:
    resultado = ejecutar_analisis(ENV_PREDETERMINADO, tmp_path)

    assert resultado["control"]["solo_lectura"] == "on"
    assert resultado["control"]["aislamiento"] == "repeatable read"
    assert len(resultado["clientes"]) == resultado["control"]["clientes_sql"]
    assert len(resultado["compras"]) == resultado["control"]["compras_sql"]
    assert resultado["validaciones"]["cumple"].all()
    assert resultado["contraste"]["todo_coincide"].all()
    assert len(resultado["estadisticas"]) == 10
    assert (tmp_path / "estadisticas_basicas.csv").is_file()
    assert (tmp_path / "resumen_extraccion.json").is_file()
