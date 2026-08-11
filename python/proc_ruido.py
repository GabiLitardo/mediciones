# proc_ruido.py
import numpy as np
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

def obtener_evolucion_ruido(lista_dispositivos, corrientes_nominales, es_larga=False, restar_deriva=True):
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            datos_matriz = cargar_medicion_ruido(disp, corr, es_larga)
            if datos_matriz is not None:
                datos = procesar_matriz_ruido(datos_matriz)
                y_val = datos["i_ruido_neto_uA"] if restar_deriva else datos["corriente_uA"]
                resultado[disp][corr] = {"x": datos["tiempo_s"], "y": y_val}

    return resultado

def obtener_evolucion_temperatura_ruido(lista_dispositivos, corrientes_nominales, es_larga=False):
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            datos_matriz = cargar_medicion_ruido(disp, corr, es_larga)
            if datos_matriz is not None:
                datos = procesar_matriz_ruido(datos_matriz)
                resultado[disp][corr] = {
                    "x": datos["tiempo_s"], 
                    "y": datos["temperatura_C"],
                    "y_fit": datos["temperatura_fit_C"]
                }

    return resultado

def obtener_corriente_vs_temperatura_ruido(lista_dispositivos, corrientes_nominales, es_larga=False):
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            datos_matriz = cargar_medicion_ruido(disp, corr, es_larga)
            if datos_matriz is not None:
                datos = procesar_matriz_ruido(datos_matriz)
                resultado[disp][corr] = {
                    "x": datos["temperatura_C"],
                    "y": datos["corriente_uA"],
                    "y_fit": datos["corriente_fit_uA"]
                }

    return resultado

def procesar_ruido(lista_dispositivos, corrientes_nominales, es_larga=False, restar_deriva=True):
    resultado = {}
    todas_las_evos = obtener_evolucion_ruido(lista_dispositivos, corrientes_nominales, es_larga, restar_deriva)

    for disp in lista_dispositivos:
        std_list = []
        for corr in corrientes_nominales:
            if corr in todas_las_evos[disp]:
                std_val = np.std(todas_las_evos[disp][corr]["y"] * 1000.0, ddof=1)
                std_list.append(std_val)

        resultado[disp] = {
            "x": np.array([float(corr) for corr in corrientes_nominales]),
            "y": np.array(std_list)
        }

    return resultado