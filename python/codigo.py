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
mostrar_evolucion = st.checkbox("1. Análisis temporal", value=True)
mostrar_sensibilidad = st.checkbox("2. Análisis de Sensibilidad a radiación", value=False)
mostrar_ruido = st.checkbox("3. Análisis de Ruido", value=False)

# =====================================================================
# SECCIÓN 1: EVOLUCIÓN TEMPORAL
# =====================================================================
if mostrar_evolucion:
    st.markdown("---")
    st.header("Evolución Temporal")
    
    datos_fg_t1 = proc_evo.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1")
    graficos.graficar_dispositivos(
        titulo="Evolución Floating Gates Tanda 1 (I @ V = -4.5 V)",
        ylabel=r"$I_D$ [$\mu$A]",
        datos_procesados=datos_fg_t1,
        tanda = 1,
        es_fg = True
    )

    datos_fg_t2 = proc_evo.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2")
    graficos.graficar_dispositivos(
        titulo="Evolución Floating Gates Tanda 2 (I @ V = -4.5 V)",
        ylabel=r"$I_D$ [$\mu$A]",
        datos_procesados=datos_fg_t2,
        tanda = 2,
        es_fg = True
    )

    datos_foxfet = proc_evo.obtener_datos_crudos_tanda(["FFC1", "FFC2", "FFC3", "FFL", "FFS"], "FOXFET")
    graficos.graficar_dispositivos(
        titulo="Evolución FOXFETs (Tensión interpolada @ I = 10 uA)",
        ylabel="Tensión [V]",
        datos_procesados=datos_foxfet,
        tanda = 0, 
        es_fg = False
    )

    st.subheader("Evolución de la Tensión de Compuerta Equivalente ($V_{FG}$)")
    
    datos_vg_t1 = proc_evo.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2"], "FG_tanda1")
    #graficos.graficar_evolucion_vg(titulo="Descarga Temporal de Floating Gates Tanda 1 en Voltaje", datos_procesados=datos_vg_t1)
    graficos.graficar_dispositivos(titulo="Descarga Temporal de Floating Gates Tanda 1 en Tensión", ylabel = r"Tensión $V_{FG}$ [V]", datos_procesados = datos_vg_t1, tanda = 1, es_fg = True)
    
    datos_vg_t2 = proc_evo.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2", "PFGIP2"], "FG_tanda2")
    #graficos.graficar_evolucion_vg(titulo="Descarga Temporal de Floating Gates Tanda 2 en Voltaje", datos_procesados=datos_vg_t2)
    graficos.graficar_dispositivos(titulo="Descarga Temporal de Floating Gates Tanda 2 en Tensión", ylabel = r"Tensión $V_{FG}$ [V]", datos_procesados = datos_vg_t2, tanda = 2, es_fg = True)
# =====================================================================
# SECCIÓN 2: SENSIBILIDAD
# =====================================================================
if mostrar_sensibilidad:
    st.markdown("---")
    st.header("Análisis de Sensibilidad")
    st.subheader("Normalizada")
    
    sens_norm_t1 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=True)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad FG Tanda 1 (Tasa vs $I_D$ Promedio Normalizado)", datos_sensibilidad=sens_norm_t1, xlabel = r"Corriente Promedio Normalizada $I_{D\_norm}$ [$\mu$A]", ylabel = r"Tasa de Cambio normalizada [($\mu$A)/min]")
        
    sens_norm_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=True)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad FG Tanda 2 (Tasa vs $I_D$ Promedio Normalizado)", datos_sensibilidad=sens_norm_t2, xlabel = r"Corriente Promedio Normalizada $I_{D\_norm}$ [$\mu$A]", ylabel = r"Tasa de Cambio normalizada [($\mu$A)/min]")
        
    st.subheader("Sin normalizar")
    
    sens_abs_t1 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=False)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad Absoluta FG Tanda 1 (Tasa Absoluta vs $I_D$ Promedio Absoluto)", datos_sensibilidad=sens_abs_t1, xlabel = r"Corriente Promedio Normalizada $I_{D\_norm}$ [$\mu$A]", ylabel = r"Tasa de Cambio Absoluta [$\mu$A/min]")
        
    sens_abs_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=False)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad Absoluta FG Tanda 2 (Tasa Absoluta vs $I_D$ Promedio Absoluto)", datos_sensibilidad=sens_abs_t2, xlabel = r"Corriente Promedio Normalizada $I_{D\_norm}$ [$\mu$A]" ylabel = r"Tasa de Cambio Absoluta [$\mu$A/min]")
    
# =====================================================================
# SECCIÓN 3: RUIDO
# =====================================================================
if mostrar_ruido:
    st.markdown("---")
    st.header("Análisis de Ruido")
    st.subheader("Resumen de Desvío Estándar del Ruido (nA)")
    
    lista_dispositivos = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_nominales = [100, 150, 200, 250, 350]
    resultados = proc_ruido.calcular_desvio(lista_dispositivos, corrientes_nominales)
    st.write(resultados)
