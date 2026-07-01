# proc_ruido.py
import numpy as np
from lector_archivos import matchear_archivos

A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    ln_R = np.log(resistencia)
    return (1.0 / (A_SH + B_SH * ln_R + C_SH * (ln_R ** 3))) - 273.15

def calcular_desvio_archivo(nombre_archivo):
    lista_mediciones = matchear_archivos(nombre_archivo, tipo_medicion="ruido")
    datos = lista_mediciones[0]
    corriente_uA = np.abs(datos[:, 1]) * 1e6
    resistencia = datos[:, 2]
    
    temperatura_C = convertir_r_a_temp_steinhart(resistencia)
    coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
    corriente_tendencia = np.polyval(coefs, temperatura_C)
    
    corriente_ruido_uA = corriente_uA - corriente_tendencia
        
    return np.std(corriente_ruido_uA, ddof=1) * 1000.0

def procesar_ruido(lista_dispositivos, corrientes_nominales):
    resultado = {}
    for disp in lista_dispositivos:
        eje_x = []
        eje_y = []
        for corr in corrientes_nominales:
            nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1.txt"
            sigma = calcular_desvio_archivo(nombre_archivo)
            
            eje_x.append(float(corr))
            eje_y.append(sigma)
            
        resultado[disp] = {"x": np.array(eje_x), "y": np.array(eje_y)}

    return resultado
