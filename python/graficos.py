# graficos.py
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
from proc_sens import calcular_fit_polinomico

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

def graficar_curvas(titulo, dict_datos, xlabel, ylabel, modo='markers+lines', es_log=False):
    """Función genérica pública para graficar series simples o anidadas."""
    fig = go.Figure()
    for disp, corr_dict in dict_datos.items():
        for corr, datos in corr_dict.items():
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
            a, b, c, d, e = calcular_fit_polinomico(t.tolist(), v.tolist())
            t_cont = np.linspace(t.min(), t.max(), 200)
            i_fit = a*(t_cont**4) + b*(t_cont**3) + c*(t_cont**2) + d*t_cont + e
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
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}
    graficar_curvas(titulo, datos_temperatura, "Temperatura [°C]", r"$\text{Corriente }I_D \text{ @ }V_D \text{ = -4.5V [}\mu \text{A]}$", modo='markers+lines')

    fig_alpha = go.Figure()
    for disp, corrientes_dict in datos_temperatura.items():
        x_corr = [float(c) for c, d in corrientes_dict.items() if "alpha" in d]
        y_alpha = [d["alpha"] for c, d in corrientes_dict.items() if "alpha" in d]
        if x_corr:
            idx = np.argsort(x_corr)
            fig_alpha.add_trace(go.Scatter(x=np.array(x_corr)[idx], y=np.array(y_alpha)[idx], mode='markers+lines', name=disp, line=dict(color=colores.get(disp))))
    
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

def graficar_snr(titulo, datos_sensibilidad, datos_ruido):
    fig = go.Figure()
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}
    for disp, d_sens in datos_sensibilidad.items():
        if disp in datos_ruido:
            xr = datos_ruido[disp]["x"]
            snr = (datos_ruido[disp]["y"] / 1000.0) / np.interp(xr, d_sens["x"], d_sens["y"])
            fig.add_trace(go.Scatter(x=xr, y=snr, mode='markers+lines', name=disp, line=dict(color=colores.get(disp))))
    _renderizar_grafico(fig, dict(text=titulo, x=0.5, xanchor="center"), xaxis_kwargs=dict(title=r"$\text{Corriente Normalizada }I_{D_{norm}} \text{ [}\mu \text{A]}$"), yaxis_kwargs=dict(title="Resolución [Gy]"))

def graficar_histograma_ruido(titulo, todas_las_evos):
    fig = go.Figure()
    for disp, corrientes_dict in todas_las_evos.items():
        for corr, datos in corrientes_dict.items():
            fig.add_trace(go.Histogram(x=datos["y"] * 1000.0, name=f"{disp} @ {corr} uA", opacity=0.5, histnorm='probability density'))
    _renderizar_grafico(fig, titulo, xaxis_kwargs=dict(title="Ruido Neto [nA]"), yaxis_kwargs=dict(title="Densidad de Probabilidad"), barmode='overlay')

def graficar_error_termico_equivalente(titulo, datos_sensibilidad, datos_temp):
    fig = go.Figure()
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}
    for disp, d_sens in datos_sensibilidad.items():
        if datos_temp and disp in datos_temp:
            x_tc = [float(c) for c, d in datos_temp[disp].items() if "alpha" in d]
            a_vals = [np.abs(d["alpha"]) for c, d in datos_temp[disp].items() if "alpha" in d]
            if x_tc:
                idx = np.argsort(x_tc)
                x_arr, a_arr = np.array(x_tc)[idx], np.array(a_vals)[idx]
                err = a_arr / np.interp(x_arr, d_sens["x"], d_sens["y"])
                fig.add_trace(go.Scatter(x=x_arr, y=err, mode='markers+lines', name=disp, line=dict(color=colores.get(disp))))
    _renderizar_grafico(fig, dict(text=titulo, x=0.5, xanchor="center"), xaxis_kwargs=dict(title=r"$\text{Corriente Normalizada }I_{D_{norm}} \text{ [}\mu \text{A]}$"), yaxis_kwargs=dict(title=r"$\text{Error Térmico Equivalente [Gy/°C]}$"))

def graficar_superposicion_sens_ruido(titulo, datos_sensibilidad, datos_ruido, datos_temp):
    fig = go.Figure()
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}
    s_max = max(np.max(d["y"]) for d in datos_sensibilidad.values())
    r_max = max(np.max(d["y"]) for d in datos_ruido.values())

    datos_tc = {}
    for disp in datos_sensibilidad.keys():
        x_c, y_c = [], []
        if datos_temp and disp in datos_temp:
            for corr, d in datos_temp[disp].items():
                if "alpha" in d:
                    x_c.append(float(corr))
                    y_c.append(np.abs(d["alpha"]))
        idx = np.argsort(x_c) if x_c else []
        datos_tc[disp] = {"x": np.array(x_c)[idx], "y": np.array(y_c)[idx]}

    vals_tc = [val for d in datos_tc.values() if len(d["y"]) > 0 for val in d["y"]]
    tc_min, tc_max = (min(min(vals_tc) * 1.1, -0.05), max(max(vals_tc) * 1.1, 0.05)) if vals_tc else (-0.05, 0.05)

    for disp in datos_sensibilidad.keys():
        color = colores.get(disp)
        fig.add_trace(go.Scatter(x=datos_sensibilidad[disp]["x"], y=datos_sensibilidad[disp]["y"], mode='lines', name=f"{disp} (Sens)", line=dict(dash='solid', color=color)))
        fig.add_trace(go.Scatter(x=datos_ruido[disp]["x"], y=datos_ruido[disp]["y"], mode='markers+lines', name=f"{disp} (Ruido)", line=dict(dash='longdash', color=color), yaxis='y2'))
        if len(datos_tc[disp]["x"]) > 0:
            fig.add_trace(go.Scatter(x=datos_tc[disp]["x"], y=datos_tc[disp]["y"], mode='markers+lines', name=f"{disp} (TC)", line=dict(dash='dot', color=color), marker=dict(symbol='triangle-up-open'), yaxis='y3'))

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