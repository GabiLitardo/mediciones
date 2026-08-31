# FOXFET.py
import numpy as np
import streamlit as st
import graficos
import proc_evo
import proc_sens
import proc_ruido
import proc_temp

def render_FOXFET ():
    st.title("Resumen mediciones Chaves-Litardo")

    opcion = st.sidebar.radio(
        "Seleccionar Análisis",
        ["Evolución temporal", "Sensibilidad", "Ruido", "Temperatura", "Resumen"]
    )
    DISPOS = ["FFC1", "FFC2", "FFC3", "FFL", "FFS"]
    CORRIENTES = [0.1, 1, 10, 100]
    #temperaturas = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]

    # =====================================================================
    # SECCIÓN 1: EVOLUCIÓN TEMPORAL
    # =====================================================================
    if opcion == "Evolución temporal":
        st.markdown("---")
        st.header("Evolución Temporal")
        en_dosis = st.checkbox("Graficar en función de dosis acumulada?", value=False)

        I_interps = st.multiselect(
            "Corrientes de interpolación:",
            options=CORRIENTES,
            default=[10]
        )

        datos_totales = {}
        for I_interp in I_interps:
            datos_foxfet = proc_evo.obtener_datos_crudos_tanda(
                lista_dispositivos=DISPOS,
                tipo_tanda="FOXFET",
                I_interp=I_interp * 1e-6,
                en_dosis=en_dosis
            )
            # Prefijar la clave para distinguir dispositivo y corriente en el mismo grafico
            for key, val in datos_foxfet.items():
                datos_totales[f"{key} @ {I_interp :.1f} uA"] = val

        graficos.graficar_curvas(
            titulo="Evolución FOXFETs Tanda 1",
            dict_datos=datos_totales,
            xlabel="Dosis Acumulada [Gy]" if en_dosis else "Tiempo de irradiación [min]",
            ylabel="Tensión [V]",
            modo='markers'
        )

    # =====================================================================
    # SECCIÓN 2: SENSIBILIDAD
    # =====================================================================
    elif opcion == "Sensibilidad":
        st.markdown("---")
        st.header("Análisis de sensibilidad")

        I_interps = st.multiselect(
            "Corrientes de interpolación:",
            options=CORRIENTES,
            default=[10]
        )

        sens_totales = {}
        for I_interp in I_interps:
            sens = proc_sens.procesar_sensibilidad(DISPOS, "FOXFET", normalizado=False, I_interp=I_interp * 1e-6, n_ventana=20)
            # Prefijar la clave para distinguir dispositivo y corriente en el mismo grafico
            for key, val in sens.items():
                sens_totales[f"{key} @ {I_interp :.1f} uA"] = val

        
        graficos.graficar_curvas(
            titulo=r"$\text{Sensibilidad FOXFET tanda 1}$",
            dict_datos=sens_totales,
            xlabel=r"$\text{Tensión }V_{GS}\text{ [V]}$",
            ylabel=r"$\text{Sensibilidad [V/Gy]}$",
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
        die = st.selectbox("Seleccionar DIE", options=["DIE4", "DIE19"])

        ruido_corto = proc_ruido.obtener_analisis_ruido_completo(
            DISPOS, CORRIENTES, es_larga=False, restar_deriva=restar_deriva, es_fox=True, die=die
        )

        graficos.graficar_curvas(
            "Desvío estándar del ruido neto vs Corrientes Normalizadas",
            dict_datos=ruido_corto["std_ruido"],
            xlabel=r"$\text{Corrientes normalizadas }I_D\text{ [}\mu \text{A]}$",
            ylabel="Desvío de Ruido [nA]",
            modo='markers',
            logx=True
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
        st.image("martillo.png", width="stretch")

    # =====================================================================
    # SECCIÓN 5: RESUMEN
    # =====================================================================
    elif opcion == "Resumen":
        st.markdown("---")
        st.image("martillo.png", width="stretch")