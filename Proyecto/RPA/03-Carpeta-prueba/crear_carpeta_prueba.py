# Crea Proyecto/RPA/Entrada (en el repo) con la jerarquía del enunciado para probar el robot.
# Uso (desde cualquier carpeta):  python crear_carpeta_prueba.py  [carpeta_destino]
import os, sys, shutil
from openpyxl import Workbook

RPA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Proyecto/RPA
BASE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RPA, "Entrada")
CLI = ["Name*", "Company Type*", "Related Company", "Email", "Phone", "Street", "Street2", "City",
       "State", "Zip", "Country", "Tax ID", "Website", "Tags", "Reference", "Notes"]
PRO = ["External ID", "Name", "Product Type", "Internal Reference", "Barcode", "Sales Price", "Cost",
       "Weight", "Sales Description", "Product Values", "Cantidad a la mano", "Está publicado"]

def cliente(n, nombre, tipo, ciudad, correo, etiquetas, empresa=None):
    return [nombre, tipo, empresa, correo, "+502 2%03d 4%03d" % (n, n), "%d calle %d-%02d zona %d" % (n, n, n, n % 16 + 1),
            None, ciudad, None, "0%04d" % (1000 + n), "GT", None, None, etiquetas, "QM-CLI-%03d" % n, "Cargado por RPA"]

def producto(n, nombre, tipo, precio, costo, cantidad, publicado=True):
    return ["QM_PROD_%03d" % n, nombre, tipo, "QM-%03d" % n, None, precio, costo, 0.5, nombre + " - QuetzalMart", None,
            cantidad, publicado]

ARCHIVOS = {
    r"clientes - region central\clientes - region central.xlsx": {
        "clientes": [CLI, cliente(1, "Abarrotes La Ceiba", "Company", "Guatemala", "compras@laceiba.gt", "Mayorista"),
                     cliente(2, "Maria Lopez", "Person", "Mixco", "maria.lopez@example.com", "Frecuente"),
                     cliente(3, "Carlos Perez", "Person", "Villa Nueva", "carlos.perez@example.com", "Nuevo", "Abarrotes La Ceiba")],
        "reclamos": [["Fecha", "Cliente", "Motivo"], ["2026-09-01", "Maria Lopez", "Entrega tardia"]]},
    r"clientes - occidente\clientes occidente 2026.xlsx": {
        "notas": [["Nota"], ["Esta hoja se ignora"]],
        "clientes": [CLI, cliente(4, "Tienda El Quetzal", "Company", "Quetzaltenango", "ventas@elquetzal.gt", "Mayorista, Occidente"),
                     cliente(5, "Ana Garcia", "Person", "Retalhuleu", "ana.garcia@example.com", "Occidente")]},
    r"productos - bodega principal\productos bodega principal.xlsx": {
        "registros": [["Fecha", "Movimiento"], ["2026-09-02", "Ingreso de mercaderia"]],
        "productos": [PRO, producto(1, "Cafe Antigua 454 g", "Goods", 65, 40, 120),
                      producto(2, "Frijol negro 1 lb", "Goods", 12.5, 8, 300),
                      producto(3, "Agua pura 600 ml", "Goods", 5, 2.75, 500),
                      producto(4, "Servicio de entrega a domicilio", "Service", 20, 10, None)]},
    r"productos - temporada\productos temporada.xlsx": {
        "productos": [PRO, producto(5, "Chocolate de mesa 4 tabletas", "Goods", 18, 11, 80),
                      producto(6, "Pan dulce surtido", "Goods", 25, 15, 40, False)]},
    r"proveedores - locales\proveedores locales.xlsx": {
        "proveedor": [["Nombre", "Telefono"], ["Distribuidora Maya", "+502 2222 3333"]]},
    r"reclamos - septiembre\reclamos septiembre.xlsx": {
        "reclamos": [["Fecha", "Motivo"], ["2026-09-10", "Producto golpeado"]]},
    r"registro - ventas\registro ventas.xlsx": {
        "registros": [["Fecha", "Total"], ["2026-09-12", 1500]],
        "clientes": [CLI, cliente(6, "Jose Hernandez", "Person", "Escuintla", "jose.hernandez@example.com", "Frecuente")]},
}

for ruta, hojas in ARCHIVOS.items():
    completo = os.path.join(BASE, ruta)
    os.makedirs(os.path.dirname(completo), exist_ok=True)
    libro = Workbook()
    libro.remove(libro.active)
    for nombre, filas in hojas.items():
        hoja = libro.create_sheet(nombre)
        for fila in filas:
            hoja.append(fila)
    libro.save(completo)
    print("Creado:", completo)
# Copia los dos archivos de ejemplo del catedrático
ejemplos = os.path.join(BASE, "ejemplos - catedra")
os.makedirs(ejemplos, exist_ok=True)
for nombre in ("clientes-archivo de ejemplo.xlsx", "productos - archivo de ejemplo.xls"):
    shutil.copy2(os.path.join(RPA, "Archivos-ejemplo-catedra", nombre), ejemplos)
    print("Copiado:", os.path.join(ejemplos, nombre))
print("Listo. Carpeta de prueba en", BASE)
