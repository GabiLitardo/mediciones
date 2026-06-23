from pathlib import Path
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

def matchear_archivos (nombre_archivo_generico):
    directorio_base = Path(".")
    # Buscamos y guardamos la lista de rutas en 'lista_de_rutas'
    lista_de_rutas = directorio_base.glob(
        "**/"+nombre_archivo_generico
    )
    mediciones = []
    for ruta_archivo in lista_de_rutas:
        medicion = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
        mediciones.append(medicion)
    return mediciones


mediciones = matchear_archivos("MOSISV72M_DIE4_PFGIW1_VG=0_postrad*_M1_2.ri")
st.write(f"¡Hecho! Se cargaron {len(mediciones)} mediciones.")

medicion = mediciones[0]
V = medicion[:, 0]
I = medicion[:, 1]

fig = plt.figure()
plt.plot(V, 1e6 * I, color="red")

plt.xlabel("V [V]")
plt.ylabel(r"I [$\mu$A]")
st.pyplot(fig)
