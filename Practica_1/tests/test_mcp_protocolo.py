from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


RAIZ_PRACTICA = Path(__file__).resolve().parents[1]


def _puerto_disponible() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind(("127.0.0.1", 0))
        return int(servidor.getsockname()[1])


def _esperar_puerto(puerto: int, timeout: float = 15.0) -> None:
    limite = time.monotonic() + timeout
    while time.monotonic() < limite:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
            cliente.settimeout(0.2)
            if cliente.connect_ex(("127.0.0.1", puerto)) == 0:
                return
        time.sleep(0.1)
    raise TimeoutError("El servidor MCP no inicio dentro del tiempo esperado.")


async def _probar_cliente_mcp(url: str) -> tuple[set[str], bool]:
    async with streamable_http_client(url) as (lectura, escritura, _):
        async with ClientSession(lectura, escritura) as sesion:
            await sesion.initialize()
            herramientas = await sesion.list_tools()
            resultado = await sesion.call_tool("obtener_estadisticas_basicas")
            nombres = {herramienta.name for herramienta in herramientas.tools}
            return nombres, bool(resultado.isError)


async def _probar_toolset_adk(url: str) -> set[str]:
    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=url, timeout=60.0)
    )
    try:
        herramientas = await toolset.get_tools()
        return {herramienta.name for herramienta in herramientas}
    finally:
        await toolset.close()


@pytest.mark.integration
def test_servidor_mcp_expone_e_invoca_herramientas() -> None:
    puerto = _puerto_disponible()
    entorno = os.environ.copy()
    entorno["MCP_HOST"] = "127.0.0.1"
    entorno["MCP_PORT"] = str(puerto)
    proceso = subprocess.Popen(
        [sys.executable, "-m", "app.mcp_server"],
        cwd=RAIZ_PRACTICA,
        env=entorno,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _esperar_puerto(puerto)
        url = f"http://127.0.0.1:{puerto}/mcp"
        nombres, contiene_error = asyncio.run(_probar_cliente_mcp(url))
        nombres_adk = asyncio.run(_probar_toolset_adk(url))
    finally:
        proceso.terminate()
        try:
            proceso.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proceso.kill()
            proceso.wait(timeout=5)

    herramientas_punto_02 = {
        "obtener_resumen_datos",
        "obtener_estadisticas_basicas",
        "obtener_muestra_datos",
    }
    assert herramientas_punto_02.issubset(nombres)
    assert nombres_adk == nombres
    assert contiene_error is False


def test_aplicacion_del_agente_expone_salud_y_sesiones(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ADK_SESSION_DB_PATH", str(tmp_path / "sessions.db"))
    sys.modules.pop("app.main", None)
    from app.main import app
    from app.ventas_agent.agent import GEMINI_MODEL, mcp_toolset, root_agent

    with TestClient(app) as cliente:
        respuesta_salud = cliente.get("/health")
        respuesta_agentes = cliente.get("/list-apps")
        respuesta_crear = cliente.post(
            "/apps/ventas_agent/users/usuario-prueba/sessions/sesion-prueba",
            json={},
        )
        respuesta_sesion = cliente.get(
            "/apps/ventas_agent/users/usuario-prueba/sessions/sesion-prueba"
        )

    assert respuesta_salud.status_code == 200
    assert respuesta_salud.json() == {"status": "ok"}
    assert respuesta_agentes.status_code == 200
    assert respuesta_agentes.json() == ["ventas_agent"]
    assert respuesta_crear.status_code == 200
    assert respuesta_sesion.status_code == 200
    assert respuesta_sesion.json()["id"] == "sesion-prueba"
    assert root_agent.model == GEMINI_MODEL
    assert root_agent.tools == [mcp_toolset]
