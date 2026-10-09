# Expresiones del robot (bloques A–J)

Copiar tal cual en UiPath Studio (VB.NET). Todas van dentro de la secuencia **Robot QuetzalMart**.

## Bloque A · Preparar la corrida
- Assign `lote`: `Now.ToString("yyyyMMdd_HHmmss")`
- Browse for Folder › Selected folder: `carpetaEntrada`
- If: `String.IsNullOrWhiteSpace(carpetaEntrada)` › Then › Assign `carpetaEntrada` = `System.IO.Path.GetFullPath("..\Entrada")`
- Assign `carpetaSalida`: `System.IO.Path.Combine(System.IO.Path.GetFullPath(".."), "Salida", lote)`

## Bloque B · For Each File in Folder
- In folder: `carpetaEntrada` · Filter: `"*.xls*"` · IncludeSubdirectories: Yes
- If: `CurrentFile.Name.StartsWith("~$")` (Else › Try Catch)

## Bloque C · Hojas (dentro del Try)
- Get Sheets Workbook › File: `LocalResource.FromPath(CurrentFile.FullName)` › Sheets: `hojas`
- If: `hoja.Trim().ToLower() = "clientes" OrElse hoja.Trim().ToLower() = "productos"`

## Bloque D · Leer y normalizar (Then del If anterior)
- Read Range Workbook › File: `LocalResource.FromPath(CurrentFile.FullName)` · SheetName: `hoja` · Range: `""` · Add headers: Yes · DataTable: `dtHoja`
- Invoke Code «Normalizar hoja»: `01_invoke_code_normalizar_hoja.vb`

| Key | Type | Direction | Value |
|---|---|---|---|
| in_dtHoja | DataTable | In | `dtHoja` |
| in_tipo | String | In | `hoja.Trim().ToLower()` |
| in_archivo | String | In | `CurrentFile.FullName.Substring(carpetaEntrada.Length).TrimStart("\"c)` |
| io_dtClientes | DataTable | InOut | `dtClientes` |
| io_dtProductos | DataTable | InOut | `dtProductos` |
| out_filas | Int32 | Out | `filasHoja` |

## Bloque E · Consolidado (fuera del For Each File in Folder)
- If: `dtClientes.Rows.Count = 0 AndAlso dtProductos.Rows.Count = 0` › Throw `New Exception("No se encontraron hojas clientes ni productos en " + carpetaEntrada)`
- If `dtClientes.Rows.Count > 0` › Write Range Workbook › WorkbookPath (texto, no File): `System.IO.Path.Combine(carpetaSalida, "clientes_consolidado.xlsx")` · Sheet `"clientes"` · `"A1"` · `dtClientes`
- If `dtProductos.Rows.Count > 0` › Write Range Workbook › WorkbookPath (texto, no File): `System.IO.Path.Combine(carpetaSalida, "productos_consolidado.xlsx")` · Sheet `"productos"` · `"A1"` · `dtProductos`

## Bloque F · Generar los INSERT
Invoke Code «Generar SQL clientes» y «Generar SQL productos»: `02_invoke_code_generar_sql.vb`

| Key | Type | Direction | Value (clientes / productos) |
|---|---|---|---|
| in_dt | DataTable | In | `dtClientes` / `dtProductos` |
| in_tipo | String | In | `"clientes"` / `"productos"` |
| in_lote | String | In | `lote` |
| out_sqls | List<String> | Out | `sqlsClientes` / `sqlsProductos` |

## Bloque G · Conexión
- Get Secure Credentials › Target `"QuetzalMart_BD"` · Generic · Username `usuarioBD` · Password `claveBD` · Result `credencialOk`
- If `Not credencialOk` › Throw `New Exception("No existe la credencial QuetzalMart_BD en el Administrador de credenciales de Windows")`
- Connect to Database › Provider name `"System.Data.Odbc"` · Connection string:

```vb
"Driver={PostgreSQL Unicode(x64)};Server=" + hostBD + ";Port=" + puertoBD + ";Database=" + nombreBD + ";Uid=" + usuarioBD + ";Pwd=" + New System.Net.NetworkCredential("", claveBD).Password + ";"
```
- Database connection (Out): `conexion`

## Bloque H · Insertar cada fila
- For Each `sql` · In: `sqlsClientes.Concat(sqlsProductos).ToList()` · TypeArgument: String
  - Try: Run Command › Existing connection `conexion` · SQL command `sql` · Command type Text; Assign `filasInsertadas = filasInsertadas + 1`
  - Catch (System.Exception): Log Error `"Fila no insertada: " + exception.Message`; Assign `erroresInsert = erroresInsert + 1`
- Log: `"Insertadas " + filasInsertadas.ToString + " filas en la BD (lote " + lote + "), errores: " + erroresInsert.ToString + ". Esperando a Odoo..."`

## Bloque I · Esperar a Odoo (Do While)
Condition: `pendientes > 0 AndAlso intentos < 24` — dentro del Body, en orden:
- Delay `00:00:10`
- Run Query › Existing connection `conexion` › Data table `dtConteo` › SQL:
```vb
"SELECT (SELECT count(*) FROM x_rpa_cliente WHERE x_lote = '" + lote + "' AND x_estado = 'Pendiente') + (SELECT count(*) FROM x_rpa_producto WHERE x_lote = '" + lote + "' AND x_estado = 'Pendiente') AS pendientes"
```
- Assign `pendientes = Convert.ToInt32(dtConteo.Rows(0)(0))`
- Assign `intentos = intentos + 1`
- Log `"Filas pendientes de procesar en Odoo: " + pendientes.ToString`

Después del Do While (mismo nivel):
- Run Query › `conexion` › Data table `dtResumen` › SQL:
```vb
"SELECT 'clientes' AS tabla, x_estado AS estado, count(*) AS filas FROM x_rpa_cliente WHERE x_lote = '" + lote + "' GROUP BY x_estado UNION ALL SELECT 'productos', x_estado, count(*) FROM x_rpa_producto WHERE x_lote = '" + lote + "' GROUP BY x_estado"
```
- Disconnect from Database › `conexion`
- Output Data Table as Text › DataTable `dtResumen` › Text `textoResumen`
- Write Range Workbook › **File (local path)** (⊕ › Use Local File): `System.IO.Path.Combine(carpetaSalida, "resumen.xlsx")` · `"resumen"` · `"A1"` · `dtResumen`
- If `pendientes > 0` › Log Warn `"Odoo aún no procesa todo. Abre Settings > Technical > Scheduled Actions > RPA - Procesar cargas pendientes > Run Manually"`

## Bloque J · Resultado
- Log `"Resumen del lote " + lote + Environment.NewLine + textoResumen`
- Invoke Code «Abrir tienda»: `04_invoke_code_abrir_tienda.vb` (argumento `in_url` = `urlTienda`)
- Message Box › Text `"Carga terminada (lote " + lote + ")" + Environment.NewLine + textoResumen`

## Nota sobre los campos File
- Leer (Get Sheets, Read Range): `LocalResource.FromPath(CurrentFile.FullName)` funciona porque el archivo existe.
- Escribir (Write Range): usar ⊕ › **Use Local File** → «File (local path)», porque el consolidado todavía no existe.
