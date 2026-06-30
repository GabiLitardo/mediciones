# codigo.py
import streamlit as st
import procesamiento
import graficos

st.title("Resumen mediciones Chaves-Litardo")

# =====================================================================
# CONFIGURACIÓN DE CHECKBOXES
# =====================================================================
mostrar_evolucion = st.checkbox("1. Análisis temporal", value=True)
mostrar_sensibilidad = st.checkbox("2. Análisis de Sensibilidad a radiación", value=False)
mostrar_ruido = st.checkbox("3. Análisis de Ruido", value=False)

# =====================================================================
# SECCIÓN 1: EVOLUCIÓN TEMPORAL
# =====================================================================
if mostrar_evolucion:
    st.markdown("---")
    st.header("Evolución Temporal")
    
    # Gráfico 1: Floating Gates Tanda 1
    datos_fg_t1 = procesamiento.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1")
    graficos.graficar_dispositivos(
        titulo="Evolución Floating Gates Tanda 1 (I @ V = -4.5 V)",
        ylabel=r"$I_D$ [$\mu$A]",
        datos_procesados=datos_fg_t1
    )

    # Gráfico 2: Floating Gates Tanda 2
    datos_fg_t2 = procesamiento.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2")
    graficos.graficar_dispositivos(
        titulo="Evolución Floating Gates Tanda 2 (I @ V = -4.5 V)",
        ylabel=r"$I_D$ [$\mu$A]",
        datos_procesados=datos_fg_t2
    )

    # Gráfico 3: FOXFETs Tensión Interpolada
    datos_foxfet = procesamiento.obtener_datos_crudos_tanda(["FFC1", "FFC2", "FFC3", "FFL", "FFS"], "FOXFET")
    graficos.graficar_dispositivos(
        titulo="Evolución FOXFETs (Tensión interpolada @ I = 10 uA)",
        ylabel="Tensión [V]",
        datos_procesados=datos_foxfet
    )

    # Gráfico 4 y 5: EVOLUCIÓN TEMPORAL EQUIVALENTE EN VOLTAJE VFG
    st.subheader("Evolución del Voltaje de Compuerta Equivalente ($V_{FG}$)")
    
    datos_vg_t1 = procesamiento.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2"], "FG_tanda1")
    graficos.graficar_evolucion_vg(
        titulo="Descarga Temporal de Floating Gates Tanda 1 en Voltaje",
        datos_procesados=datos_vg_t1
    )
    
    datos_vg_t2 = procesamiento.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2", "PFGIP2"], "FG_tanda2")
    graficos.graficar_evolucion_vg(
        titulo="Descarga Temporal de Floating Gates Tanda 2 en Voltaje",
        datos_procesados=datos_vg_t2
    )

# =====================================================================
# SECCIÓN 2: SENSIBILIDAD
# =====================================================================
if mostrar_sensibilidad:
    st.markdown("---")
    st.header("Análisis de Sensibilidad")
    
    st.subheader("Normalizada")
    # Gráficos de Sensibilidad Normalizada Tanda 1 (V1 y V2)
    sens_norm_t1_v1 = procesamiento.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=True, analitico=True)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad FG Tanda 1 (Tasa vs $I_D$ Promedio Normalizado)", datos_sensibilidad=sens_norm_t1_v1)
    
    sens_norm_t1_v2 = procesamiento.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=True, analitico=False)
    graficos.graficar_sensibilidad_fg2(titulo="Sensibilidad FG Tanda 1 (Tasa vs $I_D$ Promedio Normalizado)", datos_sensibilidad=sens_norm_t1_v2)
    
    # Gráficos de Sensibilidad Normalizada Tanda 2 (V1 y V2)
    sens_norm_t2_v1 = procesamiento.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=True, analitico=True)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad FG Tanda 2 (Tasa vs $I_D$ Promedio Normalizado)", datos_sensibilidad=sens_norm_t2_v1)
    
    sens_norm_t2_v2 = procesamiento.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=True, analitico=False)
    graficos.graficar_sensibilidad_fg2(titulo="Sensibilidad FG Tanda 2 (Tasa vs $I_D$ Promedio Normalizado)", datos_sensibilidad=sens_norm_t2_v2)
    
    st.subheader("Sin normalizar")
    # Gráficos de Sensibilidad Absoluta Tanda 1 (V1 y V2)
    sens_abs_t1_v1 = procesamiento.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=False, analitico=True)
    graficos.graficar_sensibilidad_fg_absoluta(titulo="Sensibilidad Absoluta FG Tanda 1 (Tasa Absoluta vs $I_D$ Promedio Absoluto)", datos_sensibilidad=sens_abs_t1_v1)
    
    sens_abs_t1_v2 = procesamiento.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=False, analitico=False)
    graficos.graficar_sensibilidad_fg_absoluta2(titulo="Sensibilidad Absoluta FG Tanda 1 (Tasa Absoluta vs $I_D$ Promedio Absoluto)", datos_sensibilidad=sens_abs_t1_v2)
    
    # Gráficos de Sensibilidad Absoluta Tanda 2 (V1 y V2)
    sens_abs_t2_v1 = procesamiento.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=False, analitico=True)
    graficos.graficar_sensibilidad_fg_absoluta(titulo="Sensibilidad Absoluta FG Tanda 2 (Tasa Absoluta vs $I_D$ Promedio Absoluto)", datos_sensibilidad=sens_abs_t2_v1)
    
    sens_abs_t2_v2 = procesamiento.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=False, analitico=False)
    graficos.graficar_sensibilidad_fg_absoluta2(titulo="Sensibilidad Absoluta FG Tanda 2 (Tasa Absoluta vs $I_D$ Promedio Absoluto)", datos_sensibilidad=sens_abs_t2_v2)

# =====================================================================
# SECCIÓN 3: RUIDO
# =====================================================================
if mostrar_ruido:
    st.markdown("---")
    st.header("Análisis de Ruido")
    st.subheader("Resumen de Desvío Estándar del Ruido (nA)")
    
    lista_dispositivos = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_nominales = [100, 150, 200, 250, 350]
    resultados = {}
    
    for disp in lista_dispositivos:
        resultados[disp] = {}
        for curr in corrientes_nominales:
            nombre_archivo = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{curr}u_M1.txt"
            sigma = procesamiento.calcular_desvio_archivo(nombre_archivo)
            
            if sigma is not None:
                resultados[disp][f"{curr} uA"] = f"{sigma:.2f} nA"
            else:
                resultados[disp][f"{curr} uA"] = "Falta medición / Incompleto"
                
    st.write(resultados)
