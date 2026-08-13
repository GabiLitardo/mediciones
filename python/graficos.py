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
            es_diccionario_temp = isinstance(datos_numerador[disp].get(next(iter(datos_numerador[disp]), {})), dict)
            
            x_vals = [float(c) for c, d in datos_numerador[disp].items() if "alpha" in d] if es_diccionario_temp else datos_numerador[disp]["x"]
            y_vals = [np.abs(d["alpha"]) for c, d in datos_numerador[disp].items() if "alpha" in d] if es_diccionario_temp else datos_numerador[disp]["y"] * factor_escala
            
            if len(x_vals) > 0:
                idx = np.argsort(x_vals)
                x_arr, y_arr = np.array(x_vals)[idx], np.array(y_vals)[idx]
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

def graficar_curvas(titulo, dict_datos, xlabel, ylabel, modo='markers+lines', es_log=False):
    fig = go.Figure()
    for etiqueta, serie in dict_datos.items():
        modo_real = 'lines' if ("(Fit" in etiqueta or "(Poly)" in etiqueta) else modo

        fig.add_trace(go.Scatter(
            x=serie["x"], 
            y=serie["y"], 
            mode=modo_real, 
            name=str(etiqueta)
        ))
            
    _renderizar_grafico(
        fig, titulo,
        xaxis_kwargs=dict(title=xlabel, type="log" if es_log else "-"),
        yaxis_kwargs=dict(title=ylabel)
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