# orquestador.py
import streamlit as st
from FG import render_FG
from FOXFET import render_FOXFET

st.set_page_config(page_title="Mediciones Chaves-Litardo", layout="wide")

es_oscuro = st.checkbox("Modo oscuro", value=True)
template = "plotly_dark" if es_oscuro else "plotly_white"

familia = st.sidebar.radio(
    "Familia de Dispositivos",
    ["Floating Gates (FG)", "FOXFETs"]
)
st.sidebar.markdown("---")

if familia == "Floating Gates (FG)":
    render_FG(template)
else:
    render_FOXFET(template)