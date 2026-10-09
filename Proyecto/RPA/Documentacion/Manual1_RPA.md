# Manual 1 · Parte RPA (UiPath)

Proyecto QuetzalMart · SOG2 · Segundo semestre 2026

---

## 1. Instalación del robot RPA

### 1.1 Componentes

| Componente | Dónde | Versión usada |
|---|---|---|
| Odoo Community (ERP) | Instancia EC2 de AWS, contenedor Docker | 19.0 |
| PostgreSQL (base de datos de Odoo y tablas del RPA) | Misma instancia, contenedor Docker, puerto 5432 | 15 |
| UiPath Studio (Community) | PC del operador, Windows 10/11 de 64 bits | Licencia Community |
| Driver ODBC de PostgreSQL | PC del operador | psqlODBC x64 (`PostgreSQL Unicode(x64)`) |
| Proyecto del robot | Repositorio, `Proyecto/RPA/QuetzalMart_RPA_Carga` | — |

Odoo y PostgreSQL ya están instalados en la nube. Para el RPA, en el servidor solo se agregan dos tablas, una acción planificada y un usuario de base de datos; eso se hace **una sola vez** y se detalla en la [sección 4.1](#41-configuración-en-odoo-y-postgresql-una-sola-vez). En cada PC donde se quiera ejecutar el robot se siguen los pasos 1.2 a 1.7.

### 1.2 Obtener el proyecto

```powershell
git clone https://github.com/AngelMendoz/SOG2-2S26_grupo8.git
cd SOG2-2S26_grupo8
git checkout feature/robot_rpa
```

El robot calcula sus rutas desde su propia ubicación (`..\Entrada` y `..\Salida`), así que el repositorio puede clonarse en cualquier carpeta sin cambiar nada.

### 1.3 Instalar UiPath Studio

1. Entrar a <https://cloud.uipath.com> y registrarse (se puede usar la cuenta de Google). Se crea una organización de Automation Cloud con licencia Community.
2. En **Downloads › Studio, Assistant and Robot › Community Edition** pulsar **Download** y ejecutar el instalador `UiPathPlatform.msi`.

![Descargar Studio](../Capturas/09a_uipath_descargar_studio.png)

3. En el instalador dejar marcados **Studio**, **Assistant**, **Robot** y **Extensiones**, aceptar el acuerdo de licencia y pulsar **Instalar**.

![Productos del instalador](../Capturas/09a1_uipath_instalador_productos.png)

4. Esperar a que diga *Descarga completa* e *Instalación completa* y pulsar **Cerrar**.

5. Abrir UiPath Studio, iniciar sesión con la misma cuenta y elegir el perfil **UiPath Studio** (no StudioX).
6. Dejar Studio en inglés: **Home › Settings › General › Language › English**.

### 1.4 Instalar el driver ODBC de PostgreSQL

UiPath se conecta a PostgreSQL por ODBC. En PowerShell (script en `02-PostgreSQL/06_instalar_driver_odbc.ps1`):

```powershell
winget install --id PostgreSQL.psqlODBC --exact
Get-OdbcDriver -Platform 64-bit | Where-Object Name -like "PostgreSQL*" | Select-Object Name
```

Debe aparecer `PostgreSQL Unicode(x64)`, que es el nombre que usa la cadena de conexión del robot. Si no hay `winget`, se descarga `psqlodbc_x64.msi` de <https://github.com/postgresql-interfaces/psqlodbc/releases>.

![Driver ODBC instalado](../Capturas/09_driver_odbc_postgresql_instalado.png)

### 1.5 Comprobar que la base de datos responde desde la red

```powershell
Test-NetConnection 3.133.123.138 -Port 5432 | Select-Object ComputerName, RemotePort, TcpTestSucceeded
```

Debe decir `TcpTestSucceeded : True`. Si dice `False`, hay que agregar la IP pública de esa red al grupo de seguridad de la instancia en AWS (regla de entrada PostgreSQL, puerto 5432).

![Test-NetConnection puerto 5432](../Capturas/09e_test_netconnection_puerto_5432.png)

Prueba opcional: **Orígenes de datos ODBC (64 bits) › DSN de usuario › Agregar › PostgreSQL Unicode(x64)**, con servidor `3.133.123.138`, puerto `5432`, base `dbquetzalmart`, usuario `rpa_robot` y su contraseña. El botón **Test** debe decir *Connection successful* (después se cancela; el robot no usa el DSN).

![Test ODBC](../Capturas/09d_odbc_test_conexion.png)

### 1.6 Guardar la contraseña del robot en Windows

La contraseña de la base de datos no se escribe en el flujo ni en el repositorio. Se guarda en el Administrador de credenciales de Windows:

**Panel de control › Cuentas de usuario › Administrador de credenciales › Credenciales de Windows › Agregar una credencial genérica**

| Campo | Valor |
|---|---|
| Dirección de Internet o de red | `QuetzalMart_BD` |
| Nombre de usuario | `rpa_robot` |
| Contraseña | la del usuario `rpa_robot` |

![Credencial QuetzalMart_BD](../Capturas/09c_credencial_quetzalmart_bd.png)

### 1.7 Abrir el proyecto y validar

1. Studio › **Open** › `Proyecto\RPA\QuetzalMart_RPA_Carga\project.json`.
2. La primera vez Studio descarga los paquetes `UiPath.Excel.Activities`, `UiPath.Database.Activities` y `UiPath.Credentials.Activities`. Quedan en **Dependencias** junto con `UiPath.System.Activities`, que trae todo proyecto.
3. **Design › Analyze File › Validate File**: debe terminar sin errores.

![Paquetes del proyecto](../Capturas/09b_uipath_paquetes_instalados.png)

4. Ejecutar el robot (**Run File**) con la carpeta `Entrada` de la sección 1.8. El panel Output debe terminar con 0 filas pendientes y el mensaje final debe mostrar las filas en estado *Procesado* (ver sección 4.4).

### 1.8 Carpeta de entrada de prueba

El repositorio ya incluye `Proyecto/RPA/Entrada/` con una estructura de carpetas de prueba. Para regenerarla (requiere Python con `openpyxl`):

```powershell
python "Proyecto\RPA\03-Carpeta-prueba\crear_carpeta_prueba.py"
```

Crea 7 Excel en carpetas como `clientes - region central`, `productos - bodega principal`, `proveedores - locales`, `reclamos - septiembre` y `registro - ventas`, con hojas que deben ignorarse (`reclamos`, `notas`, `registros`, `proveedor`) y hojas `clientes`/`productos` incluso dentro de carpetas con otro nombre. También copia los dos Excel de ejemplo a `Entrada\ejemplos - catedra\`.

---

## 2. Funcionamiento del módulo RPA

### 2.1 Problema que resuelve

El departamento de ventas guarda su información en carpetas con nombres poco prácticos (`clientes - …`, `proveedores - …`, `reclamos - …`, `registro - …`, `productos - …`). Cada carpeta tiene archivos Excel con varias hojas, y solo interesan las hojas llamadas **clientes** y **productos**, estén en la carpeta que estén. Revisarlas a mano es lento y propenso a errores.

El RPA recorre toda la estructura, extrae solo esas hojas, las consolida y las carga en una base de datos centralizada. Desde ahí los datos pasan a Odoo y se ven en el sitio web y por consultas SQL.

![Vista general](diagramas/01_vista_general.png)

### 2.2 Componentes

| Componente | Función |
|---|---|
| **Robot UiPath** `QuetzalMart_RPA_Carga` | Lee la carpeta, filtra las hojas, normaliza encabezados, guarda los consolidados en Excel e inserta cada fila en la base de datos. Al final verifica por SQL y abre la tienda. |
| **Tablas centralizadas** `x_rpa_cliente` y `x_rpa_producto` | Viven en la base PostgreSQL de Odoo (`dbquetzalmart`). Tienen una columna por cada campo más `x_archivo_origen`, `x_lote`, `x_estado`, `x_mensaje` y `x_registro_odoo`. |
| **Menú «Cargas RPA»** en Odoo | Muestra las filas cargadas (*Clientes cargados*, *Productos cargados*) con su estado y mensaje. |
| **Acción planificada** «RPA - Procesar cargas pendientes» | Se ejecuta cada minuto en Odoo. Convierte cada fila pendiente en un contacto o en un producto publicado con existencias. |
| **Usuario de base de datos** `rpa_robot` | Solo puede leer e insertar en las dos tablas del RPA. No tiene acceso a ninguna tabla de Odoo. |
| **Credencial de Windows** `QuetzalMart_BD` | Guarda la contraseña de `rpa_robot` fuera del proyecto. |

### 2.3 Campos que se cargan

| Clientes (hoja `clientes`) | Productos (hoja `productos`) |
|---|---|
| Name, Company Type, Related Company, Email, Phone, Street, Street2, City, State, Zip, Country, Tax ID, Website, Tags, Reference, Notes | External ID, Name, Product Type, Internal Reference, Barcode, Sales Price, Cost, Weight, Sales Description, Product Values, Cantidad a la mano, Está publicado |

Obligatorios: en clientes **Name** y **Company Type**; en productos **External ID**, **Name** y **Product Type**. Las demás columnas pueden venir vacías.

### 2.4 Ciclo de una ejecución

1. El operador ejecuta el robot y elige la carpeta de entrada. Si cancela, usa `Proyecto\RPA\Entrada`.
2. Se crea un **lote** con la fecha y hora (`yyyyMMdd_HHmmss`) que identifica la corrida.
3. El robot recorre todos los `.xls`/`.xlsx` (incluidas subcarpetas), ignora los temporales de Excel (`~$…`) y, en cada archivo, toma solo las hojas `clientes` y `productos`. Cada hoja ignorada queda registrada en el panel Output.
4. Guarda `clientes_consolidado.xlsx` y `productos_consolidado.xlsx` en `Proyecto\RPA\Salida\<lote>\`.
5. Se conecta a PostgreSQL con la credencial de Windows e inserta cada fila con estado **Pendiente**. Una fila que falla no detiene a las demás.
6. La acción planificada de Odoo procesa las filas pendientes:
   - **Clientes:** empresa o persona, país y departamento, empresa relacionada y etiquetas. Si el contacto ya existe (misma Reference, Email o Name) lo actualiza en vez de duplicarlo. El Tax ID (NIT) se guarda en la empresa dueña del contacto.
   - **Productos:** Goods se crea como almacenable y Service como servicio. Se cargan precio, costo, peso y descripciones; se publica en la tienda (categoría «Cargados por RPA») si *Está publicado* es verdadero, y se ajusta el inventario a la *Cantidad a la mano* exacta. Usa el External ID para no duplicar.
   - Cada fila queda en **Procesado**, **Omitido** (falta un dato obligatorio) o **Error**, con el motivo en *Mensaje*.
7. El robot consulta cada 10 segundos (hasta 4 minutos) cuántas filas del lote siguen pendientes. Cuando llegan a 0 guarda `resumen.xlsx`, abre la tienda `/shop` y muestra un cuadro con el resumen.

Si el robot se ejecuta otra vez con la misma carpeta, se crea un lote nuevo, pero los contactos y productos se **actualizan** en vez de duplicarse.

### 2.5 Dónde se ven los resultados

| Nivel | Dónde |
|---|---|
| Robot | Panel Output de UiPath Studio y cuadro final con el resumen |
| Archivos | `Proyecto\RPA\Salida\<lote>\` (consolidados y resumen) |
| Odoo | *Cargas RPA › Clientes cargados / Productos cargados*, *Contacts*, *Inventory › Products* |
| Sitio web | `/shop` › categoría **Cargados por RPA** |
| Base de datos | `02-PostgreSQL/05_consultas_rpa.sql` (con el usuario `odoo`) |

Consultas:

1. Resumen de cada ejecución (lote, tabla, estado, filas).
2. Clientes de la última corrida y el contacto creado en Odoo (`res_partner`).
3. Productos de la última corrida con precio, si está publicado y existencia real (`stock_quant`).
4. Filas con error u omitidas y su motivo.

---

## 4. Construcción del RPA paso a paso

La solución tiene dos partes: la configuración del servidor (Odoo y PostgreSQL, una sola vez) y el robot en UiPath Studio. El código de cada paso está en `Proyecto/RPA/`.

### 4.1 Configuración en Odoo y PostgreSQL (una sola vez)

**Paso 1 · Crear las tablas centralizadas.** Con el modo desarrollador activo (`/odoo?debug=1`), en *Settings › Technical › Actions › Server Actions* se crea la acción **RPA - Crear tablas (ejecutar 1 vez)**, modelo *Server Action*, tipo *Execute Code*, con el código de `01-Odoo/01_server_action_crear_tablas.py`, y se pulsa **Run**.

![Server Action](../Capturas/01_server_action_crear_tablas.webp)

Odoo crea los modelos `x_rpa_cliente` y `x_rpa_producto` (tablas en PostgreSQL). Abajo se ven los campos de clientes; los de productos se crean de la misma forma:

![Modelos creados](../Capturas/02_modelos_x_rpa_creados.webp)

![Campos de clientes](../Capturas/03_campos_x_rpa_cliente.png)

También crea el menú **Cargas RPA** con *Clientes cargados* y *Productos cargados*:

![Menú Cargas RPA](../Capturas/05_menu_cargas_rpa_con_accion.png)

**Paso 2 · Acción planificada.** En *Settings › Technical › Automation › Scheduled Actions* se crea **RPA - Procesar cargas pendientes**, modelo *Carga RPA - Clientes*, cada **1 minuto**, tipo *Execute Code*, con el código de `01-Odoo/02_scheduled_action_procesar_cargas.py`, y se deja **Active**.

![Cada 1 minuto y activa](../Capturas/05c_scheduled_action_cada_minuto_activa.png)

El botón **Run Manually** ejecuta la acción en ese momento sin esperar al siguiente minuto. No hace falta usarlo: con *Active* encendido, Odoo la corre sola cada minuto.

**Paso 3 · Usuario del robot con permisos mínimos.** Conectado como `odoo` (DBeaver), se ejecuta `02-PostgreSQL/01_crear_usuario_robot.sql`:

```sql
CREATE ROLE rpa_robot LOGIN PASSWORD 'CAMBIA_ESTA_CLAVE';
GRANT CONNECT ON DATABASE dbquetzalmart TO rpa_robot;
GRANT USAGE ON SCHEMA public TO rpa_robot;
GRANT SELECT, INSERT ON x_rpa_cliente, x_rpa_producto TO rpa_robot;
GRANT USAGE ON SEQUENCE x_rpa_cliente_id_seq, x_rpa_producto_id_seq TO rpa_robot;
```

![Crear usuario rpa_robot](../Capturas/06_crear_usuario_rpa_robot.png)

Prueba de seguridad (`02-PostgreSQL/02_prueba_permisos_robot.sql`): conectado como `rpa_robot`, puede leer `x_rpa_cliente`, pero al intentar leer `res_partner` PostgreSQL responde *permission denied*.

![rpa_robot sin permiso en res_partner](../Capturas/08_rpa_robot_sin_permiso_res_partner.png)

### 4.2 Preparación del equipo

Driver ODBC, credencial de Windows y paquetes de Studio: ver [sección 1](#1-instalación-del-robot-rpa).

### 4.3 Construcción del robot en UiPath Studio

Proyecto **Process** llamado `QuetzalMart_RPA_Carga` (Windows, VB). Todo el flujo está dentro de un Sequence **Robot QuetzalMart**, organizado en bloques A a J. Las expresiones de cada bloque están en `04-UiPath/03_expresiones.md` y el código de los *Invoke Code* en `04-UiPath/01_…`, `02_…` y `04_…`.

**Variables del flujo**

![Variables](../Capturas/12_uipath_variables.png)

**Bloque A · Preparar la corrida.** Registra el inicio, crea el lote con la fecha y hora, deja elegir la carpeta de entrada (*Browse for Folder*; si se cancela usa `..\Entrada`) y crea `Salida\<lote>`.

![Bloque A terminado](../Capturas/11_uipath_bloque_A_final.png)

**Bloque B · Recorrer todos los Excel.** *For Each File in Folder* sobre la carpeta de entrada, con *Include subfolders* y filtro `*.xls*`. Ignora los temporales `~$` y protege cada archivo con un *Try Catch* para que un Excel dañado no detenga al robot.

![If y Try Catch](../Capturas/15_uipath_bloque_B_if_try_catch.png)

**Bloque C · Elegir solo las hojas clientes y productos.** *Get Workbook Sheets* obtiene los nombres de las hojas y un *If* deja pasar solo `clientes` y `productos`. Las demás se registran como «Hoja ignorada».

![Bloque C](../Capturas/16_uipath_bloque_C_hojas.png)

**Bloque D · Leer y normalizar.** *Read Range Workbook* lee la hoja completa y el *Invoke Code* «Normalizar hoja» (`01_invoke_code_normalizar_hoja.vb`) pasa las filas al consolidado con los encabezados correctos.

![Leer y normalizar](../Capturas/18_uipath_bloque_D_leer_normalizar.png)

**Bloque E · Consolidado.** Fuera del recorrido: registra cuántos clientes y productos se encontraron, se detiene con un error claro si no hay ninguno y guarda `clientes_consolidado.xlsx` y `productos_consolidado.xlsx` con *Write Range Workbook* (opción *Use Local File* para que cree el archivo).

![Bloque E](../Capturas/20_uipath_bloque_E_consolidado.png)

![Write Range clientes](../Capturas/21_uipath_bloque_E_write_clientes.png)

**Bloque F · Generar los INSERT.** El *Invoke Code* «Generar SQL» (`02_invoke_code_generar_sql.vb`) crea un `INSERT` por fila. Cada valor va entre comillas simples con las comillas internas duplicadas, y las celdas vacías se guardan como `NULL`.

![Generar SQL](../Capturas/23_uipath_bloque_F_generar_sql.png)

![Argumentos clientes](../Capturas/24_uipath_bloque_F_argumentos_clientes.png)

**Bloque G · Conexión segura.** *Get Secure Credential* lee `QuetzalMart_BD` del Administrador de credenciales y *Connect to Database* abre la conexión ODBC (`System.Data.Odbc`, driver `PostgreSQL Unicode(x64)`).

![Get Secure Credential](../Capturas/26_uipath_bloque_G_credencial.png)

![Connect to Database](../Capturas/27_uipath_bloque_G_conexion.png)

![Estructura A a G](../Capturas/28_uipath_estructura_bloques_A_G.png)

**Bloque H · Insertar cada fila.** *For Each* sobre todos los `INSERT`. Cada uno se ejecuta con *Run Command* dentro de un *Try Catch* que cuenta los errores sin detener la carga.

![Try de inserción](../Capturas/29_uipath_bloque_H_insertar_try.png)

![Run Command](../Capturas/31_uipath_bloque_H_run_command_propiedades.png)

**Bloque I · Esperar a Odoo y verificar por SQL.** *Do While* que cada 10 segundos (máximo 24 veces) cuenta las filas pendientes del lote con *Run Query*. Después consulta el resumen por estado, lo guarda en `resumen.xlsx` y se desconecta.

![Do While y Run Query](../Capturas/33_uipath_bloque_I_do_while_run_query.png)

![Estructura bloque I](../Capturas/36_uipath_bloque_I_estructura.png)

**Bloque J · Mostrar el resultado.** Registra el resumen, abre la tienda con el *Invoke Code* «Abrir tienda» (`04_invoke_code_abrir_tienda.vb`) y muestra un *Message Box*.

![Bloque J](../Capturas/39_uipath_bloque_J_resultado.png)

El diagrama completo del flujo está en el Manual 2 (`Documentacion/Manual2_RPA.md`).

### 4.4 Ejecución y comprobación

**Ejecutar.** Antes, abrir Odoo en el navegador e iniciar sesión (así se activan las acciones planificadas). En Studio: **Debug File › Run File** y elegir la carpeta de entrada.

![Run File](../Capturas/39b_uipath_ejecutar_run_file.png)

**Panel Output.** Muestra qué hojas toma y cuáles ignora. Con la carpeta de prueba: 10 clientes y 13 productos consolidados, 23 filas insertadas sin errores y 0 pendientes al final (1 minuto 11 segundos).

![Output de la ejecución](../Capturas/42_ejecucion_output_exitosa.png)

![Mensaje final](../Capturas/43_ejecucion_message_box_resumen.png)

![Carpeta Salida](../Capturas/43b_carpeta_salida_consolidados.png)

**En Odoo (nivel web).** Todas las filas en *Procesado*, con el mensaje y el ID creado:

![Clientes cargados](../Capturas/44_odoo_clientes_cargados_procesado.webp)

![Productos cargados](../Capturas/45_odoo_productos_cargados_procesado.webp)

![Contactos creados](../Capturas/46_odoo_contactos_creados.webp)

![Existencias](../Capturas/47_odoo_inventario_on_hand.webp)

![Tienda filtrada](../Capturas/48b_tienda_filtrada_cargados_por_rpa.png)

**En la base de datos (nivel SQL).** Consultas de `05_consultas_rpa.sql` con el usuario `odoo`:

![Resumen por lote](../Capturas/49_sql_resumen_por_lote.png)

![Productos con precio, publicación y existencia](../Capturas/50_sql_productos_precio_publicado_existencia.png)

**Segunda ejecución: no duplica.** Con la misma carpeta se crea un lote nuevo; los mensajes dicen *Actualizado* y no aparecen contactos ni productos repetidos.

![Segunda ejecución](../Capturas/51_segunda_ejecucion_output.png)

![Clientes actualizados](../Capturas/52_segunda_ejecucion_clientes_actualizado.webp)

![Contactos sin duplicados](../Capturas/55_segunda_ejecucion_contactos_sin_duplicados.webp)

### 4.5 Ventajas de implementar el RPA

- **Tiempo.** Revisar decenas de carpetas y hojas a mano toma horas; el robot procesa toda la estructura en alrededor de un minuto y siempre de la misma forma.
- **Precisión.** Toma solo las hojas `clientes` y `productos`, normaliza los encabezados y no copia mal ni omite filas. Las filas incompletas no se pierden: quedan marcadas como *Omitido* con el dato que falta.
- **Trazabilidad.** Cada fila guarda el archivo de origen, el lote (fecha y hora de la corrida), su estado y el contacto o producto que generó en Odoo. Además quedan los consolidados y el resumen en Excel por cada ejecución.
- **Sin duplicados.** Se puede ejecutar varias veces: los contactos y productos existentes se actualizan en vez de repetirse.
- **Seguridad.** El robot usa un usuario de base de datos que solo puede leer e insertar en sus dos tablas, y la contraseña vive en el Administrador de credenciales de Windows, no en el proyecto. Los contactos y productos los crea Odoo con su propia lógica.
- **Tolerancia a fallos.** Un archivo dañado, una hoja con otro nombre o una fila con datos inválidos se registran y el robot sigue con lo demás.
- **Escalabilidad.** Con la expansión a México y El Salvador basta con agregar las carpetas de las nuevas sucursales a la entrada; no hay que cambiar el robot.
- **Disponibilidad inmediata.** Lo cargado queda visible en el ERP, en la tienda en línea y por consultas SQL apenas termina la ejecución.
