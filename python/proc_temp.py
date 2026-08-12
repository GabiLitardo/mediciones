# proc_temp.py
import numpy as np
import streamlit as st
from lector_archivos import cargar_medicion_temperatura

@st.cache_data
def obtener_analisis_temperatura(lista_dispositivos, corrientes_nominales, temperaturas):
    """
    Procesa las mediciones de temperatura y retorna estructuras aplanadas unificadas:
    - 'i_vs_t': familias de curvas I_D vs T para cada (dispositivo, corriente).
    - 'alpha_vs_i': coeficiente térmico alpha vs Corriente Nominal por dispositivo.
    """
    i_vs_t = {}
    alpha_vs_i = {}

    for disp in lista_dispositivos:
        x_alpha = []
        y_alpha = []

        for corr in corrientes_nominales:
            temps_medidas = []
            corrientes_medidas = []

            for temp in temperaturas:
                datos = cargar_medicion_temperatura(disp, corr, temp)
                if datos is not None:
                    # Se toma el valor promedio de la medición en ese escalón
                    t_prom = np.mean(datos[:, 0]) if datos.ndim > 1 else datos[0]
                    i_prom = np.mean(datos[:, 1]) if datos.ndim > 1 else datos[1]
                    temps_medidas.append(t_prom)
                    corrientes_medidas.append(np.abs(i_prom) * 1e6)

            if len(temps_medidas) > 1:
                temps_arr = np.array(temps_medidas)
                corrientes_arr = np.array(corrientes_medidas)

                # Fit lineal para obtener el coeficiente térmico alpha (pendiente)
                coefs = np.polyfit(temps_arr, corrientes_arr, deg=1)
                alpha = coefs[0]

                tag = f"{disp} @ {corr} uA"
                i_vs_t[tag] = {"x": temps_arr, "y": corrientes_arr}

                x_alpha.append(float(corr))
                y_alpha.append(alpha)

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