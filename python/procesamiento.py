# procesamiento.py
from pathlib import Path
import numpy as np


def matchear_archivos(nombre_archivo_generico):
    directorio_base = Path(".")
    lista_de_rutas = directorio_base.glob("**/" + nombre_archivo_generico)
    mediciones = []
    for ruta_archivo in lista_de_rutas:
        medicion = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1, 2), encoding="cp1252")
        mediciones.append(medicion)
    return mediciones
