# proc_ruido.py
import numpy as np
from lector_archivos import matchear_archivos

# Constantes del termistor (Modelo Steinhart-Hart)
A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    """Calcula la temperatura en °C a partir de la resistencia del termistor."""
    ln_R = np.log(resistencia)
    return (1.0 / (A_SH + B_SH * ln_R + C_SH * (ln_R ** 3))) - 273.15

def procesar_archivo_ruido(nombre_archivo):
    """
    Lee un archivo de ruido y calcula todas las magnitudes asociadas.
    Devuelve un diccionario con: tiempo_s, corriente_uA, temperatura_C, 
    corriente_fit_uA e i_ruido_neto_uA.
    """
    lista_mediciones = matchear_archivos(nombre_archivo, tipo_medicion="ruido")
    if not lista_mediciones:
        return None

    datos = lista_mediciones[0]
    tiempo_s = datos[:, 0]
    corriente_uA = np.abs(datos[:, 1]) * 1e6
    resistencia = datos[:, 2]
    temperatura_C = convertir_r_a_temp_steinhart(resistencia)

    # Tendencia térmica mediante ajuste lineal
    coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
    corriente_fit_uA = np.polyval(coefs, temperatura_C)
    i_ruido_neto_uA = corriente_uA - corriente_fit_uA

    return {
        "tiempo_s": tiempo_s,
        "corriente_uA": corriente_uA,
        "temperatura_C": temperatura_C,
        "corriente_fit_uA": corriente_fit_uA,
        "i_ruido_neto_uA": i_ruido_neto_uA
    }

def obtener_evolucion_ruido(lista_dispositivos, corrientes_nominales, es_larga=False, restar_deriva=True):
    """Obtiene la evolución temporal de la corriente (neta o bruta según restar_deriva)."""
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1_LARGA.txt" if es_larga else f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1.txt"
            datos = procesar_archivo_ruido(nombre_archivo)
            
            y_val = datos["i_ruido_neto_uA"] if restar_deriva else datos["corriente_uA"]
            resultado[disp][corr] = {"x": datos["tiempo_s"], "y": y_val}

    return resultado

def obtener_evolucion_temperatura_ruido(lista_dispositivos, corrientes_nominales, es_larga=False):
    """Obtiene la evolución temporal de la temperatura (°C)."""
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1_LARGA.txt" if es_larga else f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1.txt"
            datos = procesar_archivo_ruido(nombre_archivo)
            
            resultado[disp][corr] = {"x": datos["tiempo_s"], "y": datos["temperatura_C"]}

    return resultado

def obtener_corriente_vs_temperatura_ruido(lista_dispositivos, corrientes_nominales, es_larga=False):
    """Obtiene los pares Corriente vs Temperatura y su ajuste lineal."""
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1_LARGA.txt" if es_larga else f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1.txt"
            datos = procesar_archivo_ruido(nombre_archivo)
            
            resultado[disp][corr] = {
                "x": datos["temperatura_C"],
                "y": datos["corriente_uA"],
                "y_fit": datos["corriente_fit_uA"]
            }

    return resultado

def procesar_ruido(lista_dispositivos, corrientes_nominales, es_larga=False, restar_deriva=True):
    """Calcula el desvío estándar del ruido (en nA) vs Corriente nominal."""
    resultado = {}
    todas_las_evos = obtener_evolucion_ruido(lista_dispositivos, corrientes_nominales, es_larga, restar_deriva)

    for disp in lista_dispositivos:
        std_list = []
        for corr in corrientes_nominales:
            if corr in todas_las_evos[disp]:
                # Multiplicamos por 1000 para llevar uA a nA
                std_val = np.std(todas_las_evos[disp][corr]["y"] * 1000.0, ddof=1)
                std_list.append(std_val)

        resultado[disp] = {
            "x": np.array([float(corr) for corr in corrientes_nominales]),
            "y": np.array(std_list)
        }

    return resultado