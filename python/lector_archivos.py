from pathlib import Path
import numpy as np

def matchear_archivos(nombre_buscar, tipo_medicion="iv"):
    """
    Busca archivos de forma recursiva en el directorio y subcarpetas,
    devolviendo una lista con las matrices de datos cargadas.
    """
    directorio_base = Path(".")
    rutas_encontradas = directorio_base.glob("**/" + nombre_buscar)
    
    mediciones = []
    
    for ruta in rutas_encontradas:
        if tipo_medicion == "ruido":
            datos = np.genfromtxt(ruta, delimiter='\t', skip_header=5, usecols=(0, 1, 2), encoding="cp1252")
        elif tipo_medicion == "temperatura":
            datos = np.genfromtxt(ruta, delimiter=',', skip_header=1, usecols=(3, 4))
        else:
            datos = np.genfromtxt(ruta, skip_header=2, usecols=(0, 1), encoding="cp1252")
            
        mediciones.append(datos)
        
    return mediciones
