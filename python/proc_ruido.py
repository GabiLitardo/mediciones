# proc_ruido.py
import numpy as np
from lector_archivos import matchear_archivos

# Definición de variables
A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    """
    Calcula la temperatura asociada a la resistencia d eun termistor con la fórmula de Steinhart-Hart

    Args:
        resistencia (float): Valor de resistencia

    Returns:
        temperatura (float): Devuelve la temperatura asociada al valor de resistencia del termistor
    """
    ln_R = np.log(resistencia)
    return (1.0 / (A_SH + B_SH * ln_R + C_SH * (ln_R ** 3))) - 273.15

def obtener_ruido_neto_archivo(nombre_archivo, restar_deriva):
    """
    Calcula 
    """
    lista_mediciones = matchear_archivos(nombre_archivo, tipo_medicion="ruido")
    if lista_mediciones == None:
        print(nombre_archivo)
    datos = lista_mediciones[0]
    tiempo_s = datos[:, 0]
    corriente_uA = np.abs(datos[:, 1]) * 1e6
    resistencia = datos[:, 2]
    temperatura_C = convertir_r_a_temp_steinhart(resistencia)
    coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
    corriente_tendencia = np.polyval(coefs, temperatura_C)
    corriente_ruido = (corriente_uA - corriente_tendencia)

    if restar_deriva:
        return tiempo_s, corriente_ruido
    else:
        return tiempo_s, corriente_uA

def obtener_evolucion_ruido(lista_dispositivos, corrientes_nominales, es_larga, restar_deriva = True):
    """
    Calcula
    """
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            if es_larga:
                nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1_LARGA.txt"
            else:
                nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1.txt"            
            tiempo_s, corriente_ruido = obtener_ruido_neto_archivo(nombre_archivo, restar_deriva)
            resultado[disp][corr] = {"x": tiempo_s, "y": corriente_ruido}
            
    return resultado

def procesar_ruido(lista_dispositivos, corrientes_nominales, es_larga = False, restar_deriva = True):
    resultado = {}
    todas_las_evos = obtener_evolucion_ruido(lista_dispositivos, corrientes_nominales, es_larga, restar_deriva)
    for disp in lista_dispositivos:    
        resultado[disp] = {
            "x": np.array([float(corr) for corr in corrientes_nominales]),
            "y": np.array([np.std(todas_las_evos[disp][corr]["y"] * 1000, ddof=1) for corr in corrientes_nominales])
        }
    return resultado

def obtener_evolucion_temperatura_ruido(lista_dispositivos, corrientes_nominales, es_larga=False):
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            if es_larga:
                nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1_LARGA.txt"
            else:
                nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1.txt"
            
            lista_mediciones = matchear_archivos(nombre_archivo, tipo_medicion="ruido")
            if lista_mediciones:
                datos = lista_mediciones[0]
                tiempo_s = datos[:, 0]
                resistencia = datos[:, 2]
                temperatura_C = convertir_r_a_temp_steinhart(resistencia)
                resultado[disp][corr] = {"x": tiempo_s, "y": temperatura_C}
            
    return resultado

def obtener_corriente_vs_temperatura_ruido(lista_dispositivos, corrientes_nominales, es_larga=False):
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            if es_larga:
                nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1_LARGA.txt"
            else:
                nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1.txt"
            
            lista_mediciones = matchear_archivos(nombre_archivo, tipo_medicion="ruido")
            if lista_mediciones:
                datos = lista_mediciones[0]
                
                corriente_uA = np.abs(datos[:, 1]) * 1e6
                resistencia = datos[:, 2]
                temperatura_C = convertir_r_a_temp_steinhart(resistencia)
                
                # Ajuste lineal (grado 1)
                coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
                corriente_fit = np.polyval(coefs, temperatura_C)
                
                resultado[disp][corr] = {
                    "x": temperatura_C,
                    "y": corriente_uA,
                    "y_fit": corriente_fit
                }            
    return resultado
    
