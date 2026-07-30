# proc_sens.py
import numpy as np
import streamlit as st
from proc_evo import obtener_datos_crudos_tanda

factores_normalizacion = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}

def calcular_fit_polinomico(tiempos_list, corrientes_list):
    coeficientes = np.polyfit(tiempos_list, corrientes_list, deg=4)
    return coeficientes.tolist()

def calcular_sensibilidad_ventana(tiempos, corrientes_proc, corrientes_norm, n_ventana):   
    eje_x, eje_y = [], []
    k = n_ventana // 2  # Número de pares simétricos dentro de la ventana
    
    # Recorremos todas las ventanas posibles
    for i in range(len(corrientes_proc) - n_ventana + 1):
        sub_t = tiempos[i : i + n_ventana]
        sub_i_proc = corrientes_proc[i : i + n_ventana]
        sub_i_norm = corrientes_norm[i : i + n_ventana]
        
        tasas_pares = []
        # Para N=6 (k=3): pares (idx_izq, idx_der) son (2,3), (1,4), (0,5)
        for p in range(k):
            idx_izq = (k - 1) - p
            idx_der = k + p
            
            dt = sub_t[idx_der] - sub_t[idx_izq]
            if dt > 0:
                tasa_par = np.abs(sub_i_proc[idx_der] - sub_i_proc[idx_izq]) / dt
                tasas_pares.append(tasa_par)
                
        if tasas_pares:
            tasa_promedio_ventana = np.mean(tasas_pares)
            corriente_promedio_ventana = np.mean(sub_i_norm)
            
            eje_y.append(tasa_promedio_ventana)
            eje_x.append(corriente_promedio_ventana)
            
    return np.array(eje_x), np.array(eje_y)

def procesar_sensibilidad(lista_dispositivos, tipo_tanda, normalizado=True, n_ventana=6):
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda)
    resultado_fit = {}
    resultado_discreto = {}
    
    # 1. Ajuste Polinómico Grado 4
    for disp, datos in datos_crudos.items():
        tiempos = datos["tiempos"]
        corrientes = datos["valores"]
        factor = factores_normalizacion.get(disp, 1.0)
        
        corrientes_norm = corrientes / factor
        corrientes_proc = corrientes_norm if normalizado else corrientes
        
        coefs_y = calcular_fit_polinomico(tiempos.tolist(), corrientes_proc.tolist())
        a_y, b_y, c_y, d_y, e_y = coefs_y
        
        coefs_x = calcular_fit_polinomico(tiempos.tolist(), corrientes_norm.tolist())
        a_x, b_x, c_x, d_x, e_x = coefs_x
        
        t_cont = np.linspace(tiempos.min(), tiempos.max(), 200)
        eje_y = np.abs(4*a_y*(t_cont**3) + 3*b_y*(t_cont**2) + 2*c_y*t_cont + d_y)
        eje_x = a_x*(t_cont**4) + b_x*(t_cont**3) + c_x*(t_cont**2) + d_x*t_cont + e_x
        
        resultado_fit[disp] = {"x": eje_x, "y": eje_y}
        
    # 2. Sensibilidad Discreta mediante Ventana Deslizante
    for disp, datos in datos_crudos.items():   
        tiempos = datos["tiempos"]
        corrientes = datos["valores"]
        factor = factores_normalizacion.get(disp, 1.0)
        
        corrientes_norm = corrientes / factor
        corrientes_proc = corrientes_norm if normalizado else corrientes
        
        eje_x, eje_y = calcular_sensibilidad_ventana(
            tiempos=tiempos, 
            corrientes_proc=corrientes_proc, 
            corrientes_norm=corrientes_norm, 
            n_ventana=n_ventana
        )
            
        resultado_discreto[disp] = {"x": eje_x, "y": eje_y}
        
    return [resultado_fit, resultado_discreto]
