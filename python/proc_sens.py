# proc_sens.py
import numpy as np
import streamlit as st
from proc_evo import obtener_datos_crudos_tanda, obtener_datos_evolucion_vg

factores_normalizacion = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}
tasa_dosis = 0.18

def calcular_fit_polinomico(tiempos_list, corrientes_list):
    coeficientes = np.polyfit(tiempos_list, corrientes_list, deg=4)
    return coeficientes.tolist()

def calcular_sensibilidad_ventana(tiempos, corrientes_proc, corrientes_norm, n_ventana):   
    eje_x, eje_y = [], []
    k = n_ventana // 2
    
    for i in range(len(corrientes_proc) - n_ventana + 1):
        sub_t = tiempos[i : i + n_ventana]
        sub_i_proc = corrientes_proc[i : i + n_ventana]
        sub_i_norm = corrientes_norm[i : i + n_ventana]
        
        tasas_pares = []
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
            
    return np.array(eje_x), np.array(eje_y) / tasa_dosis

@st.cache_data
def procesar_sensibilidad(lista_dispositivos, tipo_tanda, normalizado=True, n_ventana=6):
    datos_crudos = obtener_datos_evolucion_vg(lista_dispositivos, tipo_tanda) if normalizado else obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda)
    resultado_fit, resultado_discreto = {}, {}
    print(list(datos_crudos.keys()), flush = True)

    for disp, datos in datos_crudos.items():
        tiempos, corrientes = datos["tiempos"], datos["valores"]
        factor = factores_normalizacion.get(disp, 1.0)
        corrientes_norm = corrientes if normalizado else corrientes / factor
        
        # Fit polinómico
        coefs_y = calcular_fit_polinomico(tiempos.tolist(), corrientes.tolist())
        coefs_x = calcular_fit_polinomico(tiempos.tolist(), corrientes_norm.tolist())
        t_cont = np.linspace(tiempos.min(), tiempos.max(), 200)
        
        eje_y = np.abs(4*coefs_y[0]*(t_cont**3) + 3*coefs_y[1]*(t_cont**2) + 2*coefs_y[2]*t_cont + coefs_y[3]) / tasa_dosis
        eje_x = coefs_x[0]*(t_cont**4) + coefs_x[1]*(t_cont**3) + coefs_x[2]*(t_cont**2) + coefs_x[3]*t_cont + coefs_x[4]
        resultado_fit[disp] = {"x": eje_x, "y": eje_y}
        
        # Discreto por ventana
        ex_disc, ey_disc = calcular_sensibilidad_ventana(tiempos, corrientes, corrientes_norm, n_ventana)
        resultado_discreto[disp] = {"x": ex_disc, "y": ey_disc}
        
    return [resultado_fit, resultado_discreto]