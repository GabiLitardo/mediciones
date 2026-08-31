# proc_evo.py
import numpy as np
import streamlit as st
from lector_archivos import cargar_curva_iv_referencia
from lector_archivos import cargar_medicion_tanda
TASA_DOSIS = 0.18

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


def obtener_vg_por_corriente(dispositivo, corriente_buscada):
    datos = cargar_curva_iv_referencia(dispositivo)
    tensiones_g = datos[:, 0]
    corrientes_d = np.abs(datos[:, 1])

    indices_ordenados = np.argsort(corrientes_d)
    if dispositivo == "PFGIW3":
        corriente_buscada = corriente_buscada / 56.0
    return np.interp(corriente_buscada, corrientes_d[indices_ordenados], tensiones_g[indices_ordenados])


def obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda, I_interp = 1e-5, rng = 60, en_dosis = False):
    resultado = {}
    factor_x = TASA_DOSIS if en_dosis else 1.0
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
            x_arr = np.array(tiempos)[indices] * factor_x
            y_arr = np.array(valores)[indices]
            
            # Serie 1: Medido
            resultado[f"{disp} (Medido)"] = {"x": x_arr, "y": y_arr}

            # Serie 2: Fit Polinómico
            coefs = calcular_fit_polinomico(x_arr.tolist(), y_arr.tolist())
            t_cont = np.linspace(x_arr.min(), x_arr.max(), 200)
            y_fit = np.polyval(coefs, t_cont)
            resultado[f"{disp} (Fit)"] = {"x": t_cont, "y": y_fit}

    return resultado


def obtener_datos_evolucion_vg(lista_dispositivos, tipo_tanda, en_dosis=False):
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda, en_dosis=en_dosis)
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
                resultado[f"{disp} (Fit)"] = {"x": t_cont, "y": y_fit}

    return resultado


def obtener_curvas_iv_referencia(lista_dispositivos):
    """
    Retorna las curvas de transferencia I-V de referencia en formato plano unificado
    con corriente negativa y el cálculo de Vt por extrapolación de sqrt(|Id|) en saturación:
    {"Etiqueta": {"x": array_vg, "y": array_id_uA, "vt": float}}
    """
    resultado = {}
    for disp in lista_dispositivos:
        datos = cargar_curva_iv_referencia(disp)

        datos_validos = datos[~np.isnan(datos).any(axis=1)]

        vg = datos_validos[:, 0]
        id_ua = datos_validos[:, 1] * 1e6

        # --- Cálculo de Vt en saturación: recta sobre sqrt(|Id|) ---
        sqrt_id = np.sqrt(np.abs(id_ua))
        
        # Derivada de sqrt(|Id|) respecto a Vg
        d_sqrt_id = np.gradient(sqrt_id, vg)
        
        # Buscamos la zona de mayor linealidad/pendiente
        d_limpia = np.nan_to_num(np.abs(d_sqrt_id), nan=0.0, posinf=0.0, neginf=0.0)
        idx_max = int(np.nanargmax(d_limpia))

        m_max = d_sqrt_id[idx_max]
        vg_max = vg[idx_max]
        sqrt_id_max = sqrt_id[idx_max]

        vt = vg_max - (sqrt_id_max / m_max)

        resultado[disp] = {
            "x": vg,
            "y": id_ua,
            "vt": float(vt)
        }

    return resultado
