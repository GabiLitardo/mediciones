# proc_sens.py
import numpy as np
import streamlit as st
from proc_evo import obtener_datos_crudos_tanda, obtener_vg_por_corriente

factores_normalizacion = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}

def calcular_fit_polinomico(tiempos_list, valores_list):
    coeficientes = np.polyfit(tiempos_list, valores_list, deg=4)
    return coeficientes.tolist()

def calcular_sensibilidad_ventana(tiempos, valores, n_ventana):
    if n_ventana % 2 != 0 or n_ventana <= 0:
        raise ValueError("El tamaño de ventana N debe ser un número entero par y mayor a 0.")
        
    eje_x, eje_y = [], []
    k = n_ventana // 2
    
    for i in range(len(valores) - n_ventana + 1):
        sub_t = tiempos[i : i + n_ventana]
        sub_v = valores[i : i + n_ventana]
        
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
        
        if normalizado:
            # =========================================================
            # CASO NORMALIZADO: Tensión V_FG (Fit + Discreto)
            # =========================================================
            tensiones_vg = []
            tiempos_validos = []
            
            for t, i_ua in zip(tiempos, corrientes):
                if disp == "PFGIW3":
                    i_norm_amp = (i_ua / 56.0) * 1e-6
                    disp_mapeo = "PFGIW2"
                else:
                    i_norm_amp = i_ua * 1e-6
                    disp_mapeo = disp
                
                try:
                    vg_val = obtener_vg_por_corriente(disp_mapeo, i_norm_amp)[cite: 4]
                    tensiones_vg.append(vg_val)
                    tiempos_validos.append(t)
                except Exception:
                    continue
            
            t_arr = np.array(tiempos_validos)
            v_arr = np.array(tensiones_vg)
            
            # 1. PARTE CONTINUA (Fit en Tensión)
            coefs_v = calcular_fit_polinomico(t_arr.tolist(), v_arr.tolist())
            a_v, b_v, c_v, d_v, e_v = coefs_v
            
            t_cont = np.linspace(t_arr.min(), t_arr.max(), 200)
            eje_y_fit = np.abs(4*a_v*(t_cont**3) + 3*b_v*(t_cont**2) + 2*c_v*t_cont + d_v) # dV_FG/dt
            eje_x_fit = a_v*(t_cont**4) + b_v*(t_cont**3) + c_v*(t_cont**2) + d_v*t_cont + e_v # V_FG
            
            resultado_fit[disp] = {"x": eje_x_fit, "y": eje_y_fit}
            
            # 2. PARTE DISCRETA (Ventana en Tensión)
            eje_x_disc, eje_y_disc = calcular_sensibilidad_ventana(
                tiempos=t_arr, 
                valores=v_arr, 
                n_ventana=n_ventana
            )
            resultado_discreto[disp] = {"x": eje_x_disc, "y": eje_y_disc}

        else:
            # =========================================================
            # CASO SIN NORMALIZAR: Corriente pura (Fit + Discreto original)
            # =========================================================
            # 1. PARTE CONTINUA (Fit en Corriente)
            coefs_y = calcular_fit_polinomico(tiempos.tolist(), corrientes.tolist())
            a_y, b_y, c_y, d_y, e_y = coefs_y
            
            corrientes_norm = corrientes / factor
            coefs_x = calcular_fit_polinomico(tiempos.tolist(), corrientes_norm.tolist())
            a_x, b_x, c_x, d_x, e_x = coefs_x
            
            t_cont = np.linspace(tiempos.min(), tiempos.max(), 200)
            eje_y_fit = np.abs(4*a_y*(t_cont**3) + 3*b_y*(t_cont**2) + 2*c_y*t_cont + d_y)
            eje_x_fit = a_x*(t_cont**4) + b_x*(t_cont**3) + c_x*(t_cont**2) + d_x*t_cont + e_x
            
            resultado_fit[disp] = {"x": eje_x_fit, "y": eje_y_fit}
            
            # 2. PARTE DISCRETA (Ventana en Corriente)
            eje_x_disc, eje_y_disc = calcular_sensibilidad_ventana(
                tiempos=tiempos, 
                valores=corrientes, 
                n_ventana=n_ventana
            )
            resultado_discreto[disp] = {"x": eje_x_disc, "y": eje_y_disc}
            
    return [resultado_fit, resultado_discreto]