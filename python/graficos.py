# graficos.py
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from proc_sens import calcular_fit_polinomico

def graficar_dispositivos(titulo, ylabel, datos_procesados, tanda, es_fg):
    """Dibuja la evolución temporal absoluta de corrientes o voltajes interpolados."""
    fig_mpl = plt.figure(figsize=(10, 5))
    fig_ply = go.Figure()    
    for disp, datos in datos_procesados.items():
        tiempos_ordenados = datos["tiempos"]
        valores_ordenados = datos["valores"]
        plt.plot(tiempos_ordenados, valores_ordenados, "x", label=f"{disp} (Medido)")
        fig_ply.add_trace(go.Scatter(x=tiempos_ordenados, y=valores_ordenados, mode='markers', name=f"{disp} (Medido)"))
        if es_fg:
            if tanda == 1:
                coefs = calcular_fit_polinomico(tiempos_ordenados.tolist(), valores_ordenados.tolist())
            if tanda == 2:
                coefs = calcular_fit_polinomico(tiempos_ordenados.tolist(), valores_ordenados.tolist())
            a, b, c, d, e = coefs
            t_continuo = np.linspace(tiempos_ordenados.min(), tiempos_ordenados.max(), 200)
            i_fitteada = a * (t_continuo ** 4) + b * (t_continuo ** 3) + c * (t_continuo ** 2) + d * t_continuo + e
            plt.plot(t_continuo, i_fitteada, "-", label=f"{disp} (Fit Poly g4)")
            fig_ply.add_trace(go.Scatter(x=t_continuo, y=i_fitteada, mode='lines', name=f"{disp} (Fit Poly g4)"))        
    plt.title(titulo)
    plt.xlabel("Tiempo Acumulado [min]")
    plt.ylabel(ylabel)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    st.pyplot(fig_mpl)
    fig_ply.update_layout(title=titulo, xaxis_title="Tiempo Acumulado [min]", yaxis_title=ylabel, template="plotly_white")
    st.plotly_chart(fig_ply, width='stretch')
    plt.close(fig_mpl)
    
def graficar_evolucion_vg(titulo, datos_procesados):
    """Dibuja la descarga temporal equivalente en tensión V_FG."""
    fig_mpl = plt.figure(figsize=(10, 5))
    fig_ply = go.Figure()
    for disp, datos in datos_procesados.items():
        tiempos_ordenados = datos["tiempos"]
        valores_ordenados = datos["valores"]
        plt.plot(tiempos_ordenados, valores_ordenados, "o--", label=disp)
        fig_ply.add_trace(go.Scatter(x=tiempos_ordenados, y=valores_ordenados, mode='lines+markers', name=disp))       
    plt.title(titulo)
    plt.xlabel("Tiempo Acumulado [min]")
    plt.ylabel(r"Tensión $V_{FG}$ [V]")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    st.pyplot(fig_mpl)
    fig_ply.update_layout(title=titulo, xaxis_title="Tiempo Acumulado [min]", yaxis_title=r"Tensión $V_{FG}$ [V]", template="plotly_white")
    st.plotly_chart(fig_ply, width='stretch')
    plt.close(fig_mpl)

def graficar_sensibilidad_fg(titulo, datos_sensibilidad):
    """Dibuja la sensibilidad normalizada"""
    fig_mpl = plt.figure(figsize=(10, 5))
    fig_ply = go.Figure()
    
    for disp, datos in datos_sensibilidad.items():
        plt.plot(datos["x"], datos["y"], "-", label=f"{disp} (Poly Fit g4)")
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines', name=f"{disp} (Poly)"))
        
    plt.title(titulo)
    plt.xlabel(r"Corriente Promedio Normalizada $I_{D\_norm}$ [$\mu$A]")
    plt.ylabel(r"Tasa de Cambio normalizada [($\mu$A)/min]")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    st.pyplot(fig_mpl)
    
    fig_ply.update_layout(title=titulo, xaxis_title=r"Corriente Promedio Normalizada I_D_norm [$\mu$A]", yaxis_title=r"Tasa de Cambio normalizada[($\mu$A)/min]", template="plotly_white")
    st.plotly_chart(fig_ply, width='stretch')
    plt.close(fig_mpl)

def graficar_sensibilidad_fg_absoluta(titulo, datos_sensibilidad):
    """Dibuja la sensibilidad absoluta sin normalizar (Versión 1: Polinómica Analítica)."""
    fig_mpl = plt.figure(figsize=(10, 5))
    fig_ply = go.Figure()
    hay_datos = False    
    
    for disp, datos in datos_sensibilidad.items():
        plt.plot(datos["x"], datos["y"], "-", label=f"{disp} (Poly Fit g4)")
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines', name=f"{disp} (Poly)"))
            
    plt.title(titulo)
    plt.xlabel(r"Corriente Promedio Absoluta $I_D$ [$\mu$A]")
    plt.ylabel(r"Tasa de Cambio Absoluta [$\mu$A/min]")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    st.pyplot(fig_mpl)
    
    fig_ply.update_layout(title=titulo, xaxis_title="Corriente Promedio Absoluta I_D [uA]", yaxis_title=r"Tasa de Cambio Absoluta [$\mu$A/min]", template="plotly_white")
    st.plotly_chart(fig_ply, width='stretch')
    plt.close(fig_mpl)

def graficar_sensibilidad_fg2(titulo, datos_sensibilidad):
    """Dibuja la sensibilidad normalizada (Versión 2: Diferencial Discreta)."""
    fig_mpl = plt.figure(figsize=(10, 5))
    fig_ply = go.Figure()

    for disp, datos in datos_sensibilidad.items():
        plt.plot(datos["x"], datos["y"], "o--", label=disp)
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines+markers', name=disp))

    plt.title(titulo)
    plt.xlabel(r"Corriente Promedio Normalizada $I_{D\_norm}$ [$\mu$A]")
    plt.ylabel(r"Tasa de Cambio normalizada[($\mu$A)/min]")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    st.pyplot(fig_mpl)

    fig_ply.update_layout(title=titulo, xaxis_title=r"Corriente Promedio Normalizada $I_D$ [$\mu$A]", yaxis_title=r"Tasa de Cambio normalizada [($\mu$A)/min]", template="plotly_white")
    st.plotly_chart(fig_ply, width='stretch')
    plt.close(fig_mpl)

def graficar_sensibilidad_fg_absoluta2(titulo, datos_sensibilidad):
    """Dibuja la sensibilidad absoluta sin normalizar (Versión 2: Diferencial Discreta)."""
    fig_mpl = plt.figure(figsize=(10, 5))
    fig_ply = go.Figure()

    for disp, datos in datos_sensibilidad.items():
        plt.plot(datos["x"], datos["y"], "o--", label=disp)
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines+markers', name=disp))

    plt.title(titulo)
    plt.xlabel(r"Corriente Promedio Absoluta $I_D$ [$\mu$A]")
    plt.ylabel(r"Tasa de Cambio Absoluta [$\mu$A/min]")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    st.pyplot(fig_mpl)
    fig_ply.update_layout(title=titulo, xaxis_title=r"Corriente Promedio Absoluta $I_D$ [$\mu$A]", yaxis_title=r"Tasa de Cambio Absoluta [$\mu$A/min]", template="plotly_white")
    st.plotly_chart(fig_ply, width='stretch')
    plt.close(fig_mpl)
