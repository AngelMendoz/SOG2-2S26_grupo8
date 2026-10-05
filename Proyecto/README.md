# Proyecto QuetzalMart · SOG2 2S2026

- `Enunciado/`: PDF del proyecto.
- `RPA/`: robot de UiPath que carga las hojas `clientes` y `productos` en la base de Odoo.

## RPA (avance)

Guía completa: `RPA/Guia_RPA_UiPath_QuetzalMart.html`.

| Fase de la guía | Archivo | Estado |
|---|---|---|
| 03 · Odoo | `RPA/01-Odoo/01_server_action_crear_tablas.py` | Hecho (tablas `x_rpa_cliente`, `x_rpa_producto` y menú *Cargas RPA*) |
| 03 · Odoo | `RPA/01-Odoo/02_scheduled_action_procesar_cargas.py` | Scheduled Action *RPA - Procesar cargas pendientes* |
| 04 · PostgreSQL | `RPA/02-PostgreSQL/01_crear_usuario_robot.sql` | Hecho (la clave real no se sube) |
| 04 · PostgreSQL | `RPA/02-PostgreSQL/02_prueba_permisos_robot.sql` | Hecho: `rpa_robot` lee `x_rpa_cliente` y recibe *permission denied* en `res_partner` |
| 04 · PostgreSQL | `RPA/02-PostgreSQL/04_diagnostico_permisos.sql` | Revisa el usuario de la conexión y los permisos reales del robot |
| 04 · PostgreSQL | `RPA/02-PostgreSQL/03_prueba_puerto.ps1` | Prueba que el puerto 5432 responde |
| 05 · Tu PC | `RPA/03-Carpeta-prueba/crear_carpeta_prueba.py` | Hecho: genera `RPA/Entrada/` (7 Excel + 2 ejemplos del catedrático) |
| 05 · Tu PC | `winget install --id PostgreSQL.psqlODBC --exact` | Hecho: driver `PostgreSQL Unicode(x64)` instalado |

- `RPA/Capturas/`: capturas para el Manual 1, sección 4.
- `RPA/Archivos-ejemplo-catedra/`: Excel de ejemplo del catedrático (entrada del robot).
