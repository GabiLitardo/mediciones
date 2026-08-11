# codigo.py
import streamlit as st
import graficos
import proc_evo
import proc_sens
import proc_ruido
import proc_temp
 
st.title("Resumen mediciones Chaves-Litardo")

opcion = st.sidebar.radio(
    "Seleccionar Análisis",
    ["Evolución temporal", "Sensibilidad", "Ruido", "Temperatura", "Resumen"]
)

# =====================================================================
# SECCIÓN 1: EVOLUCIÓN TEMPORAL
# =====================================================================
if opcion == "Evolución temporal":
    st.markdown("---")
    st.header("Evolución Temporal")
    
    datos_fg_t1 = proc_evo.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1")
    graficos.graficar_dispositivos(
        titulo="Evolución Floating Gates tanda 1 (I @ V = -4.5 V)",
        ylabel=r"$I_D\text{ [}\mu \text{A}]$",
        datos_procesados=datos_fg_t1,
        tanda=1,
        es_fg=True
    )

    datos_fg_t2 = proc_evo.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2")
    graficos.graficar_dispositivos(
        titulo="Evolución Floating Gates tanda 2 (I @ V = -4.5 V)",
        ylabel=r"$I_D\text{ [}\mu \text{A}]$",
        datos_procesados=datos_fg_t2,
        tanda=2,
        es_fg=True
    )

    datos_foxfet = proc_evo.obtener_datos_crudos_tanda(["FFC1", "FFC2", "FFC3", "FFL", "FFS"], "FOXFET")
    graficos.graficar_dispositivos(
        titulo="Evolución FOXFETs (Tensión interpolada @ I = 0.1 uA)",
        ylabel="Tensión [V]",
        datos_procesados=datos_foxfet,
        tanda=0, 
        es_fg=False
    )

    st.subheader("Evolución de la tensión de compuerta equivalente ($V_{FG}$)")
    
    datos_vg_t1 = proc_evo.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2"], "FG_tanda1")
    graficos.graficar_dispositivos(
        titulo="Descarga temporal de Floating Gates tanda 1 en tensión",
        ylabel=r"$\text{Tensión }V_{FG}\text{ [V]}$",
        datos_procesados=datos_vg_t1,
        tanda=1,
        es_fg=True
    )
    
    datos_vg_t2 = proc_evo.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2", "PFGIP2"], "FG_tanda2")
    graficos.graficar_dispositivos(
        titulo="Descarga temporal de Floating Gates tanda 2 en tensión",
        ylabel=r"$\text{Tensión }V_{FG}\text{ [V]}$",
        datos_procesados=datos_vg_t2,
        tanda=2,
        es_fg=True
    )

# =====================================================================
# SECCIÓN 2: SENSIBILIDAD
# =====================================================================
elif opcion == "Sensibilidad":
    st.markdown("---")
    st.header("Análisis de sensibilidad")
    st.subheader("Normalizada")
    
    sens_norm_t1 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=True)
    graficos.graficar_sensibilidad_fg(
        titulo=r"$\text{Sensibilidad FG tanda 1 (Sensibilidad vs }V_{FG}\text{)}$",
        datos_sensibilidad=sens_norm_t1,
        xlabel=r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$",
        ylabel=r"$\text{Sensibilidad normalizada [V/Gy]}$"
    )
        
    sens_norm_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=True)
    graficos.graficar_sensibilidad_fg(
        titulo=r"$\text{Sensibilidad FG tanda 2 (Sensibilidad vs }V_{FG}\text{)}$",
        datos_sensibilidad=sens_norm_t2,
        xlabel=r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$",
        ylabel=r"$\text{Sensibilidad normalizada [V/Gy]}$"
    )
        
    st.subheader("Sin normalizar")
    
    sens_abs_t1 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=False)
    graficos.graficar_sensibilidad_fg(
        titulo=r"$\text{Sensibilidad absoluta FG tanda 1 (Sensibilidad vs }I_D\text{ Normalizado)}$",
        datos_sensibilidad=sens_abs_t1,
        xlabel=r"$\text{Corriente normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$",
        ylabel=r"$\text{Tasa de cambio [(}\mu\text{A)/Gy]}$"
    )
        
    sens_abs_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=False)
    graficos.graficar_sensibilidad_fg(
        titulo=r"$\text{Sensibilidad absoluta FG tanda 2 (Sensibilidad vs }I_D\text{ Normalizado)}$",
        datos_sensibilidad=sens_abs_t2,
        xlabel=r"$\text{Corriente normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$",
        ylabel=r"$\text{Tasa de cambio [(}\mu\text{A)/Gy]}$"
    )

# =====================================================================
# SECCIÓN 3: RUIDO
# =====================================================================
elif opcion == "Ruido":
    st.markdown("---")
    st.header("Análisis de Ruido")
    
    lista_dispositivos = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_nominales = [100, 150, 200, 250, 350]

    restar_deriva = st.checkbox("Restar deriva térmica para visualizar el ruido?", value=True)
    log = st.checkbox("Graficar Semilog?", value=False)

    # Procesamiento en una sola pasada para corto plazo
    datos_corto = proc_ruido.obtener_analisis_ruido_completo(lista_dispositivos, corrientes_nominales, es_larga=False)
    evos1, evos_temp, evos_i_vs_t, resultados_ruido = proc_ruido.extraer_estructuras_ruido(datos_corto, restar_deriva)
    _, _, _, ruido_neto_corto = proc_ruido.extraer_estructuras_ruido(datos_corto, restar_deriva=True)

    graficos.graficar_ruido(titulo="Desvío estándar del ruido neto vs Corriente nominal", datos_ruido=resultados_ruido)

    graficos.graficar_evolucion_ruido(titulo="Corriente vs tiempo a corto plazo", todas_las_evos=evos1, es_log=log)
    graficos.graficar_histograma_ruido(titulo="Distribución del Ruido Neto a corto plazo", todas_las_evos=evos1)

    # Procesamiento en una sola pasada para largo plazo
    datos_largo = proc_ruido.obtener_analisis_ruido_completo(["PFGIW1"], corrientes_nominales, es_larga=True)
    evos2, _, _, _ = proc_ruido.extraer_estructuras_ruido(datos_largo, restar_deriva)

    graficos.graficar_evolucion_ruido(titulo="Corriente vs tiempo a largo plazo", todas_las_evos=evos2, es_log=log)
    graficos.graficar_histograma_ruido(titulo="Distribución del Ruido Neto a largo plazo", todas_las_evos=evos2)

    graficos.graficar_evolucion_temperatura(titulo="Evolución de Temperatura vs Tiempo durante medición de ruido", datos_temp=evos_temp)
    graficos.graficar_corriente_vs_temperatura_ruido(titulo="Corriente vs Temperatura durante medición de ruido", todas_las_evos_i_vs_t=evos_i_vs_t)

# =====================================================================
# SECCIÓN 4: TEMPERATURA
# =====================================================================
elif opcion == "Temperatura":
    st.markdown("---")
    st.header("Análisis de Coeficiente Térmico")
    
    lista_disp_temp = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_temp = [100, 150, 200, 250, 350]
    lista_temps = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
    
    datos_temp = proc_temp.obtener_datos_I_vs_T(lista_disp_temp, corrientes_temp, lista_temps)
    
    if datos_temp and any(datos_temp[d] for d in datos_temp):
        graficos.graficar_I_vs_T(
            titulo="Evolución de Corriente de Drain vs Temperatura (@ VD = -4.5V)",
            datos_temperatura=datos_temp
        )
    else:
        st.warning("No se encontraron archivos de medición de temperatura para los parámetros seleccionados.")

# =====================================================================
# SECCIÓN 5: RESUMEN
# =====================================================================
elif opcion == "Resumen":
    st.markdown("---")
    st.header("Sensibilidad absoluta, ruido y coef. térmico vs $I_D$ normalizada")
    
    dispositivos_cruce = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes_ruido = [100, 150, 200, 250, 350]
    lista_temps_resumen = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
    
    sens_abs_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=False)
    resultados_ruido = proc_ruido.procesar_ruido(dispositivos_cruce, corrientes_ruido)
    datos_temp_resumen = proc_temp.obtener_datos_I_vs_T(dispositivos_cruce, corrientes_ruido, lista_temps_resumen)
    
    sens_resumen = {disp: sens_abs_t2[0][disp] for disp in dispositivos_cruce}
    ruido_resumen = {disp: resultados_ruido[disp] for disp in dispositivos_cruce}
    
    graficos.graficar_superposicion_sens_ruido(
        titulo=r"$\text{Sensibilidad absoluta, ruido y coef. térmico vs }I_D \text{ normalizada}$",
        datos_sensibilidad=sens_resumen,
        datos_ruido=ruido_resumen,
        datos_temp=datos_temp_resumen
    )
    
    st.subheader("Error equivalente por ruido ($\\sigma/S$)")
    graficos.graficar_snr(
        titulo=r"$\text{Error equivalente por ruido (}\sigma\text{/S) vs Corriente Normalizada}$",
        datos_sensibilidad=sens_resumen,
        datos_ruido=ruido_resumen
    )

    st.subheader("Error Equivalente por Temperatura ($|\\alpha| / S$)")
    graficos.graficar_error_termico_equivalente(
        titulo=r"$\text{Error Térmico Equivalente vs Corriente Normalizada}$",
        datos_sensibilidad=sens_resumen,
        datos_temp=datos_temp_resumen
    )