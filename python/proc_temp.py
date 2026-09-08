# proc_temp.py
import numpy as np
import streamlit as st
from lector_archivos import cargar_medicion_temperatura


def obtener_analisis_temperatura(lista_dispositivos, corrientes_normalizadas, lista_temperaturas, vd=-4.5):
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

                    idx_vd = np.argmin(np.abs(v_drain - (vd)))
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
    Procesa curvas de transferencia I-V a distintas temperaturas.
    - es_std=False (FOXFET): alpha_V [V/°C] vs I_D y V_GS vs T a corrientes fijas.
    - es_std=True (STD): alpha_I [uA/°C] vs V_GS y vs I_D (ref a T amb).
    """
    iv_vs_t = {}
    alpha_vs_vgs = {}
    alpha_vs_i = {}
    vgs_vs_t_fijo = {}

    CORRIENTES_TEST_UA = [0.1, 1.0, 10.0, 100.0]

    for disp in lista_dispositivos:
        curvas_por_temp = {}

        # 1. Carga y preordenamiento
        for temp in lista_temperaturas:
            datos = cargar_medicion_temperatura(disp, corr=None, temp=temp, es_fox=True, die=die, es_std=es_std)
            if datos is not None:
                vgs = datos[:, 0]
                id_uA = np.abs(datos[:, 1]) * 1e6

                idx_vgs = np.argsort(vgs)
                curvas_por_temp[temp] = {
                    "vgs": vgs[idx_vgs],
                    "id": id_uA[idx_vgs]
                }
                iv_vs_t[f"{disp} @ {temp}°C"] = {
                    "x": vgs[idx_vgs],
                    "y": id_uA[idx_vgs]
                }

        if len(curvas_por_temp) >= 2:
            temps_disponibles = np.array(sorted(curvas_por_temp.keys()))

            if es_std:
                # =========================================================
                # MODO STD: alpha_I = d(Id)/dT [uA/°C]
                # =========================================================
                vgs_base = list(curvas_por_temp.values())[0]["vgs"]

                matriz_id = np.array([
                    np.interp(vgs_base, curvas_por_temp[t]["vgs"], curvas_por_temp[t]["id"])
                    for t in temps_disponibles
                ])

                # Ajuste lineal en bloque para cada Vgs
                alphas_i = np.polyfit(temps_disponibles, matriz_id, deg=1)[0]

                alpha_vs_vgs[disp] = {"x": vgs_base, "y": alphas_i}

                # alpha vs Id (referenciado a T ambiente: fila 0)
                id_ref = matriz_id[0, :]
                idx_ord = np.argsort(id_ref)
                alpha_vs_i[disp] = {"x": id_ref[idx_ord], "y": alphas_i[idx_ord]}

            else:
                # =========================================================
                # MODO FOXFET: alpha_V = d(Vgs)/dT [V/°C] vs I_D
                # =========================================================
                i_min = max(np.min(curvas_por_temp[t]["id"]) for t in temps_disponibles)
                i_max = min(np.max(curvas_por_temp[t]["id"]) for t in temps_disponibles)

                if i_min < i_max and i_min > 0:
                    id_base = np.geomspace(i_min, i_max, 150)

                    matriz_vgs = []
                    for t in temps_disponibles:
                        id_t = curvas_por_temp[t]["id"]
                        vgs_t = curvas_por_temp[t]["vgs"]
                        idx_id = np.argsort(id_t)
                        matriz_vgs.append(np.interp(id_base, id_t[idx_id], vgs_t[idx_id]))

                    matriz_vgs = np.array(matriz_vgs)  # Shape: (n_temps, 150)

                    # Ajuste lineal en bloque para todo el vector continuo: matriz_vgs (n_temps, 150)
                    # np.polyfit devuelve matriz (deg+1, 150)
                    coefs = np.polyfit(temps_disponibles, matriz_vgs, deg=1)
                    alphas_v = coefs[0]
                    intercepts_v = coefs[1]

                    alpha_vs_i[disp] = {"x": id_base, "y": alphas_v}

                    # Extracción directa de V_GS vs T interpolando sobre la grilla ya calculada
                    for i_target in CORRIENTES_TEST_UA:
                        if i_min <= i_target <= i_max:
                            # Interpola el perfil Vgs(T) para esa corriente fija
                            vgs_a_target = np.array([
                                np.interp(i_target, id_base, matriz_vgs[i_t, :])
                                for i_t in range(len(temps_disponibles))
                            ])
                            
                            # alpha y b correspondientes interpolados directamente
                            alpha_target = np.interp(i_target, id_base, alphas_v)
                            b_target = np.interp(i_target, id_base, intercepts_v)
                            recta_ajuste = alpha_target * temps_disponibles + b_target

                            etiqueta_base = f"{disp} @ {i_target} µA"
                            vgs_vs_t_fijo[f"{etiqueta_base} (Medido)"] = {
                                "x": temps_disponibles,
                                "y": vgs_a_target
                            }
                            vgs_vs_t_fijo[f"{etiqueta_base} (Fit)"] = {
                                "x": temps_disponibles,
                                "y": recta_ajuste
                            }

    return {
        "iv_vs_t": iv_vs_t,
        "alpha_vs_vgs": alpha_vs_vgs,
        "alpha_vs_i": alpha_vs_i,
        "vgs_vs_t_fijo": vgs_vs_t_fijo
    }
