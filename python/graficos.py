# graficos.py
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from procesamiento import matchear_archivos
from mapeo_vg import obtener_vg_por_corriente
from scipy.optimize import curve_fit

factores_normalizacion = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}

@st.cache_data
def calcular_fit_polinomico_cached(disp_name, tipo_tanda, tiempos_list, corrientes_list):
    try:
        # np.polyfit encuentra los coeficientes [a, b, c, d] exactos que minimizan el ECM
        coeficientes = np.polyfit(tiempos_list, corrientes_list, deg=5)
        return coeficientes.tolist()  # Retorna [a, b, c, d]
    except:
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
            
            # 1. Graficamos los puntos crudos medidos (en Matplotlib usamos 'x' y en Plotly marcadores solos)
            ax.plot(tiempos_ordenados, valores_ordenados, "x", label=f"{disp} (Medido)")
            fig_ply.add_trace(go.Scatter(x=tiempos_ordenados, y=valores_ordenados, mode='markers', name=f"{disp} (Medido)"))
            
            # 2. Si es Floating Gate, calculamos y superponemos la curva continua del polinomio
            if tipo_tanda != "FOXFET":
                try:
                    # Usamos la misma función con caché que creamos antes
                    coefs = calcular_fit_polinomico_cached(disp, tipo_tanda, tiempos_ordenados.tolist(), valores_ordenados.tolist())
                    if coefs is not None:
                        a, b, c, d, e, f = coefs
                        t_continuo = np.linspace(tiempos_ordenados.min(), tiempos_ordenados.max(), 200)
                        i_fitteada = a * (t_continuo ** 5) + b * (t_continuo ** 4) + c * (t_continuo ** 3) + d * (t_continuo ** 2) + e * t_continuo + f
                        
                        # Dibujamos la línea sólida del ajuste para auditarlo visualmente
                        ax.plot(t_continuo, i_fitteada, "-", label=f"{disp} (Fit Poly g5)")
                        fig_ply.add_trace(go.Scatter(x=t_continuo, y=i_fitteada, mode='lines', name=f"{disp} (Fit Poly)"))
                except:
                    pass
                    
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
            
            # Obtenemos los coeficientes del polinomio congelados en caché
            coefs = calcular_fit_polinomico_cached(
                disp, tipo_tanda, tiempos_ord.tolist(), corrientes_norm.tolist()
            )
            
            if coefs is not None:
                a, b, c, d, e, f = coefs
                
                # Creamos el vector de tiempo continuo para evaluar la curva suave
                tiempos_continuos = np.linspace(tiempos_ord.min(), tiempos_ord.max(), 200)
                
                # Derivada analítica exacta: dI/dt = |5a*t^4 + 4b*t^3 + 3c*t^2 + 2d*t + e|
                eje_y_tasas = np.abs(5 * a * (tiempos_continuos ** 4) + 4 * b * (tiempos_continuos ** 3) + 3 * c * (tiempos_continuos ** 2) + 2 * d * tiempos_continuos + e)
                
                # Eje X continuo: evaluamos el polinomio original para obtener la corriente promedio fitteada
                eje_x_promedios = a * (tiempos_continuos ** 5) + b * (tiempos_continuos ** 4) + c * (tiempos_continuos ** 3) + d * (tiempos_continuos ** 2) + e * tiempos_continuos + f
                
                ax.plot(eje_x_promedios, eje_y_tasas, "-", label=f"{disp} (Poly Fit g5)")
                fig_ply.add_trace(go.Scatter(x=eje_x_promedios, y=eje_y_tasas, mode='lines', name=f"{disp} (Poly)"))
                hay_datos = True
            else:
                # Fallback tradicional por si las moscas
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
            
            # Reutilizamos el fit polinómico con caché (acá pasamos las corrientes absolutas, sin normalizar)
            coefs = calcular_fit_polinomico_cached(
                disp, f"{tipo_tanda}_abs", tiempos_ord.tolist(), corrientes_ord.tolist()
            )
            
            if coefs is not None:
                a, b, c, d, e, f = coefs
                
                tiempos_continuos = np.linspace(tiempos_ord.min(), tiempos_ord.max(), 200)
                
                # Derivada analítica absoluta de la corriente dI_abs/dt
                eje_y_tasas_abs = np.abs(5 * a * (tiempos_continuos ** 4) + 4 * b * (tiempos_continuos ** 3) + 3 * c * (tiempos_continuos ** 2) + 2 * d * tiempos_continuos + e)
                
                # Eje X continuo: corrientes absolutas promedio estimadas por el polinomio
                eje_x_promedios_abs = a * (tiempos_continuos ** 5) + b * (tiempos_continuos ** 4) + c * (tiempos_continuos ** 3) + d * (tiempos_continuos ** 2) + e * tiempos_continuos + f
                
                ax.plot(eje_x_promedios_abs, eje_y_tasas_abs, "-", label=f"{disp} (Poly Fit g5)")
                fig_ply.add_trace(go.Scatter(x=eje_x_promedios_abs, y=eje_y_tasas_abs, mode='lines', name=f"{disp} (Poly)"))
                hay_datos = True
            else:
                # Fallback tradicional por si el fit falla
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

# --- SENSIBILIDAD EJE X NORMALIZADO ---
def graficar_sensibilidad_fg2(titulo, lista_dispositivos, tipo_tanda):
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
        ax.set_xlabel("Corriente Promedio Normalizada $I_{D\_norm}$ [u.a.]")
        ax.set_ylabel("Tasa de Cambio [($\mu$A/unid_norm)/min]")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig_mpl)

        fig_ply.update_layout(title=titulo, xaxis_title="Corriente Promedio Normalizada I_D_norm [u.a.]", yaxis_title="Tasa de Cambio [(uA/unid_norm)/min]", template="plotly_white")
        st.plotly_chart(fig_ply, use_container_width=True)
    plt.close(fig_mpl)


# --- SENSIBILIDAD EJE X ABSOLUTO ---
def graficar_sensibilidad_fg_absoluta2(titulo, lista_dispositivos, tipo_tanda):
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
        ax.set_xlabel("Corriente Promedio Absoluta $I_D$ [$\mu$A]")
        ax.set_ylabel("Tasa de Cambio Absoluta [$\mu$A/min]")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig_mpl)

        fig_ply.update_layout(title=titulo, xaxis_title="Corriente Promedio Absoluta I_D [uA]", yaxis_title="Tasa de Cambio Absoluta [uA/min]", template="plotly_white")
        st.plotly_chart(fig_ply, use_container_width=True)
    plt.close(fig_mpl)
