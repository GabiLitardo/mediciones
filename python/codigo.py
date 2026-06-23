from pathlib import Path
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

directorio_base = Path(".")
# Buscamos y guardamos la lista de rutas en 'lista_de_rutas'
lista_de_rutas = directorio_base.glob(
    "**/MOSISV72M_DIE4_PFGIW1_VG=0_postrad*_M1_2.ri"
)

super_arreglo = []

# Recorremos la lista de rutas explícitamente
for ruta_archivo in lista_de_rutas:
    datos = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
    super_arreglo.append(datos)

st.write(f"¡Hecho! Se cargaron {len(super_arreglo)} mediciones.")
st.write(f"{super_arreglo.size}")

(V, I) = super_arreglo[0]

fig = plt.figure()
plt.plot(V, 1e6 * I, color="red")

plt.xlabel("V [V]")
plt.ylabel(r"I [$\mu$A]")
st.pyplot(fig)
