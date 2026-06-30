# lector_archivos.py
import os
from pathlib import Path
import numpy as np
import streamlit as st

def matchear_archivos_iv(nombre_archivo_generico):
    """Busca un archivo de curvas I-V recursivamente y devuelve su matriz de datos."""
    directorio_base = Path(".")
    lista_de_rutas = directorio_base.glob("**/" + nombre_archivo_generico)
    mediciones = []
    for ruta_archivo in lista_de_rutas:
        medicion = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
        mediciones.append(medicion)
    return mediciones

def matchear_archivos_ruido(nombre_buscar):
    """Busca un archivo de ruido .txt y extrae sus 5 columnas limpias."""
    directorio_base = "."
    for root, dirs, files in os.walk(directorio_base):
        if nombre_buscar in files:
            ruta_completa = os.path.join(root, nombre_buscar)
            try:
                with open(ruta_completa, "r", encoding="cp1252") as f:
                    lineas = f.readlines()
                
                lineas_datos = []
                for linea in lineas:
                    l_limpia = linea.strip()
                    # Verificamos que no esté vacía y que empiece con número o signo menos
                    if l_limpia and (l_limpia[0].isdigit() or l_limpia[0] == '-'):
                        lineas_datos.append(l_limpia)
                
                if not lineas_datos:
                    return None
                    
                datos = np.loadtxt(lineas_datos)
                return datos
            except Exception as error_lectura:
                return None
    return None
