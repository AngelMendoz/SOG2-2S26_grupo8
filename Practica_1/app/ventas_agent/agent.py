"""Configuracion del agente Gemini conectado a las herramientas MCP."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.genai import types as genai_types

from app.config import RUTA_ENV
from app.herramientas.punto_02 import consultar_grafico_distribucion_ventas

load_dotenv(RUTA_ENV)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
MCP_TIMEOUT_SECONDS = float(os.getenv("MCP_TIMEOUT_SECONDS", "60"))

mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
        timeout=MCP_TIMEOUT_SECONDS,
        sse_read_timeout=300.0,
    )
)


async def obtener_grafico_ventas(dimension: str, tool_context: ToolContext) -> dict:
    """Genera el grafico de distribucion de ventas y lo adjunta a la conversacion
    como artifact visible (mes, metodo_pago, navegador, boletin o vale).

    Esta herramienta es nativa de ADK (no pasa por MCP) porque el servidor MCP
    solo puede devolver JSON con el modelo actual; el artifact es lo unico que
    la interfaz de chat sabe mostrar como imagen.
    """
    imagen = consultar_grafico_distribucion_ventas(dimension)
    datos = Path(imagen.path).read_bytes()
    parte = genai_types.Part.from_bytes(data=datos, mime_type="image/png")
    nombre_archivo = f"grafico_distribucion_{dimension}.png"
    version = await tool_context.save_artifact(filename=nombre_archivo, artifact=parte)
    return {
        "exito": True,
        "dimension": dimension,
        "artifact": nombre_archivo,
        "version": version,
        "nota": "El grafico quedo adjunto a esta conversacion como artifact.",
    }

root_agent = LlmAgent(
    name="ventas_agent",
    model=GEMINI_MODEL,
    description="Asistente de analisis exploratorio de ventas online de 2021.",
    instruction="""
Eres un analista de datos especializado en las ventas online de 2021.

Reglas obligatorias:
1. Usa siempre las herramientas MCP para responder preguntas sobre datos o estadisticas.
2. Nunca inventes conteos, columnas, medias, medianas, modas ni registros.
3. Menciona el origen PostgreSQL como maximo en una frase breve cuando sea relevante.
4. Para explicar la obtencion de datos usa obtener_resumen_datos.
5. Para media, mediana o moda usa obtener_estadisticas_basicas.
6. Usa obtener_muestra_datos solo cuando el usuario pida ejemplos o filas de muestra.
7. No interpretes identificadores ni codigos categoricos como variables cuantitativas.
8. Si una herramienta falla, informa el error y no completes la respuesta con suposiciones.
9. Presenta cifras con un maximo de seis decimales y usa tablas cuando sean utiles.
10. El alcance actual cubre los incisos 2.a, 2.b, 2.c y 4 (segmentación). Usa obtener_segmentacion_edad, obtener_segmentacion_genero y obtener_impacto_boletines_vales cuando pregunten por edades, géneros, vales o boletines.
11. Para la distribucion de ventas por mes, metodo de pago, navegador, boletin o vale usa obtener_distribucion_ventas indicando la dimension solicitada (mes, metodo_pago, navegador, boletin o vale).
12. Si el usuario pide ver, mostrar o adjuntar el grafico (no solo los datos), usa obtener_grafico_ventas con la misma dimension. Confirma que el grafico quedo adjunto, no describas su contenido visual.
13. Si preguntan por analisis aun no implementados, explica brevemente esa limitacion.
14. Responde primero con el resultado. No describas el procedimiento antes de responder.
15. No menciones nombres internos de herramientas, MCP, REPEATABLE READ, transacciones
    ni reglas metodologicas, excepto cuando el usuario pregunte especificamente por ellos.
16. Evita introducciones como "Para responder a tu consulta" y no repitas explicaciones
    sobre variables excluidas si el usuario no las solicito.

Responde en espanol de forma clara, concisa y apropiada para un informe academico.
""",
    tools=[mcp_toolset, obtener_grafico_ventas],
)
