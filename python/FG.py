# FG.py
import numpy as np
import streamlit as st
import graficos, proc_evo, proc_sens, proc_ruido, proc_temp

def render_FG():
    st.title("Resumen mediciones Chaves-Litardo")

    DISPOS = ["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"]
    CORRIENTES = [100, 150, 200, 250, 350]
    TEMPERATURAS = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]

    tab_evo, tab_sens, tab_ruido, tab_temp, tab_resumen, tab_pruebas = st.tabs(
        ["Evolución temporal", "Sensibilidad", "Ruido", "Temperatura", "Resumen", "Pruebas"]
    )

    with tab_evo:
        st.header("Evolución Temporal")
        datos_fg_t1 = proc_evo.obtener_datos_crudos_tanda(DISPOS, "FG_tanda1")
        graficos.graficar_curvas("Evolución Floating Gates tanda 1 (I @ V = -4.5 V)", datos_fg_t1, "Tiempo de irradiación [min]", r"$I_D\text{ [}\mu \text{A]}$", modo='markers+lines')

        datos_fg_t2 = proc_evo.obtener_datos_crudos_tanda(DISPOS, "FG_tanda2")
        graficos.graficar_curvas("Evolución Floating Gates tanda 2 (I @ V = -4.5 V)", datos_fg_t2, "Tiempo de irradiación [min]", r"$I_D\text{ [}\mu \text{A]}$", modo='markers+lines')

        st.subheader("Evolución de la tensión de compuerta equivalente ($V_{FG}$)")
        datos_vg_t1 = proc_evo.obtener_datos_evolucion_vg(DISPOS, "FG_tanda1")
        graficos.graficar_curvas("Descarga temporal de Floating Gates tanda 1 en tensión", datos_vg_t1, "Tiempo de irradiación [min]", r"$\text{Tensión }V_{FG}\text{ [V]}$", modo='markers+lines')

        datos_vg_t2 = proc_evo.obtener_datos_evolucion_vg(DISPOS, "FG_tanda2")
        graficos.graficar_curvas("Descarga temporal de Floating Gates tanda 2 en tensión", datos_vg_t2, "Tiempo de irradiación [min]", r"$\text{Tensión }V_{FG}\text{ [V]}$", modo='markers+lines')

    with tab_sens:
        st.header("Análisis de sensibilidad")
        st.subheader("Normalizada")
        sens_norm_t1 = proc_sens.procesar_sensibilidad(DISPOS, "FG_tanda1", normalizado=True)
        graficos.graficar_curvas(r"$\text{Sensibilidad FG tanda 1 (Sensibilidad vs }V_{FG}\text{)}$", sens_norm_t1, r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$", r"$\text{Sensibilidad normalizada [V/Gy]}$", modo='markers+lines')

        sens_norm_t2 = proc_sens.procesar_sensibilidad(DISPOS, "FG_tanda2", normalizado=True)
        graficos.graficar_curvas(r"$\text{Sensibilidad FG tanda 2 (Sensibilidad vs }V_{FG}\text{)}$", sens_norm_t2, r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$", r"$\text{Sensibilidad normalizada [V/Gy]}$", modo='markers+lines')

        st.subheader("Sin normalizar")
        sens_abs_t1 = proc_sens.procesar_sensibilidad(DISPOS, "FG_tanda1", normalizado=False)
        graficos.graficar_curvas(r"$\text{Sensibilidad absoluta FG tanda 1 (Sensibilidad vs }I_D\text{ Normalizado)}$", sens_abs_t1, r"$\text{Corriente normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$", r"$\text{Tasa de cambio [(}\mu\text{A)/Gy]}$", modo='markers+lines')

        sens_abs_t2 = proc_sens.procesar_sensibilidad(DISPOS, "FG_tanda2", normalizado=False)
        graficos.graficar_curvas(r"$\text{Sensibilidad absoluta FG tanda 2 (Sensibilidad vs }I_D\text{ Normalizado)}$", sens_abs_t2, r"$\text{Corriente normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$", r"$\text{Tasa de cambio [(}\mu\text{A)/Gy]}$", modo='markers+lines')

    with tab_ruido:
        st.header("Análisis de Ruido")
        restar_deriva = st.checkbox("Restar deriva térmica para visualizar el ruido?", value=True)
        logx = st.checkbox("Escala logarítmica en eje x?", value=False)

        ruido_corto = proc_ruido.obtener_analisis_ruido_completo(DISPOS, CORRIENTES, es_larga=False, restar_deriva=restar_deriva)
        graficos.graficar_curvas("Desvío estándar del ruido neto vs Corrientes Normalizadas", dict_datos=ruido_corto["std_ruido"], xlabel=r"$\text{Corrientes normalizadas }I_D\text{ [}\mu \text{A]}$", ylabel="Desvío de Ruido [nA]", modo='markers')
        graficos.graficar_curvas("Corriente vs tiempo a corto plazo", dict_datos=ruido_corto["evos"], xlabel="Tiempo [s]", ylabel=r"$\text{Corriente de Ruido Neto [}\mu\text{A]}$", modo='lines', logx=logx)
        graficos.graficar_histograma_ruido("Distribución del Ruido Neto a corto plazo", dict_datos=ruido_corto["evos"])
        graficos.graficar_curvas("Densidad Espectral de Potencia (PSD) - Corto Plazo", dict_datos=ruido_corto["psd"], xlabel="Frecuencia [Hz]", ylabel=r"$\text{PSD [}\mu\text{A}^2/\text{Hz]}$", modo='lines', logx=True, logy=True)

        ruido_largo = proc_ruido.obtener_analisis_ruido_completo(DISPOS, CORRIENTES, es_larga=True, restar_deriva=restar_deriva)
        graficos.graficar_curvas("Corriente vs tiempo a largo plazo", dict_datos=ruido_largo["evos"], xlabel="Tiempo [s]", ylabel=r"$\text{Corriente de Ruido Neto [}\mu\text{A]}$", modo='lines', logx=logx)
        graficos.graficar_histograma_ruido("Distribución del Ruido Neto a largo plazo", dict_datos=ruido_largo["evos"])
        graficos.graficar_curvas("Evolución de Temperatura vs Tiempo durante medición de ruido", dict_datos=ruido_corto["evos_temp"], xlabel="Tiempo [s]", ylabel="Temperatura [°C]", modo='lines')
        graficos.graficar_curvas("Corriente vs Temperatura durante medición de ruido", dict_datos=ruido_corto["i_vs_t"], xlabel="Temperatura [°C]", ylabel=r"$\text{Corriente }I_D \text{ [}\mu \text{A]}$", modo='markers+lines')

    with tab_temp:
        st.header("Análisis de Coeficiente Térmico")
        datos_temp = proc_temp.obtener_analisis_temperatura(DISPOS, CORRIENTES, TEMPERATURAS)
        graficos.graficar_curvas("Evolución de Corriente de Drain vs Temperatura (@ VD = -4.5V)", datos_temp["i_vs_t"], "Temperatura [°C]", r"$\text{Corriente }I_D \text{ @ }V_D \text{ = -4.5V [}\mu \text{A]}$", modo='markers+lines')
        graficos.graficar_curvas(r"$\text{Coeficiente Térmico (}\alpha\text{) vs Corrientes Normalizadas}$", datos_temp["alpha_vs_i"], r"$\text{Corrientes Normalizadas }I_D\text{ [}\mu \text{A]}$", r"$\text{Coeficiente Térmico }\alpha\text{ [}\mu \text{A/°C]}$", modo='markers+lines')

    with tab_resumen:
        st.header("Sensibilidad absoluta, ruido y coef. térmico vs $I_D$ normalizada")
        sens_abs_t2 = proc_sens.procesar_sensibilidad(DISPOS, "FG_tanda2", normalizado=False)
        ruido_resumen_data = proc_ruido.obtener_analisis_ruido_completo(DISPOS, CORRIENTES, es_larga=False, restar_deriva=True)
        temp_resumen_data = proc_temp.obtener_analisis_temperatura(DISPOS, CORRIENTES, TEMPERATURAS)
        sens_resumen = {disp: d for disp, d in sens_abs_t2.items() if "(Fit)" not in disp}

        st.subheader(r"Error equivalente por ruido ($\sigma/S$)")
        graficos.graficar_relacion_normalizada(r"$\text{Error equivalente por ruido (}\sigma\text{/S) vs Corriente Normalizada}$", ruido_resumen_data["std_ruido"], sens_resumen, "Error Equivalente por Ruido [cGy]", 100.0/1000.0)

        temp_resumen_abs = {disp: {"x": d["x"], "y": np.abs(d["y"])} for disp, d in temp_resumen_data["alpha_vs_i"].items()}
        st.subheader(r"Error Equivalente por Temperatura ($|\alpha| / S$)")
        graficos.graficar_relacion_normalizada(r"$\text{Error Térmico Equivalente vs Corriente Normalizada}$", temp_resumen_abs, sens_resumen, "Error Térmico Equivalente [cGy/°C]", 100.0)

    with tab_pruebas:
        st.subheader("Curvas de Transferencia I-V de Referencia")
        datos_iv_ref = proc_evo.obtener_curvas_iv_referencia(["PFGIW1", "PFGIW2"])
        graficos.graficar_curvas("Curvas de Transferencia I-V de Referencia (@ VD = -4.5 V)", datos_iv_ref, r"$\text{Tensión de Compuerta }V_G\text{ [V]}$", r"$I_D\text{ [}\mu \text{A]}$", modo='markers')