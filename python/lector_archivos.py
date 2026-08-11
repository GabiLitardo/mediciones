# lector_archivos.py
from pathlib import Path
import re
import numpy as np
import streamlit as st

@st.cache_data
def matchear_archivos(nombre_archivo_generico, tipo_medicion="iv"):
    directorio_base = Path(".")
    lista_de_rutas = directorio_base.glob("**/" + nombre_archivo_generico)
    mediciones = []
    for ruta_archivo in lista_de_rutas:
        if tipo_medicion == "ruido":
            medicion = np.genfromtxt(ruta_archivo, delimiter='\t', skip_header=5, usecols=(0, 1, 2), encoding="cp1252")
        elif tipo_medicion == "temperatura":
            medicion = np.genfromtxt(ruta_archivo, delimiter=',', skip_header=1, usecols=(3, 4))
        else:
            medicion = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
        mediciones.append(medicion)  
    return mediciones

@st.cache_data
def cargar_curva_iv_referencia(dispositivo):
    if dispositivo in ["PFGIW2", "PFGIP2", "PFGIW3"]:
        nombre_archivo = "MOSISV72M_DIE4_PMOS_STD1_IV_VD=-4.5V_M1.ri"
    elif dispositivo == "PFGIW1":
        nombre_archivo = "MOSISV72M_DIE4_PMOS_STD2_IV_VD=-4.5V_M1.ri"
    else:
        raise ValueError("Dispositivo no válido.")
    
    datos = matchear_archivos(nombre_archivo, tipo_medicion="iv")
    if not datos:
        raise FileNotFoundError(f"No se encontró {nombre_archivo}")
    return datos[0]

@st.cache_data
def cargar_medicion_tanda(disp, tipo_tanda, nro):
    if tipo_tanda in ["FG_tanda1", "FOXFET"]:
        sufijo = ".ri"; prefijo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_" if tipo_tanda != "FOXFET" else f"MOSISV72M_DIE4_{disp}_IV_VD=5V_postrad{nro}_"
    elif tipo_tanda == "FG_tanda2":
        sufijo = "_2.ri"; prefijo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_"

    for m_ver in ["M2", "M1"]:
        datos = matchear_archivos(f"{prefijo}{m_ver}{sufijo}")
        if datos:
            return datos[0]
    return None

@st.cache_data
def cargar_medicion_ruido(disp, corr, es_larga):
    sufijo_larga = "_LARGA" if es_larga else ""
    nombre = f"MOSISV72M_DIE4_{disp}_VD=-4.5_RUIDO_{corr}u_M1{sufijo_larga}.txt"
    mediciones = matchear_archivos(nombre, tipo_medicion="ruido")
    return mediciones[0] if mediciones else None

@st.cache_data
def cargar_medicion_temperatura(disp, corr, temp):
    directorio_base = Path(".")
    patrones = [f"*_UTN_DIE4_{disp}_{corr}uA_{temp}_M*.csv", f"*_UTN_DIE4_{disp}_{corr}u_{temp}_M*.csv"]
    archivos = []
    for pat in patrones:
        archivos.extend(list(directorio_base.glob(f"**/{pat}")))
    
    if not archivos:
        return None

    def extraer_m(path):
        match = re.search(r"_M(\d+)\.csv$", path.name)
        return int(match.group(1)) if match else -1

    archivo_reciente = max(archivos, key=extraer_m)
    return np.genfromtxt(archivo_reciente, delimiter=',', skip_header=1, usecols=(3, 4))