# proc_ruido.py
import numpy as np
from lector_archivos import matchear_archivos_ruido

A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    ln_R = np.log(resistencia)
    return (1.0 / (A_SH + B_SH * ln_R + C_SH * (ln_R ** 3))) - 273.15

def calcular_desvio_archivo(nombre_archivo):
    """Remueve la deriva térmica lineal del archivo de ruido y extrae el desvío AC neto."""
    lista_mediciones = matchear_archivos_ruido(nombre_archivo)
    
    if not lista_mediciones:
        return None
        
    datos = lista_mediciones[0]
    
    if datos.size == 0 or len(datos.shape) < 2 or datos.shape[1] < 3:
        return None

    try:
        corriente_uA = np.abs(datos[:, 1]) * 1e6
        resistencia = datos[:, 2]
        
        temperatura_C = convertir_r_a_temp_steinhart(resistencia)
        coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
        corriente_tendencia = np.polyval(coefs, temperatura_C)
        
        corriente_ruido_uA = corriente_uA - corriente_tendencia
        
        if len(corriente_ruido_uA) < 2:
            return None
            
        return np.std(corriente_ruido_uA, ddof=1) * 1000.0
    except:
        return None
