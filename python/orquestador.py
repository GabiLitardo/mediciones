# orquestador.py
import streamlit as st
from FG import render_FG
from FOXFET import render_FOXFET

st.set_page_config(page_title="Mediciones Chaves-Litardo", layout="wide")

familia = st.sidebar.selectbox(
    "Familia de Dispositivos",
    ["Floating Gates (FG)", "FOXFETs"]
)
st.sidebar.markdown("---")

if familia == "Floating Gates (FG)":
    render_FG()
else:
    render_FOXFET()