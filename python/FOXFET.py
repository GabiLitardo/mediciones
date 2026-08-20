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
    dispos = ["FFC1", "FFC2", "FFC3", "FFL", "FFS"]
    #temperaturas = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]

    # =====================================================================
    # SECCIÓN 1: EVOLUCIÓN TEMPORAL
    # =====================================================================
    if opcion == "Evolución temporal":
        st.markdown("---")
        st.header("Evolución Temporal")

        I_interps = st.multiselect(
            "Corrientes de interpolación:",
            options=[0.1e-6, 1e-6, 10e-6, 100e-6],
            default=[10e-6]
        )

        datos_totales = {}
        for I_interp in I_interps:
            datos_foxfet = proc_evo.obtener_datos_crudos_tanda(
                lista_dispositivos=dispos,
                tipo_tanda="FOXFET",
                I_interp=I_interp
            )
            # Prefijar la clave para distinguir dispositivo y corriente en el mismo grafico
            for key, val in datos_foxfet.items():
                datos_totales[f"{key} @ {I_interp * 1e6:.1f} uA"] = val

        graficos.graficar_curvas(
            titulo="Evolución FOXFETs Tanda 1",
            dict_datos=datos_totales,
            xlabel="Tiempo de irradiación [min]",
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
            options=[0.1e-6, 1e-6, 10e-6, 100e-6],
            default=[10e-6]
        )

        sens_totales = {}
        for I_interp in I_interps:
            sens = proc_sens.procesar_sensibilidad(dispos, "FOXFET", normalizado=False, I_interp=I_interp, n_ventana=20)
            # Prefijar la clave para distinguir dispositivo y corriente en el mismo grafico
            for key, val in sens.items():
                sens_totales[f"{key} @ {I_interp * 1e6:.1f} uA"] = val

        
        graficos.graficar_curvas(
            titulo=r"$\text{Sensibilidad FOXFET (Sensibilidad vs }V_{GS}\text{)}$",
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
        log = st.checkbox("Graficar Semilog?", value=False)

    # =====================================================================
    # SECCIÓN 4: TEMPERATURA
    # =====================================================================
    elif opcion == "Temperatura":
        st.markdown("---")
        st.header("Análisis de Coeficiente Térmico")

    # =====================================================================
    # SECCIÓN 5: RESUMEN
    # =====================================================================
    elif opcion == "Resumen":
        st.markdown("---")
        st.header("Sensibilidad absoluta, ruido y coef. térmico vs $I_D$ normalizada")