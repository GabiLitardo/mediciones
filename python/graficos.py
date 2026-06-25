# graficos.py
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from procesamiento import matchear_archivos
from mapeo_vg import obtener_vg_por_corriente
from scipy.optimize import curve_fit

factores_normalizacion = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}

# =====================================================================
# NUEVO AJUSTE FÍSICO EXPONENCIAL
# =====================================================================

# Definimos el modelo físico de descarga para la Floating Gate
def modelo_exponencial_fg(t, I_final, I_0, tau):
    return I_final + (I_0 - I_final) * np.exp(-t / tau)

@st.cache_data
def calcular_fit_exponencial_cached(tiempos_list, corrientes_list):
    try:
        t_arr = np.array(tiempos_list)
        i_arr = np.array(corrientes_list)
        
        # Estimaciones iniciales lógicas para ayudar al algoritmo a converger:
        i_0_est = i_arr[0]                  # Corriente al inicio de la irradiación
        i_final_est = i_arr[-1]             # Última corriente medida (aproximación al estado neutro)
        tau_est = t_arr.max() / 2.0         # Una constante de tiempo intermedia
        
        p0 = [i_final_est, i_0_est, tau_est]
        
        # Ajuste por mínimos cuadrados no lineales
        popt, pcov = curve_fit(modelo_exponencial_fg, t_arr, i_arr, p0=p0, maxfev=5000)
        return popt.tolist()  # Retorna [I_final, I_0, tau] óptimos
    except Exception as e:
        return None

# --- EVOLUCIÓN TEMPORAL ABSOLUTA (CORRIENTES) ---
def graficar_dispositivos(titulo, ylabel, lista_dispositivos, tipo_tanda):
    fig_mpl, ax = plt.subplots(figsize=(10, 5))
    fig_ply = go.Figure()
    hay_datos = False    
    
    for disp in lista_dispositivos:
        tiempos, valores = [], []
        for nro in range(0, 100):
            if tipo_tanda == "FG_tanda1":
                sufijo = ".ri"
                prefijo_archivo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_"
            elif tipo_tanda == "FG_tanda2":
                sufijo = "_2.ri"
                prefijo_archivo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_"
            elif tipo_tanda == "FOXFET":
                sufijo = ".ri"
                prefijo_archivo = f"MOSISV72M_DIE4_{disp}_IV_VD=5V_postrad{nro}_"
                
            archivo_encontrado = None    
            for m_ver in ["M2", "M1"]:
                nombre_buscar = f"{prefijo_archivo}{m_ver}{sufijo}"
                datos = matchear_archivos(nombre_buscar)
                if datos:
                    archivo_encontrado = datos[0]
                    break
            
            if archivo_encontrado is not None:
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
                    else:
                        if i <= 9: t += 10
                        elif i <= 21: t += 15
                        elif i <= 24: t += 20
                        elif i <= 27: t += 25
                        elif i <= 29: t += 30
                        elif i <= 30: t += 35
                        else: t += 10
                
                voltajes = archivo_encontrado[:, 0]
                corrientes = archivo_encontrado[:, 1]
                
                if tipo_tanda == "FOXFET":
                    corrientes_abs = np.abs(corrientes)
                    indices_orden = np.argsort(corrientes_abs)
                    v_interp = np.interp(1e-5, corrientes_abs[indices_orden], voltajes[indices_orden])
                    valores.append(v_interp)
                    tiempos.append(t)
                else:
                    idx = np.where(np.round(voltajes, 1) == -4.5)[0]
                    if len(idx) > 0:
                        valores.append(np.abs(corrientes[idx[0]] * 1e6))
                        tiempos.append(t)
                        
        if tiempos:
            indices_finales = np.argsort(tiempos)
            tiempos_ordenados = np.array(tiempos)[indices_finales]
            valores_ordenados = np.array(valores)[indices_finales]
            
            ax.plot(tiempos_ordenados, valores_ordenados, "x", label=f"{disp} (Medido)")
            fig_ply.add_trace(go.Scatter(x=tiempos_ordenados, y=valores_ordenados, mode='markers', name=f"{disp} (Medido)"))
            
            # Ajuste Exponencial Físico para Floating Gates
            if tipo_tanda != "FOXFET":
                popt = calcular_fit_exponencial_cached(tiempos_ordenados.tolist(), valores_ordenados.tolist())
                if popt is not None:
                    i_final_opt, i_0_opt, tau_opt = popt
                    t_continuo = np.linspace(tiempos_ordenados.min(), tiempos_ordenados.max(), 200)
                    i_fitteada = modelo_exponencial_fg(t_continuo, i_final_opt, i_0_opt, tau_opt)
                    
                    ax.plot(t_continuo, i_fitteada, "-", label=f"{disp} (Fit Exponencial)")
                    fig_ply.add_trace(go.Scatter(x=t_continuo, y=i_fitteada, mode='lines', name=f"{disp} (Fit Exp)"))
                    
            hay_datos = True
            
    if hay_datos:
        ax.set_title(titulo)
        ax.set_xlabel("Tiempo Acumulado [min]")
        ax.set_ylabel(ylabel)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig_mpl)
        
        fig_ply.update_layout(title=titulo, xaxis_title="Tiempo Acumulado [min]", yaxis_title=ylabel.replace("$", ""), template="plotly_white")
        st.plotly_chart(fig_ply, width='stretch')
    plt.close(fig_mpl)


# --- SENSIBILIDAD EJE X NORMALIZADO ---
def graficar_sensibilidad_fg(titulo, lista_dispositivos, tipo_tanda):
    fig_mpl, ax = plt.subplots(figsize=(10, 5))
    fig_ply = go.Figure()
    hay_datos = False    
    
    for disp in lista_dispositivos:
        tiempos, valores = [], []
        for nro in range(0, 100):
            sufijo = ".ri" if tipo_tanda == "FG_tanda1" else "_2.ri"
            prefijo_archivo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_"
            
            archivo_encontrado = None    
            for m_ver in ["M2", "M1"]:
                nombre_buscar = f"{prefijo_archivo}{m_ver}{sufijo}"
                datos = matchear_archivos(nombre_buscar)
                if datos:
                    archivo_encontrado = datos[0]
                    break
            
            if archivo_encontrado is not None:
                t = 0
                for i in range(1, nro + 1):
                    if i <= 9: t += 10
                    elif i <= 21: t += 15
                    elif i <= 24: t += 20
                    elif i <= 27: t += 25
                    elif i <= 29: t += 30
                    elif i <= 30: t += 35
                    else: t += 10
                
                voltajes = archivo_encontrado[:, 0]
                corrientes = archivo_encontrado[:, 1]
                idx = np.where(np.round(voltajes, 1) == -4.5)[0]
                if len(idx) > 0:
                    valores.append(np.abs(corrientes[idx[0]] * 1e6))
                    tiempos.append(t)
                        
        if tiempos:
            indices_finales = np.argsort(tiempos)
            tiempos_ord = np.array(tiempos)[indices_finales]
            corrientes_ord = np.array(valores)[indices_finales]
            
            factor = factores_normalizacion.get(disp, 1.0)
            corrientes_norm = corrientes_ord / factor
            
            # Hacemos el fit sobre los datos normalizados
            popt = calcular_fit_exponencial_cached(tiempos_ord.tolist(), corrientes_norm.tolist())
            
            if popt is not None:
                i_final_opt, i_0_opt, tau_opt = popt
                tiempos_continuos = np.linspace(tiempos_ord.min(), tiempos_ord.max(), 200)
                
                # Derivada analítica exacta: dI/dt = | -((I_0 - I_final) / tau) * exp(-t/tau) |
                eje_y_tasas = np.abs(-((i_0_opt - i_final_opt) / tau_opt) * np.exp(-tiempos_continuos / tau_opt))
                
                # Eje X continuo: evaluación de la corriente normalizada estimada
                eje_x_promedios = modelo_exponencial_fg(tiempos_continuos, i_final_opt, i_0_opt, tau_opt)
                
                ax.plot(eje_x_promedios, eje_y_tasas, "-", label=f"{disp} (Exp Fit)")
                fig_ply.add_trace(go.Scatter(x=eje_x_promedios, y=eje_y_tasas, mode='lines', name=f"{disp} (Exp)"))
                hay_datos = True
            
    if hay_datos:
        ax.set_title(titulo)
        ax.set_xlabel(r"Corriente Promedio Normalizada $I_{D\_norm}$ [u.a.]")
        ax.set_ylabel(r"Tasa de Cambio [($\mu$A/unid_norm)/min]")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig_mpl)
        
        fig_ply.update_layout(title=titulo, xaxis_title="Corriente Promedio Normalizada I_D_norm [u.a.]", yaxis_title="Tasa de Cambio [(uA/unid_norm)/min]", template="plotly_white")
        st.plotly_chart(fig_ply, width='stretch')
    plt.close(fig_mpl)

# --- SENSIBILIDAD EJE X ABSOLUTO ---
def graficar_sensibilidad_fg_absoluta(titulo, lista_dispositivos, tipo_tanda):
    fig_mpl, ax = plt.subplots(figsize=(10, 5))
    fig_ply = go.Figure()
    hay_datos = False    
    
    for disp in lista_dispositivos:
        tiempos, valores = [], []
        for nro in range(0, 100):
            sufijo = ".ri" if tipo_tanda == "FG_tanda1" else "_2.ri"
            prefijo_archivo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_"
            
            archivo_encontrado = None    
            for m_ver in ["M2", "M1"]:
                nombre_buscar = f"{prefijo_archivo}{m_ver}{sufijo}"
                datos = matchear_archivos(nombre_buscar)
                if datos:
                    archivo_encontrado = datos[0]
                    break
            
            if archivo_encontrado is not None:
                t = 0
                for i in range(1, nro + 1):
                    if i <= 9: t += 10
                    elif i <= 21: t += 15
                    elif i <= 24: t += 20
                    elif i <= 27: t += 25
                    elif i <= 29: t += 30
                    elif i <= 30: t += 35
                    else: t += 10
                
                voltajes = archivo_encontrado[:, 0]
                corrientes = archivo_encontrado[:, 1]
                idx = np.where(np.round(voltajes, 1) == -4.5)[0]
                if len(idx) > 0:
                    valores.append(np.abs(corrientes[idx[0]] * 1e6))
                    tiempos.append(t)
                        
        if tiempos:
            indices_finales = np.argsort(tiempos)
            tiempos_ord = np.array(tiempos)[indices_finales]
            corrientes_ord = np.array(valores)[indices_finales]
            
            # Hacemos el fit sobre las corrientes absolutas
            popt = calcular_fit_exponencial_cached(tiempos_ord.tolist(), corrientes_ord.tolist())
            
            if popt is not None:
                i_final_opt, i_0_opt, tau_opt = popt
                tiempos_continuos = np.linspace(tiempos_ord.min(), tiempos_ord.max(), 200)
                
                # Derivada analítica absoluta: dI_abs/dt
                eje_y_tasas_abs = np.abs(-((i_0_opt - i_final_opt) / tau_opt) * np.exp(-tiempos_continuos / tau_opt))
                
                # Eje X continuo: corrientes absolutas promedio
                eje_x_promedios_abs = modelo_exponencial_fg(tiempos_continuos, i_final_opt, i_0_opt, tau_opt)
                
                ax.plot(eje_x_promedios_abs, eje_y_tasas_abs, "-", label=f"{disp} (Exp Fit)")
                fig_ply.add_trace(go.Scatter(x=eje_x_promedios_abs, y=eje_y_tasas_abs, mode='lines', name=f"{disp} (Exp)"))
                hay_datos = True
            
    if hay_datos:
        ax.set_title(titulo)
        ax.set_xlabel(r"Corriente Promedio Absoluta $I_D$ [$\mu$A]")
        ax.set_ylabel(r"Tasa de Cambio Absoluta [$\mu$A/min]")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig_mpl)
        
        fig_ply.update_layout(title=titulo, xaxis_title="Corriente Promedio Absoluta I_D [uA]", yaxis_title="Tasa de Cambio Absoluta [uA/min]", template="plotly_white")
        st.plotly_chart(fig_ply, width='stretch')
    plt.close(fig_mpl)
