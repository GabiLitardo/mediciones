# proc_ruido.py
import numpy as np
import streamlit as st
from scipy.signal import welch
from lector_archivos import cargar_medicion_ruido, cargar_medicion_tanda

A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    ln_R = np.log(resistencia)
    return (1.0 / (A_SH + B_SH * ln_R + C_SH * (ln_R ** 3))) - 273.15

def calcular_psd(tiempo_s, i_ruido_uA):
    dt = float(np.mean(np.diff(tiempo_s)))
    fs = 1.0 / dt
    n = len(i_ruido_uA)
    nperseg = min(n, 256)
    noverlap = nperseg // 2

    freqs, psd = welch(
        i_ruido_uA,
        fs=fs,
        window='hann',
        nperseg=nperseg,
        noverlap=noverlap,
        scaling='density'
    )
    return freqs[1:], psd[1:]


def obtener_analisis_ruido_completo(lista_dispositivos, corrientes_normalizadas, es_larga=False, restar_deriva=True, es_fox=False, die="DIE4"):
    """
    Retorna cuatro diccionarios planos unificados con formato:
    {"Etiqueta Leyenda": {"x": array, "y": array}}
    """
    evos = {}
    evos_temp = {}
    i_vs_t = {}
    std_ruido = {}
    psd = {}

    for disp in lista_dispositivos:
        std_list = []
        corrientes_validas = []

        for disp in lista_dispositivos:
            std_list = []
            corrientes_validas = []

            for corr in corrientes_normalizadas:
                datos_matriz = cargar_medicion_ruido(disp, corr, es_larga, es_fox, die)
                if datos_matriz is None:
                    continue

                tiempo_s = datos_matriz[:, 0]
                corriente_uA = np.abs(datos_matriz[:, 1]) * 1e6
                resistencia = datos_matriz[:, 2]
                temperatura_C = convertir_r_a_temp_steinhart(resistencia)

                if es_fox:
                    # Cargamos la curva IV postrad59 usando la función existente
                    datos_iv = cargar_medicion_tanda(disp, "FOXFET", 59)
                    if datos_iv is not None:
                        vgs_iv = datos_iv[:, 0]
                        id_iv = np.abs(datos_iv[:, 1]) * 1e6
                        
                        # Ordenamos por corriente para que np.interp funcione
                        idx_sort = np.argsort(id_iv)
                        
                        # Interpolamos la corriente ruidosa para obtener la tensión de ruido [V]
                        tension_V = np.interp(corriente_uA, id_iv[idx_sort], vgs_iv[idx_sort])
                        
                        # Pasamos a mV para que los gráficos y desvíos tengan escalas legibles
                        magnitud_y = tension_V * 1000.0
                    else:
                        # Fallback por si no encuentra el archivo (evita que crashee)
                        st.warning(f"No se encontró curva IV de referencia (postrad59) para {disp}. Graficando corriente.")
                        magnitud_y = corriente_uA
                else:
                    # En FGs mantenemos la corriente en uA
                    magnitud_y = corriente_uA

                # Ajuste de temperatura
                coefs_T = np.polyfit(tiempo_s, temperatura_C, deg=9)
                temperatura_fit_C = np.polyval(coefs_T, tiempo_s)

                # Ajuste lineal de la deriva (ahora se hace sobre la tensión si es FOXFET)
                coefs_Y = np.polyfit(temperatura_fit_C, magnitud_y, deg=1)
                y_fit = np.polyval(coefs_Y, temperatura_fit_C)
                
                y_ruido_neto = magnitud_y - y_fit
                y_val = y_ruido_neto if restar_deriva else magnitud_y

                tag = f"{disp} @ {corr} uA"
                tag_fit = f"{disp} @ {corr} uA (Fit)"

                # 1. Evolución del ruido
                evos[tag] = {"x": tiempo_s, "y": y_val}

                # 2. Evolución de temperatura (medida y fit)
                evos_temp[tag] = {"x": tiempo_s, "y": temperatura_C}
                evos_temp[tag_fit] = {"x": tiempo_s, "y": temperatura_fit_C}

                # 3. Variable vs Temperatura 
                i_vs_t[tag] = {"x": temperatura_C, "y": magnitud_y}
                i_vs_t[tag_fit] = {"x": temperatura_fit_C, "y": y_fit}

                # 4. Densidad Espectral de Potencia (PSD)
                if len(tiempo_s) > 1:
                    f_eje, psd_eje = calcular_psd(tiempo_s, y_val)
                    psd[tag] = {"x": f_eje, "y": psd_eje}

                # Si es FOX (mV), al multiplicar por 1000 el desvío queda en uV.
                # Si es FG (uA), al multiplicar por 1000 el desvío queda en nA.
                std_val = np.std(y_val * 1000.0, ddof=1)
                std_list.append(std_val)
                corrientes_validas.append(float(corr))

            if corrientes_validas:
                std_ruido[disp] = {
                    "x": np.array(corrientes_validas),
                    "y": np.array(std_list)
                }

        return {
            "evos": evos,
            "evos_temp": evos_temp,
            "i_vs_t": i_vs_t,
            "std_ruido": std_ruido,
            "psd": psd
        }