# procesamiento.py
import numpy as np
import streamlit as st
from pathlib import Path
from lector_archivos import matchear_archivos_iv, matchear_archivos_ruido

factores_normalizacion = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}

# Constantes de Steinhart-Hart para el termistor
A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

@st.cache_data
def calcular_fit_polinomico_cached(disp_name, tipo_tanda, tiempos_list, corrientes_list):
    try:
        coeficientes = np.polyfit(tiempos_list, corrientes_list, deg=5)
        return coeficientes.tolist()
    except:
        return None

def calcular_tiempo_acumulado(nro, tipo_tanda):
    """Calcula el tiempo acumulado basándose en el historial de ráfagas de la tesis."""
    t = 0
    for i in range(1, nro + 1):
        if tipo_tanda == "FOXFET":
            if i <= 32: t += 10
            elif i <= 44: t += 15
            elif i <= 47: t += 20
            elif i <= 50: t += 25
            elif i <= 52: t += 30
            elif i <= 53: t += 35
            else: t += 10
        else:
            if i <= 9: t += 10
            elif i <= 21: t += 15
            elif i <= 24: t += 20
            elif i <= 27: t += 25
            elif i <= 29: t += 30
            elif i <= 30: t += 35
            else: t += 10
    return t

def obtener_vg_por_corriente(dispositivo, corriente_buscada):
    """Calibra el voltaje de compuerta equivalente usando transistores de referencia."""
    if dispositivo in ["PFGIW2", "PFGIP2"]:
        nombre_archivo = "MOSISV72M_DIE4_PMOS_STD1_IV_VD=-4.5V_M1.ri"
    elif dispositivo == "PFGIW1":
        nombre_archivo = "MOSISV72M_DIE4_PMOS_STD2_IV_VD=-4.5V_M1.ri"
    else:
        raise ValueError("Dispositivo no válido. Elegir entre PFGIW1, PFGIW2 o PFGIP2.")

    raiz = Path(__file__).resolve().parent.parent
    lista_rutas = list(raiz.glob(f"*/{nombre_archivo}"))
    if not lista_rutas:
        raise FileNotFoundError(f"No se encontró el archivo {nombre_archivo} en mediciones.")
    
    ruta_archivo = lista_rutas[0]
    datos = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
    voltajes_g = datos[:, 0]
    corrientes_d = np.abs(datos[:, 1])

    indices_ordenados = np.argsort(corrientes_d)
    return np.interp(corriente_buscada, corrientes_d[indices_ordenados], voltajes_g[indices_ordenados])

def obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda):
    """Barre los archivos del 0 al 100 y extrae los arrays de tiempos y valores (Corriente o Tensión)."""
    resultado = {}
    for disp in lista_dispositivos:
        tiempos, valores = [], []
        for nro in range(0, 100):
            if tipo_tanda == "FG_tanda1":
                sufijo = ".ri"; prefijo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_"
            elif tipo_tanda == "FG_tanda2":
                sufijo = "_2.ri"; prefijo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_"
            elif tipo_tanda == "FOXFET":
                sufijo = ".ri"; prefijo = f"MOSISV72M_DIE4_{disp}_IV_VD=5V_postrad{nro}_"
                
            archivo_encontrado = None    
            for m_ver in ["M2", "M1"]:
                nombre_buscar = f"{prefijo}{m_ver}{sufijo}"
                datos = matchear_archivos_iv(nombre_buscar)
                if datos:
                    archivo_encontrado = datos[0]
                    break
            
            if archivo_encontrado is not None:
                t = calcular_tiempo_acumulado(nro, tipo_tanda)
                voltajes = archivo_encontrado[:, 0]
                corrientes = archivo_encontrado[:, 1]
                
                if tipo_tanda == "FOXFET":
                    corrientes_abs = np.abs(corrientes)
                    indices_orden = np.argsort(corrientes_abs)
                    v_interp = np.interp(1e-5, corrientes_abs[indices_orden], voltajes[indices_orden])
                    valores.append(v_interp)
                    tiempos.append(t)
                else:
                    idx = np.where(np.round(voltajes, 1) == -4.5)[0]
                    if len(idx) > 0:
                        valores.append(np.abs(corrientes[idx[0]] * 1e6))
                        tiempos.append(t)
                        
        if tiempos:
            indices = np.argsort(tiempos)
            resultado[disp] = {
                "tiempos": np.array(tiempos)[indices],
                "valores": np.array(valores)[indices]
            }
    return resultado

def obtener_datos_evolucion_vg(lista_dispositivos, tipo_tanda):
    """Genera la evolución temporal mapeada al voltaje equivalente V_FG."""
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda)
    resultado = {}
    for disp, datos in datos_crudos.items():
        tiempos_vg, voltajes_vg = [], []
        for t, corriente_ua in zip(datos["tiempos"], datos["valores"]):
            try:
                vg_val = obtener_vg_por_corriente(disp, corriente_ua * 1e-6)
                voltajes_vg.append(vg_val)
                tiempos_vg.append(t)
            except:
                continue
        if tiempos_vg:
            resultado[disp] = {"tiempos": np.array(tiempos_vg), "valores": np.array(voltajes_vg)}
    return resultado

def procesar_sensibilidad(lista_dispositivos, tipo_tanda, normalizado=True, analitico=True):
    """Calcula los arreglos X e Y para los gráficos de sensibilidad de manera unificada."""
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda)
    resultado = {}
    
    for disp, datos in datos_crudos.items():
        tiempos = datos["tiempos"]
        corrientes = datos["valores"]
        factor = factores_normalizacion.get(disp, 1.0) if normalizado else 1.0
        corrientes_proc = corrientes / factor
        
        coefs = None
        if analitico:
            llave_cache = f"{tipo_tanda}" if normalizado else f"{tipo_tanda}_abs"
            coefs = calcular_fit_polinomico_cached(disp, llave_cache, tiempos.tolist(), corrientes_proc.tolist())
            
        if coefs is not None and analitico:
            a, b, c, d, e, f = coefs
            t_cont = np.linspace(tiempos.min(), tiempos.max(), 200)
            eje_y = np.abs(5*a*(t_cont**4) + 4*b*(t_cont**3) + 3*c*(t_cont**2) + 2*d*t_cont + e)
            eje_x = a*(t_cont**5) + b*(t_cont**4) + c*(t_cont**3) + d*(t_cont**2) + e*t_cont + f
            resultado[disp] = {"x": eje_x, "y": eje_y, "es_lineal": True}
        else:
            # Algoritmo discreto diferencial (Versión 2 / Fallback)
            eje_x, eje_y = [], []
            for k in range(len(corrientes_proc) - 1):
                dt = tiempos[k+1] - tiempos[k]
                if dt > 0:
                    tasa = np.abs(corrientes_proc[k+1] - corrientes_proc[k]) / dt
                    promedio = (corrientes_proc[k+1] + corrientes_proc[k]) / 2.0
                    eje_y.append(tasa)
                    eje_x.append(promedio)
            if eje_x:
                resultado[disp] = {"x": np.array(eje_x), "y": np.array(eje_y), "es_lineal": False}
    return resultado

def convertir_r_a_temp_steinhart(resistencia):
    ln_R = np.log(resistencia)
    return (1.0 / (A_SH + B_SH * ln_R + C_SH * (ln_R ** 3))) - 273.15

def calcular_desvio_archivo(nombre_archivo):
    """Remueve la deriva térmica lineal del archivo de ruido y extrae el desvío AC neto."""
    datos = matchear_archivos_ruido(nombre_archivo)
    
    # —— SEGURIDAD: Si el archivo no existe, está vacío o corrupto, salimos elegantemente ——
    if datos is None or datos.size == 0 or len(datos.shape) < 2 or datos.shape[1] < 3:
        return None

    try:
        corriente_uA = np.abs(datos[:, 1]) * 1e6
        resistencia = datos[:, 2]
        
        temperatura_C = convertir_r_a_temp_steinhart(resistencia)
        coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
        corriente_tendencia = np.polyval(coefs, temperatura_C)
        
        corriente_ruido_uA = corriente_uA - corriente_tendencia
        
        # Si por alguna razón el array quedó vacío tras el proceso, evitamos el crash
        if len(corriente_ruido_uA) < 2:
            return None
            
        return np.std(corriente_ruido_uA, ddof=1) * 1000.0
    except:
        return None
