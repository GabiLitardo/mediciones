# proc_sens.py
import numpy as np
import streamlit as st
from proc_evo import obtener_datos_crudos_tanda, obtener_vg_por_corriente

factores_normalizacion = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}

def calcular_fit_polinomico(tiempos_list, valores_list):
    coeficientes = np.polyfit(tiempos_list, valores_list, deg=4)
    return coeficientes.tolist()

def calcular_sensibilidad_vg_ventana(tiempos, tensiones_vg, n_ventana):
    if n_ventana % 2 != 0 or n_ventana <= 0:
        raise ValueError("El tamaño de ventana N debe ser un número entero par y mayor a 0.")
        
    eje_x, eje_y = [], []
    k = n_ventana // 2
    
    for i in range(len(tensiones_vg) - n_ventana + 1):
        sub_t = tiempos[i : i + n_ventana]
        sub_v = tensiones_vg[i : i + n_ventana]
        
        tasas_pares = []
        for p in range(k):
            idx_izq = (k - 1) - p
            idx_der = k + p
            
            dt = sub_t[idx_der] - sub_t[idx_izq]
            if dt > 0:
                tasa_par = np.abs(sub_v[idx_der] - sub_v[idx_izq]) / dt
                tasas_pares.append(tasa_par)
                
        if tasas_pares:
            tasa_promedio_ventana = np.mean(tasas_pares)
            v_promedio_ventana = np.mean(sub_v)
            
            eje_y.append(tasa_promedio_ventana)
            eje_x.append(v_promedio_ventana)
            
    return np.array(eje_x), np.array(eje_y)

def procesar_sensibilidad(lista_dispositivos, tipo_tanda, normalizado=True, n_ventana=6):
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda)
    resultado_fit = {}
    resultado_discreto = {}
    
    for disp, datos in datos_crudos.items():
        tiempos = datos["tiempos"]
        corrientes = datos["valores"] # uA
        factor = factores_normalizacion.get(disp, 1.0)
        
        tensiones_vg = []
        tiempos_validos = []
        
        for t, i_ua in zip(tiempos, corrientes):
            # Para PFGIW3 normalizamos previamente por su W/L=56
            i_norm_amp = (i_ua / factor) * 1e-6
            disp_mapeo = "PFGIW2" if disp == "PFGIW3" else disp
            
            try:
                vg_val = obtener_vg_por_corriente(disp_mapeo, i_norm_amp)
                tensiones_vg.append(vg_val)
                tiempos_validos.append(t)
            except:
                continue
                
        t_arr = np.array(tiempos_validos)
        v_arr = np.array(tensiones_vg)
        
        # 1. Fit Continuo (Polinomio Grado 4 sobre V_FG vs t)
        coefs_v = calcular_fit_polinomico(t_arr.tolist(), v_arr.tolist())
        a_v, b_v, c_v, d_v, e_v = coefs_v
        
        t_cont = np.linspace(t_arr.min(), t_arr.max(), 200)
        eje_y_fit = np.abs(4*a_v*(t_cont**3) + 3*b_v*(t_cont**2) + 2*c_v*t_cont + d_v)
        eje_x_fit = a_v*(t_cont**4) + b_v*(t_cont**3) + c_v*(t_cont**2) + d_v*t_cont + e_v
        
        resultado_fit[disp] = {"x": eje_x_fit, "y": eje_y_fit}
        
        # 2. Sensibilidad Discreta (Ventana Deslizante)
        eje_x_disc, eje_y_disc = calcular_sensibilidad_vg_ventana(t_arr, v_arr, n_ventana)
        resultado_discreto[disp] = {"x": eje_x_disc, "y": eje_y_disc}
        
    return [resultado_fit, resultado_discreto]