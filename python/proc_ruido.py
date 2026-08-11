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

def procesar_matriz_ruido(datos):
    tiempo_s = datos[:, 0]
    corriente_uA = np.abs(datos[:, 1]) * 1e6
    resistencia = datos[:, 2]
    temperatura_C = convertir_r_a_temp_steinhart(resistencia)

    coefs_T = np.polyfit(tiempo_s, temperatura_C, deg=9)
    temperatura_fit_C = np.polyval(coefs_T, tiempo_s)

    coefs_I = np.polyfit(temperatura_C, corriente_uA, deg=1)
    corriente_fit_uA = np.polyval(coefs_I, temperatura_C)
    
    i_ruido_neto_uA = corriente_uA - corriente_fit_uA

    return {
        "tiempo_s": tiempo_s,
        "corriente_uA": corriente_uA,
        "temperatura_C": temperatura_C,
        "temperatura_fit_C": temperatura_fit_C,
        "corriente_fit_uA": corriente_fit_uA,
        "i_ruido_neto_uA": i_ruido_neto_uA
    }

@st.cache_data
def obtener_analisis_ruido_completo(lista_dispositivos, corrientes_nominales, es_larga=False):
    """
    Procesa las mediciones en una sola pasada y retorna todas las estructuras 
    necesarias para los gráficos de ruido, evoluciones y temperatura.
    """
    datos_procesados = {}
    
    for disp in lista_dispositivos:
        datos_procesados[disp] = {}
        for corr in corrientes_nominales:
            datos_matriz = cargar_medicion_ruido(disp, corr, es_larga)
            if datos_matriz is not None:
                datos_procesados[disp][corr] = procesar_matriz_ruido(datos_matriz)
                
    return datos_procesados

def extraer_estructuras_ruido(datos_procesados, restar_deriva=True):
    """
    Sustrae las series específicas para cada gráfico sin recomputar ajustes.
    """
    evos = {}
    evos_temp = {}
    i_vs_t = {}
    std_ruido = {}

    for disp, corrientes_dict in datos_procesados.items():
        evos[disp] = {}
        evos_temp[disp] = {}
        i_vs_t[disp] = {}
        std_list = []
        corrientes_validas = []

        for corr, datos in corrientes_dict.items():
            y_val = datos["i_ruido_neto_uA"] if restar_deriva else datos["corriente_uA"]
            evos[disp][corr] = {"x": datos["tiempo_s"], "y": y_val}
            
            evos_temp[disp][corr] = {
                "x": datos["tiempo_s"],
                "y": datos["temperatura_C"],
                "y_fit": datos["temperatura_fit_C"]
            }
            
            i_vs_t[disp][corr] = {
                "x": datos["temperatura_C"],
                "y": datos["corriente_uA"],
                "y_fit": datos["corriente_fit_uA"]
            }
            
            # Cálculo de desviación estándar del ruido en nA
            std_val = np.std(datos["i_ruido_neto_uA"] * 1000.0, ddof=1) if restar_deriva else np.std(datos["corriente_uA"] * 1000.0, ddof=1)
            std_list.append(std_val)
            corrientes_validas.append(float(corr))

        std_ruido[disp] = {
            "x": np.array(corrientes_validas),
            "y": np.array(std_list)
        }

    return evos, evos_temp, i_vs_t, std_ruido