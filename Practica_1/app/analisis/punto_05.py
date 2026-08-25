"""Analisis de correlacion (Punto 5)."""

import numpy as np # Importa NumPy para operaciones numericas 
import pandas as pd # Importa Pandas para manipulacion de datos
import matplotlib.pyplot as plt # Importa Pyplot para crear los graficos
import seaborn as sns # Importa Seaborn para graficos estadisticos
from pathlib import Path # Importa Path para manejar rutas de carpetas
from scipy import stats # Importa scipy.stats para pearsonr, spearmanr y chi2_contingency

# Configuracion de estilos para los graficos
sns.set_theme(style="whitegrid") # Establece un fondo con cuadricula blanca para todos los graficos


def _interpretar_fuerza(valor_coeficiente: float) -> str:
    """Traduce un coeficiente de correlacion a una descripcion cualitativa estandar."""
    valor = abs(valor_coeficiente) # Trabaja con el valor absoluto sin importar el signo
    if valor < 0.1: # Umbral estandar de Cohen para correlaciones
        return 'Nula o insignificante'
    if valor < 0.3:
        return 'Debil'
    if valor < 0.5:
        return 'Moderada'
    if valor < 0.7:
        return 'Fuerte'
    return 'Muy fuerte'


def correlacion_venta_edad(clientes: pd.DataFrame, directorio_resultados: Path = None, graficar: bool = True) -> dict:
    """Investiga si existe una relacion entre el total de la venta y la edad del cliente."""
    df = clientes.copy() # Copia el DataFrame para no alterar el original

    r_pearson, p_pearson = stats.pearsonr(df['edad'], df['venta_total']) # Correlacion lineal
    r_spearman, p_spearman = stats.spearmanr(df['edad'], df['venta_total']) # Correlacion de rangos (no asume linealidad)

    resultado = {
        'variable_x': 'edad',
        'variable_y': 'venta_total',
        'pearson_r': float(r_pearson),
        'pearson_p_valor': float(p_pearson),
        'spearman_r': float(r_spearman),
        'spearman_p_valor': float(p_spearman),
        'interpretacion': _interpretar_fuerza(r_pearson),
        'significativo': bool(p_pearson < 0.05), # Con 95% de confianza
    }

    if graficar: # Si se solicito graficar (falso si lo llama la IA)
        plt.figure(figsize=(8, 5)) # Ventana del grafico
        sns.regplot(data=df, x='edad', y='venta_total', scatter_kws={'alpha': 0.4}, line_kws={'color': 'red'}) # Dispersion + linea de tendencia
        plt.title(f"Venta Total vs Edad (r = {r_pearson:.3f})", fontsize=14)
        plt.xlabel('Edad')
        plt.ylabel('Venta Total ($)')
        if directorio_resultados: # Si nos pasaron carpeta donde guardar
            directorio_resultados.mkdir(parents=True, exist_ok=True)
            plt.savefig(directorio_resultados / 'correlacion_venta_edad.png', bbox_inches='tight')
        plt.show()

    return resultado


def correlacion_genero_metodo_pago(clientes: pd.DataFrame, compras: pd.DataFrame, directorio_resultados: Path = None, graficar: bool = True) -> dict:
    """Examina si hay una correlacion entre el genero del cliente y el metodo de pago preferido."""
    # Un cliente puede tener varias compras, tomamos el metodo de pago mas usado por cada cliente
    metodo_preferido = (
        compras.groupby('id_cliente')['metodo_pago']
        .agg(lambda serie: serie.mode().iloc[0]) # Toma el valor mas frecuente (moda) por cliente
        .reset_index()
        .rename(columns={'metodo_pago': 'metodo_pago_preferido'})
    )
    df = clientes[['id_cliente', 'genero']].merge(metodo_preferido, on='id_cliente') # Une clientes con su metodo preferido
    df['genero_desc'] = df['genero'].map({1: 'Femenino', 0: 'Masculino'}) # Traduce el codigo a texto
    df['metodo_desc'] = df['metodo_pago_preferido'].map({0: 'Efectivo', 1: 'Tarjeta de Credito', 2: 'Tarjeta de Debito'})

    tabla_contingencia = pd.crosstab(df['genero_desc'], df['metodo_desc']) # Tabla cruzada de frecuencias
    chi2, p_valor, grados_libertad, _esperado = stats.chi2_contingency(tabla_contingencia) # Prueba chi-cuadrado
    n = tabla_contingencia.sum().sum() # Total de observaciones
    minimo_dim = min(tabla_contingencia.shape) - 1 # Dimension minima para normalizar Cramer's V
    cramers_v = float(np.sqrt((chi2 / n) / minimo_dim)) if minimo_dim > 0 else 0.0 # Fuerza de asociacion (0 a 1)

    resultado = {
        'tabla_contingencia': tabla_contingencia,
        'chi2': float(chi2),
        'p_valor': float(p_valor),
        'grados_libertad': int(grados_libertad),
        'cramers_v': cramers_v,
        'interpretacion': _interpretar_fuerza(cramers_v),
        'significativo': bool(p_valor < 0.05),
    }

    if graficar:
        plt.figure(figsize=(8, 5))
        sns.heatmap(tabla_contingencia, annot=True, fmt='d', cmap='YlGnBu') # Mapa de calor de la tabla cruzada
        plt.title(f"Genero vs Metodo de Pago (Cramer V = {cramers_v:.3f})", fontsize=14)
        plt.xlabel('Metodo de Pago')
        plt.ylabel('Genero')
        if directorio_resultados:
            directorio_resultados.mkdir(parents=True, exist_ok=True)
            plt.savefig(directorio_resultados / 'correlacion_genero_metodo_pago.png', bbox_inches='tight')
        plt.show()

    return resultado


def correlacion_boletin_vale(compras: pd.DataFrame, directorio_resultados: Path = None, graficar: bool = True) -> dict:
    """Investiga si existe una correlacion entre los clientes que utilizan boletines y vales."""
    df = compras.copy()
    df['boletin_num'] = df['boletin'].astype(int) # Convierte booleano a 0/1 para calcular Pearson
    df['vale_num'] = df['vale'].astype(int)

    tabla_contingencia = pd.crosstab(df['boletin'], df['vale']) # Tabla cruzada 2x2
    chi2, p_valor, grados_libertad, _esperado = stats.chi2_contingency(tabla_contingencia)
    n = tabla_contingencia.sum().sum()
    r_pearson, _p = stats.pearsonr(df['boletin_num'], df['vale_num']) # El coeficiente phi para 2x2 es equivalente a Pearson sobre 0/1
    phi = float(r_pearson)

    resultado = {
        'tabla_contingencia': tabla_contingencia,
        'chi2': float(chi2),
        'p_valor': float(p_valor),
        'grados_libertad': int(grados_libertad),
        'phi': phi,
        'interpretacion': _interpretar_fuerza(phi),
        'significativo': bool(p_valor < 0.05),
    }

    if graficar:
        plt.figure(figsize=(6, 5))
        sns.heatmap(tabla_contingencia, annot=True, fmt='d', cmap='rocket_r')
        plt.title(f"Boletin vs Vale (Phi = {phi:.3f})", fontsize=14)
        plt.xlabel('Vale')
        plt.ylabel('Boletin')
        if directorio_resultados:
            directorio_resultados.mkdir(parents=True, exist_ok=True)
            plt.savefig(directorio_resultados / 'correlacion_boletin_vale.png', bbox_inches='tight')
        plt.show()

    return resultado


def ejecutar_correlacion(clientes: pd.DataFrame, compras: pd.DataFrame, directorio_resultados: Path = None):
    """Funcion maestra que ejecuta todo el punto 5 e imprime los resultados en consola."""
    print("--- 5.a Correlacion Venta Total vs Edad ---")
    res_edad = correlacion_venta_edad(clientes, directorio_resultados)
    print(f"Pearson r = {res_edad['pearson_r']:.4f} (p = {res_edad['pearson_p_valor']:.4f}) -> {res_edad['interpretacion']}")

    print("\n--- 5.b Correlacion Genero vs Metodo de Pago ---")
    res_pago = correlacion_genero_metodo_pago(clientes, compras, directorio_resultados)
    print(res_pago['tabla_contingencia'])
    print(f"Chi2 = {res_pago['chi2']:.4f} (p = {res_pago['p_valor']:.4f}), Cramer V = {res_pago['cramers_v']:.4f} -> {res_pago['interpretacion']}")

    print("\n--- 5.c Correlacion Boletin vs Vale ---")
    res_bv = correlacion_boletin_vale(compras, directorio_resultados)
    print(res_bv['tabla_contingencia'])
    print(f"Chi2 = {res_bv['chi2']:.4f} (p = {res_bv['p_valor']:.4f}), Phi = {res_bv['phi']:.4f} -> {res_bv['interpretacion']}")