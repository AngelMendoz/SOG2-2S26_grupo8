"""Aplicacion web de desarrollo para el agente conversacional de ventas."""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app


DIRECTORIO_ACTUAL = Path(__file__).resolve().parent
load_dotenv(DIRECTORIO_ACTUAL.parent / ".env")

AGENT_HOST = os.getenv("AGENT_HOST", "127.0.0.1")
AGENT_PORT = int(os.getenv("AGENT_PORT", "8080"))
SESSION_DB_PATH = Path(
    os.getenv("ADK_SESSION_DB_PATH", str(DIRECTORIO_ACTUAL / "sessions.db"))
)
if not SESSION_DB_PATH.is_absolute():
    SESSION_DB_PATH = DIRECTORIO_ACTUAL / SESSION_DB_PATH
SESSION_DB_PATH = SESSION_DB_PATH.resolve()

app: FastAPI = get_fast_api_app(
    agents_dir=str(DIRECTORIO_ACTUAL),
    session_service_uri=f"sqlite:///{SESSION_DB_PATH.as_posix()}",
    allow_origins=[
        f"http://127.0.0.1:{AGENT_PORT}",
        f"http://localhost:{AGENT_PORT}",
    ],
    web=True,
)


if __name__ == "__main__":
    uvicorn.run(app, host=AGENT_HOST, port=AGENT_PORT)
