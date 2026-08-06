# graficos.py
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from proc_sens import calcular_fit_polinomico
import plotly.io as pio

def _renderizar_grafico(fig_ply, titulo, xaxis_kwargs=None, yaxis_kwargs=None, **layout_kwargs):
    """
    Función auxiliar para centralizar la configuración de estilo y el renderizado en Streamlit.
    """
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

def graficar_dispositivos(titulo, ylabel, datos_procesados, tanda, es_fg):
    fig_ply = go.Figure()    
    for disp, datos in datos_procesados.items():
        tiempos_ordenados = datos["tiempos"]
        valores_ordenados = datos["valores"]
        fig_ply.add_trace(go.Scatter(x=tiempos_ordenados, y=valores_ordenados, mode='markers', name=f"{disp} (Medido)"))
        if es_fg:
            coefs = calcular_fit_polinomico(tiempos_ordenados.tolist(), valores_ordenados.tolist())
            a, b, c, d, e = coefs
            t_continuo = np.linspace(tiempos_ordenados.min(), tiempos_ordenados.max(), 200)
            i_fitteada = a * (t_continuo ** 4) + b * (t_continuo ** 3) + c * (t_continuo ** 2) + d * t_continuo + e
            fig_ply.add_trace(go.Scatter(x=t_continuo, y=i_fitteada, mode='lines', name=f"{disp} (Fit Poly g4)"))        
    
    _renderizar_grafico(
        fig_ply, 
        titulo, 
        xaxis_kwargs=dict(title="Tiempo de irradiación [min]"),
        yaxis_kwargs=dict(title=ylabel)
    )

def graficar_sensibilidad_fg(titulo, datos_sensibilidad, xlabel, ylabel):
    fig_ply = go.Figure()
    
    datos_sensibilidad_continuo = datos_sensibilidad[0]
    for disp, datos in datos_sensibilidad_continuo.items():
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines', name=f"{disp} (Poly)"))
    
    datos_sensibilidad_discreto = datos_sensibilidad[1]
    for disp, datos in datos_sensibilidad_discreto.items():
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines+markers', name=disp))
        
    _renderizar_grafico(
        fig_ply, 
        titulo, 
        xaxis_kwargs=dict(title=xlabel),
        yaxis_kwargs=dict(title=ylabel)
    )

def graficar_ruido(titulo, datos_ruido):
    fig_ply = go.Figure()
    for disp, datos in datos_ruido.items():
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='markers', name=disp))            

    _renderizar_grafico(
        fig_ply, 
        titulo, 
        xaxis_kwargs=dict(title=r"$\text{Corriente Nominal }I_D\text{ [}\mu \text{A]}$"),
        yaxis_kwargs=dict(title="Desvío de Ruido [nA]")
    )

def graficar_superposicion_sens_ruido(titulo, datos_sensibilidad, datos_ruido, datos_temp):
    fig_ply = go.Figure()
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}
    
    s_max = max(np.max(d["y"]) for d in datos_sensibilidad.values())
    r_max = max(np.max(d["y"]) for d in datos_ruido.values())

    datos_tc = {}
    for disp in datos_sensibilidad.keys():
        x_coefs, y_coefs = [], []
        if datos_temp and disp in datos_temp:
            for corr_nominal, curvas in datos_temp[disp].items():
                if "alpha" in curvas:
                    x_coefs.append(float(corr_nominal))
                    y_coefs.append(np.abs(curvas["alpha"]))
        
        if x_coefs:
            indices_orden = np.argsort(x_coefs)
            datos_tc[disp] = {"x": np.array(x_coefs)[indices_orden], "y": np.array(y_coefs)[indices_orden]}
        else:
            datos_tc[disp] = {"x": np.array([]), "y": np.array([])}

    lista_valores_tc = [val for d in datos_tc.values() if len(d["y"]) > 0 for val in d["y"]]
    tc_min, tc_max = (min(min(lista_valores_tc) * 1.1, -0.05), max(max(lista_valores_tc) * 1.1, 0.05)) if lista_valores_tc else (-0.05, 0.05)

    for disp in datos_sensibilidad.keys():
        color = colores.get(disp, None)
        fig_ply.add_trace(go.Scatter(x=datos_sensibilidad[disp]["x"], y=datos_sensibilidad[disp]["y"], mode='lines', name=f"{disp} (Sens)", line=dict(dash='solid', color=color)))
        fig_ply.add_trace(go.Scatter(x=datos_ruido[disp]["x"], y=datos_ruido[disp]["y"], mode='markers+lines', name=f"{disp} (Ruido)", line=dict(dash='longdash', color=color), yaxis='y2'))
        if len(datos_tc[disp]["x"]) > 0:
            fig_ply.add_trace(go.Scatter(x=datos_tc[disp]["x"], y=datos_tc[disp]["y"], mode='markers+lines', name=f"{disp} (TC)", line=dict(dash='dot', color=color), marker=dict(symbol='triangle-up-open'), yaxis='y3'))

    _renderizar_grafico(
        fig_ply,
        titulo=dict(text=titulo, y=0.98, yanchor="top", x=0.5, xanchor="center"),
        xaxis_kwargs=dict(title=r"$\text{Corriente Normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$", domain=[0, 0.82]),
        yaxis_kwargs=dict(title=dict(text=r"$\text{Tasa de Cambio Absoluta [}\mu\text{A/min]}$", font=dict(color="#1f77b4")), range=[0, s_max * 1.1]),
        yaxis2=dict(
            title=dict(text="Desvío de Ruido [nA]", font=dict(color="#ff7f0e")),
            range=[0, r_max * 1.1], overlaying='y', side='right',
            showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", showline=False, zeroline=False            
        ),
        yaxis3=dict(
            title=dict(text=r"$\text{Módulo de Coeficiente Térmico [}\mu\text{A/°C]}$", font=dict(color="#2ca02c")),
            range=[tc_min, tc_max], overlaying='y', side='right', anchor='free', position=0.94,
            showgrid=True, gridcolor="rgba(255, 255, 255, 0.2)", showline=False, zeroline=False            
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5)
    )

def graficar_evolucion_ruido(titulo, todas_las_evos, es_log):
    fig_ply = go.Figure()
    for disp, evos_disp in todas_las_evos.items():
        for corr, datos in evos_disp.items():
            fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines', name=f"{disp} @ {corr} uA", opacity=0.8))
                
    _renderizar_grafico(
        fig_ply, 
        titulo, 
        xaxis_kwargs=dict(title="Tiempo [s]", type="log" if es_log else "-"),
        yaxis_kwargs=dict(title=r"$\text{Corriente de Ruido Neto [}\mu\text{A]}$")
    )

def graficar_I_vs_T(titulo, datos_temperatura):
    fig_ply = go.Figure()
    for disp, corrientes_dict in datos_temperatura.items():
        for corr, curvas in corrientes_dict.items():
            fig_ply.add_trace(go.Scatter(x=curvas["x"], y=curvas["y"], mode='markers+lines', name=f"{disp} ({corr} uA)"))
            
    _renderizar_grafico(
        fig_ply, 
        dict(text=titulo, y=0.95, x=0.5, xanchor='center', yanchor='top'),
        xaxis_kwargs=dict(title="Temperatura [°C]"),
        yaxis_kwargs=dict(title=r"$\text{Corriente }I_D \text{ @ }V_D \text{ = -4.5V [}\mu \text{A]}$"),
        margin=dict(t=100)
    )

    fig_alpha = go.Figure()
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}
    hay_datos_alpha = False

    for disp, corrientes_dict in datos_temperatura.items():
        x_corr = [float(corr) for corr, curvas in corrientes_dict.items() if "alpha" in curvas]
        y_alpha = [curvas["alpha"] for corr, curvas in corrientes_dict.items() if "alpha" in curvas]
        
        if x_corr:
            hay_datos_alpha = True
            indices = np.argsort(x_corr)
            color = colores.get(disp, None)
            fig_alpha.add_trace(go.Scatter(x=np.array(x_corr)[indices], y=np.array(y_alpha)[indices], mode='markers+lines', name=disp, line=dict(color=color) if color else None))

    if hay_datos_alpha:
        _renderizar_grafico(
            fig_alpha,
            dict(text=r"$\text{Coeficiente Térmico (}\alpha\text{) vs Corriente Nominal}$", y=0.95, x=0.5, xanchor='center', yanchor='top'),
            xaxis_kwargs=dict(title=r"$\text{Corriente Nominal }I_D\text{ [}\mu \text{A]}$"),
            yaxis_kwargs=dict(title=r"$\text{Coeficiente Térmico }\alpha\text{ [}\mu \text{A/°C]}$")
        )

def graficar_evolucion_temperatura(titulo, datos_temp):
    fig_ply = go.Figure()
    for disp, evos_disp in datos_temp.items():
        for corr, datos in evos_disp.items():
            grupo_id = f"temp_{disp}_{corr}uA"
            fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines', name=f"{disp} @ {corr} uA", legendgroup=grupo_id, opacity=0.5))
            if datos.get("y_fit") is not None:
                fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y_fit"], mode='lines', name=f"{disp} @ {corr} uA (Fit)", legendgroup=grupo_id, showlegend=False, line=dict(width=2, dash='dash')))
            
    _renderizar_grafico(
        fig_ply, 
        titulo, 
        xaxis_kwargs=dict(title="Tiempo [s]"),
        yaxis_kwargs=dict(title="Temperatura [°C]")
    )

def graficar_corriente_vs_temperatura_ruido(titulo, todas_las_evos_i_vs_t):
    fig_ply = go.Figure()
    for disp, evos_disp in todas_las_evos_i_vs_t.items():
        for corr, datos in evos_disp.items():
            grupo_id = f"{disp}_{corr}uA"
            fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='markers', name=f"{disp} @ {corr} uA", legendgroup=grupo_id, marker=dict(size=4), opacity=0.6))
            fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y_fit"], mode='lines', name=f"{disp} @ {corr} uA (Fit)", legendgroup=grupo_id, showlegend=False, line=dict(width=2)))
                
    _renderizar_grafico(
        fig_ply, 
        titulo, 
        xaxis_kwargs=dict(title="Temperatura [°C]"),
        yaxis_kwargs=dict(title=r"$\text{Corriente }I_D \text{ [}\mu \text{A]}$")
    )

def graficar_snr(titulo, datos_sensibilidad, datos_ruido): 
    fig_ply = go.Figure()
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}

    for disp in datos_sensibilidad.keys():
        if disp in datos_ruido:
            x_ruido = datos_ruido[disp]["x"]
            sigma_ruido_uA = datos_ruido[disp]["y"] / 1000.0
            sens_interpolada = np.interp(x_ruido, datos_sensibilidad[disp]["x"], datos_sensibilidad[disp]["y"])
            snr = sigma_ruido_uA / sens_interpolada
            fig_ply.add_trace(go.Scatter(x=x_ruido, y=snr, mode='markers+lines', name=disp, line=dict(color=colores.get(disp, None))))

    _renderizar_grafico(
        fig_ply, 
        dict(text=titulo, x=0.5, xanchor="center"), 
        xaxis_kwargs=dict(title=r"$\text{Corriente Normalizada }I_{D_{norm}} \text{ [}\mu \text{A]}$"),
        yaxis_kwargs=dict(title="Resolución [Gy]")
    )

def graficar_histograma_ruido(titulo, todas_las_evos):
    fig_ply = go.Figure()
    for disp, evos_disp in todas_las_evos.items():
        for corr, datos in evos_disp.items():
            fig_ply.add_trace(go.Histogram(x=datos["y"] * 1000.0, name=f"{disp} @ {corr} uA", opacity=0.5, histnorm='probability density'))

    _renderizar_grafico(
        fig_ply, 
        titulo, 
        xaxis_kwargs=dict(title="Ruido Neto [nA]"),
        yaxis_kwargs=dict(title="Densidad de Probabilidad"),
        barmode='overlay'
    )

def graficar_error_termico_equivalente(titulo, datos_sensibilidad, datos_temp):
    fig_ply = go.Figure()
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}

    for disp in datos_sensibilidad.keys():
        if datos_temp and disp in datos_temp:
            x_tc = [float(corr_nominal) for corr_nominal, curvas in datos_temp[disp].items() if "alpha" in curvas]
            alpha_vals = [np.abs(curvas["alpha"]) for corr_nominal, curvas in datos_temp[disp].items() if "alpha" in curvas]
            
            if x_tc:
                indices = np.argsort(x_tc)
                x_tc_arr, alpha_arr = np.array(x_tc)[indices], np.array(alpha_vals)[indices]
                sens_interpolada = np.interp(x_tc_arr, datos_sensibilidad[disp]["x"], datos_sensibilidad[disp]["y"])
                error_termico = alpha_arr / sens_interpolada
                fig_ply.add_trace(go.Scatter(x=x_tc_arr, y=error_termico, mode='markers+lines', name=disp, line=dict(color=colores.get(disp, None))))

    _renderizar_grafico(
        fig_ply, 
        dict(text=titulo, x=0.5, xanchor="center"), 
        xaxis_kwargs=dict(title=r"$\text{Corriente Normalizada }I_{D_{norm}} \text{ [}\mu \text{A]}$"),
        yaxis_kwargs=dict(title=r"$\text{Error Térmico Equivalente [Gy/°C]}$")
    )