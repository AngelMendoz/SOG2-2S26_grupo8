# Proyecto QuetzalMart · SOG2 2S2026

- `Enunciado/`: PDF del proyecto y distribución de tareas del grupo.
- `RPA/`: robot de UiPath que carga las hojas `clientes` y `productos` en la base de Odoo (parte de Angel).

## RPA

Estado, requisitos cumplidos y pendientes de documentación: [`RPA/ESTADO_RPA.md`](RPA/ESTADO_RPA.md).

| Carpeta | Contenido |
|---|---|
| `RPA/01-Odoo/` | Server Action (crear tablas) y Scheduled Action (procesar cargas) |
| `RPA/02-PostgreSQL/` | Usuario `rpa_robot`, pruebas de permisos y puerto, consultas para la calificación, driver ODBC |
| `RPA/03-Carpeta-prueba/` | Script que genera `RPA/Entrada/` |
| `RPA/04-UiPath/` | Código de los Invoke Code y expresiones de los bloques A–J |
| `RPA/QuetzalMart_RPA_Carga/` | Proyecto de UiPath Studio (abrir `project.json`) |
| `RPA/Entrada/` | Carpeta de prueba con la jerarquía del enunciado |
| `RPA/Capturas/` | Evidencia para el Manual 1, sección 4 |
| `RPA/Documentacion/` | Manual 1 (secciones 1, 2 y 4) y diagramas del Manual 2 |

Para ejecutarlo en otra PC, ver la fase 08 de la guía: https://claude.ai/artifact/BTUdPHtGqa7TH7v1fLtDWs
