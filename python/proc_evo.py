# proc_evo.py
import numpy as np
import streamlit as st
from lector_archivos import cargar_medicion_tanda, cargar_curva_iv_referencia

FACTOR_TENSION = 0.05
VALOR_CERO_VOLT_TANDA2 = 57.0

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
def obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda, incluir_fit=True):
    """
    Retorna la estructura aplanada unificada para mediciones crudas:
    {"Etiqueta": {"x": array_tiempos, "y": array_valores}}
    """
    resultado = {}
    limite = 55 if tipo_tanda == "FOXFET" else 31

    for disp in lista_dispositivos:
        tiempos, valores = [], []

        for i in range(0, limite + 1):
            matriz = cargar_medicion_tanda(disp, tipo_tanda, i)
            if matriz is not None and matriz.size > 0:
                t_acum = calcular_tiempo_acumulado(i, tipo_tanda)
                
                if tipo_tanda == "FOXFET":
                    col_i, col_v = matriz[:, 0], matriz[:, 1]
                    v_interp = np.interp(0.1, col_i, col_v)
                    tiempos.append(t_acum)
                    valores.append(v_interp)
                else:
                    val_uA = np.abs(matriz[0, 1]) * 1e6
                    tiempos.append(t_acum)
                    valores.append(val_uA)

        if tiempos:
            t_arr = np.array(tiempos)
            v_arr = np.array(valores)
            
            # Puntos medidos
            resultado[f"{disp} (Medido)"] = {"x": t_arr, "y": v_arr}

            # Fit polinómico de grado 4 si corresponde
            if incluir_fit and disp in ["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"]:
                coefs = calcular_fit_polinomico(t_arr.tolist(), v_arr.tolist())
                t_cont = np.linspace(t_arr.min(), t_arr.max(), 200)
                v_fit = np.polyval(coefs, t_cont)
                resultado[f"{disp} (Fit Poly g4)"] = {"x": t_cont, "y": v_fit}

    return resultado

@st.cache_data
def obtener_datos_evolucion_vg(lista_dispositivos, tipo_tanda, incluir_fit=True):
    """
    Calcula la evolución de V_FG equivalente y retorna la estructura aplanada unificada:
    {"Etiqueta": {"x": array_tiempos, "y": array_vg}}
    """
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda, incluir_fit=False)
    resultado = {}

    for disp in lista_dispositivos:
        tag_medido = f"{disp} (Medido)"
        if tag_medido not in datos_crudos:
            continue

        datos_disp = datos_crudos[tag_medido]
        tiempos = datos_disp["x"]
        corrientes_uA = datos_disp["y"]

        med_ref = cargar_curva_iv_referencia(disp)
        if med_ref is None:
            continue

        v_ref = med_ref[:, 0]
        i_ref = np.abs(med_ref[:, 1]) * 1e6

        vg_equiv = []
        for i_val in corrientes_uA:
            v_int = np.interp(i_val, i_ref, v_ref)
            vg_equiv.append(v_int)

        t_arr = np.array(tiempos)
        vg_arr = np.array(vg_equiv)

        if tipo_tanda == "FG_tanda1":
            vg_arr = (vg_arr - vg_arr[0]) * FACTOR_TENSION
        elif tipo_tanda == "FG_tanda2":
            vg_arr = (vg_arr - vg_arr[0]) * FACTOR_TENSION + VALOR_CERO_VOLT_TANDA2

        resultado[f"{disp} (Medido)"] = {"x": t_arr, "y": vg_arr}

        if incluir_fit and disp in ["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"]:
            coefs = calcular_fit_polinomico(t_arr.tolist(), vg_arr.tolist())
            t_cont = np.linspace(t_arr.min(), t_arr.max(), 200)
            vg_fit = np.polyval(coefs, t_cont)
            resultado[f"{disp} (Fit Poly g4)"] = {"x": t_cont, "y": vg_fit}

    return resultado