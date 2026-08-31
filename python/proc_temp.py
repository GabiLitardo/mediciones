# proc_temp.py
import numpy as np
import streamlit as st
from lector_archivos import cargar_medicion_temperatura


def obtener_analisis_temperatura(lista_dispositivos, corrientes_normalizadas, lista_temperaturas):
    """
    Procesa las mediciones de temperatura y retorna dos diccionarios planos unificados:
    - 'i_vs_t': {"disp @ corr uA": {"x": array_temp, "y": array_corriente}}
    - 'alpha_vs_i': {"disp": {"x": array_corrientes, "y": array_alphas}}
    """
    i_vs_t = {}
    alpha_vs_i = {}

    for disp in lista_dispositivos:
        x_alpha = []
        y_alpha = []

        for corr in corrientes_normalizadas:
            temps_aux = []
            corrientes_aux = []

            for temp in lista_temperaturas:
                datos = cargar_medicion_temperatura(disp, corr, temp)

                if datos is not None:
                    v_drain = datos[:, 0]
                    i_drain = datos[:, 1]

                    idx_vd = np.argmin(np.abs(v_drain - (-4.5)))
                    i_en_v5 = np.abs(i_drain[idx_vd]) * 1e6

                    temps_aux.append(float(temp))
                    corrientes_aux.append(i_en_v5)

            if len(temps_aux) >= 2:
                indices_orden = np.argsort(temps_aux)
                x_ordenado = np.array(temps_aux)[indices_orden]
                y_ordenado = np.array(corrientes_aux)[indices_orden]

                coefs = np.polyfit(x_ordenado, y_ordenado, deg=1)

                tag = f"{disp} @ {corr} uA"
                i_vs_t[tag] = {
                    "x": x_ordenado,
                    "y": y_ordenado
                }

                x_alpha.append(float(corr))
                y_alpha.append(coefs[0])

        if x_alpha:
            idx = np.argsort(x_alpha)
            x_arr = np.array(x_alpha)[idx]
            y_arr = np.array(y_alpha)[idx]
            alpha_vs_i[disp] = {
                "x": x_arr,
                "y": y_arr
            }
            coefs_alpha = np.polyfit(x_arr, y_arr, deg=1)
            m, b = coefs_alpha[0], coefs_alpha[1]
            x_cont = np.linspace(0.0, x_arr.max(), 100)
            y_cont = np.polyval(coefs_alpha, x_cont)
            ztc = float(-b / m)
            
            alpha_vs_i[f"{disp} (Fit)"] = {
                "x": x_cont,
                "y": y_cont,
                "ztc": ztc
            }
            

    return {
        "i_vs_t": i_vs_t,
        "alpha_vs_i": alpha_vs_i
    }


def obtener_analisis_temperatura_v2(lista_dispositivos, lista_temperaturas, die="DIE4", es_std=False):
    """
    Procesa curvas de transferencia I-V a distintas temperaturas para FOXFET.
    Retorna:
    - 'iv_vs_t': {"disp @ T°C": {"x": array_vgs, "y": array_id_uA}}
    - 'alpha_vs_vgs': {"disp": {"x": array_vgs, "y": array_alpha}}
    - 'alpha_vs_i': {"disp": {"x": array_id_ref_uA, "y": array_alpha}}
    """
    iv_vs_t = {}
    alpha_vs_vgs = {}
    alpha_vs_i = {}

    for disp in lista_dispositivos:
        curvas_por_temp = {}

        # 1. Carga de curvas I-V por temperatura
        for temp in lista_temperaturas:
            datos = cargar_medicion_temperatura(disp, corr=None, temp=temp, es_fox=True, die=die, es_std=es_std)
            if datos is not None:
                print("", flush=True)
                # Ordenar por Vgs ascendente para evitar problemas de interpolación
                idx_ord = np.argsort(datos[:, 0])
                vgs = datos[idx_ord, 0]
                id_uA = np.abs(datos[idx_ord, 1]) * 1e6

                curvas_por_temp[temp] = {"vgs": vgs, "id": id_uA}
                iv_vs_t[f"{disp} @ {temp}°C"] = {"x": vgs, "y": id_uA}

        if len(curvas_por_temp) >= 2:
            # Vector común de Vgs para alinear todas las temperaturas
            vgs_base = list(curvas_por_temp.values())[0]["vgs"]
            temps_disponibles = np.array(sorted(curvas_por_temp.keys()))

            # Matriz de corrientes: filas = temperaturas, columnas = puntos de Vgs
            matriz_id = []
            for t in temps_disponibles:
                vgs_t = curvas_por_temp[t]["vgs"]
                id_t = curvas_por_temp[t]["id"]
                id_interp = np.interp(vgs_base, vgs_t, id_t)
                matriz_id.append(id_interp)

            matriz_id = np.array(matriz_id)  # Shape: (n_temps, n_vgs)

            # 2. Ajuste lineal I vs T punto por punto en cada Vgs
            # Coeficiente alpha = d(Id)/dT
            n_puntos = len(vgs_base)
            alphas = np.zeros(n_puntos)

            for col in range(n_puntos):
                coef = np.polyfit(temps_disponibles, matriz_id[:, col], deg=1)
                alphas[col] = coef[0]

            alpha_vs_vgs[disp] = {
                "x": vgs_base,
                "y": alphas
            }

            # Corriente de referencia a temperatura ambiente más baja (primer elemento)
            id_referencia = matriz_id[0, :]
            idx_i_ord = np.argsort(id_referencia)

            alpha_vs_i[disp] = {
                "x": id_referencia[idx_i_ord],
                "y": alphas[idx_i_ord]
            }

    return {
        "iv_vs_t": iv_vs_t,
        "alpha_vs_vgs": alpha_vs_vgs,
        "alpha_vs_i": alpha_vs_i
    }