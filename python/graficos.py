# graficos.py
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
from proc_sens import calcular_fit_polinomico

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

def _graficar_relacion_normalizada(titulo, datos_numerador, datos_sensibilidad, ylabel, factor_escala=1.0):
    """
    Función auxiliar genérica para graficar (Métrica / Sensibilidad) vs Corriente Normalizada.
    Sirve tanto para Error por Ruido (sigma/S) como para Error Térmico (|alpha|/S).
    """
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
    for disp, subdict in dict_datos.items():
        if "x" in subdict and "y" in subdict:
            fig.add_trace(go.Scatter(x=subdict["x"], y=subdict["y"], mode=modo, name=str(disp)))
        else:
            for corr, datos in subdict.items():
                fig.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode=modo, name=f"{disp} @ {corr} uA"))
            
    _renderizar_grafico(
        fig, titulo,
        xaxis_kwargs=dict(title=xlabel, type="log" if es_log else "-"),
        yaxis_kwargs=dict(title=ylabel)
    )

def graficar_dispositivos(titulo, ylabel, datos_procesados):
    fig = go.Figure()
    for disp, datos in datos_procesados.items():
        t, v = datos["tiempos"], datos["valores"]
        fig.add_trace(go.Scatter(x=t, y=v, mode='markers', name=f"{disp} (Medido)"))
        if disp in ["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"]:
            coefs = calcular_fit_polinomico(t.tolist(), v.tolist())
            t_cont = np.linspace(t.min(), t.max(), 200)
            i_fit = np.polyval(coefs, t_cont)
            fig.add_trace(go.Scatter(x=t_cont, y=i_fit, mode='lines', name=f"{disp} (Fit Poly g4)"))
    _renderizar_grafico(fig, titulo, xaxis_kwargs=dict(title="Tiempo de irradiación [min]"), yaxis_kwargs=dict(title=ylabel))

def graficar_sensibilidad_fg(titulo, datos_sensibilidad, xlabel, ylabel):
    fig = go.Figure()
    for disp, datos in datos_sensibilidad[0].items():
        fig.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines', name=f"{disp} (Poly)"))
    for disp, datos in datos_sensibilidad[1].items():
        fig.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines+markers', name=disp))
    _renderizar_grafico(fig, titulo, xaxis_kwargs=dict(title=xlabel), yaxis_kwargs=dict(title=ylabel))

def graficar_I_vs_T(titulo, datos_temperatura):
    graficar_curvas(titulo, datos_temperatura, "Temperatura [°C]", r"$\text{Corriente }I_D \text{ @ }V_D \text{ = -4.5V [}\mu \text{A]}$", modo='markers+lines')

    fig_alpha = go.Figure()
    for disp, corrientes_dict in datos_temperatura.items():
        x_corr = [float(c) for c, d in corrientes_dict.items() if "alpha" in d]
        y_alpha = [d["alpha"] for c, d in corrientes_dict.items() if "alpha" in d]
        if x_corr:
            idx = np.argsort(x_corr)
            fig_alpha.add_trace(go.Scatter(x=np.array(x_corr)[idx], y=np.array(y_alpha)[idx], mode='markers+lines', name=disp, line=dict(color=COLORES_DISPOSITIVOS.get(disp))))
    
    if fig_alpha.data:
        _renderizar_grafico(fig_alpha, dict(text=r"$\text{Coeficiente Térmico (}\alpha\text{) vs Corriente Nominal}$", y=0.95, x=0.5, xanchor='center', yanchor='top'), xaxis_kwargs=dict(title=r"$\text{Corriente Nominal }I_D\text{ [}\mu \text{A]}$"), yaxis_kwargs=dict(title=r"$\text{Coeficiente Térmico }\alpha\text{ [}\mu \text{A/°C]}$"))

def graficar_evolucion_temperatura(titulo, datos_temp):
    fig = go.Figure()
    for disp, corrientes_dict in datos_temp.items():
        for corr, datos in corrientes_dict.items():
            gid = f"temp_{disp}_{corr}uA"
            fig.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines', name=f"{disp} @ {corr} uA", legendgroup=gid, opacity=0.5))
            if datos.get("y_fit") is not None:
                fig.add_trace(go.Scatter(x=datos["x"], y=datos["y_fit"], mode='lines', name=f"{disp} @ {corr} uA (Fit)", legendgroup=gid, showlegend=False, line=dict(width=2, dash='dash')))
    _renderizar_grafico(fig, titulo, xaxis_kwargs=dict(title="Tiempo [s]"), yaxis_kwargs=dict(title="Temperatura [°C]"))

def graficar_corriente_vs_temperatura_ruido(titulo, todas_las_evos_i_vs_t):
    fig = go.Figure()
    for disp, corrientes_dict in todas_las_evos_i_vs_t.items():
        for corr, datos in corrientes_dict.items():
            gid = f"{disp}_{corr}uA"
            fig.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='markers', name=f"{disp} @ {corr} uA", legendgroup=gid, marker=dict(size=4), opacity=0.6))
            fig.add_trace(go.Scatter(x=datos["x"], y=datos["y_fit"], mode='lines', name=f"{disp} @ {corr} uA (Fit)", legendgroup=gid, showlegend=False, line=dict(width=2)))
    _renderizar_grafico(fig, titulo, xaxis_kwargs=dict(title="Temperatura [°C]"), yaxis_kwargs=dict(title=r"$\text{Corriente }I_D \text{ [}\mu \text{A]}$"))

def graficar_error_ruido_equivalente(titulo, datos_sensibilidad, datos_ruido):
    _graficar_relacion_normalizada(titulo, datos_ruido, datos_sensibilidad, "Error Equivalente por Ruido [Gy]", factor_escala=1/1000.0)

def graficar_error_termico_equivalente(titulo, datos_sensibilidad, datos_temp):
    _graficar_relacion_normalizada(titulo, datos_temp, datos_sensibilidad, r"$\text{Error Térmico Equivalente [Gy/°C]}$")

def graficar_histograma_ruido(titulo, todas_las_evos):
    fig = go.Figure()
    for disp, corrientes_dict in todas_las_evos.items():
        for corr, datos in corrientes_dict.items():
            fig.add_trace(go.Histogram(x=datos["y"] * 1000.0, name=f"{disp} @ {corr} uA", opacity=0.5, histnorm='probability density'))
    _renderizar_grafico(fig, titulo, xaxis_kwargs=dict(title="Ruido Neto [nA]"), yaxis_kwargs=dict(title="Densidad de Probabilidad"), barmode='overlay')
