"""Analisis exploratorio manual de las ventas almacenadas en PostgreSQL."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import Connection, Engine, URL, create_engine, text
from sqlalchemy.exc import OperationalError

from app.config import RUTA_ENV, RUTA_RESULTADOS_PUNTO_02

ENV_PREDETERMINADO = RUTA_ENV

VARIABLES_NUMERICAS = (
    {"tabla": "clientes", "columna": "edad", "unidad": "anios"},
    {"tabla": "clientes", "columna": "venta_total", "unidad": "moneda"},
    {"tabla": "clientes", "columna": "n_compras", "unidad": "compras"},
    {"tabla": "compras", "columna": "monto_compra", "unidad": "moneda"},
    {"tabla": "compras", "columna": "tiempo", "unidad": "segundos"},
)

CONSULTA_CLIENTES = """
SELECT id_cliente, edad, genero, venta_total, n_compras
FROM public.clientes
ORDER BY id_cliente
"""

CONSULTA_COMPRAS = """
SELECT id_compra, id_cliente, fecha_compra, monto_compra,
       metodo_pago, tiempo, navegador, boletin, vale
FROM public.compras
ORDER BY id_compra
"""


def crear_motor(ruta_env: str | Path = ENV_PREDETERMINADO) -> Engine:
    """Crea un motor SQLAlchemy sin incluir secretos en mensajes o archivos."""
    ruta_env = Path(ruta_env).resolve()
    if not ruta_env.is_file():
        raise FileNotFoundError(f"No se encontro el archivo de configuracion: {ruta_env}")

    load_dotenv(ruta_env, override=True)
    requeridas = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    faltantes = [nombre for nombre in requeridas if not os.getenv(nombre)]
    if faltantes:
        raise ValueError(f"Faltan variables en .env: {', '.join(faltantes)}")

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    )
    return create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )


def _normalizar_tipos(
    clientes: pd.DataFrame, compras: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    clientes = clientes.copy()
    compras = compras.copy()

    for columna in ("id_cliente", "edad", "genero", "venta_total", "n_compras"):
        clientes[columna] = pd.to_numeric(clientes[columna], errors="raise")

    for columna in (
        "id_compra",
        "id_cliente",
        "monto_compra",
        "metodo_pago",
        "tiempo",
        "navegador",
    ):
        compras[columna] = pd.to_numeric(compras[columna], errors="raise")

    compras["fecha_compra"] = pd.to_datetime(compras["fecha_compra"], errors="raise")
    # El tipo nullable conserva posibles nulos para que la validacion los detecte.
    compras["boletin"] = compras["boletin"].astype("boolean")
    compras["vale"] = compras["vale"].astype("boolean")
    return clientes, compras


def _obtener_datos_conexion(
    conexion: Connection,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    origen = conexion.execute(
        text(
            """
            SELECT current_database() AS base_datos,
                   current_user AS usuario,
                   current_setting('transaction_read_only') AS solo_lectura,
                   current_setting('transaction_isolation') AS aislamiento,
                   version() AS version_postgresql
            """
        )
    ).mappings().one()
    conteos = conexion.execute(
        text(
            """
            SELECT
                (SELECT COUNT(*) FROM public.clientes) AS clientes,
                (SELECT COUNT(*) FROM public.compras) AS compras,
                (SELECT COUNT(DISTINCT id_cliente) FROM public.clientes)
                    AS clientes_unicos,
                (SELECT COUNT(*)
                 FROM public.compras p
                 LEFT JOIN public.clientes c ON c.id_cliente = p.id_cliente
                 WHERE c.id_cliente IS NULL) AS compras_huerfanas
            """
        )
    ).mappings().one()
    clientes = pd.read_sql_query(text(CONSULTA_CLIENTES), conexion)
    compras = pd.read_sql_query(text(CONSULTA_COMPRAS), conexion)

    clientes, compras = _normalizar_tipos(clientes, compras)
    control = {
        "base_datos": origen["base_datos"],
        "usuario": origen["usuario"],
        "solo_lectura": origen["solo_lectura"],
        "aislamiento": origen["aislamiento"],
        "version_postgresql": origen["version_postgresql"],
        "clientes_sql": int(conteos["clientes"]),
        "compras_sql": int(conteos["compras"]),
        "clientes_unicos_sql": int(conteos["clientes_unicos"]),
        "compras_huerfanas_sql": int(conteos["compras_huerfanas"]),
    }
    return clientes, compras, control


def obtener_datos(engine: Engine) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Obtiene las tablas en una instantanea PostgreSQL consistente y de solo lectura."""
    with engine.connect().execution_options(
        isolation_level="REPEATABLE READ"
    ) as conexion:
        with conexion.begin():
            conexion.execute(text("SET TRANSACTION READ ONLY"))
            return _obtener_datos_conexion(conexion)


def validar_integridad(
    clientes: pd.DataFrame,
    compras: pd.DataFrame,
    control: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Valida que la extraccion sea completa y coherente con el esquema."""
    ids_clientes = set(clientes["id_cliente"])
    ids_compras = set(compras["id_cliente"])
    validaciones: list[dict[str, Any]] = []

    def agregar(nombre: str, cumple: bool, detalle: str) -> None:
        validaciones.append(
            {"validacion": nombre, "cumple": bool(cumple), "detalle": detalle}
        )

    agregar("clientes no vacio", not clientes.empty, f"{len(clientes)} filas")
    agregar("compras no vacio", not compras.empty, f"{len(compras)} filas")
    agregar(
        "id_cliente unico",
        clientes["id_cliente"].is_unique,
        f"{clientes['id_cliente'].nunique()} identificadores unicos",
    )
    agregar(
        "id_compra unico",
        compras["id_compra"].is_unique,
        f"{compras['id_compra'].nunique()} identificadores unicos",
    )
    agregar(
        "sin nulos en clientes",
        not clientes.isna().any().any(),
        f"{int(clientes.isna().sum().sum())} valores nulos",
    )
    agregar(
        "sin nulos en compras",
        not compras.isna().any().any(),
        f"{int(compras.isna().sum().sum())} valores nulos",
    )
    huerfanas = ids_compras - ids_clientes
    agregar("sin compras huerfanas", not huerfanas, f"{len(huerfanas)} huerfanas")
    agregar(
        "dominio de genero",
        set(clientes["genero"].unique()).issubset({0, 1}),
        f"valores: {sorted(clientes['genero'].unique().tolist())}",
    )
    agregar(
        "dominio de metodo_pago",
        set(compras["metodo_pago"].unique()).issubset({0, 1, 2}),
        f"valores: {sorted(compras['metodo_pago'].unique().tolist())}",
    )
    agregar(
        "dominio de navegador",
        set(compras["navegador"].unique()).issubset({0, 1, 2, 3, 4}),
        f"valores: {sorted(compras['navegador'].unique().tolist())}",
    )
    agregar(
        "fechas del anio 2021",
        set(compras["fecha_compra"].dt.year.unique()) == {2021},
        f"{compras['fecha_compra'].min().date()} a {compras['fecha_compra'].max().date()}",
    )

    for especificacion in VARIABLES_NUMERICAS:
        tabla = especificacion["tabla"]
        columna = especificacion["columna"]
        datos = clientes if tabla == "clientes" else compras
        agregar(
            f"tipo numerico {tabla}.{columna}",
            pd.api.types.is_numeric_dtype(datos[columna]),
            str(datos[columna].dtype),
        )

    if control is not None:
        agregar(
            "transaccion de solo lectura",
            control["solo_lectura"] == "on",
            f"transaction_read_only={control['solo_lectura']}",
        )
        agregar(
            "instantanea consistente",
            control["aislamiento"] == "repeatable read",
            f"transaction_isolation={control['aislamiento']}",
        )
        agregar(
            "conteo de clientes coincide",
            len(clientes) == control["clientes_sql"],
            f"Pandas={len(clientes)}, SQL={control['clientes_sql']}",
        )
        agregar(
            "conteo de compras coincide",
            len(compras) == control["compras_sql"],
            f"Pandas={len(compras)}, SQL={control['compras_sql']}",
        )
        agregar(
            "control SQL sin huerfanas",
            control["compras_huerfanas_sql"] == 0,
            f"{control['compras_huerfanas_sql']} huerfanas",
        )

    return pd.DataFrame(validaciones)


def _formatear_valor(valor: Any) -> str:
    numero = float(valor)
    if numero.is_integer():
        return str(int(numero))
    return format(numero, ".12g")


def _resumir_serie(tabla: str, columna: str, unidad: str, serie: pd.Series) -> dict[str, Any]:
    valores = pd.to_numeric(serie, errors="raise").dropna()
    if valores.empty:
        raise ValueError(f"No hay datos para calcular {tabla}.{columna}")

    modas = sorted(float(valor) for valor in valores.mode().tolist())
    frecuencia_moda = int(valores.value_counts().max())
    return {
        "tabla": tabla,
        "variable": columna,
        "unidad": unidad,
        "cantidad": int(valores.size),
        "nulos": int(serie.isna().sum()),
        "media": float(valores.mean()),
        "mediana": float(valores.median()),
        "moda": ", ".join(_formatear_valor(valor) for valor in modas),
        "frecuencia_moda": frecuencia_moda,
        "cantidad_modas": len(modas),
    }


def calcular_estadisticas_basicas(
    clientes: pd.DataFrame, compras: pd.DataFrame
) -> pd.DataFrame:
    """Calcula media, mediana y todas las modas de variables cuantitativas."""
    resultados = []
    for especificacion in VARIABLES_NUMERICAS:
        tabla = especificacion["tabla"]
        datos = clientes if tabla == "clientes" else compras
        resultados.append(
            _resumir_serie(
                tabla,
                especificacion["columna"],
                especificacion["unidad"],
                datos[especificacion["columna"]],
            )
        )
    return pd.DataFrame(resultados)


def _obtener_estadisticas_sql_conexion(conexion: Connection) -> pd.DataFrame:
    resultados = []
    for especificacion in VARIABLES_NUMERICAS:
        tabla = especificacion["tabla"]
        columna = especificacion["columna"]
        resumen = conexion.execute(
            text(
                f"""
                SELECT COUNT({columna}) AS cantidad,
                       COUNT(*) - COUNT({columna}) AS nulos,
                       AVG({columna}) AS media,
                       percentile_cont(0.5)
                           WITHIN GROUP (ORDER BY {columna}) AS mediana
                FROM public.{tabla}
                """
            )
        ).mappings().one()
        filas_moda = conexion.execute(
            text(
                f"""
                WITH frecuencias AS (
                    SELECT {columna} AS valor, COUNT(*) AS frecuencia
                    FROM public.{tabla}
                    WHERE {columna} IS NOT NULL
                    GROUP BY {columna}
                )
                SELECT valor, frecuencia
                FROM frecuencias
                WHERE frecuencia = (SELECT MAX(frecuencia) FROM frecuencias)
                ORDER BY valor
                """
            )
        ).mappings().all()
        resultados.append(
            {
                "tabla": tabla,
                "variable": columna,
                "cantidad_sql": int(resumen["cantidad"]),
                "nulos_sql": int(resumen["nulos"]),
                "media_sql": float(resumen["media"]),
                "mediana_sql": float(resumen["mediana"]),
                "moda_sql": ", ".join(
                    _formatear_valor(fila["valor"]) for fila in filas_moda
                ),
                "frecuencia_moda_sql": int(filas_moda[0]["frecuencia"]),
            }
        )
    return pd.DataFrame(resultados)


def obtener_estadisticas_sql(engine: Engine) -> pd.DataFrame:
    """Calcula las mismas estadisticas directamente en PostgreSQL."""
    with engine.connect().execution_options(
        isolation_level="REPEATABLE READ"
    ) as conexion:
        with conexion.begin():
            conexion.execute(text("SET TRANSACTION READ ONLY"))
            return _obtener_estadisticas_sql_conexion(conexion)


def obtener_datos_y_estadisticas_sql(
    engine: Engine,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], pd.DataFrame]:
    """Extrae datos y calcula controles SQL sobre exactamente la misma instantanea."""
    with engine.connect().execution_options(
        isolation_level="REPEATABLE READ"
    ) as conexion:
        with conexion.begin():
            conexion.execute(text("SET TRANSACTION READ ONLY"))
            clientes, compras, control = _obtener_datos_conexion(conexion)
            estadisticas_sql = _obtener_estadisticas_sql_conexion(conexion)
    return clientes, compras, control, estadisticas_sql


def contrastar_estadisticas(
    estadisticas_pandas: pd.DataFrame,
    estadisticas_sql: pd.DataFrame,
    tolerancia: float = 1e-9,
) -> pd.DataFrame:
    """Contrasta ambos motores para detectar errores de calculo o extraccion."""
    contraste = estadisticas_pandas.merge(
        estadisticas_sql, on=["tabla", "variable"], validate="one_to_one"
    )
    contraste["cantidad_coincide"] = contraste["cantidad"] == contraste["cantidad_sql"]
    contraste["nulos_coincide"] = contraste["nulos"] == contraste["nulos_sql"]
    contraste["media_coincide"] = np.isclose(
        contraste["media"], contraste["media_sql"], rtol=0, atol=tolerancia
    )
    contraste["mediana_coincide"] = np.isclose(
        contraste["mediana"], contraste["mediana_sql"], rtol=0, atol=tolerancia
    )
    contraste["moda_coincide"] = contraste["moda"] == contraste["moda_sql"]
    contraste["frecuencia_moda_coincide"] = (
        contraste["frecuencia_moda"] == contraste["frecuencia_moda_sql"]
    )
    columnas_revision = [
        "cantidad_coincide",
        "nulos_coincide",
        "media_coincide",
        "mediana_coincide",
        "moda_coincide",
        "frecuencia_moda_coincide",
    ]
    contraste["todo_coincide"] = contraste[columnas_revision].all(axis=1)
    return contraste


def _crear_resumen(
    clientes: pd.DataFrame,
    compras: pd.DataFrame,
    control: dict[str, Any],
    validaciones: pd.DataFrame,
    contraste: pd.DataFrame,
) -> dict[str, Any]:
    return {
        "origen": {
            "motor": "PostgreSQL",
            "base_datos": control["base_datos"],
            "transaccion_solo_lectura": control["solo_lectura"] == "on",
            "aislamiento": control["aislamiento"],
        },
        "extraccion": {
            "filas_clientes": len(clientes),
            "filas_compras": len(compras),
            "columnas_clientes": clientes.columns.tolist(),
            "columnas_compras": compras.columns.tolist(),
            "tipos_clientes": {col: str(tipo) for col, tipo in clientes.dtypes.items()},
            "tipos_compras": {col: str(tipo) for col, tipo in compras.dtypes.items()},
            "fecha_minima": compras["fecha_compra"].min().date().isoformat(),
            "fecha_maxima": compras["fecha_compra"].max().date().isoformat(),
        },
        "verificacion": {
            "validaciones_superadas": bool(validaciones["cumple"].all()),
            "estadisticas_contrastadas_con_sql": bool(contraste["todo_coincide"].all()),
        },
    }


def exportar_resultados(
    directorio: str | Path,
    estadisticas: pd.DataFrame,
    estadisticas_sql: pd.DataFrame,
    contraste: pd.DataFrame,
    validaciones: pd.DataFrame,
    resumen: dict[str, Any],
) -> None:
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)

    def preparar_exportacion(datos: pd.DataFrame) -> pd.DataFrame:
        exportacion = datos.copy()
        columnas_decimales = [
            columna
            for columna in ("media", "mediana", "media_sql", "mediana_sql")
            if columna in exportacion
        ]
        exportacion[columnas_decimales] = exportacion[columnas_decimales].round(6)
        return exportacion

    preparar_exportacion(estadisticas).to_csv(
        directorio / "estadisticas_basicas.csv", index=False
    )
    preparar_exportacion(estadisticas_sql).to_csv(
        directorio / "estadisticas_sql.csv", index=False
    )
    preparar_exportacion(contraste).to_csv(
        directorio / "contraste_pandas_sql.csv", index=False
    )
    validaciones.to_csv(directorio / "validaciones_extraccion.csv", index=False)
    with (directorio / "resumen_extraccion.json").open("w", encoding="utf-8") as archivo:
        json.dump(resumen, archivo, ensure_ascii=False, indent=2)


def ejecutar_analisis(
    ruta_env: str | Path = ENV_PREDETERMINADO,
    directorio_resultados: str | Path | None = RUTA_RESULTADOS_PUNTO_02,
) -> dict[str, Any]:
    """Ejecuta y verifica de extremo a extremo los incisos 2.a y 2.b."""
    engine = crear_motor(ruta_env)
    try:
        clientes, compras, control, estadisticas_sql = obtener_datos_y_estadisticas_sql(
            engine
        )
        validaciones = validar_integridad(clientes, compras, control)
        if not validaciones["cumple"].all():
            fallos = validaciones.loc[~validaciones["cumple"], "validacion"].tolist()
            raise AssertionError(f"Fallaron validaciones de extraccion: {', '.join(fallos)}")

        estadisticas = calcular_estadisticas_basicas(clientes, compras)
        contraste = contrastar_estadisticas(estadisticas, estadisticas_sql)
        if not contraste["todo_coincide"].all():
            fallos = contraste.loc[
                ~contraste["todo_coincide"], ["tabla", "variable"]
            ].astype(str).agg(".".join, axis=1).tolist()
            raise AssertionError(f"Pandas y SQL no coinciden en: {', '.join(fallos)}")

        resumen = _crear_resumen(clientes, compras, control, validaciones, contraste)
        if directorio_resultados is not None:
            exportar_resultados(
                directorio_resultados,
                estadisticas,
                estadisticas_sql,
                contraste,
                validaciones,
                resumen,
            )
        return {
            "clientes": clientes,
            "compras": compras,
            "control": control,
            "validaciones": validaciones,
            "estadisticas": estadisticas,
            "estadisticas_sql": estadisticas_sql,
            "contraste": contraste,
            "resumen": resumen,
        }
    except OperationalError:
        raise ConnectionError(
            "No se pudo conectar con PostgreSQL. Verifique que la instancia este "
            "encendida y que el puerto configurado permita conexiones desde esta red."
        ) from None
    finally:
        engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", type=Path, default=ENV_PREDETERMINADO)
    parser.add_argument(
        "--salida", type=Path, default=RUTA_RESULTADOS_PUNTO_02
    )
    argumentos = parser.parse_args()
    try:
        resultado = ejecutar_analisis(argumentos.env, argumentos.salida)
    except ConnectionError as error:
        parser.exit(1, f"Error: {error}\n")

    print("\nExtraccion verificada")
    print(f"Clientes: {len(resultado['clientes'])}")
    print(f"Compras:  {len(resultado['compras'])}")
    print("Transaccion de solo lectura: si")
    print("\nEstadisticas basicas (calculadas con Pandas)")
    print(resultado["estadisticas"].to_string(index=False))
    print("\nContraste independiente con PostgreSQL")
    print(
        resultado["contraste"][["tabla", "variable", "todo_coincide"]].to_string(
            index=False
        )
    )
    print(f"\nResultados guardados en: {argumentos.salida.resolve()}")


if __name__ == "__main__":
    main()
