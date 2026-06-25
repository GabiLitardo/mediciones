# graficos.py
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from procesamiento import matchear_archivos
from mapeo_vg import obtener_vg_por_corriente
from scipy.optimize import curve_fit

factores_normalizacion = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}

# --- MODELO TEÓRICO DE DESCARGA EXPONENCIAL ---
def modelo_doble_exponencial(t, I_inf, A, tau1, B, tau2):
    return I_inf + A * np.exp(-t / tau1) + B * np.exp(-t / tau2)
    
# --- FUNCIÓN DE FIT CON CACHÉ (CORRE UNA SOLA VEZ) ---
@st.cache_data
def calcular_fit_doble_exponencial_cached(disp_name, tipo_tanda, tiempos_list, corrientes_list):
    t_arr = np.array(tiempos_list)
    i_arr = np.array(corrientes_list)
    try:
        I_inf_est = i_arr[-1]
        Amp_total = i_arr[0] - I_inf_est
        
        p0 = [I_inf_est, Amp_total * 0.5, 30.0, Amp_total * 0.5, 300.0]
        lower_bounds = [0, 0, 1.0, 0, 10.0]
        upper_bounds = [np.inf, np.inf, 200.0, np.inf, 2000.0]
        
        popt, _ = curve_fit(
            modelo_doble_exponencial, t_arr, i_arr, 
            p0=p0, bounds=(lower_bounds, upper_bounds), maxfev=10000
        )
        
        # --- AGREGÁ ESTA LÍNEA PARA DEBUGGEAR EN LA TERMINAL ---
        print(f"📊 PARÁMETROS {disp_name}: I_inf={popt[0]:.2f}, A={popt[1]:.2f}, tau1={popt[2]:.1f}, B={popt[3]:.2f}, tau2={popt[4]:.1f}")
        
        return popt.tolist()
    except Exception as e:
        print(f"❌ Falló fit para {disp_name}: {e}")
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
            
            ax.plot(tiempos_ordenados, valores_ordenados, "o--", label=disp)
            fig_ply.add_trace(go.Scatter(x=tiempos_ordenados, y=valores_ordenados, mode='lines+markers', name=disp))
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

# --- EVOLUCIÓN TEMPORAL UNIFICADA EN VOLTAJE VFG ---
def graficar_evolucion_vg(titulo, lista_dispositivos, tipo_tanda):
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
                    corriente_ua = np.abs(corrientes[idx[0]] * 1e6)
                    try:
                        vg_val = obtener_vg_por_corriente(disp, corriente_ua * 1e-6)
                        valores.append(vg_val)
                        tiempos.append(t)
                    except:
                        continue
                        
        if tiempos:
            indices_finales = np.argsort(tiempos)
            tiempos_ordenados = np.array(tiempos)[indices_finales]
            valores_ordenados = np.array(valores)[indices_finales]
            
            ax.plot(tiempos_ordenados, valores_ordenados, "o--", label=disp)
            fig_ply.add_trace(go.Scatter(x=tiempos_ordenados, y=valores_ordenados, mode='lines+markers', name=disp))
            hay_datos = True
            
    if hay_datos:
        ax.set_title(titulo)
        ax.set_xlabel("Tiempo Acumulado [min]")
        ax.set_ylabel("Tensión $V_{FG}$ [V]")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig_mpl)
        
        fig_ply.update_layout(title=titulo, xaxis_title="Tiempo Acumulado [min]", yaxis_title="Tensión V_FG [V]", template="plotly_white")
        st.plotly_chart(fig_ply, width='stretch')
    plt.close(fig_mpl)

# --- SENSIBILIDAD EJE X NORMALIZADO (CON FIT EXPONENCIAL) ---
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
            
            # Llamamos al nuevo fit de doble exponencial
            popt = calcular_fit_doble_exponencial_cached(
                disp, tipo_tanda, tiempos_ord.tolist(), corrientes_norm.tolist()
            )
            
            if popt is not None:
                I_inf_opt, A_opt, tau1_opt, B_opt, tau2_opt = popt
                
                # Generamos base temporal continua suave
                tiempos_continuos = np.linspace(tiempos_ord.min(), tiempos_ord.max(), 200)
                
                # Derivada analítica de la doble exponencial: dI/dt = | - (A/tau1)*e^(-t/tau1) - (B/tau2)*e^(-t/tau2) |
                eje_y_tasas = np.abs(
                    -(A_opt / tau1_opt) * np.exp(-tiempos_continuos / tau1_opt) 
                    -(B_opt / tau2_opt) * np.exp(-tiempos_continuos / tau2_opt)
                )
                
                # Eje X continuo evaluado en el modelo
                eje_x_promedios = modelo_doble_exponencial(tiempos_continuos, I_inf_opt, A_opt, tau1_opt, B_opt, tau2_opt)
                
                label_curva = f"{disp} (\\tau_1={tau1_opt:.1f}, \\tau_2={tau2_opt:.1f} min)"
                ax.plot(eje_x_promedios, eje_y_tasas, "-", label=label_curva)
                fig_ply.add_trace(go.Scatter(x=eje_x_promedios, y=eje_y_tasas, mode='lines', name=f"{disp} (Doble Fit)"))
                hay_datos = True
            else:
                # Fallback ruidoso tradicional por si no converge
                eje_x_promedios, eje_y_tasas = [], []
                for k in range(len(corrientes_norm) - 1):
                    dt = tiempos_ord[k+1] - tiempos_ord[k]
                    if dt > 0:
                        tasa = np.abs(corrientes_norm[k+1] - corrientes_norm[k]) / dt
                        promedio_i_norm = (corrientes_norm[k+1] + corrientes_norm[k]) / 2.0
                        eje_y_tasas.append(tasa)
                        eje_x_promedios.append(promedio_i_norm)
                
                if eje_x_promedios:
                    ax.plot(eje_x_promedios, eje_y_tasas, "o--", label=disp)
                    fig_ply.add_trace(go.Scatter(x=eje_x_promedios, y=eje_y_tasas, mode='lines+markers', name=disp))
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
            
            eje_x_promedios_abs, eje_y_tasas_abs = [], []
            for k in range(len(corrientes_ord) - 1):
                dt = tiempos_ord[k+1] - tiempos_ord[k]
                if dt > 0:
                    tasa_abs = np.abs(corrientes_ord[k+1] - corrientes_ord[k]) / dt
                    promedio_i_abs = (corrientes_ord[k+1] + corrientes_ord[k]) / 2.0
                    eje_y_tasas_abs.append(tasa_abs)
                    eje_x_promedios_abs.append(promedio_i_abs)
            
            if eje_x_promedios_abs:
                ax.plot(eje_x_promedios_abs, eje_y_tasas_abs, "o--", label=disp)
                fig_ply.add_trace(go.Scatter(x=eje_x_promedios_abs, y=eje_y_tasas_abs, mode='lines+markers', name=disp))
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
