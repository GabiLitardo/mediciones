# graficos.py
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from procesamiento import calcular_fit_polinomico_cached

def graficar_dispositivos(titulo, ylabel, datos_procesados):
    """Dibuja la evolución temporal absoluta de corrientes o voltajes interpolados."""
    fig_mpl, ax = plt.subplots(figsize=(10, 5))
    fig_ply = go.Figure()
    hay_datos = False    
    
    for disp, datos in datos_procesados.items():
        tiempos_ordenados = datos["tiempos"]
        valores_ordenados = datos["valores"]
        
        # 1. Graficamos los puntos crudos medidos
        ax.plot(tiempos_ordenados, valores_ordenados, "x", label=f"{disp} (Medido)")
        fig_ply.add_trace(go.Scatter(x=tiempos_ordenados, y=valores_ordenados, mode='markers', name=f"{disp} (Medido)"))
        
        # 2. Si no es FOXFET (detectado por la unidad en ylabel), superponemos la curva continua del polinomio
        if "Tensión [V]" not in ylabel:
            try:
                # Reutilizamos el fit desde la caché de procesamiento para dibujar la línea continua suave
                coefs = calcular_fit_polinomico_cached(disp, "FG_tanda1", tiempos_ordenados.tolist(), valores_ordenados.tolist())
                if coefs is None: # Intenta con la tanda 2 si no
                    coefs = calcular_fit_polinomico_cached(disp, "FG_tanda2", tiempos_ordenados.tolist(), valores_ordenados.tolist())
                
                if coefs is not None:
                    a, b, c, d, e = coefs
                    t_continuo = np.linspace(tiempos_ordenados.min(), tiempos_ordenados.max(), 200)
                    i_fitteada = a * (t_continuo ** 4) + b * (t_continuo ** 3) + c * (t_continuo ** 2) + d * t_continuo + e
                    
                    ax.plot(t_continuo, i_fitteada, "-", label=f"{disp} (Fit Poly g4)")
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
    
def graficar_evolucion_vg(titulo, datos_procesados):
    """Dibuja la descarga temporal equivalente en voltaje V_FG."""
    fig_mpl, ax = plt.subplots(figsize=(10, 5))
    fig_ply = go.Figure()
    hay_datos = False    
    
    for disp, datos in datos_procesados.items():
        tiempos_ordenados = datos["tiempos"]
        valores_ordenados = datos["valores"]
        
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

def graficar_sensibilidad_fg(titulo, datos_sensibilidad):
    """Dibuja la sensibilidad normalizada (Versión 1: Polinómica Analítica)."""
    fig_mpl, ax = plt.subplots(figsize=(10, 5))
    fig_ply = go.Figure()
    hay_datos = False    
    
    for disp, datos in datos_sensibilidad.items():
        ax.plot(datos["x"], datos["y"], "-", label=f"{disp} (Poly Fit g4)")
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines', name=f"{disp} (Poly)"))
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

def graficar_sensibilidad_fg_absoluta(titulo, datos_sensibilidad):
    """Dibuja la sensibilidad absoluta sin normalizar (Versión 1: Polinómica Analítica)."""
    fig_mpl, ax = plt.subplots(figsize=(10, 5))
    fig_ply = go.Figure()
    hay_datos = False    
    
    for disp, datos in datos_sensibilidad.items():
        ax.plot(datos["x"], datos["y"], "-", label=f"{disp} (Poly Fit g5)")
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines', name=f"{disp} (Poly)"))
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

def graficar_sensibilidad_fg2(titulo, datos_sensibilidad):
    """Dibuja la sensibilidad normalizada (Versión 2: Diferencial Discreta)."""
    fig_mpl, ax = plt.subplots(figsize=(10, 5))
    fig_ply = go.Figure()
    hay_datos = False    

    for disp, datos in datos_sensibilidad.items():
        ax.plot(datos["x"], datos["y"], "o--", label=disp)
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines+markers', name=disp))
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

def graficar_sensibilidad_fg_absoluta2(titulo, datos_sensibilidad):
    """Dibuja la sensibilidad absoluta sin normalizar (Versión 2: Diferencial Discreta)."""
    fig_mpl, ax = plt.subplots(figsize=(10, 5))
    fig_ply = go.Figure()
    hay_datos = False    

    for disp, datos in datos_sensibilidad.items():
        ax.plot(datos["x"], datos["y"], "o--", label=disp)
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines+markers', name=disp))
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
