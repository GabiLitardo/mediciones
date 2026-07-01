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
    """Busca un archivo de ruido .txt y extrae sus columnas usando tabulaciones."""
    # Buscamos el archivo recursivamente en el repo
    ruta = next(Path(".").glob(f"**/{nombre_buscar}"), None)
    
    if ruta is None:
        return None
        
    try:
        datos = np.genfromtxt(ruta, delimiter='\t', skip_header=5, usecols=(0, 1, 2), encoding="cp1252")
        return datos if datos.size > 0 else None
    except:
        return None
