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
    Interpola V_GS sobre un vector común de corriente (intersección estricta)
    y calcula el coeficiente térmico alpha_V = d(V_GS)/dT en [V/°C].
    
    Retorna:
    - 'iv_vs_t': {"disp @ T°C": {"x": array_vgs, "y": array_id_uA}}
    - 'alpha_vs_i': {"disp": {"x": array_id_comun_uA, "y": array_alpha_v}}
    """
    iv_vs_t = {}
    alpha_vs_i = {}

    for disp in lista_dispositivos:
        curvas_por_temp = {}

        # 1. Carga de curvas I-V por temperatura
        for temp in lista_temperaturas:
            datos = cargar_medicion_temperatura(disp, corr=None, temp=temp, es_fox=True, die=die, es_std=es_std)
            if datos is not None:
                # Ordenar por Id ascendente obligatorio para np.interp
                vgs = datos[:, 0]
                id_uA = np.abs(datos[:, 1]) * 1e6
                
                idx_ord = np.argsort(id_uA)
                vgs_ord = vgs[idx_ord]
                id_ord = id_uA[idx_ord]

                curvas_por_temp[temp] = {"vgs": vgs_ord, "id": id_ord}
                iv_vs_t[f"{disp} @ {temp}°C"] = {"x": vgs_ord, "y": id_ord}

        if len(curvas_por_temp) >= 2:
            temps_disponibles = np.array(sorted(curvas_por_temp.keys()))

            # 2. Intersección estricta de corrientes para evitar extrapolación
            i_min = max([np.min(curvas_por_temp[t]["id"]) for t in temps_disponibles])
            i_max = min([np.max(curvas_por_temp[t]["id"]) for t in temps_disponibles])

            if i_min < i_max and i_min > 0:
                # 150 puntos distribuidos logarítmicamente entre el piso y el techo común
                id_base = np.geomspace(i_min, i_max, 150)

                # Matriz de tensiones: filas = temperaturas, columnas = puntos de corriente común
                matriz_vgs = []
                for t in temps_disponibles:
                    vgs_t = curvas_por_temp[t]["vgs"]
                    id_t = curvas_por_temp[t]["id"]
                    vgs_interp = np.interp(id_base, id_t, vgs_t)
                    matriz_vgs.append(vgs_interp)

                matriz_vgs = np.array(matriz_vgs)  # Shape: (n_temps, n_puntos)

                # 3. Ajuste lineal V_GS vs T en cada corriente fija -> alpha_V [V/°C]
                n_puntos = len(id_base)
                alphas_v = np.zeros(n_puntos)

                for col in range(n_puntos):
                    coef = np.polyfit(temps_disponibles, matriz_vgs[:, col], deg=1)
                    alphas_v[col] = coef[0]

                alpha_vs_i[disp] = {
                    "x": id_base,
                    "y": alphas_v
                }

    return {
        "iv_vs_t": iv_vs_t,
        "alpha_vs_i": alpha_vs_i
    }