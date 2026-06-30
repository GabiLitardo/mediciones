# ruido.py
import numpy as np
from scipy.optimize import curve_fit
from procesamiento import matchear_archivos  # Reutilizamos tu función de búsqueda

# Constantes para la ecuación de Steinhart-Hart (Termistor NTC 10k)
A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    """Convierte la columna de resistencia del termistor a temperatura en °C."""
    ln_R = np.log(resistencia)
    inverso_T = A_SH + B_SH * ln_R + C_SH * (ln_R ** 3)
    temp_kelvin = 1.0 / inverso_T
    return temp_kelvin - 273.15

def calcular_desvio_ruido_limpio(nombre_archivo):
    """
    Lee un archivo de ruido, convierte la resistencia a temperatura,
    resta la deriva térmica mediante un ajuste lineal y devuelve
    el desvío estándar del ruido en nanoamperios (nA).
    """
    # Intentamos buscar y leer el archivo usando tu función existente
    datos_lista = matchear_archivos(nombre_archivo)
    if not datos_lista:
        return None
        
    datos = datos_lista[0]
    tiempo = datos[:, 0]
    corriente_uA = np.abs(datos[:, 1]) * 1e6  # Módulo de ID en microamperios
    resistencia = datos[:, 2]                 # Columna del termistor
    
    # 1. Calculamos la temperatura real en °C
    temperatura_C = convertir_r_a_temp_steinhart(resistencia)
    
    # 2. Ajuste lineal de la corriente en función de la temperatura (Deriva térmica)
    coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
    corriente_tendencia = np.polyval(coefs, temperatura_C)
    
    # 3. Restamos la deriva para aislar las fluctuaciones rápidas (Ruido AC)
    corriente_ruido_uA = corriente_uA - corriente_tendencia
    
    # 4. Calculamos el desvío estándar muestral y lo pasamos a nanoamperios (nA)
    sigma_nA = np.std(corriente_ruido_uA, ddof=1) * 1000.0
    
    return sigma_nA
