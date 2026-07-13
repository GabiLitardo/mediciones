# codigo.py
import streamlit as st
import graficos
import proc_evo
import proc_sens
import proc_ruido
import proc_temp

st.title("Resumen mediciones Chaves-Litardo")

# =====================================================================
# CONFIGURACIÓN DE CHECKBOXES
# =====================================================================
mostrar_resumen = st.checkbox("0. Resumen (Sensibilidad absoluta vs Ruido)", value=False)
mostrar_evolucion = st.checkbox("1. Análisis temporal", value=False)
mostrar_sensibilidad = st.checkbox("2. Análisis de sensibilidad a radiación", value=False)
mostrar_ruido = st.checkbox("3. Análisis de Ruido", value=False)
mostrar_temperatura = st.checkbox("4. Mostrar Efectos de Temperatura", value=False)

# variables auxiliares

sens_abs_t2 = None
resultados_ruido = None

# =====================================================================
# SECCIÓN 1: EVOLUCIÓN TEMPORAL
# =====================================================================
if mostrar_evolucion:
    st.markdown("---")
    st.header("Evolución Temporal")
    
    datos_fg_t1 = proc_evo.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1")
    graficos.graficar_dispositivos(
        titulo="Evolución Floating Gates tanda 1 (I @ V = -4.5 V)",
        ylabel=r"$I_D$ [$\mu$A]",
        datos_procesados=datos_fg_t1,
        tanda = 1,
        es_fg = True
    )

    datos_fg_t2 = proc_evo.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2")
    graficos.graficar_dispositivos(
        titulo="Evolución Floating Gates tanda 2 (I @ V = -4.5 V)",
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

    st.subheader("Evolución de la tensión de compuerta equivalente ($V_{FG}$)")
    
    datos_vg_t1 = proc_evo.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2"], "FG_tanda1")
    #graficos.graficar_evolucion_vg(titulo="Descarga Temporal de Floating Gates Tanda 1 en Voltaje", datos_procesados=datos_vg_t1)
    graficos.graficar_dispositivos(titulo="Descarga temporal de Floating Gates tanda 1 en tensión", ylabel = r"Tensión $V_{FG}$ [V]", datos_procesados = datos_vg_t1, tanda = 1, es_fg = True)
    
    datos_vg_t2 = proc_evo.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2", "PFGIP2"], "FG_tanda2")
    #graficos.graficar_evolucion_vg(titulo="Descarga Temporal de Floating Gates Tanda 2 en Voltaje", datos_procesados=datos_vg_t2)
    graficos.graficar_dispositivos(titulo="Descarga temporal de Floating Gates tanda 2 en tensión", ylabel = r"Tensión $V_{FG}$ [V]", datos_procesados = datos_vg_t2, tanda = 2, es_fg = True)
# =====================================================================
# SECCIÓN 2: SENSIBILIDAD
# =====================================================================
if mostrar_sensibilidad:
    st.markdown("---")
    st.header("Análisis de sensibilidad")
    st.subheader("Normalizada")
    
    sens_norm_t1 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=True)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad FG tanda 1 (Tasa vs $I_D$ Normalizado)", datos_sensibilidad=sens_norm_t1, xlabel = r"Corriente normalizada $I_{D_{norm}}$ [$\mu$A]", ylabel = r"Tasa de cambio normalizada [($\mu$A)/min]")
        
    sens_norm_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=True)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad FG tanda 2 (Tasa vs $I_D$ normalizado)", datos_sensibilidad=sens_norm_t2, xlabel = r"Corriente normalizada $I_{D_{norm}}$ [$\mu$A]", ylabel = r"Tasa de cambio normalizada [($\mu$A)/min]")
        
    st.subheader("Sin normalizar")
    
    sens_abs_t1 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=False)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad absoluta FG Tanda 1 (Tasa absoluta vs $I_D$ normalizado)", datos_sensibilidad=sens_abs_t1, xlabel = r"Corriente normalizada $I_{D_{norm}}$ [$\mu$A]", ylabel = r"Tasa de cambio absoluta [$\mu$A/min]")
        
    sens_abs_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=False)
    graficos.graficar_sensibilidad_fg(titulo="Sensibilidad absoluta FG Tanda 2 (Tasa absoluta vs $I_D$ normalizado)", datos_sensibilidad=sens_abs_t2, xlabel = r"Corriente normalizada $I_{D_{norm}}$ [$\mu$A]", ylabel = r"Tasa de cambio absoluta [$\mu$A/min]")
    
# =====================================================================
# SECCIÓN 3: RUIDO
# =====================================================================
if mostrar_ruido:
    st.markdown("---")
    st.header("Análisis de Ruido")
    
    lista_dispositivos = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_nominales = [100, 150, 200, 250, 350]
    
    resultados_ruido = proc_ruido.procesar_ruido(lista_dispositivos, corrientes_nominales)
    graficos.graficar_ruido(titulo="Desvío estándar del ruido neto vs Corriente nominal", datos_ruido=resultados_ruido)

    evos = proc_ruido.obtener_evolucion_ruido(["PFGIW1"], [100, 150, 200, 250, 350], True)
    
    graficos.graficar_evolucion_ruido(
        titulo="Corriente vs tiempo (log)",
        todas_las_evos=evos,
        corrientes_a_graficar=[100, 150, 200, 250, 350]
    )
# =====================================================================
# SECCIÓN 4: TEMPERATURA
# =====================================================================
if mostrar_temperatura:
    st.markdown("---")
    st.header("Análisis de Coeficiente Térmico")
    
    # Parámetros fijos que querés barrer
    lista_disp_temp = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_temp = [150, 200]
    lista_temps = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]  # Meté acá la lista de temperaturas reales de tus carpetas
    
    # Invocamos al backend que adaptamos antes
    datos_temp = proc_temp.obtener_datos_I_vs_T(lista_disp_temp, corrientes_temp, lista_temps)
    
    # Mandamos a graficar si trajo datos
    if datos_temp and any(datos_temp[d] for d in datos_temp):
        graficos.graficar_I_vs_T(
            titulo="Evolución de Corriente de Drenaje vs Temperatura (@ VD = -5V)",
            datos_temperatura=datos_temp
        )
    else:
        st.warning("No se encontraron archivos de medición de temperatura para los parámetros seleccionados.")

# =====================================================================
# SECCIÓN 4: RESUMEN
# =====================================================================
if mostrar_resumen:
    st.markdown("---")
    st.header("Correlación: sensibilidad absoluta vs ruido neto")
    
    dispositivos_cruce = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_ruido = [100, 150, 200, 250, 350]
    
    # Si las secciones de arriba no se ejecutaron, las calculamos acá de forma segura
    if sens_abs_t2 is None:
        sens_abs_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=False)
        
    if resultados_ruido is None:
        resultados_ruido = proc_ruido.procesar_ruido(dispositivos_cruce, corrientes_ruido)
    
    sens_resumen = {disp: sens_abs_t2[0][disp] for disp in dispositivos_cruce}
    ruido_resumen = {disp: resultados_ruido[disp] for disp in dispositivos_cruce}
    
    graficos.graficar_superposicion_sens_ruido(titulo="Tanda 2: Sensibilidad absoluta y ruido vs I_D normalizada",datos_sensibilidad=sens_resumen,datos_ruido=ruido_resumen)
