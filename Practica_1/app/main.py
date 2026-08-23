"""Aplicacion web de desarrollo para el agente conversacional de ventas."""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

from app.config import RAIZ_PRACTICA, RUTA_ENV, es_host_local

DIRECTORIO_APP = Path(__file__).resolve().parent
load_dotenv(RUTA_ENV)

AGENT_HOST = os.getenv("AGENT_HOST", "127.0.0.1")
AGENT_PORT = int(os.getenv("AGENT_PORT", "8080"))
if not es_host_local(AGENT_HOST):
    raise ValueError(
        "AGENT_HOST debe ser una direccion local mientras la aplicacion no tenga autenticacion."
    )
SESSION_DB_PATH = Path(
    os.getenv("ADK_SESSION_DB_PATH", str(RAIZ_PRACTICA / "sessions.db"))
)
if not SESSION_DB_PATH.is_absolute():
    SESSION_DB_PATH = RAIZ_PRACTICA / SESSION_DB_PATH
SESSION_DB_PATH = SESSION_DB_PATH.resolve()

app: FastAPI = get_fast_api_app(
    agents_dir=str(DIRECTORIO_APP),
    session_service_uri=f"sqlite:///{SESSION_DB_PATH.as_posix()}",
    allow_origins=[
        f"http://127.0.0.1:{AGENT_PORT}",
        f"http://localhost:{AGENT_PORT}",
    ],
    web=True,
)


if __name__ == "__main__":
    uvicorn.run(app, host=AGENT_HOST, port=AGENT_PORT)
