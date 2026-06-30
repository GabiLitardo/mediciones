# ruido.py
import os
import numpy as np
import streamlit as st

# Constantes de Steinhart-Hart para el termistor
A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    """Convierte la columna de resistencia del termistor a temperatura en °C."""
    ln_R = np.log(resistencia)
    inverso_T = A_SH + B_SH * ln_R + C_SH * (ln_R ** 3)
    temp_kelvin = 1.0 / inverso_T
    return temp_kelvin - 273.15

def matchear_archivos_ruido(nombre_buscar):
    """
    Busca el archivo en el repositorio, limpia los fines de línea y 
    levanta las 5 columnas completas de forma nativa sin trabarse.
    """
    directorio_base = "."
    for root, dirs, files in os.walk(directorio_base):
        if nombre_buscar in files:
            ruta_completa = os.path.join(root, nombre_buscar)
            
            try:
                # Abrimos con la codificación de Windows que se banca la "ó"
                with open(ruta_completa, "r", encoding="cp1252") as f:
                    lineas = f.readlines()
                
                # Filtramos las líneas de texto para quedarnos SOLO con las numéricas
                lineas_datos = []
                for linea in lineas:
                    l_limpia = linea.strip()
                    # Si la línea empieza con un número o signo menos, es un dato numérico
                    if l_limpia and (l_limpia[0].isdigit() or l_limpia[0] == '-'):
                        lineas_datos.append(l_limpia)
                
                # np.loadtxt procesa las 5 columnas de forma impecable
                datos = np.loadtxt(lineas_datos)
                return datos
                
            except Exception as error_lectura:
                st.error(f"⚠️ Error leyendo {nombre_buscar}: {error_lectura}")
                return None
                
    return None

def calcular_desvio_archivo(nombre_archivo):
    """Procesa un archivo de ruido, remueve la deriva térmica y devuelve el desvío en nA."""
    datos = matchear_archivos_ruido(nombre_archivo)
    
    if datos is None or datos.size == 0:
        return None
        
    if len(datos.shape) < 2 or datos.shape[1] < 3:
        return None

    # Mapeo limpio de las columnas numéricas reales
    tiempo = datos[:, 0]
    corriente_uA = np.abs(datos[:, 1]) * 1e6  # Pasamos ID a módulo en uA
    resistencia = datos[:, 2]                 # Columna del termistor
    
    # 1. Convertimos resistencia a temperatura (°C)
    temperatura_C = convertir_r_a_temp_steinhart(resistencia)
    
    # 2. Ajuste lineal (Corriente vs Temperatura) para extraer la deriva térmica
    coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
    corriente_tendencia = np.polyval(coefs, temperatura_C)
    
    # 3. Restamos la tendencia térmica para aislar el ruido AC puro
    corriente_ruido_uA = corriente_uA - corriente_tendencia
    
    # 4. Calculamos el desvío estándar muestral y lo pasamos a nanoamperios (nA)
    sigma_nA = np.std(corriente_ruido_uA, ddof=1) * 1000.0
    return sigma_nA
    
def mostrar_resumen_ruido():
    """Barre los archivos de ruido y muestra los desvíos en la interfaz."""
    st.subheader("Resumen de Desvío Estándar del Ruido (nA)")
    
    lista_dispositivos = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_nominales = [100, 150, 200, 250, 350]
    
    resultados = {}
    
    for disp in lista_dispositivos:
        resultados[disp] = {}
        for curr in corrientes_nominales:
            nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{curr}u_M1.txt"
            
            sigma = calcular_desvio_archivo(nombre_archivo)
            
            if sigma is not None:
                resultados[disp][f"{curr} uA"] = f"{sigma:.2f} nA"
            else:
                resultados[disp][f"{curr} uA"] = "Falta medición / Incompleto"
                
    st.write(resultados)
