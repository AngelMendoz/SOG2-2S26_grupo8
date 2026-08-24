"""Segmentación de clientes (Punto 4)."""

import pandas as pd # Importa Pandas para manipulación y análisis de grandes volúmenes de datos
import matplotlib.pyplot as plt # Importa Pyplot de Matplotlib para la creación de gráficos
import seaborn as sns # Importa Seaborn para generar gráficos estadísticos visualmente atractivos
from pathlib import Path # Importa Path para manejar las rutas de carpetas de forma segura en Windows/Mac/Linux

# Configuración de estilos para los gráficos
sns.set_theme(style="whitegrid") # Establece un fondo con cuadrícula blanca y tonos suaves para todos los gráficos

def segmentar_por_edad(clientes: pd.DataFrame, directorio_resultados: Path = None, graficar: bool = True) -> pd.DataFrame:
    """Agrupa a los clientes por rangos de edad y analiza patrones de compra."""
    df = clientes.copy() # Crea una copia del DataFrame de clientes para no alterar los datos originales
    
    # Definir rangos de edad
    bins = [17, 25, 35, 45, 55, 65, 120] # Define los puntos de corte numéricos para los intervalos de edad
    labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+'] # Define los nombres legibles de cada categoría de edad
    df['rango_edad'] = pd.cut(df['edad'], bins=bins, labels=labels) # Crea una nueva columna 'rango_edad' clasificando a cada cliente en un rango
    
    # Agrupar y calcular métricas
    resumen = df.groupby('rango_edad', observed=False).agg( # Agrupa todos los registros usando la nueva columna 'rango_edad'
        total_clientes=('id_cliente', 'count'), # Cuenta cuántos id_cliente hay por cada rango
        ventas_totales=('venta_total', 'sum'), # Suma la columna 'venta_total' de todos los clientes de ese rango
        promedio_compras=('n_compras', 'mean'), # Calcula el promedio de la cantidad de compras
        venta_promedio=('venta_total', 'mean') # Calcula el promedio en dinero de las ventas totales
    ).reset_index() # Convierte el índice agrupado ('rango_edad') de vuelta en una columna normal
    
    # Gráfico 1: Ventas Totales por Rango de Edad
    if graficar: # Verifica si se solicitó graficar (falso si lo llama la Inteligencia Artificial)
        plt.figure(figsize=(10, 5)) # Crea una ventana para el gráfico con medidas de 10x5 pulgadas
        sns.barplot(data=resumen, x='rango_edad', y='ventas_totales', hue='rango_edad', palette="viridis", legend=False) # Dibuja un gráfico de barras con los datos
        plt.title('Ventas Totales por Rango de Edad', fontsize=14) # Coloca el título en la parte superior
        plt.xlabel('Rango de Edad') # Nombra el eje inferior (X)
        plt.ylabel('Ventas Totales ($)') # Nombra el eje vertical (Y)
        if directorio_resultados: # Si nos pasaron una carpeta donde guardar la imagen
            directorio_resultados.mkdir(parents=True, exist_ok=True) # Crea la carpeta 'resultados' si no existe
            plt.savefig(directorio_resultados / 'ventas_por_edad.png', bbox_inches='tight') # Guarda el gráfico en formato PNG
        plt.show() # Muestra el gráfico en la pantalla (Ej. en Jupyter Notebook)

    # Gráfico 2: Venta Promedio por Cliente según Edad
    if graficar:
        plt.figure(figsize=(10, 5)) # Crea una nueva ventana para el segundo gráfico
        sns.barplot(data=resumen, x='rango_edad', y='venta_promedio', hue='rango_edad', palette="magma", legend=False) # Dibuja el gráfico usando otros colores (magma)
        plt.title('Venta Promedio por Cliente según Edad', fontsize=14) # Coloca el título
        plt.xlabel('Rango de Edad') # Etiqueta el eje X
        plt.ylabel('Venta Promedio ($)') # Etiqueta el eje Y
        if directorio_resultados:
            plt.savefig(directorio_resultados / 'venta_promedio_edad.png', bbox_inches='tight') # Guarda este segundo gráfico
        plt.show() # Imprime el gráfico en el Notebook
    
    return resumen # Devuelve la tabla con los cálculos a quien haya llamado la función

def comportamiento_por_genero(clientes: pd.DataFrame, directorio_resultados: Path = None, graficar: bool = True) -> pd.DataFrame:
    """Compara el comportamiento de compra entre géneros."""
    df = clientes.copy() # Hace una copia de los clientes
    df['genero_desc'] = df['genero'].map({1: 'Femenino', 0: 'Masculino'}) # Convierte los números 1 y 0 a textos legibles
    
    resumen = df.groupby('genero_desc').agg( # Agrupa por la nueva columna textual de género
        total_clientes=('id_cliente', 'count'), # Cuenta los clientes de cada género
        ventas_totales=('venta_total', 'sum'), # Suma todo su dinero gastado
        venta_promedio=('venta_total', 'mean'), # Calcula la venta promedio
        promedio_compras=('n_compras', 'mean') # Calcula el promedio de la cantidad de compras
    ).reset_index() # Devuelve los índices a formato de columna
    
    if graficar: # Valida si debemos crear los gráficos
        plt.figure(figsize=(8, 5)) # Inicia un gráfico de 8x5 pulgadas
        sns.barplot(data=resumen, x='genero_desc', y='ventas_totales', hue='genero_desc', palette="Set2", legend=False) # Dibuja gráfico de barras
        plt.title('Ventas Totales por Género', fontsize=14)
        plt.xlabel('Género')
        plt.ylabel('Ventas Totales ($)')
        if directorio_resultados:
            plt.savefig(directorio_resultados / 'ventas_por_genero.png', bbox_inches='tight') # Guarda en PNG
        plt.show()
        
        plt.figure(figsize=(8, 5)) # Inicia un segundo gráfico para el promedio
        sns.barplot(data=resumen, x='genero_desc', y='venta_promedio', hue='genero_desc', palette="Pastel1", legend=False)
        plt.title('Venta Promedio por Género', fontsize=14)
        plt.xlabel('Género')
        plt.ylabel('Venta Promedio ($)')
        if directorio_resultados:
            plt.savefig(directorio_resultados / 'venta_promedio_genero.png', bbox_inches='tight')
        plt.show()
    
    return resumen # Devuelve el resumen tabular

def impacto_boletines_vales(compras: pd.DataFrame, directorio_resultados: Path = None, graficar: bool = True) -> pd.DataFrame:
    """Analiza los patrones de compra según uso de boletín y vales."""
    df = compras.copy() # En este caso copiamos la tabla de 'compras' en lugar de clientes
    
    df['tipo_compra'] = 'Normal' # Primero asumimos que todas las compras son Normales (sin vales ni boletín)
    # A continuación usamos condiciones lógicas (== True / False) para clasificar cada compra
    df.loc[(df['boletin'] == True) & (df['vale'] == False), 'tipo_compra'] = 'Solo Boletín' # Marca si solo usó boletín
    df.loc[(df['boletin'] == False) & (df['vale'] == True), 'tipo_compra'] = 'Solo Vale' # Marca si solo usó vale
    df.loc[(df['boletin'] == True) & (df['vale'] == True), 'tipo_compra'] = 'Boletín y Vale' # Marca si usó los dos
    
    resumen = df.groupby('tipo_compra').agg( # Agrupa usando estas 4 clasificaciones
        cantidad_compras=('id_compra', 'count'), # Cuenta cuántas compras caen en cada categoría
        monto_total=('monto_compra', 'sum'), # Suma el dinero generado en esas compras
        monto_promedio=('monto_compra', 'mean') # Calcula el ticket promedio (monto/cantidad)
    ).reset_index()
    
    # Ordenar por cantidad para mejor visualización
    resumen = resumen.sort_values(by='cantidad_compras', ascending=False) # Ordena la tabla de mayor a menor según la cantidad de compras
    
    if graficar:
        plt.figure(figsize=(10, 5)) # Gráfico de 10x5
        sns.barplot(data=resumen, x='tipo_compra', y='monto_total', hue='tipo_compra', palette="cubehelix", legend=False) # Barras con colores cubehelix
        plt.title('Monto Total de Compras por Uso de Boletín/Vale', fontsize=14)
        plt.xlabel('Clasificación')
        plt.ylabel('Monto Total ($)')
        if directorio_resultados:
            plt.savefig(directorio_resultados / 'monto_por_boletin_vale.png', bbox_inches='tight') # Guarda archivo
        plt.show()
        
        plt.figure(figsize=(10, 5)) # Otro gráfico de 10x5
        sns.barplot(data=resumen, x='tipo_compra', y='monto_promedio', hue='tipo_compra', palette="crest", legend=False) # Barras de monto promedio
        plt.title('Monto Promedio por Compra según Uso de Boletín/Vale', fontsize=14)
        plt.xlabel('Clasificación')
        plt.ylabel('Monto Promedio ($)')
        if directorio_resultados:
            plt.savefig(directorio_resultados / 'monto_promedio_boletin_vale.png', bbox_inches='tight')
        plt.show()
    
    return resumen # Devuelve el resultado en formato Pandas DataFrame

def ejecutar_segmentacion(clientes: pd.DataFrame, compras: pd.DataFrame, directorio_resultados: Path = None):
    """Función maestra que ejecuta todo el punto 4 e imprime las tablas en consola."""
    print("--- 4.a Segmentación por Edad ---") # Imprime un separador
    res_edad = segmentar_por_edad(clientes, directorio_resultados) # Ejecuta la función de edad
    display(res_edad) # Usa display de IPython para mostrar una tabla bonita en el Notebook
    
    print("\\n--- 4.b Comportamiento por Género ---")
    res_genero = comportamiento_por_genero(clientes, directorio_resultados) # Ejecuta la función de género
    display(res_genero)
    
    print("\\n--- 4.c Impacto de Boletines y Vales ---")
    res_boletin_vale = impacto_boletines_vales(compras, directorio_resultados) # Ejecuta la función de boletines
    display(res_boletin_vale)
