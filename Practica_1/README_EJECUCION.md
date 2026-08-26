# SOG2-2S26 Grupo 8 - Guia de uso

Esta es la guia operativa para instalar, ejecutar y extender la Practica 1. El informe de avance se encuentra en [`Practica_1/Documentacion/README.md`](Practica_1/Documentacion/README.md).

## Estructura principal

```text
Practica_1/
|-- 02-Analisis-exploratorio/   # Notebook y resultados del punto 2
|-- app/                        # Analisis, herramientas MCP y agente ADK
|-- BD/                         # Modelos y schema.sql
|-- Documentacion/              # Informe y capturas
|-- Enunciado/                  # PDF y CSV proporcionados
|-- ETL/                        # Notebook de preparacion y carga
|-- tests/                      # Pruebas automatizadas
|-- .env.example               # Plantilla de configuracion
`-- requirements.txt           # Dependencias Python
```

Todos los comandos locales de esta guia se ejecutan desde `Practica_1`.

## Requisitos

- Python 3.12 o superior.
- Acceso al PostgreSQL del equipo.
- Clave de Google AI Studio para ejecutar el agente.
- Git.

## Instalacion local

En PowerShell:

```powershell
Set-Location Practica_1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Si PowerShell bloquea la activacion, se puede usar directamente `\.venv\Scripts\python.exe` en lugar de `python`.

## Configuracion

Completar `Practica_1/.env` sin compartir sus valores:

```dotenv
DB_HOST=
DB_PORT=5432
DB_NAME=ventas_online
DB_USER=
DB_PASSWORD=

GOOGLE_API_KEY=
GEMINI_MODEL=gemini-3.5-flash-lite

MCP_HOST=127.0.0.1
MCP_PORT=8000
MCP_SERVER_URL=http://127.0.0.1:8000/mcp
MCP_TIMEOUT_SECONDS=60

AGENT_HOST=127.0.0.1
AGENT_PORT=8080
ADK_SESSION_DB_PATH=sessions.db
```

No se deben subir `.env`, contraseñas, API keys ni credenciales incluidas en capturas.

## Ejecutar el analisis exploratorio

Desde `Practica_1`:

```powershell
python -m app.analisis.punto_02
```

Los archivos generados quedan en `02-Analisis-exploratorio/resultados/`.

El inciso 2.b calcula media, mediana y moda para las diez variables enumeradas por la rubrica:

```text
edad, genero, venta_total, n_compras, monto_compra,
metodo_pago, tiempo, navegador, boletin, vale
```

Los identificadores quedan excluidos. `genero`, `metodo_pago`, `navegador`, `boletin` y `vale` se conservan como categorias codificadas; se calculan las medidas solicitadas, pero su interpretacion de negocio prioriza moda y proporciones. Cada resultado se contrasta de forma independiente con PostgreSQL y se exporta en:

- `resultados/estadisticas_basicas.csv`
- `resultados/estadisticas_sql.csv`
- `resultados/contraste_pandas_sql.csv`
- `resultados/validaciones_extraccion.csv`
- `resultados/resumen_extraccion.json`

Para usar Jupyter localmente:

```powershell
jupyter lab 02-Analisis-exploratorio/analisis_exploratorio.ipynb
```

## Ejecutar el notebook en Google Colab

1. Abrir `Practica_1/02-Analisis-exploratorio/analisis_exploratorio.ipynb` desde GitHub con Google Colab.
2. En Colab, abrir el panel de llave **Secrets**.
3. Crear `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD`.
4. Habilitar el acceso del notebook a esos secretos.
5. Ejecutar **Entorno de ejecucion > Ejecutar todas**.

El notebook instala sus dependencias, clona este repositorio cuando se ejecuta en Colab, crea un `.env` temporal dentro de la sesion y ejecuta el mismo modulo que se utiliza localmente. Los secretos no se imprimen ni se guardan en GitHub.

## Ejecutar el agente conversacional

Se requieren dos terminales abiertas en `Practica_1`.

Terminal 1:

```powershell
python -m app.mcp_server
```

Terminal 2:

```powershell
python -m app.main
```

Abrir `http://127.0.0.1:8080`, seleccionar `ventas_agent` y crear una conversacion nueva. Consultas iniciales:

```text
Consulta la base y dime cuantos clientes y compras hay.
Calcula media, mediana y moda de las diez variables solicitadas.
Muestrame tres registros de compras.
```

## Ejecutar pruebas

Suite completa, incluida la conexion con PostgreSQL:

```powershell
python -m pytest -v
```

Validacion focalizada de los incisos 2.a y 2.b:

```powershell
python -m pytest -v tests/test_punto_02.py tests/test_herramientas_punto_02.py
```

Pruebas que no requieren la base en la nube:

```powershell
python -m pytest -v -m "not integration"
```

## Agregar otro punto del proyecto

1. Crear el calculo determinista en `app/analisis/punto_XX.py`.
2. Crear una funcion segura y serializable en `app/herramientas/punto_XX.py`.
3. Registrar esa funcion como herramienta en `app/mcp_server.py`.
4. Orientar el uso de la herramienta en `app/ventas_agent/agent.py` sin escribir resultados numericos fijos en el prompt.
5. Agregar pruebas bajo `tests/`.
6. Documentar los resultados y capturas necesarias en `Documentacion/README.md`.

Las herramientas no deben aceptar SQL libre. Los calculos deben poder verificarse sin depender de la respuesta del modelo de IA.

## Reglas de colaboracion

- Trabajar desde `Practica_1` y usar imports que comiencen con `app.`.
- Crear una rama propia antes de implementar un punto.
- Mantener las consultas analiticas en modo de solo lectura.
- Limitar los parametros y la cantidad de registros devueltos al agente.
- Ejecutar las pruebas antes de solicitar integracion.
- Actualizar el informe solo con resultados comprobados.

## Problemas frecuentes

**PostgreSQL no responde:** verificar que la instancia este encendida, que el puerto `5432` sea accesible y que las variables `DB_*` sean correctas.

**MCP no conecta:** comprobar que `python -m app.mcp_server` siga activo y que `MCP_SERVER_URL` termine en `/mcp`.

**El agente no refleja cambios:** reiniciar `python -m app.main` y crear una conversacion nueva.

**Gemini devuelve un error temporal:** verificar la clave y el modelo configurado, esperar unos segundos y volver a intentar.
