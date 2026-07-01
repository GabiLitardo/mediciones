# proc_sens.py
import numpy as np
import streamlit as st
from proc_evo import obtener_datos_crudos_tanda

factores_normalizacion = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}

@st.cache_data
def calcular_fit_polinomico_cached(disp_name, tipo_tanda, tiempos_list, corrientes_list):
    try:
        coeficientes = np.polyfit(tiempos_list, corrientes_list, deg=4)
        return coeficientes.tolist()
    except:
        return None

def procesar_sensibilidad(lista_dispositivos, tipo_tanda, normalizado=True, analitico=True):
    """Calcula los arreglos X e Y para los gráficos de sensibilidad de manera unificada."""
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda)
    resultado = {}
    
    for disp, datos in datos_crudos.items():
        tiempos = datos["tiempos"]
        corrientes = datos["valores"]
        factor = factores_normalizacion.get(disp, 1.0) if normalizado else 1.0
        corrientes_proc = corrientes / factor
        
        coefs = None
        if analitico:
            llave_cache = f"{tipo_tanda}" if normalizado else f"{tipo_tanda}_abs"
            coefs = calcular_fit_polinomico_cached(disp, llave_cache, tiempos.tolist(), corrientes_proc.tolist())
            
        if coefs is not None and analitico:
            a, b, c, d, e = coefs
            t_cont = np.linspace(tiempos.min(), tiempos.max(), 200)
            eje_y = np.abs(4*a*(t_cont**3) + 3*b*(t_cont**2) + 2*c*t_cont + d)
            eje_x = a*(t_cont**4) + b*(t_cont**3) + c*(t_cont**2) + d*t_cont + e
            resultado[disp] = {"x": eje_x, "y": eje_y, "es_lineal": True}
        else:
            eje_x, eje_y = [], []
            for k in range(len(corrientes_proc) - 1):
                dt = tiempos[k+1] - tiempos[k]
                if dt > 0:
                    tasa = np.abs(corrientes_proc[k+1] - corrientes_proc[k]) / dt
                    promedio = (corrientes_proc[k+1] + corrientes_proc[k]) / 2.0
                    eje_y.append(tasa)
                    eje_x.append(promedio)
            if eje_x:
                resultado[disp] = {"x": np.array(eje_x), "y": np.array(eje_y), "es_lineal": False}
    return resultado
