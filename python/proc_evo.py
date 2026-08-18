# proc_evo.py
import numpy as np
import streamlit as st
from lector_archivos import cargar_curva_iv_referencia
from lector_archivos import cargar_medicion_tanda

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

def calcular_fit_polinomico(tiempos_list, corrientes_list):
    coeficientes = np.polyfit(tiempos_list, corrientes_list, deg=4)
    return coeficientes.tolist()

@st.cache_data
def obtener_vg_por_corriente(dispositivo, corriente_buscada):
    datos = cargar_curva_iv_referencia(dispositivo)
    tensiones_g = datos[:, 0]
    corrientes_d = np.abs(datos[:, 1])

    indices_ordenados = np.argsort(corrientes_d)
    if dispositivo == "PFGIW3":
        corriente_buscada = corriente_buscada / 56.0
    return np.interp(corriente_buscada, corrientes_d[indices_ordenados], tensiones_g[indices_ordenados])

@st.cache_data
def obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda, I_interp = 1e-7, rng=60):
    resultado = {}
    for disp in lista_dispositivos:
        tiempos, valores = [], []
        for nro in range(0, rng):
            archivo_encontrado = cargar_medicion_tanda(disp, tipo_tanda, nro)
            
            if archivo_encontrado is not None:
                t = calcular_tiempo_acumulado(nro, tipo_tanda)
                tensiones = archivo_encontrado[:, 0]
                corrientes = archivo_encontrado[:, 1]
                
                if tipo_tanda == "FOXFET":
                    corrientes_abs = np.abs(corrientes)
                    indices_orden = np.argsort(corrientes_abs)
                    x_sort = corrientes_abs[indices_orden]
                    y_sort = tensiones[indices_orden]
                    valores.append(np.interp(I_interp, x_sort, y_sort))
                    tiempos.append(t)
                else:
                    idx = np.where(np.round(tensiones, 1) == -4.5)[0]
                    if len(idx) > 0:
                        valores.append(np.abs(corrientes[idx[0]] * 1e6))
                        tiempos.append(t)
            else:
                break               
        if tiempos:
            indices = np.argsort(tiempos)
            x_arr = np.array(tiempos)[indices]
            y_arr = np.array(valores)[indices]
            
            # Serie 1: Medido
            resultado[f"{disp} (Medido)"] = {"x": x_arr, "y": y_arr}

            # Serie 2: Fit Polinómico (solo para los dispositivos que corresponden)
            if disp in ["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"]:
                coefs = calcular_fit_polinomico(x_arr.tolist(), y_arr.tolist())
                t_cont = np.linspace(x_arr.min(), x_arr.max(), 200)
                y_fit = np.polyval(coefs, t_cont)
                resultado[f"{disp} (Fit Poly g4)"] = {"x": t_cont, "y": y_fit}

    return resultado

@st.cache_data
def obtener_datos_evolucion_vg(lista_dispositivos, tipo_tanda):
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda)
    resultado = {}
    
    # Filtramos para hacer la conversión de V_FG solo sobre las series medidas
    for tag, datos in datos_crudos.items():
        if "(Fit" in tag:
            continue
        disp = tag.replace(" (Medido)", "")
        
        tiempos_vg, tensiones_vg = [], []
        for t, corriente_ua in zip(datos["x"], datos["y"]):
            try:
                vg_val = obtener_vg_por_corriente(disp, corriente_ua * 1e-6)
                tensiones_vg.append(vg_val)
                tiempos_vg.append(t)
            except (ValueError, IndexError):
                continue

        if tiempos_vg:
            x_arr = np.array(tiempos_vg)
            y_arr = np.array(tensiones_vg)
            
            resultado[f"{disp} (Medido)"] = {"x": x_arr, "y": y_arr}
            
            if disp in ["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"]:
                coefs = calcular_fit_polinomico(x_arr.tolist(), y_arr.tolist())
                t_cont = np.linspace(x_arr.min(), x_arr.max(), 200)
                y_fit = np.polyval(coefs, t_cont)
                resultado[f"{disp} (Fit Poly g4)"] = {"x": t_cont, "y": y_fit}

    return resultado

@st.cache_data
def obtener_curvas_iv_referencia(lista_dispositivos):
    """
    Retorna las curvas de transferencia I-V de referencia en formato plano unificado:
    {"Etiqueta": {"x": array_vg, "y": array_id_uA}}
    """
    resultado = {}
    for disp in lista_dispositivos:
        datos = cargar_curva_iv_referencia(disp)
        if datos is not None and len(datos) > 0:
            vg = datos[:, 0]
            id_ua = datos[:, 1] * 1e6
            
            # Si es PFGIW3, normalizamos por su factor de escala (56x)
            if disp == "PFGIW3":
                id_ua = id_ua / 56.0
                
            idx = np.argsort(vg)
            resultado[disp] = {
                "x": vg[idx],
                "y": id_ua[idx]
            }
    return resultado
