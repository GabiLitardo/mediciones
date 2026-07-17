import numpy as np
from lector_archivos import matchear_archivos

# Constantes para la ecuación de Steinhart-Hart (Termistor)
A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    """Convierte la resistencia del termistor a temperatura en grados Celsius."""
    ln_R = np.log(resistencia)
    temperatura_k = 1.0 / (A_SH + B_SH * ln_R + C_SH * (ln_R ** 3))
    return temperatura_k - 273.15

def obtener_ruido_neto_archivo(nombre_archivo):
    """Lee el archivo de ruido, remueve la tendencia térmica y devuelve el ruido neto."""
    lista_mediciones = matchear_archivos(nombre_archivo, tipo_medicion="ruido")
    datos = lista_mediciones[0]
    
    tiempo_s = datos[:, 0]
    corriente_uA = np.abs(datos[:, 1]) * 1e6
    resistencia = datos[:, 2]
    
    temperatura_C = convertir_r_a_temp_steinhart(resistencia)
    
    # Ajuste lineal para remover la deriva provocada por la temperatura
    coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
    corriente_tendencia = np.polyval(coefs, temperatura_C)
    corriente_ruido = corriente_uA - corriente_tendencia
    
    return tiempo_s, corriente_ruido

def obtener_evolucion_ruido(lista_dispositivos, corrientes_nominales, es_larga):
    """Genera las series temporales de ruido para cada dispositivo y corriente."""
    resultado = {}
    
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            sufijo = "_LARGA.txt" if es_larga else ".txt"
            nombre_archivo = f"MOSISV72M_DIE4_{disp}VD=-4.5_RUIDO{corr}u_M1{sufijo}"
            
            tiempo_s, corriente_ruido = obtener_ruido_neto_archivo(nombre_archivo)
            resultado[disp][corr] = {"x": tiempo_s, "y": corriente_ruido}
            
    return resultado

def procesar_ruido(lista_dispositivos, corrientes_nominales, es_larga=False):
    """Calcula el desvío estándar del ruido neto (en nA) vs las corrientes nominales."""
    resultado = {}
    todas_las_evos = obtener_evolucion_ruido(lista_dispositivos, corrientes_nominales, es_larga)
    
    for disp in lista_dispositivos:
        valores_y = []
        for corr in corrientes_nominales:
            ruido_uA = todas_las_evos[disp][corr]["y"]
            # Multiplicamos por 1000 para pasar de uA a nA
            valores_y.append(np.std(ruido_uA * 1000, ddof=1))
            
        resultado[disp] = {
            "x": np.array([float(corr) for corr in corrientes_nominales]),
            "y": np.array(valores_y)
        }
        
    return resultado
