# proc_sens.py
import numpy as np
import streamlit as st
from proc_evo import obtener_datos_crudos_tanda

factores_normalizacion = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}

def calcular_fit_polinomico(tiempos_list, corrientes_list):
    coeficientes = np.polyfit(tiempos_list, corrientes_list, deg=4)
    return coeficientes.tolist()

def procesar_sensibilidad(lista_dispositivos, tipo_tanda, normalizado=True):
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda)
    resultado_fit = {}
    resultado_discreto = {}
    
    for disp, datos in datos_crudos.items():
        tiempos = datos["tiempos"]
        corrientes = datos["valores"]
        factor = factores_normalizacion.get(disp, 1.0)
        
        corrientes_norm = corrientes / factor
        if normalizado:
            corrientes_proc = corrientes_norm
        else:
            corrientes_proc = corrientes       
        
        coefs_y = calcular_fit_polinomico(tiempos.tolist(), corrientes_proc.tolist())
        a_y, b_y, c_y, d_y, e_y = coefs_y
        
        coefs_x = calcular_fit_polinomico(tiempos.tolist(), corrientes_norm.tolist())
        a_x, b_x, c_x, d_x, e_x = coefs_x
        
        t_cont = np.linspace(tiempos.min(), tiempos.max(), 200)
        eje_y = np.abs(4*a_y*(t_cont**3) + 3*b_y*(t_cont**2) + 2*c_y*t_cont + d_y)
        eje_x = a_x*(t_cont**4) + b_x*(t_cont**3) + c_x*(t_cont**2) + d_x*t_cont + e_x
        
        resultado_fit[disp] = {"x": eje_x, "y": eje_y}
        
    for disp, datos in datos_crudos.items():   
        tiempos = datos["tiempos"]
        corrientes = datos["valores"]
        factor = factores_normalizacion.get(disp, 1.0)
        
        corrientes_norm = corrientes / factor
        if normalizado:
            corrientes_proc = corrientes_norm
        else:
            corrientes_proc = corrientes
        
        eje_x, eje_y = [], []
        for k in range(len(corrientes_proc) - 1):
            dt = tiempos[k+1] - tiempos[k]
            tasa = np.abs(corrientes_proc[k+1] - corrientes_proc[k]) / dt
            promedio = (corrientes_norm[k+1] + corrientes_norm[k]) / 2.0
            eje_y.append(tasa)
            eje_x.append(promedio)
            
        resultado_discreto[disp] = {"x": np.array(eje_x), "y": np.array(eje_y)}
        
    return [resultado_fit, resultado_discreto]
