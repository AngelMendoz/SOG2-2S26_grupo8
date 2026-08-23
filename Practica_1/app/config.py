"""Configuracion compartida, independiente del directorio de ejecucion."""

from ipaddress import ip_address
from pathlib import Path


RAIZ_PRACTICA = Path(__file__).resolve().parents[1]
RUTA_ENV = RAIZ_PRACTICA / ".env"
RUTA_ENUNCIADO = RAIZ_PRACTICA / "Enunciado"
RUTA_PUNTO_02 = RAIZ_PRACTICA / "02-Analisis-exploratorio"
RUTA_RESULTADOS_PUNTO_02 = RUTA_PUNTO_02 / "resultados"


def es_host_local(host: str) -> bool:
    """Indica si un servicio se limita a la maquina local."""
    if host.lower() == "localhost":
        return True
    try:
        return ip_address(host).is_loopback
    except ValueError:
        return False
