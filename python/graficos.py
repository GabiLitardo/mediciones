# graficos.py
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
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
    # Renderizado correcto de HTML en Streamlit
    html = pio.to_html(fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False)
    components.html(html, height=500)

def graficar_curvas(titulo, datos, xlabel, ylabel, modo='lines', es_log=False):
    """
    Función unificada para graficar cualquier conjunto de datos.
    Estructura esperada de 'datos': {"Etiqueta Leyenda": {"x": array_x, "y": array_y}}
    """
    fig = go.Figure()
    if not datos:
        st.warning(f"No hay datos para mostrar en: {titulo}")
        return

    for etiqueta, serie in datos.items():
        disp_base = etiqueta.split()[0] if " " in etiqueta else etiqueta
        color = COLORES_DISPOSITIVOS.get(disp_base)

        fig.add_trace(go.Scatter(
            x=serie["x"], 
            y=serie["y"], 
            mode=modo, 
            name=etiqueta,
            line=dict(color=color) if color else None
        ))

    _renderizar_grafico(
        fig, titulo,
        xaxis_kwargs=dict(title=xlabel, type="log" if es_log else "-"),
        yaxis_kwargs=dict(title=ylabel)
    )