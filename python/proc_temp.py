# proc_temp.py
import numpy as np
import streamlit as st
from lector_archivos import cargar_medicion_temperatura

@st.cache_data
def obtener_datos_I_vs_T(lista_dispositivos, corrientes_nominales, lista_temperaturas):
    resultado = {}
    
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            temps_aux = []
            corrientes_aux = []
            
            for temp in lista_temperaturas:
                datos = cargar_medicion_temperatura(disp, corr, temp)
                
                if datos is not None:
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