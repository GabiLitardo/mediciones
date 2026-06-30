# ruido.py
import numpy as np
import os
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
    """Procesa un archivo individual normalizando sus separadores mixtos."""
    # Buscamos la ruta usando tu lógica (asumiendo que matchear_archivos busca por nombre)
    # Si matchear_archivos no te da la ruta sino la matriz, vamos a tener que buscar la ruta.
    # Como matchear_archivos adentro usa la ruta, hagamos la búsqueda de la ruta directo:
    
    directorio_base = "."
    ruta_completa = None
    for root, dirs, files in os.walk(directorio_base):
        if nombre_archivo in files:
            ruta_completa = os.path.join(root, nombre_archivo)
            break
            
    if not ruta_completa:
        return None
        
    try:
        # Reemplazamos la ensalada de separadores abriendo el archivo en memoria
        with open(ruta_completa, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            
        # Filtramos el encabezado (primeras 2 líneas) y normalizamos los tabs \t a espacios
        lineas_datos = [linea.replace("\t", " ") for linea in lineas[2:]]
        
        # np.loadtxt ahora lee los strings limpios con separador de espacios puros
        datos = np.loadtxt(lineas_datos)
        
        if len(datos.shape) < 2 or datos.shape[1] < 3:
            return None

        tiempo = datos[:, 0]
        corriente_uA = np.abs(datos[:, 1]) * 1e6  # Módulo en uA
        resistencia = datos[:, 2]                 # Columna del termistor
        
        # 1. Convertimos a temperatura (Steinhart-Hart)
        temperatura_C = convertir_r_a_temp_steinhart(resistencia)
        
        # 2. Ajuste lineal (Corriente vs Temperatura) para la deriva
        coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
        corriente_tendencia = np.polyval(coefs, temperatura_C)
        
        # 3. Restamos la deriva térmica
        corriente_ruido_uA = corriente_uA - corriente_tendencia
        
        # 4. Desvío estándar muestral convertido a nanoamperios (nA)
        sigma_nA = np.std(corriente_ruido_uA, ddof=1) * 1000.0
        return sigma_nA
        
    except Exception as e:
        # Si el archivo está incompleto o se está escribiendo ahora, da error y devuelve None de forma segura
        return None

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
