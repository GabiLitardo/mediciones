# FG.py
import numpy as np
import streamlit as st
import graficos
import proc_evo
import proc_sens
import proc_ruido
import proc_temp

def render_FG ():
    st.title("Resumen mediciones Chaves-Litardo")

    opcion = st.sidebar.radio(
        "Seleccionar Análisis",
        ["Evolución temporal", "Sensibilidad", "Ruido", "Temperatura", "Resumen", "Pruebas"]
    )
    DISPOS = ["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"]
    corrientes_normalizadas = [100, 150, 200, 250, 350]
    temperaturas = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]

    # =====================================================================
    # SECCIÓN 1: EVOLUCIÓN TEMPORAL
    # =====================================================================
    if opcion == "Evolución temporal":
        st.markdown("---")
        st.header("Evolución Temporal")
        
        datos_fg_t1 = proc_evo.obtener_datos_crudos_tanda(DISPOS, "FG_tanda1")
        graficos.graficar_curvas(
            titulo="Evolución Floating Gates tanda 1 (I @ V = -4.5 V)",
            dict_datos=datos_fg_t1,
            xlabel="Tiempo de irradiación [min]",
            ylabel=r"$I_D\text{ [}\mu \text{A]}$",
            modo='markers+lines'
        )

        datos_fg_t2 = proc_evo.obtener_datos_crudos_tanda(DISPOS, "FG_tanda2")
        graficos.graficar_curvas(
            titulo="Evolución Floating Gates tanda 2 (I @ V = -4.5 V)",
            dict_datos=datos_fg_t2,
            xlabel="Tiempo de irradiación [min]",
            ylabel=r"$I_D\text{ [}\mu \text{A]}$",
            modo='markers+lines'
        )

        st.subheader("Evolución de la tensión de compuerta equivalente ($V_{FG}$)")
        
        datos_vg_t1 = proc_evo.obtener_datos_evolucion_vg(DISPOS, "FG_tanda1")
        graficos.graficar_curvas(
            titulo="Descarga temporal de Floating Gates tanda 1 en tensión",
            dict_datos=datos_vg_t1,
            xlabel="Tiempo de irradiación [min]",
            ylabel=r"$\text{Tensión }V_{FG}\text{ [V]}$",
            modo='markers+lines'
        )
        
        datos_vg_t2 = proc_evo.obtener_datos_evolucion_vg(DISPOS, "FG_tanda2")
        graficos.graficar_curvas(
            titulo="Descarga temporal de Floating Gates tanda 2 en tensión",
            dict_datos=datos_vg_t2,
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
        
        sens_norm_t1 = proc_sens.procesar_sensibilidad(DISPOS, "FG_tanda1", normalizado=True)
        graficos.graficar_curvas(
            titulo=r"$\text{Sensibilidad FG tanda 1 (Sensibilidad vs }V_{FG}\text{)}$",
            dict_datos=sens_norm_t1,
            xlabel=r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$",
            ylabel=r"$\text{Sensibilidad normalizada [V/Gy]}$",
            modo='markers+lines'
        )
            
        sens_norm_t2 = proc_sens.procesar_sensibilidad(DISPOS, "FG_tanda2", normalizado=True)
        graficos.graficar_curvas(
            titulo=r"$\text{Sensibilidad FG tanda 2 (Sensibilidad vs }V_{FG}\text{)}$",
            dict_datos=sens_norm_t2,
            xlabel=r"$\text{Tensión equivalente }V_{FG}\text{ [V]}$",
            ylabel=r"$\text{Sensibilidad normalizada [V/Gy]}$",
            modo='markers+lines'
        )
            
        st.subheader("Sin normalizar")
        
        sens_abs_t1 = proc_sens.procesar_sensibilidad(DISPOS, "FG_tanda1", normalizado=False)
        graficos.graficar_curvas(
            titulo=r"$\text{Sensibilidad absoluta FG tanda 1 (Sensibilidad vs }I_D\text{ Normalizado)}$",
            dict_datos=sens_abs_t1,
            xlabel=r"$\text{Corriente normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$",
            ylabel=r"$\text{Tasa de cambio [(}\mu\text{A)/Gy]}$",
            modo='markers+lines'
        )
            
        sens_abs_t2 = proc_sens.procesar_sensibilidad(DISPOS, "FG_tanda2", normalizado=False)
        graficos.graficar_curvas(
            titulo=r"$\text{Sensibilidad absoluta FG tanda 2 (Sensibilidad vs }I_D\text{ Normalizado)}$",
            dict_datos=sens_abs_t2,
            xlabel=r"$\text{Corriente normalizada }I_{D_{norm}}\text{ [}\mu\text{A]}$",
            ylabel=r"$\text{Tasa de cambio [(}\mu\text{A)/Gy]}$",
            modo='markers+lines'
        )

    # =====================================================================
    # SECCIÓN 3: RUIDO
    # =====================================================================
    elif opcion == "Ruido":
        st.markdown("---")
        st.header("Análisis de Ruido")

        restar_deriva = st.checkbox("Restar deriva térmica para visualizar el ruido?", value=True)
        logx = st.checkbox("Escala logarítmica en eje x?", value=False)

        ruido_corto = proc_ruido.obtener_analisis_ruido_completo(
            DISPOS, corrientes_normalizadas, es_larga=False, restar_deriva=restar_deriva
        )

        graficos.graficar_curvas(
            "Desvío estándar del ruido neto vs Corrientes Normalizadas",
            dict_datos=ruido_corto["std_ruido"],
            xlabel=r"$\text{Corrientes normalizadas }I_D\text{ [}\mu \text{A]}$",
            ylabel="Desvío de Ruido [nA]",
            modo='markers'
        )
        graficos.graficar_curvas(
            "Corriente vs tiempo a corto plazo",
            dict_datos=ruido_corto["evos"],
            xlabel="Tiempo [s]",
            ylabel=r"$\text{Corriente de Ruido Neto [}\mu\text{A]}$",
            modo='lines',
            logx=logx
        )
        graficos.graficar_histograma_ruido(
            "Distribución del Ruido Neto a corto plazo",
            dict_datos=ruido_corto["evos"]
        )

        graficos.graficar_curvas(
            "Densidad Espectral de Potencia (PSD) - Corto Plazo",
            dict_datos=ruido_corto["psd"],
            xlabel="Frecuencia [Hz]",
            ylabel=r"$\text{PSD [}\mu\text{A}^2/\text{Hz]}$",
            modo='lines',
            logx=True,
            logy=True
        )

        ruido_largo = proc_ruido.obtener_analisis_ruido_completo(
            DISPOS, corrientes_normalizadas, es_larga=True, restar_deriva=restar_deriva
        )

        graficos.graficar_curvas(
            "Corriente vs tiempo a largo plazo",
            dict_datos=ruido_largo["evos"],
            xlabel="Tiempo [s]",
            ylabel=r"$\text{Corriente de Ruido Neto [}\mu\text{A]}$",
            modo='lines',
            logx=logx
        )
        graficos.graficar_histograma_ruido(
            "Distribución del Ruido Neto a largo plazo",
            dict_datos=ruido_largo["evos"]
        )

        graficos.graficar_curvas(
            "Evolución de Temperatura vs Tiempo durante medición de ruido",
            dict_datos=ruido_corto["evos_temp"],
            xlabel="Tiempo [s]",
            ylabel="Temperatura [°C]",
            modo='lines'
        )
        graficos.graficar_curvas(
            "Corriente vs Temperatura durante medición de ruido",
            dict_datos=ruido_corto["i_vs_t"],
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

        datos_temp = proc_temp.obtener_analisis_temperatura(
            DISPOS, corrientes_normalizadas, temperaturas
        )

        graficos.graficar_curvas(
            titulo="Evolución de Corriente de Drain vs Temperatura (@ VD = -4.5V)",
            dict_datos=datos_temp["i_vs_t"],
            xlabel="Temperatura [°C]",
            ylabel=r"$\text{Corriente }I_D \text{ @ }V_D \text{ = -4.5V [}\mu \text{A]}$",
            modo='markers+lines'
        )
        graficos.graficar_curvas(
            titulo=r"$\text{Coeficiente Térmico (}\alpha\text{) vs Corrientes Normalizadas}$",
            dict_datos=datos_temp["alpha_vs_i"],
            xlabel=r"$\text{Corrientes Normalizadas }I_D\text{ [}\mu \text{A]}$",
            ylabel=r"$\text{Coeficiente Térmico }\alpha\text{ [}\mu \text{A/°C]}$",
            modo='markers+lines'
        )

        fits_ztc = {
            tag.replace(" (Fit)", ""): datos["ztc"]
            for tag, datos in datos_temp["alpha_vs_i"].items()
            if "(Fit)" in tag and "ztc" in datos
        }

        if fits_ztc:
            cols = st.columns(len(fits_ztc))
            for col, (disp_nombre, val_ztc) in zip(cols, fits_ztc.items()):
                col.metric(
                    label=f"$I_{{ZTC}}$ ({disp_nombre})",
                    value=f"{val_ztc:.2f} µA"
                )
    # =====================================================================
    # SECCIÓN 5: RESUMEN
    # =====================================================================
    elif opcion == "Resumen":
        st.markdown("---")
        st.header("Sensibilidad absoluta, ruido y coef. térmico vs $I_D$ normalizada")
            
        # 1. Obtención de datos con la estructura plana unificada
        sens_abs_t2 = proc_sens.procesar_sensibilidad(DISPOS, "FG_tanda2", normalizado=False)
        ruido_resumen_data = proc_ruido.obtener_analisis_ruido_completo(DISPOS, corrientes_normalizadas, es_larga=False, restar_deriva=True)
        temp_resumen_data = proc_temp.obtener_analisis_temperatura(DISPOS, corrientes_normalizadas, temperaturas)
        
        # 2. Filtrado de la sensibilidad discreta (sin los ajustes 'Fit')
        sens_resumen = {disp: datos for disp, datos in sens_abs_t2.items() if "(Fit)" not in disp}
        
        # 3. Gráfico: Error equivalente por ruido (\sigma / S)
        st.subheader("Error equivalente por ruido ($\\sigma/S$)")
        graficos.graficar_relacion_normalizada(
            titulo=r"$\text{Error equivalente por ruido (}\sigma\text{/S) vs Corriente Normalizada}$",
            datos_numerador=ruido_resumen_data["std_ruido"],         
            datos_sensibilidad=sens_resumen, 
            ylabel="Error Equivalente por Ruido [cGy]", 
            factor_escala=100.0/1000.0
        )

        # 4. Modulo de alpha para el error térmico (|alpha| / S)
        temp_resumen_abs = {
            disp: {"x": datos["x"], "y": np.abs(datos["y"])} 
            for disp, datos in temp_resumen_data["alpha_vs_i"].items()
        }

        # 5. Gráfico: Error térmico equivalente (|alpha| / S)
        st.subheader("Error Equivalente por Temperatura ($|\\alpha| / S$)")
        graficos.graficar_relacion_normalizada(
            titulo=r"$\text{Error Térmico Equivalente vs Corriente Normalizada}$",
            datos_numerador=temp_resumen_abs,         
            datos_sensibilidad=sens_resumen, 
            ylabel="Error Térmico Equivalente [cGy/°C]",
            factor_escala=100.0
        )

    # =====================================================================
    # SECCIÓN 6: PRUEBAS
    # =====================================================================
    elif opcion == "Pruebas":
        st.subheader("Curvas de Transferencia I-V de Referencia")
        
        datos_iv_ref = proc_evo.obtener_curvas_iv_referencia(["PFGIW1", "PFGIW2"])
        graficos.graficar_curvas(
            titulo="Curvas de Transferencia I-V de Referencia (@ VD = -4.5 V)",
            dict_datos=datos_iv_ref,
            xlabel=r"$\text{Tensión de Compuerta }V_G\text{ [V]}$",
            ylabel=r"$I_D\text{ [}\mu \text{A]}$",
            modo='markers'
        )

        ztc_iw1 = 30.58e-6
        ztc_iw2 = 13.96e-6
        ztc_ip2 = 17.39e-6
        st.text(f"Se estima que las corrientes de ZTC son: PFGIW1->{ztc_iw1*1e6:.2f}uA ; PFGIW2->{ztc_iw2*1e6:.2f}uA ; PFGIP2->{ztc_ip2*1e6:.2f}uA")
        st.text("Para saber si en esa corriente los dispositivos estarían en saturación, me fijo su tensión de Floating Gate equivalente")
        vg_iw1 = {proc_evo.obtener_vg_por_corriente("PFGIW1", ztc_iw1)}
        vg_iw2 = {proc_evo.obtener_vg_por_corriente("PFGIW2", ztc_iw2)}
        vg_ip2 = {proc_evo.obtener_vg_por_corriente("PFGIP2", ztc_ip2)}
        st.text(f"Las tensiones equivalentes para ZTC son: PFGIW1->{vg_iw1:.2f}V ; PFGIW2->{vg_iw2:.2f}V ; PFGIP2->{vg_ip2:.2f}V")
        st.text(f"Se estiman los Vt: PFGIW1->{datos_iv_ref["PFGIW1"]["vt"] :.2f} ; (PFGIW2, PFGIP2)->{datos_iv_ref["PFGIW2"]["vt"] :.2f}")
        st.text(f"Entonces para el PFGIW1: {vg_iw1}V < {datos_iv_ref["PFGIW1"]["vt"] :.2f} y -4.5V < {vg_iw1 - datos_iv_ref["PFGIW1"]["vt"] :.2f}")
        st.text(f"Para el PFGIW2: {vg_iw2}V < {datos_iv_ref["PFGIW2"]["vt"] :.2f} y -4.5V < {vg_iw2 - datos_iv_ref["PFGIW2"]["vt"] :.2f}")
        st.text(f"Para el PFGIP2: {vg_ip2}V < {datos_iv_ref["PFGIW2"]["vt"] :.2f} y -4.5V < {vg_ip2 - datos_iv_ref["PFGIW2"]["vt"] :.2f}")
