# Guia de ejecucion y colaboracion

Esta guia permite instalar, ejecutar, probar y extender la practica. Todos los comandos se ejecutan desde la carpeta `Practica_1`.

## 1. Estructura

```text
Practica_1/
|-- app/
|   |-- config.py                 # Rutas compartidas
|   |-- main.py                   # Aplicacion web Google ADK
|   |-- mcp_server.py             # Servidor MCP compartido
|   |-- analisis/
|   |   `-- punto_02.py           # Calculos manuales 2.a y 2.b
|   |-- herramientas/
|   |   `-- punto_02.py           # Funciones usadas por MCP
|   `-- ventas_agent/
|       `-- agent.py              # Modelo, prompt y conexion MCP
|-- 02-Analisis-exploratorio/
|   |-- analisis_exploratorio.ipynb
|   |-- resultados/
|   `-- Preguntas.txt
|-- referencias/
|   |-- clase.txt
|   `-- notebook_mcp_datos_gob.ipynb.reference
|-- tests/
|-- .env
|-- .env.example
|-- requirements.txt
|-- pytest.ini
|-- README.md                     # Base del informe
`-- README_EJECUCION.md           # Esta guia
```

Las carpetas `BD`, `ETL`, `Enunciado` y `Documentacion` conservan los artefactos de los demas puntos.

## 2. Requisitos

- Python 3.12 o superior. La suite fue verificada en Python 3.12 y 3.14.
- PostgreSQL de la VM encendido y accesible.
- Clave valida de Google AI Studio.
- PowerShell en Windows.

## 3. Preparacion inicial

Desde la raiz del repositorio:

```powershell
cd Practica_1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activacion, se puede utilizar el ejecutable directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Variables de entorno

Crear `.env` a partir de `.env.example` y completar los secretos:

```powershell
Copy-Item .env.example .env
```

Variables principales:

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

El archivo `.env` no se debe subir a Git. `.env.example` solo contiene valores ficticios.

## 5. Ejecutar el analisis manual

```powershell
python -m app.analisis.punto_02
```

Debe mostrar:

```text
Clientes: 6500
Compras: 6500
Transaccion de solo lectura: si
```

Los resultados se guardan en:

```text
02-Analisis-exploratorio/resultados/
```

## 6. Abrir el notebook

```powershell
jupyter lab 02-Analisis-exploratorio/analisis_exploratorio.ipynb
```

El notebook detecta la raiz `Practica_1`, importa `app.analisis.punto_02` y actualiza los resultados del punto 2.

## 7. Ejecutar el agente

Se necesitan dos terminales en `Practica_1`.

Terminal 1, servidor MCP:

```powershell
python -m app.mcp_server
```

Terminal 2, aplicacion ADK:

```powershell
python -m app.main
```

Abrir:

```text
http://127.0.0.1:8080
```

Seleccionar `ventas_agent`, crear una conversacion nueva y probar:

```text
Consulta la base y dime cuantos clientes y compras hay.
```

```text
Calcula media, mediana y moda de las variables numericas.
```

```text
Muestrame tres registros de compras.
```

Las preguntas disponibles y pendientes se encuentran en `02-Analisis-exploratorio/Preguntas.txt`.

## 8. Ejecutar pruebas

Suite completa, incluida la VM y el protocolo MCP:

```powershell
python -m pytest -v
```

Solo pruebas que no requieren PostgreSQL:

```powershell
python -m pytest -v -m "not integration"
```

Solo MCP y ADK:

```powershell
python -m pytest -v tests/test_mcp_protocolo.py
```

Resultado actual esperado:

```text
15 passed
```

## 9. Agregar un nuevo punto

Cada integrante debe seguir el mismo flujo.

### Paso 1 - Calculo manual

Crear un modulo, por ejemplo:

```text
app/analisis/punto_03.py
```

Debe contener calculos deterministas y comprobables. La logica no debe depender del modelo de IA.

### Paso 2 - Herramienta segura

Crear:

```text
app/herramientas/punto_03.py
```

La herramienta debe importar el calculo manual, devolver datos serializables a JSON y limitar sus parametros. No debe aceptar SQL libre.

Ejemplo de estructura:

```python
from app.analisis.punto_03 import calcular_tendencias


def consultar_tendencias() -> dict:
    return calcular_tendencias()
```

### Paso 3 - Publicar en MCP

Importar la funcion en `app/mcp_server.py` y registrarla con un nombre unico:

```python
@mcp.tool()
def obtener_tendencias() -> dict:
    """Obtiene los resultados validados del analisis de tendencias."""
    return consultar_tendencias()
```

### Paso 4 - Orientar al agente

Actualizar `app/ventas_agent/agent.py` solamente para indicar cuando debe usar la herramienta nueva. El prompt no debe contener resultados numericos fijos.

### Paso 5 - Probar

Agregar pruebas bajo `tests/` para:

- el calculo manual;
- la serializacion de la herramienta;
- sus parametros invalidos;
- su resultado contra PostgreSQL;
- su descubrimiento mediante MCP.

La prueba del servidor verifica que las herramientas del punto 2 sean un subconjunto, por lo que agregar herramientas nuevas no rompe el catalogo existente.

## 10. Reglas de colaboracion

- Trabajar desde `Practica_1` y usar imports que comiencen con `app.`.
- No copiar credenciales a codigo, notebooks, capturas o commits.
- No ejecutar SQL generado por el modelo.
- Validar manualmente cada calculo antes de exponerlo mediante MCP.
- Mantener transacciones de analisis en solo lectura.
- Limitar muestras y parametros de usuario.
- Agregar pruebas junto con cada herramienta.
- `referencias/notebook_mcp_datos_gob.ipynb.reference` se conserva para consulta. Su extension evita ejecutarlo accidentalmente porque contiene celdas que escriben archivos.
- No cambiar versiones de ADK o MCP sin ejecutar toda la suite.

## 11. Problemas frecuentes

### La VM no responde

Encender la VM, revisar el puerto 5432 y verificar las variables `DB_*`.

### El navegador muestra 404 en `/run_sse`

Crear una conversacion nueva. Si la interfaz conserva una sesion antigua, borrar los datos del sitio `127.0.0.1:8080` o usar una ventana de incognito.

### Gemini devuelve 503

Confirmar `GEMINI_MODEL=gemini-3.5-flash-lite`, esperar unos segundos y reintentar.

### MCP no conecta

Confirmar que la primera terminal sigue ejecutando `python -m app.mcp_server` y que `MCP_SERVER_URL` termina en `/mcp`.

### Cambios del prompt no aparecen

Reiniciar `python -m app.main` y crear una conversacion nueva.
