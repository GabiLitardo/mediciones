# codigo.py
import streamlit as st
import numpy as np
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
    graficos.graficar_curvas(
        titulo="Evolución Floating Gates tanda 1 (I @ V = -4.5 V)",
        datos=datos_fg_t1,
        xlabel="Tiempo de irradiación [min]",
        ylabel=r"$I_D\text{ [}\mu \text{A]}$",
        modo='markers+lines'
    )

    datos_fg_t2 = proc_evo.obtener_datos_crudos_tanda(dispos_FG, "FG_tanda2")
    graficos.graficar_curvas(
        titulo="Evolución Floating Gates tanda 2 (I @ V = -4.5 V)",
        datos=datos_fg_t2,
        xlabel="Tiempo de irradiación [min]",
        ylabel=r"$I_D\text{ [}\mu \text{A]}$",
        modo='markers+lines'
    )

    datos_foxfet = proc_evo.obtener_datos_crudos_tanda(dispos_FOXFET, "FOXFET")
    graficos.graficar_curvas(
        titulo="Evolución FOXFETs (Tensión interpolada @ I = 0.1 uA)",
        datos=datos_foxfet,
        xlabel="Tiempo de irradiación [min]",
        ylabel="Tensión [V]",
        modo='markers+lines'
    )

    st.subheader("Evolución de la tensión de compuerta equivalente ($V_{FG}$)")
    
    datos_vg_t1 = proc_evo.obtener_datos_evolucion_vg(dispos_FG, "FG_tanda1")
    graficos.graficar_curvas(
        titulo="Descarga temporal de Floating Gates tanda 1 en tensión",
        datos=datos_vg_t1,
        xlabel="Tiempo de irradiación [min]",
        ylabel=r"$\text{Tensión }V_{FG}\text{ [V]}$",
        modo='markers+lines'
    )
    
    datos_vg_t2 = proc_evo.obtener_datos_evolucion_vg(dispos_FG, "FG_tanda2")
    graficos.graficar_curvas(
        titulo="Descarga temporal de Floating Gates tanda 2 en tensión",
        datos=datos_vg_t2,
        xlabel="Tiempo de irradiación [min]",
        ylabel=r"$\text{Tensión }V_{FG}\text{ [V]}$",
        modo='markers+lines'
    )

# =====================================================================
# SECCIÓN 2: SENSIBILIDAD
# =====================================================================
elif opcion == "Sensibilidad":
    st.markdown("---")
    st.header("Análisis de sensibilidad")
    st.subheader("Normalizada")
    
    sens_norm_t1 = proc_sens.procesar_sensibilidad(dispos_FG, "FG_tanda1", normalizado=True)
    graficos.graficar_curvas(
        titulo=r"$\text{Sensibilidad FG tanda 1 (Sensibilidad vs }V_{FG}\text{)}$",
        datos=sens_norm_t1,
        xlabel=r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$",
        ylabel=r"$\text{Sensibilidad normalizada [V/Gy]}$",
        modo='lines+markers'
    )
        
    sens_norm_t2 = proc_sens.procesar_sensibilidad(dispos_FG, "FG_tanda2", normalizado=True)
    graficos.graficar_curvas(
        titulo=r"$\text{Sensibilidad FG tanda 2 (Sensibilidad vs }V_{FG}\text{)}$",
        datos=sens_norm_t2,
        xlabel=r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$",
        ylabel=r"$\text{Sensibilidad normalizada [V/Gy]}$",
        modo='lines+markers'
    )
        
    st.subheader("Sin normalizar")
    
    sens_abs_t1 = proc_sens.procesar_sensibilidad(dispos_FG, "FG_tanda1", normalizado=False)
    graficos.graficar_curvas(
        titulo=r"$\text{Sensibilidad absoluta FG tanda 1 (Sensibilidad vs }I_D\text{ Normalizado)}$",
        datos=sens_abs_t1,
        xlabel=r"$\text{Corriente normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$",
        ylabel=r"$\text{Tasa de cambio [(}\mu\text{A)/Gy]}$",
        modo='lines+markers'
    )
        
    sens_abs_t2 = proc_sens.procesar_sensibilidad(dispos_FG, "FG_tanda2", normalizado=False)
    graficos.graficar_curvas(
        titulo=r"$\text{Sensibilidad absoluta FG tanda 2 (Sensibilidad vs }I_D\text{ Normalizado)}$",
        datos=sens_abs_t2,
        xlabel=r"$\text{Corriente normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$",
        ylabel=r"$\text{Tasa de cambio [(}\mu\text{A)/Gy]}$",
        modo='lines+markers'
    )

# =====================================================================
# SECCIÓN 3: RUIDO
# =====================================================================
elif opcion == "Ruido":
    st.markdown("---")
    st.header("Análisis de Ruido")

    restar_deriva = st.checkbox("Restar deriva térmica para visualizar el ruido?", value=True)
    log = st.checkbox("Graficar Semilog?", value=False)

    ruido_corto = proc_ruido.obtener_analisis_ruido_completo(
        dispos_FG, corrientes_normalizadas, es_larga=False, restar_deriva=restar_deriva
    )

    graficos.graficar_curvas(
        "Desvío estándar del ruido neto vs Corriente nominal",
        datos=ruido_corto["std_ruido"],
        xlabel=r"$\text{Corriente Nominal }I_D\text{ [}\mu \text{A]}$",
        ylabel="Desvío de Ruido [nA]",
        modo='markers+lines'
    )
    graficos.graficar_curvas(
        "Corriente vs tiempo a corto plazo",
        datos=ruido_corto["evos_ruido"],
        xlabel="Tiempo [s]",
        ylabel=r"$\text{Corriente de Ruido Neto [}\mu\text{A]}$",
        modo='lines',
        es_log=log
    )
    graficos.graficar_histograma_ruido(
        "Distribución del Ruido Neto a corto plazo",
        datos=ruido_corto["evos_ruido"]
    )

    ruido_largo = proc_ruido.obtener_analisis_ruido_completo(
        dispos_FG, corrientes_normalizadas, es_larga=True, restar_deriva=restar_deriva
    )

    graficos.graficar_curvas(
        "Corriente vs tiempo a largo plazo",
        datos=ruido_largo["evos_ruido"],
        xlabel="Tiempo [s]",
        ylabel=r"$\text{Corriente de Ruido Neto [}\mu\text{A]}$",
        modo='lines',
        es_log=log
    )
    graficos.graficar_histograma_ruido(
        "Distribución del Ruido Neto a largo plazo",
        datos=ruido_largo["evos_ruido"]
    )

    graficos.graficar_curvas(
        "Evolución de Temperatura vs Tiempo durante medición de ruido",
        datos=ruido_corto["evos_temp"],
        xlabel="Tiempo [s]",
        ylabel="Temperatura [°C]",
        modo='lines'
    )
    graficos.graficar_curvas(
        "Corriente vs Temperatura durante medición de ruido",
        datos=ruido_corto["i_vs_t"],
        xlabel="Temperatura [°C]",
        ylabel=r"$\text{Corriente }I_D \text{ [}\mu \text{A]}$",
        modo='markers+lines'
    )

# =====================================================================
# SECCIÓN 4: TEMPERATURA
# =====================================================================
elif opcion == "Temperatura":
    st.markdown("---")
    st.header("Análisis de Coeficiente Térmico")
    
    temp_data = proc_temp.obtener_analisis_temperatura(dispos_FG, corrientes_normalizadas, temperaturas)
    
    if temp_data["i_vs_t"]:
        graficos.graficar_curvas(
            titulo="Evolución de Corriente de Drain vs Temperatura (@ VD = -4.5V)",
            datos=temp_data["i_vs_t"],
            xlabel="Temperatura [°C]",
            ylabel=r"$\text{Corriente }I_D \text{ @ }V_D \text{ = -4.5V [}\mu \text{A]}$",
            modo='markers+lines'
        )
        graficos.graficar_curvas(
            titulo=r"$\text{Coeficiente Térmico (}\alpha\text{) vs Corriente Nominal}$",
            datos=temp_data["alpha_vs_i"],
            xlabel=r"$\text{Corriente Nominal }I_D\text{ [}\mu \text{A]}$",
            ylabel=r"$\text{Coeficiente Térmico }\alpha\text{ [}\mu \text{A/°C]}$",
            modo='markers+lines'
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
    ruido_resumen_data = proc_ruido.obtener_analisis_ruido_completo(
        dispos_FG, corrientes_normalizadas, es_larga=False, restar_deriva=True
    )
    temp_resumen_data = proc_temp.obtener_analisis_temperatura(
        dispos_FG, corrientes_normalizadas, temperaturas
    )
    
    sens_resumen = {disp: datos for disp, datos in sens_abs_t2.items() if "(Poly)" not in disp}
    
    graficos.graficar_superposicion_sens_ruido(
        titulo=r"$\text{Sensibilidad absoluta, ruido y coef. térmico vs }I_D \text{ normalizada}$",
        datos_sensibilidad=sens_resumen,
        datos_ruido=ruido_resumen_data["std_ruido"],
        datos_temp=temp_resumen_data["alpha_vs_i"]
    )
    
    st.subheader("Error equivalente por ruido ($\\sigma/S$)")
    err_ruido = {}
    for disp in dispos_FG:
        if disp in sens_resumen and disp in ruido_resumen_data["std_ruido"]:
            s_x = sens_resumen[disp]["x"]
            s_y = sens_resumen[disp]["y"]
            r_x = ruido_resumen_data["std_ruido"][disp]["x"]
            r_y = ruido_resumen_data["std_ruido"][disp]["y"] / 1000.0
            
            s_interp = np.interp(r_x, s_x, s_y)
            err_ruido[disp] = {"x": r_x, "y": r_y / s_interp}

    graficos.graficar_curvas(
        titulo=r"$\text{Error equivalente por ruido (}\sigma\text{/S) vs Corriente Normalizada}$",
        datos=err_ruido,
        xlabel=r"$\text{Corriente Normalizada }I_{D_{norm}} \text{ [}\mu \text{A]}$",
        ylabel="Error Equivalente por Ruido [Gy]",
        modo='markers+lines'
    )

    st.subheader("Error Equivalente por Temperatura ($|\\alpha| / S$)")
    err_temp = {}
    for disp in dispos_FG:
        if disp in sens_resumen and disp in temp_resumen_data["alpha_vs_i"]:
            s_x = sens_resumen[disp]["x"]
            s_y = sens_resumen[disp]["y"]
            t_x = temp_resumen_data["alpha_vs_i"][disp]["x"]
            t_y = np.abs(temp_resumen_data["alpha_vs_i"][disp]["y"])
            
            s_interp = np.interp(t_x, s_x, s_y)
            err_temp[disp] = {"x": t_x, "y": t_y / s_interp}

    graficos.graficar_curvas(
        titulo=r"$\text{Error Térmico Equivalente vs Corriente Normalizada}$",
        datos=err_temp,
        xlabel=r"$\text{Corriente Normalizada }I_{D_{norm}} \text{ [}\mu \text{A]}$",
        ylabel=r"$\text{Error Térmico Equivalente [Gy/°C]}$",
        modo='markers+lines'
    )