# graficos.py
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from proc_sens import calcular_fit_polinomico

def graficar_dispositivos(titulo, ylabel, datos_procesados, tanda, es_fg):
    """Dibuja la evolución temporal absoluta de corrientes o tensiones interpoladas."""
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
    
def graficar_sensibilidad_fg(titulo, datos_sensibilidad, xlabel, ylabel):
    """Dibuja la sensibilidad normalizada"""
    fig_mpl = plt.figure(figsize=(10, 5))
    fig_ply = go.Figure()
    
    datos_sensibilidad_continuo = datos_sensibilidad[0]
    for disp, datos in datos_sensibilidad_continuo.items():
        plt.plot(datos["x"], datos["y"], "-", label=f"{disp} (Poly Fit g4)")
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines', name=f"{disp} (Poly)"))
    
    datos_sensibilidad_discreto = datos_sensibilidad[1]
    for disp, datos in datos_sensibilidad_discreto.items():
        plt.plot(datos["x"], datos["y"], "o--", label=disp)
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines+markers', name=disp))
        
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    st.pyplot(fig_mpl)
    
    fig_ply.update_layout(title=titulo, xaxis_title=r"Corriente Promedio Normalizada I_D_norm [$\mu$A]", yaxis_title=r"Tasa de Cambio normalizada[($\mu$A)/min]", template="plotly_white")

    st.plotly_chart(fig_ply, width='stretch')
    plt.close(fig_mpl)

def graficar_ruido(titulo, datos_ruido):
    plt.figure(figsize=(10, 5))
    fig_ply = go.Figure()
    
    for disp, datos in datos_ruido.items():
        x_data = datos["x"]
        y_data = datos["y"]
        
        plt.plot(x_data, y_data, "x", label=disp)
        fig_ply.add_trace(go.Scatter(x=x_data, y=y_data, mode='markers', name=disp))
            
    plt.title(titulo)
    plt.xlabel(r"Corriente Nominal $I_D$ [$\mu$A]")
    plt.ylabel("Desvío de Ruido [nA]")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    st.pyplot(plt.gcf())
    
    fig_ply.update_layout(
        title=titulo, 
        xaxis_title="Corriente Nominal I_D [uA]", 
        yaxis_title="Desvío de Ruido [nA]", 
        template="plotly_white"
    )
    st.plotly_chart(fig_ply, width='stretch')
    plt.close()

def graficar_superposicion_sens_ruido(titulo, datos_sensibilidad, datos_ruido):
    fig_ply = go.Figure()
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}
    
    s_max = max(np.max(d["y"]) for d in datos_sensibilidad.values())
    r_max = max(np.max(d["y"]) for d in datos_ruido.values())

    tc_max = 0.15 
    datos_tc = {
        "PFGIW1": {"x": datos_ruido["PFGIW1"]["x"], "y": np.array([0.12, 0.09, 0.07, 0.05, 0.03])},
        "PFGIW2": {"x": datos_ruido["PFGIW2"]["x"], "y": np.array([0.14, 0.11, 0.08, 0.06, 0.04])},
        "PFGIP2": {"x": datos_ruido["PFGIP2"]["x"], "y": np.array([0.08, 0.06, 0.05, 0.04, 0.02])}
    }
    for disp in datos_sensibilidad.keys():
        color = colores.get(disp, None)
        
        fig_ply.add_trace(go.Scatter(
            x=datos_sensibilidad[disp]["x"], y=datos_sensibilidad[disp]["y"],
            mode='lines', name=f"{disp} (Sens)", line=dict(color=color)
        ))
        
        fig_ply.add_trace(go.Scatter(
            x=datos_ruido[disp]["x"], y=datos_ruido[disp]["y"],
            mode='markers+lines', name=f"{disp} (Ruido)", 
            line=dict(dash='dash', color=color), yaxis='y2'
        ))
        '''
        fig_ply.add_trace(go.Scatter(
            x=datos_tc[disp]["x"], y=datos_tc[disp]["y"],
            mode='markers+lines', name=f"{disp} (TC)", 
            line=dict(dash='dot', color=color), marker=dict(symbol='square'), yaxis='y3'
        ))
    '''
    fig_ply.update_layout(
        title=dict(
            text=titulo,
            y=0.98,
            yanchor="top",
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            title=r"Corriente Normalizada $I_{D_norm}$ [$\mu$A]",
            domain=[0, 0.82]
        ),
        yaxis=dict(
            title=dict(text="Tasa de Cambio Absoluta [uA/min]", font=dict(color="#1f77b4")),
            range=[0, s_max * 1.1]
        ),
        yaxis2=dict(
            title=dict(text="Desvío de Ruido [nA]", font=dict(color="#ff7f0e")),
            range=[0, r_max * 1.1],
            overlaying='y', side='right'
        ),
        yaxis3=dict(
            title=dict(text="Coeficiente Térmico [%/°C]", font=dict(color="#2ca02c")),
            range=[0, tc_max * 1.1],
            overlaying='y', side='right',
            anchor='free', position=0.94
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.4
        ),
        template="plotly_white"
    )
    st.plotly_chart(fig_ply, width='stretch')
