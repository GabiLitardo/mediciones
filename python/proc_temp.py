# proc_temp.py
import re
import numpy as np
import streamlit as st
from pathlib import Path

def _obtener_archivo_mas_reciente(disp, corr, temp):
    """
    Busca en el sistema de archivos todas las mediciones para un dispositivo, 
    corriente y temperatura, devolviendo únicamente la de mayor versión M.
    """
    directorio_base = Path(".")
    patron_uA = f"*_UTN_DIE4_{disp}_{corr}uA_{temp}_M*.csv"
    patron_u = f"*_UTN_DIE4_{disp}_{corr}u_{temp}_M*.csv"
    
    archivos = list(directorio_base.glob(f"**/{patron_uA}")) + list(directorio_base.glob(f"**/{patron_u}"))
    
    if not archivos:
        return None

    def extraer_m(path):
        match = re.search(r"_M(\d+)\.csv$", path.name)
        return int(match.group(1)) if match else -1

    return max(archivos, key=extraer_m)

@st.cache_data
def obtener_datos_I_vs_T(lista_dispositivos, corrientes_nominales, lista_temperaturas):
    """
    Obtiene los datos de corriente en función de la temperatura y calcula el coeficiente térmico.
    """
    resultado = {}
    
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            temps_aux = []
            corrientes_aux = []
            
            for temp in lista_temperaturas:
                archivo_reciente = _obtener_archivo_mas_reciente(disp, corr, temp)
                
                if archivo_reciente is not None:
                    datos = np.genfromtxt(archivo_reciente, delimiter=',', skip_header=1, usecols=(3, 4))
                    v_drain = datos[:, 0]
                    i_drain = datos[:, 1]
                    
                    idx_vd = np.argmin(np.abs(v_drain - (-4.5)))
                    i_en_v5 = np.abs(i_drain[idx_vd]) * 1e6
                    
                    temps_aux.append(float(temp))
                    corrientes_aux.append(i_en_v5)
            
            if temps_aux:
                indices_orden = np.argsort(temps_aux)
                x_ordenado = np.array(temps_aux)[indices_orden]
                y_ordenado = np.array(corrientes_aux)[indices_orden]
                
                coefs = np.polyfit(x_ordenado, y_ordenado, deg=1)
                
                resultado[disp][corr] = {
                    "x": x_ordenado,
                    "y": y_ordenado,
                    "alpha": coefs[0]
                }
                
    return resultado