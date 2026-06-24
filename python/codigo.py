# codigo.py
import streamlit as st
# Importamos las funciones de graficado desde nuestro archivo graficos.py
from graficos import graficar_dispositivos, graficar_sensibilidad_fg, graficar_sensibilidad_fg_absoluta

st.title("Resumen mediciones Chaves-Litardo")

# =====================================================================
# CONFIGURACIÓN DE CHECKBOXES EN LA BARRA LATERAL (O EN EL CUERPO)
# =====================================================================
mostrar_evolucion = st.checkbox("1. Análisis temporal", value=True)
mostrar_sensibilidad = st.checkbox("2. Análisis de Sensibilidad a radiación", value=False)
mostrar_ruido = st.checkbox("3. Análisis de Ruido", value=False)

# =====================================================================
# SECCIÓN 1: EVOLUCIÓN TEMPORAL
# =====================================================================
if mostrar_evolucion:
    st.markdown("---")
    st.header("Evolución Temporal")
    
    graficar_dispositivos(
        titulo="Evolución Floating Gates Tanda 1 (I @ V = -4.5 V)",
        ylabel=r"$I_D$ [$\mu$A]",
        lista_dispositivos=["PFGIW1", "PFGIW2", "PFGIW3"],
        tipo_tanda="FG_tanda1"
    )

    graficar_dispositivos(
        titulo="Evolución Floating Gates Tanda 2 (I @ V = -4.5 V)",
        ylabel=r"$I_D$ [$\mu$A]",
        lista_dispositivos=["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"],
        tipo_tanda="FG_tanda2"
    )

    graficar_dispositivos(
        titulo="Evolución FOXFETs (Tensión interpolada @ I = 10 uA)",
        ylabel="Tensión [V]",
        lista_dispositivos=["FFC1", "FFC2", "FFC3", "FFL", "FFS"],
        tipo_tanda="FOXFET"
    )

# =====================================================================
# SECCIÓN 2: SENSIBILIDAD
# =====================================================================
if mostrar_sensibilidad:
    st.markdown("---")
    st.header("Análisis de Sensibilidad")
    
    st.subheader("Normalizada")
    graficar_sensibilidad_fg(
        titulo="Sensibilidad FG Tanda 1 (Tasa vs $I_D$ Promedio Normalizado)",
        lista_dispositivos=["PFGIW1", "PFGIW2", "PFGIW3"],
        tipo_tanda="FG_tanda1"
    )
    graficar_sensibilidad_fg(
        titulo="Sensibilidad FG Tanda 2 (Tasa vs $I_D$ Promedio Normalizado)",
        lista_dispositivos=["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"],
        tipo_tanda="FG_tanda2"
    )
    
    st.subheader("Sin normalizar")
    graficar_sensibilidad_fg_absoluta(
        titulo="Sensibilidad Absoluta FG Tanda 1 (Tasa Absoluta vs $I_D$ Promedio Absoluto)",
        lista_dispositivos=["PFGIW1", "PFGIW2", "PFGIW3"],
        tipo_tanda="FG_tanda1"
    )
    graficar_sensibilidad_fg_absoluta(
        titulo="Sensibilidad Absoluta FG Tanda 2 (Tasa Absoluta vs $I_D$ Promedio Absoluto)",
        lista_dispositivos=["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"],
        tipo_tanda="FG_tanda2"
    )

# =====================================================================
# SECCIÓN 3: RUIDO (PENDIENTE)
# =====================================================================
if mostrar_ruido:
    st.markdown("---")
    st.header("Análisis de Ruido")
    st.info("pendiente")
