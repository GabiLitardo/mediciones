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
    CORRIENTES = [100, 150, 200, 250, 350]
    TEMPERATURAS = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]

    # =====================================================================
    # SECCIÓN 1: EVOLUCIÓN TEMPORAL
    # =====================================================================
    if opcion == "Evolución temporal":
        st.markdown("---")
        st.header("Evolución Temporal")

        en_dosis = st.checkbox("Graficar en función de dosis acumulada?", value=False)
        
        datos_fg_t1 = proc_evo.obtener_datos_crudos_tanda(DISPOS, "FG_tanda1", en_dosis=en_dosis)
        graficos.graficar_curvas(
            titulo="Evolución Floating Gates tanda 1 (I @ V = -4.5 V)",
            dict_datos=datos_fg_t1,
            xlabel="Dosis Acumulada [Gy]" if en_dosis else "Tiempo de irradiación [min]",
            ylabel=r"$I_D\text{ [}\mu \text{A]}$",
            modo='markers+lines'
        )

        datos_fg_t2 = proc_evo.obtener_datos_crudos_tanda(DISPOS, "FG_tanda2", en_dosis=en_dosis)
        graficos.graficar_curvas(
            titulo="Evolución Floating Gates tanda 2 (I @ V = -4.5 V)",
            dict_datos=datos_fg_t2,
            xlabel="Dosis Acumulada [Gy]" if en_dosis else "Tiempo de irradiación [min]",
            ylabel=r"$I_D\text{ [}\mu \text{A]}$",
            modo='markers+lines'
        )

        st.subheader("Evolución de la tensión de compuerta equivalente ($V_{FG}$)")
        
        datos_vg_t1 = proc_evo.obtener_datos_evolucion_vg(DISPOS, "FG_tanda1", en_dosis = en_dosis)
        graficos.graficar_curvas(
            titulo="Descarga temporal de Floating Gates tanda 1 en tensión",
            dict_datos=datos_vg_t1,
            xlabel="Dosis Acumulada [Gy]" if en_dosis else "Tiempo de irradiación [min]",
            ylabel=r"$\text{Tensión }V_{FG}\text{ [V]}$",
            modo='markers+lines'
        )
        
        datos_vg_t2 = proc_evo.obtener_datos_evolucion_vg(DISPOS, "FG_tanda2", en_dosis = en_dosis)
        graficos.graficar_curvas(
            titulo="Descarga temporal de Floating Gates tanda 2 en tensión",
            dict_datos=datos_vg_t2,
            xlabel="Dosis Acumulada [Gy]" if en_dosis else "Tiempo de irradiación [min]",
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
        extra = st.checkbox("Graficar cosas extra?", value=False)

        ruido_corto = proc_ruido.obtener_analisis_ruido_completo(
            DISPOS, CORRIENTES, es_larga=False, restar_deriva=restar_deriva
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
        if extra:
            graficos.graficar_histograma_ruido(
                "Distribución del Ruido Neto a corto plazo",
                dict_datos=ruido_corto["evos"]
            )
        if extra:
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
            DISPOS, CORRIENTES, es_larga=True, restar_deriva=restar_deriva
        )
        if extra:
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
            modo='lines',
            logx=logx
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
            DISPOS, CORRIENTES, TEMPERATURAS
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

        if "PFGIW1 (Fit)" in datos_temp.get("alpha_vs_i", {}):
            for disp in ["PFGIW1", "PFGIW2", "PFGIP2"]:
                st.write(r"$I_{ZTC}$"+f"({disp}): {datos_temp['alpha_vs_i'][f"{disp} (Fit)"]['ztc'] :.2f} µA")

        datos_temp_std = proc_temp.obtener_analisis_temperatura_foxfet(
            ["STD1", "STD2"], TEMPERATURAS
        )

        graficos.graficar_curvas(
            titulo="Curvas de Transferencia vs Temperatura (@ VD = 5V)",
            dict_datos=datos_temp_std["iv_vs_t"],
            xlabel=r"$\text{Tensión }V_{GS}\text{ [V]}$",
            ylabel=r"$\text{Corriente }I_D\text{ [}\mu \text{A]}$",
            modo='lines',
            logy=False
        )

        graficos.graficar_curvas(
            titulo=r"$\text{Coeficiente Térmico (}\alpha\text{) vs Tensión }V_{GS}$",
            dict_datos=datos_temp_std["alpha_vs_vgs"],
            xlabel=r"$\text{Tensión }V_{GS}\text{ [V]}$",
            ylabel=r"$\text{Coeficiente Térmico }\alpha\text{ [}\mu \text{A/°C]}$",
            modo='lines'
        )

        graficos.graficar_curvas(
            titulo=r"$\text{Coeficiente Térmico (}\alpha\text{) vs Corriente }I_D\text{ (@ 30°C)}$",
            dict_datos=datos_temp_std["alpha_vs_i"],
            xlabel=r"$\text{Corriente }I_D\text{ [}\mu \text{A]}$",
            ylabel=r"$\text{Coeficiente Térmico }\alpha\text{ [}\mu \text{A/°C]}$",
            modo='lines',
            logx=True
        )
    # =====================================================================
    # SECCIÓN 5: RESUMEN
    # =====================================================================
    elif opcion == "Resumen":
        st.markdown("---")
        st.header("Sensibilidad absoluta, ruido y coef. térmico vs $I_D$ normalizada")
            
        # 1. Obtención de datos con la estructura plana unificada
        sens_abs_t2 = proc_sens.procesar_sensibilidad(DISPOS, "FG_tanda2", normalizado=False)
        ruido_resumen_data = proc_ruido.obtener_analisis_ruido_completo(DISPOS, CORRIENTES, es_larga=False, restar_deriva=True)
        temp_resumen_data = proc_temp.obtener_analisis_temperatura(DISPOS, CORRIENTES, TEMPERATURAS)
        
        # 2. Filtrado de la sensibilidad discreta (sin los ajustes 'Fit')
        sens_resumen = {disp: datos for disp, datos in sens_abs_t2.items() if "(Fit)" not in disp}
        
        # 3. Gráfico: Error equivalente por ruido (sigma / S)
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

        st.subheader("Error Total Combinado")
        
        delta_t = st.slider(
            r"Variación de temperatura supuesta $\Delta T$ [°C]",
            min_value=0.1,
            max_value=5.0,
            value=0.1,
            step=0.1
        )

        peso_ruido = st.slider(
            "Peso del error por ruido",
            min_value=0.01,
            max_value=1.00,
            value=0.50,
            step=0.01
        )

        peso_temp = st.slider(
            "Peso del error por temperatura",
            min_value=0.01,
            max_value=1.00,
            value=0.50,
            step=0.01
        )      

        datos_error_total = {}
        for disp, d_sens in sens_resumen.items():
            if disp in ruido_resumen_data["std_ruido"] and disp in temp_resumen_abs:
                d_ruido = ruido_resumen_data["std_ruido"][disp]
                d_temp = temp_resumen_abs[disp]

                # 1. Ordenamos la sensibilidad (x creciente obligatorio para np.interp)
                idx_s = np.argsort(d_sens["x"])
                x_sens_ord = np.array(d_sens["x"])[idx_s]
                y_sens_ord = np.array(d_sens["y"])[idx_s]

                # 2. Ordenamos el coeficiente térmico
                idx_t = np.argsort(d_temp["x"])
                x_temp_ord = np.array(d_temp["x"])[idx_t]
                y_temp_ord = np.array(d_temp["y"])[idx_t]

                # 3. Corrientes de evaluación (ordenadas)
                x_corrientes = np.array(d_ruido["x"])
                idx_r = np.argsort(x_corrientes)
                x_corrientes = x_corrientes[idx_r]
                
                # Interpolar sensibilidad
                sens_interp = np.interp(x_corrientes, x_sens_ord, y_sens_ord)

                # Error de Ruido en [cGy]
                std_uA = (np.array(d_ruido["y"])[idx_r] / 1000.0)
                err_ruido_cgy = (std_uA * 100.0) / sens_interp * peso_ruido

                # Error Térmico en [cGy/°C]
                alpha_interp = np.interp(x_corrientes, x_temp_ord, y_temp_ord)
                err_temp_cgy = (alpha_interp * 100.0) / sens_interp * peso_temp

                # Suma en cuadratura [cGy]
                err_total = np.sqrt(err_ruido_cgy**2 + (err_temp_cgy * delta_t)**2)

                datos_error_total[disp] = {
                    "x": x_corrientes,
                    "y": err_total
                }

        if datos_error_total:
            st.latex(r"\text{Error Total [cGy]} = \sqrt{\left(\frac{\sigma_I}{S}\right)^2 + \left(\frac{|\alpha| \cdot \Delta T}{S}\right)^2}")
            graficos.graficar_curvas(
                titulo=f"Error Total Combinado vs Corriente Normalizada (ΔT = {delta_t:.1f} °C)",
                dict_datos=datos_error_total,
                xlabel=r"$\text{Corriente Normalizada }I_{D_{norm}} \text{ [}\mu \text{A]}$",
                ylabel="Error Total Combinado [cGy]",
                modo='markers+lines'
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

        datos_temp = proc_temp.obtener_analisis_temperatura(
            DISPOS, CORRIENTES, TEMPERATURAS
        )

        if "PFGIW1 (Fit)" in datos_temp.get("alpha_vs_i", {}):
            ztc_iw1 = datos_temp["alpha_vs_i"]["PFGIW1 (Fit)"]["ztc"] * 1e-6
            ztc_iw2 = datos_temp["alpha_vs_i"]["PFGIW2 (Fit)"]["ztc"] * 1e-6
            ztc_ip2 = datos_temp["alpha_vs_i"]["PFGIP2 (Fit)"]["ztc"] * 1e-6
            st.text(f"Se estima que las corrientes de ZTC son: PFGIW1->{ztc_iw1*1e6:.2f}µA ; PFGIW2->{ztc_iw2*1e6:.2f}µA ; PFGIP2->{ztc_ip2*1e6:.2f}µA")
            st.text("Para saber si en esa corriente los dispositivos están en saturación, me fijo su tensión de Floating Gate equivalente")
            vg_iw1 = proc_evo.obtener_vg_por_corriente("PFGIW1", ztc_iw1)
            vg_iw2 = proc_evo.obtener_vg_por_corriente("PFGIW2", ztc_iw2)
            vg_ip2 = proc_evo.obtener_vg_por_corriente("PFGIP2", ztc_ip2)
            st.text(f"Las tensiones equivalentes para ZTC son: PFGIW1->{vg_iw1 :.2f}V ; PFGIW2->{vg_iw2 :.2f}V ; PFGIP2->{vg_ip2 :.2f}V")
            st.text(f"Se estiman los Vt: PFGIW1->{datos_iv_ref['PFGIW1']['vt'] :.2f} ; (PFGIW2, PFGIP2)->{datos_iv_ref['PFGIW2']['vt'] :.2f}")
            st.text(f"Entonces para el PFGIW1: {vg_iw1:.2f}V < {datos_iv_ref["PFGIW1"]["vt"] :.2f} y -4.5V < {vg_iw1 - datos_iv_ref["PFGIW1"]["vt"] :.2f}")
            st.text(f"Para el PFGIW2: {vg_iw2:.2f}V < {datos_iv_ref['PFGIW2']['vt'] :.2f} y -4.5V < {vg_iw2 - datos_iv_ref['PFGIW2']['vt'] :.2f}")
            st.text(f"Para el PFGIP2: {vg_ip2:.2f}V < {datos_iv_ref['PFGIW2']['vt'] :.2f} y -4.5V < {vg_ip2 - datos_iv_ref['PFGIW2']['vt'] :.2f}")
