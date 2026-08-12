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
dispos_FG = ["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"]
dispos_FOXFET = ["FFC1", "FFC2", "FFC3", "FFL", "FFS"]
corrientes_normalizadas = [100, 150, 200, 250, 350]
temperaturas = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]

# =====================================================================
# SECCIÓN 1: EVOLUCIÓN TEMPORAL
# =====================================================================
if opcion == "Evolución temporal":
    st.markdown("---")
    st.header("Evolución Temporal")
    
    datos_fg_t1 = proc_evo.obtener_datos_crudos_tanda(dispos_FG, "FG_tanda1")
    graficos.graficar_dispositivos(
        titulo="Evolución Floating Gates tanda 1 (I @ V = -4.5 V)",
        ylabel=r"$I_D\text{ [}\mu \text{A}]$",
        datos_procesados=datos_fg_t1
    )

    datos_fg_t2 = proc_evo.obtener_datos_crudos_tanda(dispos_FG, "FG_tanda2")
    graficos.graficar_dispositivos(
        titulo="Evolución Floating Gates tanda 2 (I @ V = -4.5 V)",
        ylabel=r"$I_D\text{ [}\mu \text{A}]$",
        datos_procesados=datos_fg_t2
    )

    datos_foxfet = proc_evo.obtener_datos_crudos_tanda(dispos_FOXFET, "FOXFET")
    graficos.graficar_dispositivos(
        titulo="Evolución FOXFETs (Tensión interpolada @ I = 0.1 uA)",
        ylabel="Tensión [V]",
        datos_procesados=datos_foxfet
    )

    st.subheader("Evolución de la tensión de compuerta equivalente ($V_{FG}$)")
    
    datos_vg_t1 = proc_evo.obtener_datos_evolucion_vg(dispos_FG, "FG_tanda1")
    graficos.graficar_dispositivos(
        titulo="Descarga temporal de Floating Gates tanda 1 en tensión",
        ylabel=r"$\text{Tensión }V_{FG}\text{ [V]}$",
        datos_procesados=datos_vg_t1
    )
    
    datos_vg_t2 = proc_evo.obtener_datos_evolucion_vg(dispos_FG, "FG_tanda2")
    graficos.graficar_dispositivos(
        titulo="Descarga temporal de Floating Gates tanda 2 en tensión",
        ylabel=r"$\text{Tensión }V_{FG}\text{ [V]}$",
        datos_procesados=datos_vg_t2
    )

# =====================================================================
# SECCIÓN 2: SENSIBILIDAD
# =====================================================================
elif opcion == "Sensibilidad":
    st.markdown("---")
    st.header("Análisis de sensibilidad")
    st.subheader("Normalizada")
    
    sens_norm_t1 = proc_sens.procesar_sensibilidad(dispos_FG, "FG_tanda1", normalizado=True)
    graficos.graficar_sensibilidad_fg(
        titulo=r"$\text{Sensibilidad FG tanda 1 (Sensibilidad vs }V_{FG}\text{)}$",
        datos_sensibilidad=sens_norm_t1,
        xlabel=r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$",
        ylabel=r"$\text{Sensibilidad normalizada [V/Gy]}$"
    )
        
    sens_norm_t2 = proc_sens.procesar_sensibilidad(dispos_FG, "FG_tanda2", normalizado=True)
    graficos.graficar_sensibilidad_fg(
        titulo=r"$\text{Sensibilidad FG tanda 2 (Sensibilidad vs }V_{FG}\text{)}$",
        datos_sensibilidad=sens_norm_t2,
        xlabel=r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$",
        ylabel=r"$\text{Sensibilidad normalizada [V/Gy]}$"
    )
        
    st.subheader("Sin normalizar")
    
    sens_abs_t1 = proc_sens.procesar_sensibilidad(dispos_FG, "FG_tanda1", normalizado=False)
    graficos.graficar_sensibilidad_fg(
        titulo=r"$\text{Sensibilidad absoluta FG tanda 1 (Sensibilidad vs }I_D\text{ Normalizado)}$",
        datos_sensibilidad=sens_abs_t1,
        xlabel=r"$\text{Corriente normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$",
        ylabel=r"$\text{Tasa de cambio [(}\mu\text{A)/Gy]}$"
    )
        
    sens_abs_t2 = proc_sens.procesar_sensibilidad(dispos_FG, "FG_tanda2", normalizado=False)
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

    restar_deriva = st.checkbox("Restar deriva térmica para visualizar el ruido?", value=True)
    log = st.checkbox("Graficar Semilog?", value=False)

    ruido_corto = proc_ruido.obtener_analisis_ruido_completo(dispos_FG, corrientes_normalizadas, es_larga=False, restar_deriva=restar_deriva)

    graficos.graficar_curvas("Desvío estándar del ruido neto vs Corriente nominal", ruido_corto["std_ruido"], r"$\text{Corriente Nominal }I_D\text{ [}\mu \text{A]}$", "Desvío de Ruido [nA]", modo='markers')
    graficos.graficar_curvas("Corriente vs tiempo a corto plazo", ruido_corto["evos"], "Tiempo [s]", r"$\text{Corriente de Ruido Neto [}\mu\text{A]}$", modo='lines', es_log=log)
    graficos.graficar_histograma_ruido("Distribución del Ruido Neto a corto plazo", todas_las_evos=ruido_corto["evos"])

    ruido_largo = proc_ruido.obtener_analisis_ruido_completo(dispos_FG, corrientes_normalizadas, es_larga=True, restar_deriva=restar_deriva)

    graficos.graficar_curvas("Corriente vs tiempo a largo plazo", ruido_largo["evos"], "Tiempo [s]", r"$\text{Corriente de Ruido Neto [}\mu\text{A]}$", modo='lines', es_log=log)
    graficos.graficar_histograma_ruido("Distribución del Ruido Neto a largo plazo", todas_las_evos=ruido_largo["evos"])

    graficos.graficar_evolucion_temperatura("Evolución de Temperatura vs Tiempo durante medición de ruido", datos_temp=ruido_corto["evos_temp"])
    graficos.graficar_corriente_vs_temperatura_ruido("Corriente vs Temperatura durante medición de ruido", todas_las_evos_i_vs_t=ruido_corto["i_vs_t"])

# =====================================================================
# SECCIÓN 4: TEMPERATURA
# =====================================================================
elif opcion == "Temperatura":
    st.markdown("---")
    st.header("Análisis de Coeficiente Térmico")
    
    datos_temp = proc_temp.obtener_datos_I_vs_T(dispos_FG, corrientes_normalizadas, temperaturas)
    
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
        
    sens_abs_t2 = proc_sens.procesar_sensibilidad(dispos_FG, "FG_tanda2", normalizado=False)
    ruido_resumen_data = proc_ruido.obtener_analisis_ruido_completo(dispos_FG, corrientes_normalizadas, es_larga=False, restar_deriva=True)
    ruido_resumen = ruido_resumen_data["std_ruido"]
    
    datos_temp_resumen = proc_temp.obtener_datos_I_vs_T(dispos_FG, corrientes_normalizadas, temperaturas)
    
    sens_resumen = {disp: sens_abs_t2[0][disp] for disp in dispos_FG}
    
    st.subheader("Error equivalente por ruido ($\\sigma/S$)")
    graficos.graficar_error_ruido_equivalente(
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