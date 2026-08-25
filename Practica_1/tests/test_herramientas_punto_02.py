from __future__ import annotations

import pytest

from app.herramientas.punto_02 import (
    consultar_distribucion_ventas,
    consultar_estadisticas_basicas,
    consultar_muestra_datos,
    consultar_resumen_datos,
)


def test_muestra_rechaza_tabla_no_permitida() -> None:
    with pytest.raises(ValueError, match="clientes.*compras"):
        consultar_muestra_datos("usuarios", 5)


def test_muestra_rechaza_limites_no_permitidos() -> None:
    with pytest.raises(ValueError, match="entre 1 y 20"):
        consultar_muestra_datos("clientes", 21)


def test_distribucion_rechaza_dimension_no_permitida() -> None:
    with pytest.raises(ValueError, match="mes.*metodo_pago"):
        consultar_distribucion_ventas("region")


@pytest.mark.integration
def test_resumen_para_el_agente_proviene_de_postgresql() -> None:
    resultado = consultar_resumen_datos()

    assert resultado["exito"] is True
    assert resultado["origen"]["motor"] == "PostgreSQL"
    assert resultado["origen"]["transaccion_solo_lectura"] is True
    assert resultado["extraccion"]["filas_clientes"] == 6500
    assert resultado["extraccion"]["filas_compras"] == 6500
    assert resultado["verificacion"]["validaciones_superadas"] is True


@pytest.mark.integration
def test_estadisticas_para_el_agente_estan_contrastadas() -> None:
    resultado = consultar_estadisticas_basicas()

    assert resultado["exito"] is True
    assert resultado["todo_coincide"] is True
    assert len(resultado["estadisticas"]) == 5
    assert {fila["variable"] for fila in resultado["estadisticas"]} == {
        "edad",
        "venta_total",
        "n_compras",
        "monto_compra",
        "tiempo",
    }


@pytest.mark.integration
def test_muestra_para_el_agente_es_acotada() -> None:
    resultado = consultar_muestra_datos("compras", 3)

    assert resultado["exito"] is True
    assert resultado["tabla"] == "compras"
    assert resultado["filas_mostradas"] == 3
    assert len(resultado["datos"]) == 3


@pytest.mark.integration
def test_distribucion_por_mes_cubre_todas_las_compras() -> None:
    resultado = consultar_distribucion_ventas("mes")

    assert resultado["exito"] is True
    assert resultado["dimension"] == "mes"
    assert len(resultado["datos"]) == 12
    assert sum(fila["cantidad_compras"] for fila in resultado["datos"]) == 6500


@pytest.mark.integration
def test_distribucion_por_navegador_incluye_las_cinco_categorias() -> None:
    resultado = consultar_distribucion_ventas("navegador")

    assert resultado["exito"] is True
    assert {fila["navegador_desc"] for fila in resultado["datos"]} == {
        "Tienda Fisica",
        "Navegador 1",
        "Navegador 2",
        "Navegador 3",
        "Navegador 4",
    }
