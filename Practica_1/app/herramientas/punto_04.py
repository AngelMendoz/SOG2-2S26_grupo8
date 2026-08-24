"""Funciones que el servidor MCP expone al agente conversacional para segmentación."""

from __future__ import annotations # Permite usar anotaciones de tipos modernas de Python

import json # Módulo para convertir y trabajar con objetos en formato JSON
from typing import Any # Permite declarar que una variable puede ser de "Cualquier" tipo

import pandas as pd # Importa Pandas para el manejo tabular de los datos
from pathlib import Path # Importa Path por buenas prácticas de manejo de rutas de archivos

# Usamos la misma lógica de conexión de punto_02 que carga el motor global
from app.analisis.punto_02 import crear_motor, obtener_datos # Importa funciones de tu compañero para conectarnos a PostgreSQL
from app.analisis.punto_04 import segmentar_por_edad, comportamiento_por_genero, impacto_boletines_vales # Importa las 3 funciones lógicas que tú creaste
from app.config import RUTA_ENV # Importa la variable de entorno que guarda la ruta al archivo .env

def _registros_json(datos: pd.DataFrame) -> list[dict[str, Any]]:
    """Convierte tipos de Pandas y NumPy a valores JSON nativos."""
    # La IA no entiende los DataFrames directos de Python, por eso lo transformamos
    # a_json(orient='records') crea una lista de diccionarios, y json.loads() lo convierte a un objeto nativo
    return json.loads(datos.to_json(orient="records", date_format="iso")) 

def _obtener_datos_frescos():
    """Conecta a BD y extrae clientes y compras."""
    motor = crear_motor(RUTA_ENV) # Usa las credenciales del .env para crear una conexión a la DB
    clientes, compras, _ = obtener_datos(motor) # Corre la función SQL para jalar ambas tablas en tiempo real
    return clientes, compras # Devuelve las dos tablas

def consultar_segmentacion_edad() -> dict[str, Any]:
    """Obtiene el resumen de compras y clientes segmentado por rangos de edad."""
    clientes, _ = _obtener_datos_frescos() # Solo trae los datos de clientes
    # Manda a ejecutar tu análisis de edades. Le mandamos graficar=False para que no genere imágenes
    resumen = segmentar_por_edad(clientes, graficar=False) 
    
    # Se arma un diccionario estándar para devolverle al Servidor MCP
    return {
        "exito": True, # Bandera para que la IA sepa que no hubo errores
        "segmento": "Rango de Edad", # Nombre de la operación
        "datos": _registros_json(resumen), # Transforma tu resumen Pandas a JSON y se lo da a la IA
        "nota": "Los rangos de edad están definidos en intervalos (ej. 18-25, 26-35, etc.)." # Pista para la IA
    }

def consultar_segmentacion_genero() -> dict[str, Any]:
    """Obtiene el resumen de compras comparado por género."""
    clientes, _ = _obtener_datos_frescos() # Jala los datos
    resumen = comportamiento_por_genero(clientes, graficar=False) # Ejecuta tu código de género sin graficar
    
    return {
        "exito": True,
        "segmento": "Género",
        "datos": _registros_json(resumen), # Retorna los datos como texto JSON
        "nota": "Género 1 fue mapeado a Femenino y Género 0 a Masculino." # Le explica a la IA qué significaba el 0 y 1
    }

def consultar_impacto_boletines_vales() -> dict[str, Any]:
    """Obtiene los patrones de compra basados en el uso de vales y boletines."""
    _, compras = _obtener_datos_frescos() # En este caso descartamos 'clientes' (con el '_') y nos quedamos con 'compras'
    resumen = impacto_boletines_vales(compras, graficar=False) # Ejecuta tu lógica sobre la tabla compras
    
    return {
        "exito": True,
        "segmento": "Uso de Boletín y Vale",
        "datos": _registros_json(resumen), # Envía la respuesta formateada a la IA
        "nota": "Clasifica las compras según si se usó solo boletín, solo vale, ambos o ninguno (Normal)." # Ayuda de contexto
    }
