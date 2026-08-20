# graficos.py
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

COLORES_DISPOSITIVOS = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}

def _renderizar_grafico(fig_ply, titulo, xaxis_kwargs=None, yaxis_kwargs=None, **layout_kwargs):
    xaxis = dict(showgrid=False, showline=False, zeroline=False)
    if xaxis_kwargs: 
        xaxis.update(xaxis_kwargs)
    yaxis = dict(showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", showline=False, zeroline=False)
    if yaxis_kwargs: 
        yaxis.update(yaxis_kwargs)

    fig_ply.update_layout(
        title=titulo, 
        template="plotly_dark", 
        paper_bgcolor="#0e1117", 
        plot_bgcolor="#0e1117",
        font=dict(color="white"), 
        xaxis=xaxis, 
        yaxis=yaxis, 
        **layout_kwargs
    )
    html = pio.to_html(fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False)
    st.iframe(html, height="content")

def graficar_relacion_normalizada(titulo, datos_numerador, datos_sensibilidad, ylabel, factor_escala):
    fig = go.Figure()
    for disp, d_sens in datos_sensibilidad.items():
        if datos_numerador and disp in datos_numerador:
            d_num = datos_numerador[disp]
            x_arr = np.array(d_num["x"])
            y_arr = np.array(d_num["y"]) * factor_escala
            
            if len(x_arr) > 0:
                idx = np.argsort(x_arr)
                x_arr, y_arr = x_arr[idx], y_arr[idx]
                sens_interp = np.interp(x_arr, d_sens["x"], d_sens["y"])
                
                relacion = y_arr / sens_interp
                color = COLORES_DISPOSITIVOS.get(disp)
                fig.add_trace(go.Scatter(x=x_arr, y=relacion, mode='markers+lines', name=disp, line=dict(color=color)))

    _renderizar_grafico(
        fig, 
        dict(text=titulo, x=0.5, xanchor="center"), 
        xaxis_kwargs=dict(title=r"$\text{Corriente Normalizada }I_{D_{norm}} \text{ [}\mu \text{A]}$"), 
        yaxis_kwargs=dict(title=ylabel)
    )

def graficar_curvas(titulo, dict_datos, xlabel, ylabel, modo='markers+lines', logx=False, logy=False):
    fig = go.Figure()
    for etiqueta, serie in dict_datos.items():
        nombre_str = str(etiqueta)
        es_fit = "(Fit" in nombre_str
        modo_real = 'lines' if es_fit else modo

        # Limpieza estándar de strings
        grupo_base = (
            nombre_str
            .replace(" (Medido)", "")
            .replace(" (Fit)", "")
            .strip()
        )

        fig.add_trace(go.Scatter(
            x=serie["x"], 
            y=serie["y"], 
            mode=modo_real, 
            name=grupo_base,
            legendgroup=grupo_base,
            showlegend=not es_fit
        ))
            
    _renderizar_grafico(
        fig, titulo,
        xaxis_kwargs=dict(title=xlabel, type="log" if logx else "-"),
        yaxis_kwargs=dict(title=ylabel, type="log" if logy else "-")
    )

def graficar_histograma_ruido(titulo, dict_datos):
    """
    Dibuja histogramas consumiendo la estructura plana unificada {"Etiqueta": {"x": ..., "y": ...}}.
    """
    fig = go.Figure()
    for etiqueta, datos in dict_datos.items():
        fig.add_trace(go.Histogram(
            x=datos["y"] * 1000.0, 
            name=etiqueta, 
            opacity=0.5, 
            histnorm='probability density'
        ))
    _renderizar_grafico(
        fig, titulo, 
        xaxis_kwargs=dict(title="Ruido Neto [nA]"), 
        yaxis_kwargs=dict(title="Densidad de Probabilidad"), 
        barmode='overlay'
    )