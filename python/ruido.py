# ruido.py
import os
import numpy as np
import streamlit as st

# Constantes de Steinhart-Hart para el termistor
A_SH = 1.12924e-3
B_SH = 2.34108e-4
C_SH = 8.77550e-8

def convertir_r_a_temp_steinhart(resistencia):
    """Convierte la columna de resistencia del termistor a temperatura en °C."""
    ln_R = np.log(resistencia)
    inverso_T = A_SH + B_SH * ln_R + C_SH * (ln_R ** 3)
    temp_kelvin = 1.0 / inverso_T
    return temp_kelvin - 273.15

def matchear_archivos_ruido(nombre_buscar):
    """
    Versión adaptada para ruido: Busca el archivo en el repositorio
    y levanta las primeras 3 columnas tolerando espacios o tabs.
    """
    directorio_base = "."
    for root, dirs, files in os.walk(directorio_base):
        if nombre_buscar in files:
            ruta_completa = os.path.join(root, nombre_buscar)
            try:
                # Al no poner 'delimiter', se banca tabulaciones o espacios indistintamente
                # Levantamos las 3 columnas: Tiempo, Corriente, Resistencia
                datos = np.genfromtxt(ruta_completa, skip_header=2, usecols=(0, 1, 2))
                return datos
            except:
                return None
    return None

def procesar_archivo_ruido(ruta_archivo):
    """Procesa la matriz de datos de ruido aislándole la deriva térmica."""
    datos = matchear_archivos_ruido_local(ruta_archivo)
    if datos is None or datos.size == 0 or len(datos.shape) < 2:
        return None
        
    tiempo = datos[:, 0]
    corriente_uA = np.abs(datos[:, 1]) * 1e6  # Módulo en uA
    resistencia = datos[:, 2]
    
    # 1. Conversión de temperatura por Steinhart-Hart
    temperatura_C = convertir_r_a_temp_steinhart(resistencia)
    
    # 2. Remover deriva térmica mediante un ajuste lineal puro (I vs T)
    coefs = np.polyfit(temperatura_C, corriente_uA, deg=1)
    corriente_tendencia_termica = np.polyval(coefs, temperatura_C)
    
    # 3. Restamos la tendencia para aislar el ruido puro
    corriente_limpia_ruido_uA = corriente_uA - corriente_tendencia_termica
    
    return tiempo, corriente_uA, temperatura_C, corriente_limpia_ruido_uA

def analizar_ruido_panel():
    st.header("Análisis de Ruido e Interferencia Térmica")
    st.markdown("---")
    
    disp_seleccionado = st.selectbox("Seleccioná el Dispositivo", ["PFGIW1", "PFGIW2", "PFGIP2"])
    
    desvios_puntos = []
    corrientes_eje_x = []
    datos_temporales_por_corriente = {}

    for curr in corrientes_nominales_uA:
        nombre_buscar = f"MOSISV72M_DIE4_{disp_seleccionado}_VD=-4.5_RUIDO_{curr}u_M1.txt"
        
        # Llamamos a la función interna de procesamiento pasándole el nombre del archivo
        res_proc = procesar_archivo_ruido(nombre_buscar)
        if res_proc is not None:
            tiempo, corr_uA, temp_C, corr_ruido_uA = res_proc
            
            # Desvío estándar en nA (multiplicado por 1000 ya que corr_ruido_uA está en uA)
            sigma_nA = np.std(corr_ruido_uA, ddof=1) * 1000.0
            
            desvios_puntos.append(sigma_nA)
            corrientes_eje_x.append(curr)
            
            datos_temporales_por_corriente[curr] = {
                "tiempo": tiempo,
                "corriente": corr_uA,
                "temperatura": temp_C,
                "ruido_limpio": corr_ruido_uA * 1000.0
            }

    if not desvios_puntos:
        st.error("No se encontraron archivos de ruido para este dispositivo en el repositorio.")
        return

    # =====================================================================
    # GRÁFICO 1: DESVÍO ESTÁNDAR VS CORRIENTE BIAS
    # =====================================================================
    st.subheader(f"Desvío Estándar del Ruido vs. Corriente de Carga ({disp_seleccionado})")
    
    fig_res = go.Figure()
    fig_res.add_trace(go.Scatter(
        x=corrientes_eje_x, 
        y=desvios_puntos, 
        mode='lines+markers', 
        marker=dict(size=8, color='blue'),
        name=f"Ruido {disp_seleccionado}"
    ))
    fig_res.update_layout(
        xaxis_title="Corriente Normalizada de Carga [uA]",
        yaxis_title="Desvío Estándar del Ruido σ [nA]",
        template="plotly_white"
    )
    st.plotly_chart(fig_res, width='stretch')

    # =====================================================================
    # GRÁFICOS DE CONTROL TEMPORAL AUDITOR
    # =====================================================================
    st.markdown("---")
    st.subheader("Auditoría Temporal de Señales Crudas vs. Filtradas")
    
    curr_grafico = st.selectbox("Seleccioná la corriente para auditar las curvas temporales", corrientes_eje_x)
    
    if curr_grafico in datos_temporales_por_corriente:
        d_temp = datos_temporales_por_corriente[curr_grafico]
        
        fig_aud1 = go.Figure()
        fig_aud1.add_trace(go.Scatter(x=d_temp["tiempo"], y=d_temp["corriente"], mode='lines', name="Corriente Cruda [uA]", yaxis="y1"))
        fig_aud1.add_trace(go.Scatter(x=d_temp["tiempo"], y=d_temp["temperatura"], mode='lines', name="Temperatura [°C]", line=dict(dash='dash', color='orange'), yaxis="y2"))
        
        fig_aud1.update_layout(
            title=f"Evolución Simultánea a {curr_grafico} uA",
            xaxis_title="Tiempo [s]",
            yaxis=dict(title="Corriente I_D [uA]"),
            yaxis2=dict(title="Temperatura [°C]", overlaying="y", side="right"),
            template="plotly_white",
            legend=dict(x=0.01, y=0.99)
        )
        st.plotly_chart(fig_aud1, width='stretch')
        
        fig_aud2 = go.Figure()
        fig_aud2.add_trace(go.Scatter(x=d_temp["tiempo"], y=d_temp["ruido_limpio"], mode='lines', name="Ruido AC sin deriva", line=dict(color='green')))
        fig_aud2.update_layout(
            title=f"Señal de Ruido Extraída (Deriva Térmica Restada) – σ = {np.std(d_temp['ruido_limpio'], ddof=1):.2f} nA",
            xaxis_title="Tiempo [s]",
            yaxis_title="Fluctuación de Corriente [nA]",
            template="plotly_white"
        )
        st.plotly_chart(fig_aud2, width='stretch')

# Helper local para no duplicar código de búsqueda
def matchear_archivos_ruido_local(nombre_buscar):
    return matchear_archivos_ruido(nombre_buscar)
