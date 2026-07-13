from pathlib import Path
import numpy as np
import os
import streamlit as st

def matchear_archivos(nombre_archivo_generico, tipo_medicion="iv"):
    """
    Busca archivos recursivamente y devuelve una lista con sus matrices de datos.
    Acepta tipo_medicion="iv", tipo_medicion="ruido" o tipo_medicion="temperatura".
    """
    directorio_base = Path(".")
    lista_de_rutas = directorio_base.glob("**/" + nombre_archivo_generico)
    mediciones = []
    for ruta_archivo in lista_de_rutas:
        if tipo_medicion == "ruido":
            medicion = np.genfromtxt(ruta_archivo, delimiter='\t', skip_header=5, usecols=(0, 1, 2), encoding="cp1252")
        elif tipo_medicion == "temperatura":
            medicion = np.genfromtxt(ruta_archivo, delimiter=',', skip_header=1, usecols=(3, 4))
        else:
            medicion = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
        mediciones.append(medicion)  
    return mediciones
