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
from app.herramientas.punto_06 import consultar_grafico_hallazgo

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


async def obtener_grafico_hallazgo(clave: str, tool_context: ToolContext) -> dict:
    """Adjunta a la conversacion, como artifact, el grafico de un hallazgo
    especifico del punto 6 (usar obtener_hallazgos_disponibles para ver las
    claves validas)."""
    imagen = consultar_grafico_hallazgo(clave)
    datos = Path(imagen.path).read_bytes()
    parte = genai_types.Part.from_bytes(data=datos, mime_type="image/png")
    nombre_archivo = f"hallazgo_{clave}.png"
    version = await tool_context.save_artifact(filename=nombre_archivo, artifact=parte)
    return {
        "exito": True,
        "hallazgo": clave,
        "artifact": nombre_archivo,
        "version": version,
        "nota": "El grafico del hallazgo quedo adjunto a esta conversacion como artifact.",
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
10. El alcance actual cubre los incisos 2.a, 2.b, 2.c, 3 (tendencias), 4 (segmentación) y 5 (correlación).
11. Para la distribucion de ventas por mes, metodo de pago, navegador, boletin o vale usa obtener_distribucion_ventas indicando la dimension solicitada (mes, metodo_pago, navegador, boletin o vale).
12. Si el usuario pide ver, mostrar o adjuntar el grafico (no solo los datos), usa obtener_grafico_ventas con la misma dimension. Confirma que el grafico quedo adjunto, no describas su contenido visual.
13. Si preguntan que hallazgos o resumenes visuales hay disponibles, usa obtener_hallazgos_disponibles.
14. Si piden ver el grafico de un hallazgo especifico, usa obtener_grafico_hallazgo con la clave correspondiente. Confirma que quedo adjunto, no describas su contenido visual.
15. Si la herramienta de segmentación te devuelve el campo 'graficas_url', puedes usar esas rutas para mostrar las imágenes correspondientes utilizando la sintaxis de Markdown: `![Nombre de la gráfica](URL)` si consideras que aportan valor visual.
16. En preguntas de segmentación (edades, género, vales), prioriza usar tablas de Markdown para resumir las agrupaciones antes de dar tu conclusión.
17. Si el usuario te pregunta "cuál es el mejor grupo/segmento", limítate a señalar objetivamente cuál tiene mayores ventas totales o mayor ticket promedio, sin emitir juicios de valor.
18. NUNCA intentes extraer filas de muestra (obtener_muestra_datos) para calcular tú mismo promedios de edades o géneros; debes depender exclusivamente de los resultados precalculados por las herramientas de segmentación.
19. Para el punto 3 (tendencias) usa estas herramientas segun corresponda:
    - obtener_ventas_por_mes: meses con mayores y menores ventas totales.
    - obtener_navegador_preferido: navegador/canal mas preferido y menos popular.
    - obtener_ventas_efectivo_contra_entrega: total y porcentaje pagado en
      efectivo o contra entrega (metodo_pago = 0).
    - obtener_boletines_vales_por_mes: meses con mas uso de boletines y de vales.
    Usa obtener_segmentacion_edad, obtener_segmentacion_genero y
    obtener_impacto_boletines_vales cuando pregunten por edades, géneros,
    vales o boletines desde una perspectiva de segmentacion de clientes
    (no de tendencia mensual).
20. Para el punto 5 (correlacion) usa estas herramientas segun corresponda:
    - obtener_correlacion_venta_edad: relacion entre venta total y edad del cliente (Pearson y Spearman).
    - obtener_correlacion_genero_metodo_pago: asociacion entre genero y metodo de pago preferido (chi-cuadrado y V de Cramer).
    - obtener_correlacion_boletin_vale: asociacion entre uso de boletin y uso de vale (chi-cuadrado y coeficiente Phi).
    Informa el coeficiente relevante (Pearson/Spearman, Cramer's V o Phi), el p-valor
    y si el resultado es estadisticamente significativo, usando la interpretacion
    (nula, debil, moderada, fuerte, muy fuerte) que devuelve cada herramienta.
21. Si preguntan por analisis aun no implementados, explica brevemente esa limitacion.
22. Responde primero con el resultado. No describas el procedimiento antes de responder.
23. No menciones nombres internos de herramientas, MCP, REPEATABLE READ, transacciones
    ni reglas metodologicas, excepto cuando el usuario pregunte especificamente por ellos.
24. Evita introducciones como "Para responder a tu consulta" y no repitas explicaciones
    sobre variables excluidas si el usuario no las solicito.

Responde en espanol de forma clara, concisa y apropiada para un informe academico.
""",
    tools=[mcp_toolset, obtener_grafico_ventas, obtener_grafico_hallazgo],
)
