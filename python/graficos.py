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

def graficar_curvas(titulo, datos, xlabel, ylabel, modo='lines', es_log=False):
    """
    Función unificada para graficar cualquier conjunto de datos.
    Estructura esperada de 'datos': {"Etiqueta Leyenda": {"x": array_x, "y": array_y}}
    """
    fig = go.Figure()
    for etiqueta, serie in datos.items():
        # Asigna color si la etiqueta coincide con el nombre base del dispositivo
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

def graficar_histograma_ruido(titulo, datos):
    """
    Dibuja histogramas de distribución usando la estructura unificada.
    Estructura esperada de 'datos': {"Etiqueta Leyenda": {"x": array_t, "y": array_ruido_uA}}
    """
    fig = go.Figure()
    for etiqueta, serie in datos.items():
        fig.add_trace(go.Histogram(
            x=serie["y"] * 1000.0, 
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

def graficar_superposicion_sens_ruido(titulo, datos_sensibilidad, datos_ruido, datos_temp):
    """Grafico compuesto de 3 ejes Y que consume datos en formato plano unificado."""
    fig = go.Figure()
    s_max = max(np.max(d["y"]) for d in datos_sensibilidad.values())
    r_max = max(np.max(d["y"]) for d in datos_ruido.values()) if datos_ruido else 1.0

    vals_tc = [val for d in datos_temp.values() for val in d["y"]] if datos_temp else []
    tc_min, tc_max = (min(min(vals_tc) * 1.1, -0.05), max(max(vals_tc) * 1.1, 0.05)) if vals_tc else (-0.05, 0.05)

    for disp in datos_sensibilidad.keys():
        color = COLORES_DISPOSITIVOS.get(disp)
        if disp in datos_sensibilidad:
            fig.add_trace(go.Scatter(x=datos_sensibilidad[disp]["x"], y=datos_sensibilidad[disp]["y"], mode='lines', name=f"{disp} (Sens)", line=dict(dash='solid', color=color)))
        if disp in datos_ruido:
            fig.add_trace(go.Scatter(x=datos_ruido[disp]["x"], y=datos_ruido[disp]["y"], mode='markers+lines', name=f"{disp} (Ruido)", line=dict(dash='longdash', color=color), yaxis='y2'))
        if datos_temp and disp in datos_temp:
            fig.add_trace(go.Scatter(x=datos_temp[disp]["x"], y=datos_temp[disp]["y"], mode='markers+lines', name=f"{disp} (TC)", line=dict(dash='dot', color=color), marker=dict(symbol='triangle-up-open'), yaxis='y3'))

    _renderizar_grafico(
        fig, titulo=dict(text=titulo, y=0.98, yanchor="top", x=0.5, xanchor="center"),
        xaxis_kwargs=dict(title=r"$\text{Corriente Normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$", domain=[0, 0.82]),
        yaxis_kwargs=dict(title=dict(text=r"$\text{Tasa de Cambio Absoluta [}\mu\text{A/min]}$", font=dict(color="#1f77b4")), range=[0, s_max * 1.1]),
        yaxis2=dict(
            title=dict(text="Desvío de Ruido [nA]", font=dict(color="#ff7f0e")), range=[0, r_max * 1.1],
            overlaying='y', side='right', showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", showline=False, zeroline=False
        ),
        yaxis3=dict(
            title=dict(text=r"$\text{Módulo de Coeficiente Térmico [}\mu\text{A/°C]}$", font=dict(color="#2ca02c")),
            range=[tc_min, tc_max], overlaying='y', side='right', anchor='free', position=0.94,
            showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", showline=False, zeroline=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5)
    )