# proc_evo.py
import numpy as np
import streamlit as st
import lector_archivos

def calcular_tiempo_acumulado(nro, tipo_tanda):
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
        if tipo_tanda in ["FG_tanda1", "FG_tanda2"]:
            if i <= 9: t += 10
            elif i <= 21: t += 15
            elif i <= 24: t += 20
            elif i <= 27: t += 25
            elif i <= 29: t += 30
            elif i <= 30: t += 35
            else: t += 10
    return t

@st.cache_data
def obtener_vg_por_corriente(dispositivo, corriente_buscada):
    datos = lector_archivos.cargar_curva_iv_referencia(dispositivo)
    tensiones_g = datos[:, 0]
    corrientes_d = np.abs(datos[:, 1])

    indices_ordenados = np.argsort(corrientes_d)
    if dispositivo == "PFGIW3":
        corriente_buscada = corriente_buscada / 56.0
    return np.interp(corriente_buscada, corrientes_d[indices_ordenados], tensiones_g[indices_ordenados])

@st.cache_data
def obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda, rng=60):
    resultado = {}
    for disp in lista_dispositivos:
        tiempos, valores = [], []
        for nro in range(0, rng):
            archivo_encontrado = lector_archivos.cargar_medicion_tanda(disp, tipo_tanda, nro)
            
            if archivo_encontrado is not None:
                t = calcular_tiempo_acumulado(nro, tipo_tanda)
                tensiones = archivo_encontrado[:, 0]
                corrientes = archivo_encontrado[:, 1]
                
                if tipo_tanda == "FOXFET":
                    corrientes_abs = np.abs(corrientes)
                    indices_orden = np.argsort(corrientes_abs)
                    x_sort = corrientes_abs[indices_orden]
                    y_sort = tensiones[indices_orden]
                    valores.append(np.interp(1e-7, x_sort, y_sort))
                    tiempos.append(t)
                else:
                    idx = np.where(np.round(tensiones, 1) == -4.5)[0]
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

@st.cache_data
def obtener_datos_evolucion_vg(lista_dispositivos, tipo_tanda):
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda)
    resultado = {}
    for disp, datos in datos_crudos.items():
        tiempos_vg, tensiones_vg = [], []
        for t, corriente_ua in zip(datos["tiempos"], datos["valores"]):
            try:
                vg_val = obtener_vg_por_corriente(disp, corriente_ua * 1e-6)
                tensiones_vg.append(vg_val)
                tiempos_vg.append(t)
            except (ValueError, IndexError):
                continue
        if tiempos_vg:
            resultado[disp] = {"tiempos": np.array(tiempos_vg), "valores": np.array(tensiones_vg)}
    return resultado