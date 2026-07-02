# codigo.py
import streamlit as st
import graficos
import proc_evo
import proc_sens
import proc_ruido

st.title("Resumen mediciones Chaves-Litardo")

# =====================================================================
# CONFIGURACIÓN DE CHECKBOXES
# =====================================================================
mostrar_resumen = st.checkbox("0. Resumen (Sensibilidad Absoluta vs Ruido)", value=False)
mostrar_evolucion = st.checkbox("1. Análisis temporal", value=False)
mostrar_sensibilidad = st.checkbox("2. Análisis de Sensibilidad a radiación", value=False)
mostrar_ruido = st.checkbox("3. Análisis de Ruido", value=False)

# variables auxiliares

sens_abs_t2 = None
resultados_ruido = None

# =====================================================================
# SECCIÓN 1: EVOLUCIÓN TEMPORAL
# =====================================================================
if mostrar_evolucion:
    st.markdown("---")
    st.header("Evolución Temporal")
    
    # -----------------------------------------------------------------
    # FILAS 1 y 2: Evolución de Corriente / Tensión (3 Columnas)
    # -----------------------------------------------------------------
    datos_fg_t1 = proc_evo.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1")
    datos_fg_t2 = proc_evo.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2")
    datos_foxfet = proc_evo.obtener_datos_crudos_tanda(["FFC1", "FFC2", "FFC3", "FFL", "FFS"], "FOXFET")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Columna 1: Tanda 1 (Lanza Matplotlib arriba y Plotly abajo)
        graficos.graficar_dispositivos(
            titulo="Evolución Floating Gates Tanda 1 (I @ V = -4.5 V)",
            ylabel=r"$I_D$ [$\mu$A]",
            datos_procesados=datos_fg_t1,
            tanda = 1,
            es_fg = True
        )
        
    with col2:
        # Columna 2: Tanda 2 (Lanza Matplotlib arriba y Plotly abajo)
        graficos.graficar_dispositivos(
            titulo="Evolución Floating Gates Tanda 2 (I @ V = -4.5 V)",
            ylabel=r"$I_D$ [$\mu$A]",
            datos_procesados=datos_fg_t2,
            tanda = 2,
            es_fg = True
        )
        
    with col3:
        # Columna 3: FOXFET (Lanza Matplotlib arriba y Plotly abajo)
        graficos.graficar_dispositivos(
            titulo="Evolución FOXFETs (Tensión interpolada @ I = 10 uA)",
            ylabel="Tensión [V]",
            datos_procesados=datos_foxfet,
            tanda = 0, 
            es_fg = False
        )

    # -----------------------------------------------------------------
    # FILAS 3 y 4: Evolución Tensión Equivalente V_FG (3 Columnas, la 3ra vacía)
    # -----------------------------------------------------------------
    st.markdown("---")
    st.subheader("Evolución de la Tensión de Compuerta Equivalente ($V_{FG}$)")
    
    datos_vg_t1 = proc_evo.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2"], "FG_tanda1")
    datos_vg_t2 = proc_evo.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2", "PFGIP2"], "FG_tanda2")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        # Columna 1: Tensión Tanda 1 (Matplotlib arriba, Plotly abajo)
        graficos.graficar_dispositivos(
            titulo="Descarga Temporal de Floating Gates Tanda 1 en Tensión", 
            ylabel = r"Tensión $V_{FG}$ [V]", 
            datos_procesados = datos_vg_t1, 
            tanda = 1, 
            es_fg = True
        )
        
    with col5:
        # Columna 2: Tensión Tanda 2 (Matplotlib arriba, Plotly abajo)
        graficos.graficar_dispositivos(
            titulo="Descarga Temporal de Floating Gates Tanda 2 en Tensión", 
            ylabel = r"Tensión $V_{FG}$ [V]", 
            datos_procesados = datos_vg_t2, 
            tanda = 2, 
            es_fg = True
        )# =====================================================================
# SECCIÓN 2: SENSIBILIDAD
# =====================================================================
if mostrar_sensibilidad:
    st.markdown("---")
    st.header("Análisis de Sensibilidad")
    st.subheader("Normalizada")
    
    sens_norm_t1 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=True)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad FG Tanda 1 (Tasa vs $I_D$ Normalizado)", datos_sensibilidad=sens_norm_t1, xlabel = r"Corriente Normalizada $I_{D\_norm}$ [$\mu$A]", ylabel = r"Tasa de Cambio normalizada [($\mu$A)/min]")
        
    sens_norm_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=True)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad FG Tanda 2 (Tasa vs $I_D$ Normalizado)", datos_sensibilidad=sens_norm_t2, xlabel = r"Corriente Normalizada $I_{D\_norm}$ [$\mu$A]", ylabel = r"Tasa de Cambio normalizada [($\mu$A)/min]")
        
    st.subheader("Sin normalizar")
    
    sens_abs_t1 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=False)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad Absoluta FG Tanda 1 (Tasa Absoluta vs $I_D$ Normalizado)", datos_sensibilidad=sens_abs_t1, xlabel = r"Corriente Normalizada $I_{D\_norm}$ [$\mu$A]", ylabel = r"Tasa de Cambio Absoluta [$\mu$A/min]")
        
    sens_abs_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=False)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad Absoluta FG Tanda 2 (Tasa Absoluta vs $I_D$ Normalizado)", datos_sensibilidad=sens_abs_t2, xlabel = r"Corriente Normalizada $I_{D\_norm}$ [$\mu$A]", ylabel = r"Tasa de Cambio Absoluta [$\mu$A/min]")
    
# =====================================================================
# SECCIÓN 3: RUIDO
# =====================================================================
if mostrar_ruido:
    st.markdown("---")
    st.header("Análisis de Ruido")
    
    lista_dispositivos = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_nominales = [100, 150, 200, 250, 350]
    
    resultados_ruido = proc_ruido.procesar_ruido(lista_dispositivos, corrientes_nominales)
    graficos.graficar_ruido(titulo="Desvío Estándar del Ruido Neto vs Corriente Nominal", datos_ruido=resultados_ruido)
# =====================================================================
# SECCIÓN 4: RESUMEN
# =====================================================================
if mostrar_resumen:
    st.markdown("---")
    st.header("Correlación: Sensibilidad Absoluta vs Ruido Neto")
    
    dispositivos_cruce = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_ruido = [100, 150, 200, 250, 350]
    
    # Si las secciones de arriba no se ejecutaron, las calculamos acá de forma segura
    if sens_abs_t2 is None:
        sens_abs_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=False)
        
    if resultados_ruido is None:
        resultados_ruido = proc_ruido.procesar_ruido(dispositivos_cruce, corrientes_ruido)
    
    sens_resumen = {disp: sens_abs_t2[0][disp] for disp in dispositivos_cruce}
    ruido_resumen = {disp: resultados_ruido[disp] for disp in dispositivos_cruce}
    
    graficos.graficar_superposicion_sens_ruido(titulo="Tanda 2: Sensibilidad Absoluta y Ruido vs I_D Normalizada",datos_sensibilidad=sens_resumen,datos_ruido=ruido_resumen)
