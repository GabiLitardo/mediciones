import numpy as np
import streamlit as st
import plotly.graph_objects as go
from proc_sens import calcular_fit_polinomico
import pandas as pd
import plotly.io as pio

def graficar_dispositivos(titulo, ylabel, datos_procesados, tanda, es_fg):
    """
    Dibuja en plotly la evolución temporal de corrientes o tensiones interpoladas para Floating Gate o 
    FOXFET respectivamente.

    Args:
        titulo (str): Título a mostrar en el gráfico
        ylabel (str): Label a mostrar en el eje y del gráfico
        datos_procesados (dict): dict con {disp: {"tiempos": array_tiempos, "valores": array_valores}}
        tanda (int): Indicador de a qué tanda corresponden los datos (1, 2)
        es_fg (bool): Indicador de si corresponde a datos de Floating Gates
    """
    fig_ply = go.Figure()    
    for disp, datos in datos_procesados.items():
        tiempos_ordenados = datos["tiempos"]
        valores_ordenados = datos["valores"]
        fig_ply.add_trace(go.Scatter(x=tiempos_ordenados, y=valores_ordenados, mode='markers', name=f"{disp} (Medido)"))
        if es_fg:
            if tanda == 1:
                coefs = calcular_fit_polinomico(tiempos_ordenados.tolist(), valores_ordenados.tolist())
            if tanda == 2:
                coefs = calcular_fit_polinomico(tiempos_ordenados.tolist(), valores_ordenados.tolist())
            a, b, c, d, e = coefs
            t_continuo = np.linspace(tiempos_ordenados.min(), tiempos_ordenados.max(), 200)
            i_fitteada = a * (t_continuo ** 4) + b * (t_continuo ** 3) + c * (t_continuo ** 2) + d * t_continuo + e
            fig_ply.add_trace(go.Scatter(x=t_continuo, y=i_fitteada, mode='lines', name=f"{disp} (Fit Poly g4)"))        
    fig_ply.update_layout(
        title=titulo,
        xaxis_title="Tiempo de irradiación [min]",
        yaxis_title=ylabel,
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white"),
        xaxis=dict(
            showgrid=False,
            showline=False,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,
        ),
    )
    html = pio.to_html(
        fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False
    )

    st.iframe(html, height="content")
    
def graficar_sensibilidad_fg(titulo, datos_sensibilidad, xlabel, ylabel):
    """
    Dibuja en plotly la sensibilidad calculada como derivada de un fitteo y con diferencias finitas.
    
    Args:
        titulo (str): Título a mostrar en el gráfico
        datos_sensibilidad (list): list de dicts [dict_continuo, dict_discreto] donde cada dict es {disp: {"x": array_x, "y": array_y}}
        xlabel (str): Label a mostrar en el eje x del gráfico
        ylabel (str): Label a mostrar en el eje y del gráfico
    """
    fig_ply = go.Figure()
    
    datos_sensibilidad_continuo = datos_sensibilidad[0]
    for disp, datos in datos_sensibilidad_continuo.items():
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines', name=f"{disp} (Poly)"))
    
    datos_sensibilidad_discreto = datos_sensibilidad[1]
    for disp, datos in datos_sensibilidad_discreto.items():
        fig_ply.add_trace(go.Scatter(x=datos["x"], y=datos["y"], mode='lines+markers', name=disp))
        
    fig_ply.update_layout(
        title=titulo,
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white"),
        xaxis=dict(
            showgrid=False,
            showline=False,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,
        ),
    )
    html = pio.to_html(
        fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False
    )

    st.iframe(html, height="content")

def graficar_ruido(titulo, datos_ruido):
    """
    Dibuja en plotly el desvío de ruido en función de la corriente normalizada para cada dispositivo.
    
    Args:
        titulo (str): Título a mostrar en el gráfico
        datos_ruido (dict): dict con {disp: {"x": array_I_normalizada, "y": array_std_ruido}}
    """
    fig_ply = go.Figure()
    
    for disp, datos in datos_ruido.items():
        x_data = datos["x"]
        y_data = datos["y"]
        
        fig_ply.add_trace(go.Scatter(x=x_data, y=y_data, mode='markers', name=disp))            

    fig_ply.update_layout(
        title=titulo,
        xaxis_title=r"$\text{Corriente Nominal }I_D\text{ [}\mu \text{A]}$", 
        yaxis_title="Desvío de Ruido [nA]", 
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white"),
        xaxis=dict(
            showgrid=False,
            showline=False,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,
        ),
    )
    html = pio.to_html(
        fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False
    )

    st.iframe(html, height="content")

def graficar_superposicion_sens_ruido(titulo, datos_sensibilidad, datos_ruido, datos_temp):
    """
    Dibuja en plotly la superposición entre sensibilidad absoluta, desvío de ruido y coeficiente térmico en función 
    de la corriente normalizada.

    Args:
        titulo (str): Título a mostrar en el gráfico
        datos_sensibilidad (dict): dict con {disp: {"x": array_I_norm, "y": array_sens_abs}} (solo fiteo continuo)
        datos_ruido (dict): dict con {disp: {"x": array_I_nom, "y": array_std_ruido}}
        datos_temp (dict): dict con {disp: {corr: {"alpha": float_coef}}}
    """
    fig_ply = go.Figure()
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}
    
    s_max = max(np.max(d["y"]) for d in datos_sensibilidad.values())
    r_max = max(np.max(d["y"]) for d in datos_ruido.values())

    datos_tc = {}

    for disp in datos_sensibilidad.keys():
        x_coefs = []
        y_coefs = []
        
        if datos_temp and disp in datos_temp:
            for corr_nominal, curvas in datos_temp[disp].items():
                if "alpha" in curvas:
                    x_coefs.append(float(corr_nominal))
                    y_coefs.append(np.abs(curvas["alpha"]))
        
        if x_coefs:
            indices_orden = np.argsort(x_coefs)
            datos_tc[disp] = {
                "x": np.array(x_coefs)[indices_orden],
                "y": np.array(y_coefs)[indices_orden]
            }
        else:
            datos_tc[disp] = {"x": np.array([]), "y": np.array([])}

    lista_valores_tc = []
    for d in datos_tc.values():
        if len(d["y"]) > 0:
            lista_valores_tc.extend(d["y"])

    if lista_valores_tc:
        tc_min = min(min(lista_valores_tc) * 1.1, -0.05)
        tc_max = max(max(lista_valores_tc) * 1.1, 0.05)
    else:
        tc_min = -0.05
        tc_max = 0.05

    for disp in datos_sensibilidad.keys():
        color = colores.get(disp, None)
        
        fig_ply.add_trace(go.Scatter(
            x=datos_sensibilidad[disp]["x"], y=datos_sensibilidad[disp]["y"],
            mode='lines', name=f"{disp} (Sens)", line=dict(dash = 'solid', color=color)
        ))
        
        fig_ply.add_trace(go.Scatter(
            x=datos_ruido[disp]["x"], y=datos_ruido[disp]["y"],
            mode='markers+lines', name=f"{disp} (Ruido)", 
            line=dict(dash='longdash', color=color), yaxis='y2'
        ))
        
        if len(datos_tc[disp]["x"]) > 0:
            fig_ply.add_trace(go.Scatter(
                x=datos_tc[disp]["x"], y=datos_tc[disp]["y"],
                mode='markers+lines', name=f"{disp} (TC)", 
                line=dict(dash='dot', color=color), marker=dict(symbol='triangle-up-open'), yaxis='y3'
            ))

    fig_ply.update_layout(
        title=dict(
            text=titulo,
            y=0.98, yanchor="top", x=0.5, xanchor="center"
        ),
        xaxis=dict(
            title=r"$\text{Corriente Normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$",
            domain=[0, 0.82],
            showgrid=False,
            showline=False,
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(text=r"$\text{Tasa de Cambio Absoluta [}\mu\text{A/min]}$", font=dict(color="#1f77b4")),
            range=[0, s_max * 1.1],
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,
        ),
        yaxis2=dict(
            title=dict(text="Desvío de Ruido [nA]", font=dict(color="#ff7f0e")),
            range=[0, r_max * 1.1],
            overlaying='y', side='right',
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,            
        ),
        yaxis3=dict(
            title=dict(text=r"$\text{Módulo de Coeficiente Térmico [}\mu\text{A/°C]}$", font=dict(color="#2ca02c")),
            range=[tc_min, tc_max], 
            overlaying='y', side='right',
            anchor='free', position=0.94,
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,            
        ),
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.5,
        ),        
    )
    html = pio.to_html(
        fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False
    )

    st.iframe(html, height="content")
    
def graficar_evolucion_ruido(titulo, todas_las_evos, es_log):
    """
    Dibuja en plotly la corriente en función del tiempo.

    Args:
        titulo (str): Título a mostrar en el gráfico
        todas_las_evos (dict): dict con {disp: {corr: {"x": array_tiempo, "y": array_corr_ruido}}}
        es_log (bool): Booleano que indica si el gráfico se dibujará en escala semilogarítmica o lineal
    """ 
    fig_ply = go.Figure()
    
    for disp, evos_disp in todas_las_evos.items():
        for corr in evos_disp:
            x_data = evos_disp[corr]["x"]
            y_data = evos_disp[corr]["y"]
            
            fig_ply.add_trace(go.Scatter(
                x=x_data, 
                y=y_data, 
                mode='lines', 
                name=f"{disp} @ {corr} uA",
                opacity=0.8
            ))
                
    fig_ply.update_layout(
        title=titulo,
        xaxis=dict(
            title="Tiempo [s]",
            showgrid=False,
            showline=False,
            zeroline=False,            
            type="log" if es_log else "-"
        ),
        yaxis=dict(
            title=r"$\text{Corriente de Ruido Neto [}\mu\text{A]}$",
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,            
        ),
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white"),
    )
    html = pio.to_html(
        fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False
    )

    st.iframe(html, height="content")

def graficar_I_vs_T(titulo, datos_temperatura):
    """
    Dibuja en plotly la medición de corriente vs temperatura usada para calcular coeficientes térmicos.
    Muestra también en una tabla los coeficientes térmicos.

    Args:
        titulo (str): Título a mostrar en el gráfico
        datos_temperatura (dict): dict con {disp: {corr: {"x": array_temp, "y": array_corr, "alpha": float_coef}}}
    """
    fig_ply = go.Figure()
    for disp, corrientes_dict in datos_temperatura.items():
        for corr, curvas in corrientes_dict.items():
            fig_ply.add_trace(go.Scatter(
                x=curvas["x"], 
                y=curvas["y"],
                mode='markers+lines', 
                name=f"{disp} ({corr} uA)"
            ))
            
    fig_ply.update_layout(
        title={
            'text': titulo,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(
            title="Temperatura [°C]",
            showgrid=False,
            showline=False,
            zeroline=False,             
        ),
        yaxis=dict(
            title=r"$\text{Corriente }I_D \text{ @ }V_D \text{ = -4.5V [}\mu \text{A]}$",
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,            
        ),
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white"),        
        margin=dict(t=100)
    )
    html = pio.to_html(
        fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False
    )

    st.iframe(html, height="content")

    st.markdown("### Tabla de Coeficientes Térmicos")
    
    filas_tabla = []
    for disp, corrientes_dict in datos_temperatura.items():
        for corr, curvas in corrientes_dict.items():
            filas_tabla.append({
                "Dispositivo": disp,
                "Corriente Nominal [μA]": corr,
                "Coef. Térmico (α) [μA/°C]": round(curvas["alpha"], 4)
            })
                
    if filas_tabla:
        df_coefs = pd.DataFrame(filas_tabla)
        st.dataframe(df_coefs, width='stretch', hide_index=True)
    else:
        st.warning("No se encontraron coeficientes térmicos calculados para mostrar.")

    fig_ply = go.Figure()
    for disp, corrientes_dict in datos_temperatura.items():
        for corr, curvas in corrientes_dict.items():
            print(curvas["alpha"], flush = True)
            fig_ply.add_trace(go.Scatter(
                x=curvas["y"], 
                y=curvas["alpha"],
                mode='markers+lines', 
                name=f"{disp} ({corr} uA)"
            ))
            
    fig_ply.update_layout(
        title={
            'text': r"$\alpha\text{ vs }I_{D_{norm}}$",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(
            title="r$I_{D_{norm}}\text{ [}\mu\text{A]}$",
            showgrid=False,
            showline=False,
            zeroline=False,             
        ),
        yaxis=dict(
            title=r"$\alpha\text{ [°C/}\mu\text{A]}$",
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,            
        ),
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white"),        
        margin=dict(t=100)
    )
    html = pio.to_html(
        fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False
    )

    st.iframe(html, height="content")
        
def graficar_evolucion_temperatura(titulo, datos_temp):
    """
    Dibuja en plotly la evolución temporal de la temperatura medida junto con su fit lineal.
    Agrupa las leyendas por dispositivo y corriente para una visualización más limpia.

    Args:
        titulo (str): Título a mostrar en el gráfico
        datos_temp (dict): dict con {disp: {corr: {"x": array_tiempo, "y": array_temp, "y_fit": array_temp_fit}}}
    """    
    fig_ply = go.Figure()
    
    for disp, evos_disp in datos_temp.items():
        for corr in evos_disp:
            x_data = evos_disp[corr]["x"]
            y_data = evos_disp[corr]["y"]
            y_fit = evos_disp[corr].get("y_fit", None)
            
            grupo_id = f"temp_{disp}_{corr}uA"
            
            # Traza de la medición real
            fig_ply.add_trace(go.Scatter(
                x=x_data, 
                y=y_data, 
                mode='lines', 
                name=f"{disp} @ {corr} uA",
                legendgroup=grupo_id,
                opacity=0.5
            ))
            
            # Traza del ajuste lineal (si está disponible)
            if y_fit is not None:
                fig_ply.add_trace(go.Scatter(
                    x=x_data, 
                    y=y_fit, 
                    mode='lines', 
                    name=f"{disp} @ {corr} uA (Fit)",
                    legendgroup=grupo_id,
                    showlegend=False,
                    line=dict(width=2, dash='dash')
                ))
            
    fig_ply.update_layout(
        title=titulo,
        xaxis=dict(
            title="Tiempo [s]",
            showgrid=False,
            showline=False,
            zeroline=False,             
        ),
        yaxis=dict(
            title="Temperatura [°C]",
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,              
        ),
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white"),            
    )
    
    html = pio.to_html(
        fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False
    )

    st.iframe(html, height="content")

def graficar_corriente_vs_temperatura_ruido(titulo, todas_las_evos_i_vs_t):
    """
    Dibuja en plotly la medición de corriente vs temperatura para verificar la linealidad.

    Args:
        titulo (str): Título a mostrar en el gráfico
        todas_las_evos_i_vs_t (dict): dict con {disp: {corr: {"x": array_temp, "y": array_I_medida, "y_fit": array_I_interpolada}}}
    """
    fig_ply = go.Figure()
    for disp, evos_disp in todas_las_evos_i_vs_t.items():
        for corr in evos_disp:
            x_data = evos_disp[corr]["x"]
            y_data = evos_disp[corr]["y"]
            y_fit = evos_disp[corr]["y_fit"]
            
            grupo_id = f"{disp}_{corr}uA"
            
            fig_ply.add_trace(go.Scatter(
                x=x_data, 
                y=y_data, 
                mode='markers', 
                name=f"{disp} @ {corr} uA",
                legendgroup=grupo_id,
                marker=dict(size=4),
                opacity=0.6
            ))
            
            fig_ply.add_trace(go.Scatter(
                x=x_data, 
                y=y_fit, 
                mode='lines', 
                name=f"{disp} @ {corr} uA (Fit)",
                legendgroup=grupo_id,
                showlegend=False,
                line=dict(width=2)
            ))
                
    fig_ply.update_layout(
        title=titulo,
        xaxis=dict(
            title="Temperatura [°C]",
            showgrid=False,
            showline=False,
            zeroline=False,             
        ),
        yaxis=dict(
            title=r"$\text{Corriente }I_D \text{ [}\mu \text{A]}$",
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,              
        ),
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white"),    
    )
    html = pio.to_html(
        fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False
    )

    st.iframe(html, height="content")
    
def graficar_snr(titulo, datos_sensibilidad, datos_ruido): 
    """
    Dibuja en plotly la relación Señal-a-Ruido (Sensibilidad Absoluta / Desvío de Ruido)
    en función de la Corriente Normalizada.

    Args:
        titulo (str): Título a mostrar en el gráfico
        datos_sensibilidad (dict): dict con {disp: {"x": array_I_norm, "y": array_sens_abs}}
        datos_ruido (dict): dict con {disp: {"x": array_I_nom, "y": array_std_ruido_nA}}
    """
    fig_ply = go.Figure()
    
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}

    for disp in datos_sensibilidad.keys():
        if disp in datos_ruido:
            x_ruido = datos_ruido[disp]["x"]
            sigma_ruido_uA = datos_ruido[disp]["y"] / 1000.0

            sens_interpolada = np.interp(
                x_ruido, 
                datos_sensibilidad[disp]["x"], 
                datos_sensibilidad[disp]["y"]
            )

            snr = sigma_ruido_uA / sens_interpolada

            color = colores.get(disp, None)

            fig_ply.add_trace(go.Scatter(
                x=x_ruido,
                y=snr,
                mode='markers+lines',
                name=f"{disp}",
                line=dict(color=color)
            ))

    fig_ply.update_layout(
        title=dict(text=titulo, x=0.5, xanchor="center"),
        xaxis=dict(
            title=r"$\text{Corriente Normalizada }I_{D_{norm}} \text{ [}\mu \text{A]}$",
            showgrid=False,
            showline=False,
            zeroline=False,             
        ),
        yaxis=dict(
            title="Resolución [Gy]",
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.2)",
            showline=False,
            zeroline=False,             
        ),
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white"),         
    )
    html = pio.to_html(
        fig_ply, include_plotlyjs="cdn", include_mathjax="cdn", full_html=False
    )

    st.iframe(html, height="content")