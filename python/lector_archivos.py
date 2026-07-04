# lector_archivos.py
import os
from pathlib import Path
import numpy as np
import streamlit as st

def matchear_archivos(nombre_archivo_generico, tipo_medicion="iv"):
    """
    Busca archivos recursivamente y devuelve una lista con sus matrices de datos.
    Acepta tipo_medicion="iv" o tipo_medicion="ruido".
    """
    directorio_base = Path(".")
    lista_de_rutas = directorio_base.glob("**/" + nombre_archivo_generico)
    mediciones = []
    for ruta_archivo in lista_de_rutas:
        if tipo_medicion == "ruido":
            medicion = np.genfromtxt(ruta_archivo, delimiter='\t', skip_header=5, usecols=(0, 1, 2), encoding="cp1252")
        else:
            medicion = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
        mediciones.append(medicion)  
    if len(mediciones) == 0:
        print(nombre_archivo_generico)
    return mediciones
