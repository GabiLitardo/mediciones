# proc_temp.py
import numpy as np
import streamlit as st
from lector_archivos import cargar_medicion_temperatura

@st.cache_data
def obtener_analisis_temperatura(lista_dispositivos, corrientes_normalizadas, lista_temperaturas):
    """
    Procesa las mediciones de temperatura y retorna dos diccionarios planos unificados:
    - 'i_vs_t': {"disp @ corr uA": {"x": array_temp, "y": array_corriente}}
    - 'alpha_vs_i': {"disp": {"x": array_corrientes, "y": array_alphas}}
    """
    i_vs_t = {}
    alpha_vs_i = {}

    for disp in lista_dispositivos:
        x_alpha = []
        y_alpha = []

        for corr in corrientes_normalizadas:
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

            if len(temps_aux) >= 2:
                indices_orden = np.argsort(temps_aux)
                x_ordenado = np.array(temps_aux)[indices_orden]
                y_ordenado = np.array(corrientes_aux)[indices_orden]

                coefs = np.polyfit(x_ordenado, y_ordenado, deg=1)

                tag = f"{disp} @ {corr} uA"
                i_vs_t[tag] = {
                    "x": x_ordenado,
                    "y": y_ordenado
                }

                x_alpha.append(float(corr))
                y_alpha.append(coefs[0])

        if x_alpha:
            idx = np.argsort(x_alpha)
            alpha_vs_i[disp] = {
                "x": np.array(x_alpha)[idx],
                "y": np.array(y_alpha)[idx]
            }

    return {
        "i_vs_t": i_vs_t,
        "alpha_vs_i": alpha_vs_i
    }