# proc_ruido.py
import numpy as np
from lector_archivos import matchear_archivos

A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    ln_R = np.log(resistencia)
    return (1.0 / (A_SH + B_SH * ln_R + C_SH * (ln_R ** 3))) - 273.15

def obtener_ruido_neto_archivo(nombre_archivo):
    lista_mediciones = matchear_archivos(nombre_archivo, tipo_medicion="ruido")
    datos = lista_mediciones[0]
    tiempo_s = datos[:, 0]
    corriente_uA = np.abs(datos[:, 1]) * 1e6
    resistencia = datos[:, 2]
    temperatura_C = convertir_r_a_temp_steinhart(resistencia)
    coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
    corriente_tendencia = np.polyval(coefs, temperatura_C)
    corriente_ruido_nA = (corriente_uA - corriente_tendencia) * 1000.0
    
    return tiempo_s, corriente_ruido_nA

def obtener_evolucion_ruido(lista_dispositivos, corrientes_nominales, es_larga):
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            if es_larga:
                nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1_LARGA.txt"
            else:
                nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1.txt"            
            tiempo_s, corriente_ruido_nA = obtener_ruido_neto_archivo(nombre_archivo)
            resultado[disp][corr] = {"x": tiempo_s, "y": corriente_ruido_nA}
            
    return resultado

def procesar_ruido(lista_dispositivos, corrientes_nominales, es_larga = False):
    factores_normalizacion = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}
    resultado = {}
    todas_las_evos = obtener_evolucion_ruido(lista_dispositivos, corrientes_nominales, es_larga)
    for disp in lista_dispositivos:    
        resultado[disp] = {
            "x": np.array([float(corr) for corr in corrientes_nominales]),
            "y": np.array([np.std(todas_las_evos[disp][corr]["y"], ddof=1) for corr in corrientes_nominales])
        }
    return resultado
