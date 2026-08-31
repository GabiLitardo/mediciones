# lector_archivos.py
from pathlib import Path
import numpy as np
import streamlit as st


def matchear_archivos(nombre_archivo_generico, tipo_medicion="iv"):
    directorio_base = Path(".")
    lista_de_rutas = directorio_base.glob("**/" + nombre_archivo_generico)
    mediciones = []
    for ruta_archivo in lista_de_rutas:
        if tipo_medicion == "ruido":
            medicion = np.genfromtxt(ruta_archivo, delimiter='\t', skip_header=5, usecols=(0, 1, 2), encoding="cp1252")
        elif tipo_medicion == "temperatura":
            medicion = np.genfromtxt(ruta_archivo, delimiter=',', skip_header=1, usecols=(3, 4))
        elif tipo_medicion == "temperatura_fox":
                    medicion = np.genfromtxt(ruta_archivo, delimiter=',', skip_header=1, usecols=(2, 4))
        elif tipo_medicion == "iv":
            medicion = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
        mediciones.append(medicion)  
    return mediciones


def cargar_curva_iv_referencia(dispositivo):
    if dispositivo in ["PFGIW2", "PFGIP2", "PFGIW3"]:
        nombre_archivo = "MOSISV72M_DIE4_PMOS_STD1_IV_VD=-4.5V_M1.ri"
    elif dispositivo == "PFGIW1":
        nombre_archivo = "MOSISV72M_DIE4_PMOS_STD2_IV_VD=-4.5V_M1.ri"
    
    datos = matchear_archivos(nombre_archivo, tipo_medicion="iv")
    return datos[0]


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


def cargar_medicion_ruido(disp, corr, es_larga, es_fox=False, die="DIE4"):
    sufijo_larga = "_LARGA" if es_larga else ""
    if es_fox:
        nombre = f"MOSISV72M_{die}_{disp}_VD=-5_RUIDO_Id={corr}u_M1.txt"
    else:
        nombre = f"MOSISV72M_{die}_{disp}_VD=-4.5_RUIDO_{corr}u_M1{sufijo_larga}.txt"
    mediciones = matchear_archivos(nombre, tipo_medicion="ruido")
    if not mediciones:
        print(nombre, flush=True)
    return mediciones[0] if mediciones else None

def _obtener_version_m(path):
    if "_M" in path.stem:
        texto_version = path.stem.rsplit("_M", 1)[1]
        if texto_version.isdigit():
            return int(texto_version)
    return -1


def cargar_medicion_temperatura(disp, corr, temp, es_fox=False, die="DIE4", es_std=False):
    if es_fox:
        tension="-5" if es_std else "5"
        archivos = list(Path(".").glob(f"**/*_UTN_{die}_{disp}_VD={tension}_{temp}_M*.csv"))
        if archivos:
            print(f"Archivo encontrado para {die}, {disp} a {temp}°C", flush=True)
            archivo_reciente = max(archivos, key=_obtener_version_m)
            mediciones = matchear_archivos(archivo_reciente.name, tipo_medicion="temperatura_fox")
            return mediciones[0] if mediciones else None
        print(f"Archivo NO encontrado para {die}, {disp} a {temp}°C", flush=True)
    else:
        # Probamos primero la variante con 'uA' y luego con 'u'
        for variante in [f"{corr}uA", f"{corr}u"]:
            archivos = list(Path(".").glob(f"**/*_UTN_{die}_{disp}_{variante}_{temp}_M*.csv"))
            if archivos:
                archivo_reciente = max(archivos, key=_obtener_version_m)
                mediciones = matchear_archivos(archivo_reciente.name, tipo_medicion="temperatura")
                return mediciones[0] if mediciones else None
                
    return None
