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
    Busca el archivo en el repositorio y levanta la matriz numérica
    soportando cualquier ensalada de espacios o tabs de GitHub.
    """
    directorio_base = "."
    for root, dirs, files in os.walk(directorio_base):
        if nombre_buscar in files:
            ruta_completa = os.path.join(root, nombre_buscar)
            try:
                # skip_header=3 remueve exactamente el texto inicial de tus archivos
                # No le ponemos delimiter ni usecols para que digiera cualquier formato libre
                datos = np.genfromtxt(ruta_completa, skip_header=3)
                return datos
            except Exception as e:
                # Si deseas debuggear qué falla, podés descomentar la línea de abajo:
                # st.write(f"Error leyendo {nombre_buscar}: {e}")
                return None
    return None

def calcular_desvio_archivo(nombre_archivo):
    """Procesa un archivo de ruido, remueve la deriva térmica y devuelve el desvío en nA."""
    datos = matchear_archivos_ruido(nombre_archivo)
    
    if datos is None or datos.size == 0:
        return None
        
    # Si por alguna razón se leyó como un vector unidimensional plano, lo salteamos
    if len(datos.shape) < 2 or datos.shape[1] < 3:
        return None

    # Extraemos las columnas de la matriz ya levantada en memoria
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
            nombre_archivo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{curr}_M1.ri" 
            # Nota: Si tus archivos terminan en _M1.txt o similar, ajustá el string de arriba
            # Ejemplo basado en tu archivo de muestra: f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{curr}u_M1.txt"
            nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{curr}u_M1.txt"
            
            sigma = calcular_desvio_archivo(nombre_archivo)
            
            if sigma is not None:
                resultados[disp][f"{curr} uA"] = f"{sigma:.2f} nA"
            else:
                resultados[disp][f"{curr} uA"] = "Falta medición / Incompleto"
                
    st.write(resultados)
