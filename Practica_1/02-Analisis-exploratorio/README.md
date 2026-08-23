# Punto 2: Analisis exploratorio

Esta carpeta contiene la solucion manual y reproducible de los incisos asignados:

- **2.a:** obtener los datos desde la base PostgreSQL en la nube.
- **2.b:** calcular media, mediana y moda para las variables numericas.

La solucion tambien incluye un agente Google ADK conectado a un servidor MCP. El archivo `notebook.ipynb` se conserva sin cambios como referencia didactica del auxiliar sobre MCP y `datos.gob.es`; no es la solucion de este proyecto.

## Archivos

| Archivo | Proposito |
|---|---|
| `analisis_exploratorio.py` | Extraccion, validacion, calculos, contraste SQL y exportacion. |
| `analisis_exploratorio.ipynb` | Presentacion paso a paso del analisis y sus resultados. |
| `tests/test_analisis_exploratorio.py` | Pruebas unitarias y prueba real contra PostgreSQL. |
| `mcp_server.py` | Servidor MCP con herramientas seguras para 2.a y 2.b. |
| `ventas_agent/agent.py` | Agente Gemini implementado con Google ADK. |
| `main.py` | Interfaz web de desarrollo del agente. |
| `README_IA.md` | Configuracion, arquitectura, ejecucion y pruebas de la IA. |
| `resultados/` | Evidencias que se generan al ejecutar el analisis. |
| `notebook.ipynb` | Material de referencia para la futura implementacion MCP. |
| `clase.txt` | Transcripcion de la explicacion del profesor. |

## Decision metodologica

Las variables cuantitativas analizadas son:

| Tabla | Variable | Interpretacion |
|---|---|---|
| `clientes` | `edad` | Edad del cliente en anios. |
| `clientes` | `venta_total` | Venta anual acumulada por cliente. |
| `clientes` | `n_compras` | Numero anual de compras. |
| `compras` | `monto_compra` | Monto de la compra registrada. |
| `compras` | `tiempo` | Tiempo de navegacion en segundos. |

Se excluyen `id_cliente` e `id_compra` porque son identificadores. Tambien se excluyen `genero`, `metodo_pago`, `navegador`, `boletin` y `vale` porque son variables categoricas aunque algunos de sus valores esten codificados con numeros. Promediar esos codigos produciria resultados sin interpretacion empresarial valida.

Las tablas se extraen por separado. Esto evita que las metricas anuales de `clientes` se dupliquen si en el futuro un cliente tiene varias filas en `compras`.

La moda se calcula conservando todos los valores empatados. Si una variable es multimodal, el resultado incluye cada moda y la cantidad de apariciones.

## Seguridad de la consulta

- Las credenciales se leen desde `Practica_1/.env` y no se imprimen ni exportan.
- La URL se construye con `sqlalchemy.URL.create`, por lo que admite caracteres especiales en la contrasenia.
- La extraccion y el contraste SQL comparten una transaccion `REPEATABLE READ` de solo lectura, por lo que observan exactamente la misma instantanea.
- Solo se utilizan consultas `SELECT` sobre `public.clientes` y `public.compras`.
- Se recomienda usar posteriormente el rol `mcp_readonly` propuesto en `BD/schema.sql`.

El `.env` debe definir:

```dotenv
DB_HOST=
DB_PORT=5432
DB_NAME=
DB_USER=
DB_PASSWORD=
```

## Ejecucion

Desde esta carpeta:

```powershell
python -m pip install -r requirements.txt
python analisis_exploratorio.py
```

Para revisar el proceso de forma interactiva:

```powershell
jupyter lab analisis_exploratorio.ipynb
```

## Verificaciones realizadas

Antes de calcular las estadisticas, el programa comprueba:

- que ambas consultas devuelvan registros;
- que los conteos de Pandas coincidan con los conteos directos de PostgreSQL;
- que `id_cliente` e `id_compra` sean unicos;
- que no existan valores nulos ni compras huerfanas;
- que los dominios categoricos sean validos;
- que todas las fechas pertenezcan a 2021;
- que las cinco columnas seleccionadas sean numericas;
- que la transaccion de extraccion sea de solo lectura.

La media, mediana, moda, frecuencia de la moda, cantidad de filas y cantidad de nulos se calculan primero con Pandas. Despues se vuelven a calcular independientemente en PostgreSQL mediante `AVG`, `percentile_cont(0.5)` y agrupaciones de frecuencia. La ejecucion falla si ambos resultados no coinciden.

## Pruebas

Ejecutar todas las pruebas, incluida la conexion real a la nube:

```powershell
pytest -v
```

Ejecutar solo las pruebas unitarias sin consultar la nube:

```powershell
pytest -v -m "not integration"
```

Las pruebas cubren casos unimodales, multimodales, seleccion de variables, integridad referencial, deteccion de diferencias entre Pandas y SQL, conexion de solo lectura y exportacion de evidencias.

## Evidencias generadas

La carpeta `resultados/` contiene:

- `estadisticas_basicas.csv`: resultado principal de media, mediana y moda con Pandas.
- `estadisticas_sql.csv`: calculo independiente realizado por PostgreSQL.
- `contraste_pandas_sql.csv`: comparacion campo por campo de ambos calculos.
- `validaciones_extraccion.csv`: controles aplicados al obtener los datos.
- `resumen_extraccion.json`: origen, dimensiones, columnas, tipos y rango de fechas.

Estos archivos no contienen credenciales ni la direccion del servidor.

## Resultados verificados

La ejecucion contra PostgreSQL obtuvo 6,500 clientes y 6,500 compras. Pandas y PostgreSQL produjeron los mismos resultados para las cinco variables:

| Variable | Media | Mediana | Moda | Frecuencia de la moda |
|---|---:|---:|---:|---:|
| `edad` | 36.305231 | 36 | 18 | 465 |
| `venta_total` | 206.242431 | 137.350 | 98 | 12 |
| `n_compras` | 5.090000 | 4 | 2 | 1,044 |
| `monto_compra` | 39.787056 | 35.764 | 37.145 | 5 |
| `tiempo` | 767.376154 | 768 | 852 | 24 |

## Cumplimiento

| Requisito | Evidencia |
|---|---|
| 2.a Obtener datos de la base de datos | Consultas PostgreSQL de solo lectura, DataFrames `clientes` y `compras`, conteos y `resumen_extraccion.json`. |
| 2.b Calcular media, mediana y moda | `estadisticas_basicas.csv` para las cinco variables cuantitativas. |
| Resultados confiables | `contraste_pandas_sql.csv` y pruebas automatizadas. |
| Chat para 2.a y 2.b | Agente Google ADK y tres herramientas del servidor MCP. |
| Codigo para el informe | Modulo y notebook incluidos en esta carpeta. |

## Limitacion del conjunto de datos

El esquema describe `venta_total` y `n_compras` como acumulados anuales del cliente, mientras cada cliente posee actualmente una sola fila de detalle en `compras`. Por eso no debe asumirse que las 6,500 filas de `compras` representan todas las transacciones mencionadas por `n_compras`. Este punto no afecta el calculo solicitado en 2.b porque cada variable se analiza en su tabla y granularidad correctas, pero debe considerarse al interpretar analisis mensuales posteriores.
