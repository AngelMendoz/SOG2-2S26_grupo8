# Expresiones del robot (bloques A–G)

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
