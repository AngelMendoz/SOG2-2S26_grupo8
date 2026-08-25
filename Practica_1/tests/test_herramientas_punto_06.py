from __future__ import annotations

import pytest

from app.analisis.punto_02 import crear_motor, obtener_datos
from app.analisis.punto_06 import HALLAZGOS, ejecutar_visualizacion_hallazgos
from app.config import RUTA_RESULTADOS_PUNTO_06
from app.herramientas.punto_06 import (
    consultar_grafico_hallazgo,
    consultar_hallazgos_disponibles,
)


def test_hallazgos_disponibles_lista_los_siete() -> None:
    resultado = consultar_hallazgos_disponibles()

    assert resultado["exito"] is True
    assert len(resultado["hallazgos"]) == 7
    assert {hallazgo["clave"] for hallazgo in resultado["hallazgos"]} == set(HALLAZGOS)


def test_grafico_rechaza_clave_no_permitida() -> None:
    with pytest.raises(ValueError, match="boletin_vale.*genero_vs_metodo_pago"):
        consultar_grafico_hallazgo("region")


@pytest.mark.integration
def test_grafico_genera_los_siete_pngs_y_se_pueden_consultar() -> None:
    motor = crear_motor()
    clientes, compras, _ = obtener_datos(motor)

    ejecutar_visualizacion_hallazgos(
        clientes, compras, directorio_resultados=RUTA_RESULTADOS_PUNTO_06
    )

    for clave in HALLAZGOS:
        imagen = consultar_grafico_hallazgo(clave)
        assert imagen.path is not None
        assert imagen.path.is_file()
