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
def obtener_analisis_ruido(lista_dispositivos, corrientes_nominales, es_larga=False, restar_deriva=True):
    """
    Retorna la estructura unificada de 2 niveles:
    {
        disp: {
            corr: {
                "tiempo_s": array,
                "i_ruido_uA": array,
                "temp_C": array,
                "temp_fit_C": array,
                "i_fit_uA": array,
                "std_nA": float
            }
        }
    }
    """
    resultado = {}

    for disp in lista_dispositivos:
        d_corr = {}

        for corr in corrientes_nominales:
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
            std_val = np.std(y_val * 1000.0, ddof=1)

            d_corr[corr] = {
                "tiempo_s": tiempo_s,
                "i_ruido_uA": y_val,
                "temp_C": temperatura_C,
                "temp_fit_C": temperatura_fit_C,
                "i_fit_uA": corriente_fit_uA,
                "std_nA": std_val
            }

        if d_corr:
            resultado[disp] = d_corr

    return resultado