# graficos.py
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from proc_sens import calcular_fit_polinomico
import pandas as pd

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
    plt.xlabel("Tiempo de irradiación [min]")
    plt.ylabel(ylabel)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    st.pyplot(fig_mpl)
    fig_ply.update_layout(title=titulo, xaxis_title="Tiempo de irradiación [min]", yaxis_title=ylabel, template="plotly_white")
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
    plt.xlabel(r"Corriente Normalizada $I_D$ [$\mu$A]")
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

def graficar_superposicion_sens_ruido(titulo, datos_sensibilidad, datos_ruido, datos_temp):
    fig_ply = go.Figure()
    colores = {"PFGIW1": "#1f77b4", "PFGIW2": "#ff7f0e", "PFGIP2": "#2ca02c"}
    
    s_max = max(np.max(d["y"]) for d in datos_sensibilidad.values())
    r_max = max(np.max(d["y"]) for d in datos_ruido.values())

    datos_tc = {}

    # —— RESOLUCIÓN CORECTA USANDO LAS CLAVES REALES DE TEMPERATURA ——
    for disp in datos_sensibilidad.keys():
        x_coefs = []
        y_coefs = []
        
        # Iteramos únicamente sobre las corrientes que de verdad se midieron y existen en datos_temp
        if datos_temp and disp in datos_temp:
            for corr_nominal, curvas in datos_temp[disp].items():
                if "alpha" in curvas:
                    # Convertimos la clave nominal (ej: 150) a float para el eje X
                    x_coefs.append(float(corr_nominal))
                    y_coefs.append(np.abs(curvas["alpha"]))
        
        # Ordenamos los puntos por corriente para que Plotly no dibuje líneas cruzadas
        if x_coefs:
            indices_orden = np.argsort(x_coefs)
            datos_tc[disp] = {
                "x": np.array(x_coefs)[indices_orden],
                "y": np.array(y_coefs)[indices_orden]
            }
        else:
            datos_tc[disp] = {"x": np.array([]), "y": np.array([])}

    # Calculamos los límites reales del eje Y3 de forma dinámica (soporta positivos y negativos)
    lista_valores_tc = []
    for d in datos_tc.values():
        if len(d["y"]) > 0:
            lista_valores_tc.extend(d["y"])

    # Si la lista tiene datos, calculamos los mínimos y máximos; si no, asignamos un rango por defecto
    if lista_valores_tc:
        tc_min = min(min(lista_valores_tc) * 1.1, -0.05)
        tc_max = max(max(lista_valores_tc) * 1.1, 0.05)
    else:
        tc_min = -0.05
        tc_max = 0.05

    # —— GENERACIÓN DE TRAZAS ——
    for disp in datos_sensibilidad.keys():
        color = colores.get(disp, None)
        
        # 1. Sensibilidad (Eje Y principal)
        fig_ply.add_trace(go.Scatter(
            x=datos_sensibilidad[disp]["x"], y=datos_sensibilidad[disp]["y"],
            mode='lines', name=f"{disp} (Sens)", line=dict(dash = 'solid', color=color)
        ))
        
        # 2. Ruido (Eje Y2 - Derecho externo)
        fig_ply.add_trace(go.Scatter(
            x=datos_ruido[disp]["x"], y=datos_ruido[disp]["y"],
            mode='markers+lines', name=f"{disp} (Ruido)", 
            line=dict(dash='longdash', color=color), yaxis='y2'
        ))
        
        # 3. Coeficiente Térmico REAL (Eje Y3 - Derecho interno desplazado)
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
            title=dict(text="Módulo de Coeficiente Térmico [uA/°C]", font=dict(color="#2ca02c")),
            range=[tc_min, tc_max], 
            overlaying='y', side='right',
            anchor='free', position=0.94
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.4
        ),
        template="plotly_white"
    )
    st.plotly_chart(fig_ply, width='stretch')
    
def graficar_evolucion_ruido(titulo, todas_las_evos, corrientes_a_graficar):
    plt.figure(figsize=(10, 5))
    
    for disp, evos_disp in todas_las_evos.items():
        for corr in corrientes_a_graficar:
            if corr in evos_disp:
                x_data = evos_disp[corr]["x"]
                y_data = evos_disp[corr]["y"]
                
                plt.plot(x_data, y_data, alpha=0.7, label=f"{disp} @ {corr} uA")
                
    #plt.xscale('log')
    plt.title(titulo)
    plt.xlabel("Tiempo [s] (Escala Log)")
    plt.ylabel(r"Corriente de Ruido Neto [$\mu$A]")
    plt.grid(True, which="both", linestyle=":", alpha=0.6)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(plt.gcf(), clear_figure=True)
    plt.close()
    
    fig_ply = go.Figure()
    
    for disp, evos_disp in todas_las_evos.items():
        for corr in corrientes_a_graficar:
            if corr in evos_disp:
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
            #type="log"
        ),
        yaxis=dict(title=r"Corriente de Ruido Neto [$\mu$A]"),
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_ply, width='stretch')

def graficar_I_vs_T(titulo, datos_temperatura):
    """
    Grafica la Corriente ID @ VD = -5V en función de la Temperatura 
    y muestra una tabla con los coeficientes térmicos (alpha) calculados.
    """
    # —— 1. RENDER DE GRÁFICO ESTÁTICO (MATPLOTLIB) ——
    plt.figure(figsize=(10, 5))
    for disp, corrientes_dict in datos_temperatura.items():
        for corr, curvas in corrientes_dict.items():
            plt.plot(curvas["x"], curvas["y"], 'o-', label=f"{disp} ({corr} uA)")
            
    plt.title(titulo)
    plt.xlabel("Temperatura [°C]")
    plt.ylabel(r"Corriente $I_D$ @ $V_D = -5$V [$\mu$A]")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(plt.gcf(), clear_figure=True)
    plt.close()

    # —— 2. RENDER DE GRÁFICO INTERACTIVO (PLOTLY) ——
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
        xaxis=dict(title="Temperatura [°C]"),
        yaxis=dict(title="Corriente I_D @ V_D = -5V [uA]"),
        template="plotly_white",
        # Ubicamos la leyenda a la derecha de forma limpia para que no compita con el título
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        ),
        margin=dict(t=100) # Agregamos margen superior para darle aire al título
    )
    st.plotly_chart(fig_ply, width='stretch')

    # —— 3. CÁLCULO Y PRESENTACIÓN DE LA TABLA DE COEFICIENTES ——
    st.markdown("### Tabla de Coeficientes Térmicos")
    
    filas_tabla = []
    for disp, corrientes_dict in datos_temperatura.items():
        for corr, curvas in corrientes_dict.items():
            if "alpha" in curvas:
                filas_tabla.append({
                    "Dispositivo": disp,
                    "Corriente Nominal [uA]": corr,
                    "Coef. Térmico (α) [uA/°C]": round(curvas["alpha"], 4)
                })
                
    if filas_tabla:
        df_coefs = pd.DataFrame(filas_tabla)
        st.dataframe(df_coefs, use_container_width=True, hide_index=True)
    else:
        st.warning("No se encontraron coeficientes térmicos calculados para mostrar.")
