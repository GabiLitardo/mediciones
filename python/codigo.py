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

if opcion == "Evolución temporal":
    st.markdown("---")
    st.header("Evolución Temporal")
    
    datos_fg_t1 = proc_evo.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1")
    graficos.graficar_dispositivos("Evolución Floating Gates tanda 1 (I @ V = -4.5 V)", r"$I_D\text{ [}\mu \text{A}]$", datos_fg_t1, 1, True)

    datos_fg_t2 = proc_evo.obtener_datos_crudos_tanda(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2")
    graficos.graficar_dispositivos("Evolución Floating Gates tanda 2 (I @ V = -4.5 V)", r"$I_D\text{ [}\mu \text{A}]$", datos_fg_t2, 2, True)

    datos_foxfet = proc_evo.obtener_datos_crudos_tanda(["FFC1", "FFC2", "FFC3", "FFL", "FFS"], "FOXFET")
    graficos.graficar_dispositivos("Evolución FOXFETs (Tensión interpolada @ I = 0.1 uA)", "Tensión [V]", datos_foxfet, 0, False)

    st.subheader("Evolución de la tensión de compuerta equivalente ($V_{FG}$)")
    
    datos_vg_t1 = proc_evo.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2"], "FG_tanda1")
    graficos.graficar_dispositivos("Descarga temporal de Floating Gates tanda 1 en tensión", r"$\text{Tensión }V_{FG}\text{ [V]}$", datos_vg_t1, 1, True)
    
    datos_vg_t2 = proc_evo.obtener_datos_evolucion_vg(["PFGIW1", "PFGIW2", "PFGIP2"], "FG_tanda2")
    graficos.graficar_dispositivos("Descarga temporal de Floating Gates tanda 2 en tensión", r"$\text{Tensión }V_{FG}\text{ [V]}$", datos_vg_t2, 2, True)

elif opcion == "Sensibilidad":
    st.markdown("---")
    st.header("Análisis de sensibilidad")
    st.subheader("Normalizada")
    
    sens_norm_t1 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=True)
    graficos.graficar_sensibilidad_fg(r"$\text{Sensibilidad FG tanda 1 (Sensibilidad vs }V_{FG}\text{)}$", sens_norm_t1, r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$", r"$\text{Sensibilidad normalizada [V/Gy]}$")
        
    sens_norm_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=True)
    graficos.graficar_sensibilidad_fg(r"$\text{Sensibilidad FG tanda 2 (Sensibilidad vs }V_{FG}\text{)}$", sens_norm_t2, r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$", r"$\text{Sensibilidad normalizada [V/Gy]}$")
        
    st.subheader("Sin normalizar")
    
    sens_abs_t1 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3"], "FG_tanda1", normalizado=False)
    graficos.graficar_sensibilidad_fg(r"$\text{Sensibilidad absoluta FG tanda 1 (Sensibilidad vs }I_D\text{ Normalizado)}$", sens_abs_t1, r"$\text{Corriente normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$", r"$\text{Tasa de cambio [(}\mu\text{A)/Gy]}$")
        
    sens_abs_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=False)
    graficos.graficar_sensibilidad_fg(r"$\text{Sensibilidad absoluta FG tanda 2 (Sensibilidad vs }I_D\text{ Normalizado)}$", sens_abs_t2, r"$\text{Corriente normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$", r"$\text{Tasa de cambio [(}\mu\text{A)/Gy]}$")

elif opcion == "Ruido":
    st.markdown("---")
    st.header("Análisis de Ruido")
    
    dispositivos = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes = [100, 150, 200, 250, 350]

    restar_deriva = st.checkbox("Restar deriva térmica para visualizar el ruido?", value=True)
    resultados_ruido = proc_ruido.procesar_ruido(dispositivos, corrientes, False, restar_deriva)
    graficos.graficar_ruido("Desvío estándar del ruido neto vs Corriente nominal", resultados_ruido)

    evos1 = proc_ruido.obtener_evolucion_ruido(dispositivos, corrientes, False, restar_deriva)
    evos1_sin_deriva = proc_ruido.obtener_evolucion_ruido(dispositivos, corrientes, False, True)

    log = st.checkbox("Graficar Semilog?", value=False)

    graficos.graficar_evolucion_ruido("Corriente vs tiempo a corto plazo", evos1, log)
    graficos.graficar_histograma_ruido("Distribución del Ruido Neto a corto plazo", evos1_sin_deriva)

    evos2 = proc_ruido.obtener_evolucion_ruido(["PFGIW1"], corrientes, True, restar_deriva)
    evos2_sin_deriva = proc_ruido.obtener_evolucion_ruido(["PFGIW1"], corrientes, True, True)

    graficos.graficar_evolucion_ruido("Corriente vs tiempo a largo plazo", evos2, log)
    graficos.graficar_histograma_ruido("Distribución del Ruido Neto a largo plazo", evos2_sin_deriva)

    evos_temp = proc_ruido.obtener_evolucion_temperatura_ruido(dispositivos, corrientes, False)
    graficos.graficar_evolucion_temperatura("Evolución de Temperatura vs Tiempo durante medición de ruido", evos_temp)

    evos_i_vs_t = proc_ruido.obtener_corriente_vs_temperatura_ruido(dispositivos, corrientes, False)
    graficos.graficar_corriente_vs_temperatura_ruido("Corriente vs Temperatura durante medición de ruido", evos_i_vs_t)

elif opcion == "Temperatura":
    st.markdown("---")
    st.header("Análisis de Coeficiente Térmico")
    
    dispositivos = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes = [100, 150, 200, 250, 350]
    temperaturas = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
    
    datos_temp = proc_temp.obtener_datos_I_vs_T(dispositivos, corrientes, temperaturas)
    
    if datos_temp and any(datos_temp[d] for d in datos_temp):
        graficos.graficar_I_vs_T("Evolución de Corriente de Drain vs Temperatura (@ VD = -4.5V)", datos_temp)
    else:
        st.warning("No se encontraron archivos de medición de temperatura para los parámetros seleccionados.")

elif opcion == "Resumen":
    st.markdown("---")
    st.header("Sensibilidad absoluta, ruido y coef. térmico vs $I_D$ normalizada")
    
    dispositivos = ["PFGIW1", "PFGIW2", "PFGIP2"]
    corrientes = [100, 150, 200, 250, 350]
    temperaturas = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
    
    sens_abs_t2 = proc_sens.procesar_sensibilidad(["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"], "FG_tanda2", normalizado=False)
    resultados_ruido = proc_ruido.procesar_ruido(dispositivos, corrientes)
    datos_temp_resumen = proc_temp.obtener_datos_I_vs_T(dispositivos, corrientes, temperaturas)
    
    sens_resumen = {disp: sens_abs_t2[0][disp] for disp in dispositivos}
    ruido_resumen = {disp: resultados_ruido[disp] for disp in dispositivos}
    
    graficos.graficar_superposicion_sens_ruido(
        r"$\text{Sensibilidad absoluta, ruido y coef. térmico vs }I_D \text{ normalizada}$",
        sens_resumen,
        ruido_resumen,
        datos_temp_resumen
    )
    
    st.subheader("Error equivalente por ruido ($\\sigma/S$)")
    graficos.graficar_snr(r"$\text{Error equivalente por ruido (}\sigma\text{/S) vs Corriente Normalizada}$", sens_resumen, ruido_resumen)

    st.subheader("Error Equivalente por Temperatura ($|\\alpha| / S$)")
    graficos.graficar_error_termico_equivalente(r"$\text{Error Térmico Equivalente vs Corriente Normalizada}$", sens_resumen, datos_temp_resumen)