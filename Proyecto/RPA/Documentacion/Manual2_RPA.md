# Manual 2 · Diagramas de flujo del RPA (UiPath)

Proyecto QuetzalMart · SOG2 · Segundo semestre 2026 · Responsable: Angel

Corresponde al punto «Diagrama de flujo de visualización para los incisos realizados con UiPath». Los demás diagramas del Manual 2 (compras, ventas, flujo de la empresa y flujo del cliente web/tienda) se reparten con Madeline.

Los diagramas están hechos en Excalidraw. Los archivos `.excalidraw` de `diagramas/` se abren y editan en <https://excalidraw.com> (menú › **Open**). Para actualizar la imagen: menú › **Export image** › PNG.

Los diagramas 2 y 3 usan la notación estándar de diagramas de flujo (ANSI/ISO 5807) y cada uno trae su simbología: óvalo = inicio/fin, rectángulo = proceso, rombo = decisión, paralelogramo = entrada o salida, documento = archivo Excel generado, cilindro = base de datos, rectángulo con doble línea = proceso definido en otro diagrama, corchete = comentario. El diagrama 1 es una vista general de apoyo.

## 1. Vista general

De dónde sale la información y dónde termina.

![Vista general](diagramas/01_vista_general.png)

## 2. Flujo del robot UiPath

Lo que hace el robot `QuetzalMart_RPA_Carga` cada vez que se ejecuta. La parte 1 recorre los Excel y la parte 2 carga los datos y espera a que Odoo los procese.

![Flujo del robot](diagramas/02_flujo_robot_uipath.png)

## 3. Lo que hace Odoo con cada fila

La acción planificada «RPA - Procesar cargas pendientes» corre cada minuto y convierte cada fila que insertó el robot en un contacto o un producto.

![Procesamiento en Odoo](diagramas/03_procesamiento_odoo.png)
