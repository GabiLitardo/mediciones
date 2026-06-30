# ruido.py
import numpy as np
import streamlit as st
from procesamiento import matchear_archivos

# Constantes de Steinhart-Hart
A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    """Convierte la columna de resistencia del termistor a temperatura en °C."""
    ln_R = np.log(resistencia)
    inverso_T = A_SH + B_SH * ln_R + C_SH * (ln_R ** 3)
    temp_kelvin = 1.0 / inverso_T
    return temp_kelvin - 273.15

def calcular_desvio_archivo(nombre_archivo):
    """Procesa un archivo individual y devuelve su desvío estándar en nA."""
    # Le pasamos el delimiter='\t' para que no colapse las columnas
    datos_lista = matchear_archivos(nombre_archivo)
    if not datos_lista:
        return None
        
    datos = datos_lista[0]
    
    # Verificación de seguridad: si no es bidimensional, forzamos el split por tabulación
    if len(datos.shape) < 2:
        return None

    tiempo = datos[:, 0]
    corriente_uA = np.abs(datos[:, 1]) * 1e6  # Módulo en microamperios
    resistencia = datos[:, 2]                 # Columna del termistor 
    
    # 1. Convertimos a temperatura
    temperatura_C = convertir_r_a_temp_steinhart(resistencia)
    
    # 2. Ajuste lineal (Corriente vs Temperatura) para la deriva
    coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
    corriente_tendencia = np.polyval(coefs, temperatura_C)
    
    # 3. Restamos la deriva térmica
    corriente_ruido_uA = corriente_uA - corriente_tendencia
    
    # 4. Desvío estándar muestral convertido a nanoamperios (nA)
    sigma_nA = np.std(corriente_ruido_uA, ddof=1) * 1000.0
    return sigma_nA

def mostrar_resumen_ruido():
    """
    Barre todos los dispositivos y corrientes nominales, calcula sus desvíos
    y muestra una tabla/resumen de los datos calculados en Streamlit.
    """
    st.subheader("Resumen de Desvío Estándar del Ruido (nA)")
    
    lista_dispositivos = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_nominales = [100, 150, 200, 250, 350]
    
    # Estructura para almacenar los datos en formato de diccionario
    resultados = {}
    
    for disp in lista_dispositivos:
        resultados[disp] = {}
        for curr in corrientes_nominales:
            nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{curr}u_M1.txt"
            
            sigma = calcular_desvio_archivo(nombre_archivo)
            
            if sigma is not None:
                resultados[disp][f"{curr} uA"] = f"{sigma:.2f} nA"
            else:
                resultados[disp][f"{curr} uA"] = "Falta medición"
                
    # Le mandamos el diccionario directo a Streamlit para verlo en limpio
    st.write(resultados)
