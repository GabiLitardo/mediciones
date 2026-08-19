# proc_ruido.py
import numpy as np
import streamlit as st
from lector_archivos import cargar_medicion_ruido

A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    ln_R = np.log(resistencia)
    return (1.0 / (A_SH + B_SH * ln_R + C_SH * (ln_R ** 3))) - 273.15

@st.cache_data
def obtener_analisis_ruido_completo(lista_dispositivos, corrientes_normalizadas, es_larga=False, restar_deriva=True):
    """
    Retorna cuatro diccionarios planos unificados con formato:
    {"Etiqueta Leyenda": {"x": array, "y": array}}
    """
    evos = {}
    evos_temp = {}
    i_vs_t = {}
    std_ruido = {}

    for disp in lista_dispositivos:
        std_list = []
        corrientes_validas = []

        for corr in corrientes_normalizadas:
            datos_matriz = cargar_medicion_ruido(disp, corr, es_larga)
            if datos_matriz is None:
                continue

            tiempo_s = datos_matriz[:, 0]
            corriente_uA = np.abs(datos_matriz[:, 1]) * 1e6
            resistencia = datos_matriz[:, 2]
            temperatura_C = convertir_r_a_temp_steinhart(resistencia)

            coefs_T = np.polyfit(tiempo_s, temperatura_C, deg=9)
            temperatura_fit_C = np.polyval(coefs_T, tiempo_s)

            coefs_I = np.polyfit(temperatura_C, corriente_uA, deg=1)
            corriente_fit_uA = np.polyval(coefs_I, temperatura_C)
            i_ruido_neto_uA = corriente_uA - corriente_fit_uA

            y_val = i_ruido_neto_uA if restar_deriva else corriente_uA

            tag = f"{disp} @ {corr} uA"
            tag_fit = f"{disp} @ {corr} uA (Fit)"

            # 1. Evolución del ruido
            evos[tag] = {"x": tiempo_s, "y": y_val}

            # 2. Evolución de temperatura (medida y fit)
            evos_temp[tag] = {"x": tiempo_s, "y": temperatura_C}
            evos_temp[tag_fit] = {"x": tiempo_s, "y": temperatura_fit_C}

            # 3. Corriente vs Temperatura (medida y fit)
            i_vs_t[tag] = {"x": temperatura_C, "y": corriente_uA}
            i_vs_t[tag_fit] = {"x": temperatura_C, "y": corriente_fit_uA}

            std_val = np.std(y_val * 1000.0, ddof=1)
            std_list.append(std_val)
            corrientes_validas.append(float(corr))

        if corrientes_validas:
            std_ruido[disp] = {
                "x": np.array(corrientes_validas),
                "y": np.array(std_list)
            }

    return {
        "evos": evos,
        "evos_temp": evos_temp,
        "i_vs_t": i_vs_t,
        "std_ruido": std_ruido
    }