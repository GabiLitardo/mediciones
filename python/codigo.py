import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# =====================================================================
# 1. FUNCIÓN SOLICITADA PARA CARGAR MEDICIONES
# =====================================================================
def matchear_archivos(nombre_archivo_generico):
    directorio_base = Path(".")
    # Busca el archivo en cualquier subcarpeta (ej: 2026-05-05/PFGIW1_postrad1_M1.ri)
    lista_de_rutas = directorio_base.glob("**/" + nombre_archivo_generico)
    
    mediciones = []
    for ruta_archivo in lista_de_rutas:
        # Cargamos solo Voltaje (Col 0) y Corriente (Col 1)
        medicion = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
        mediciones.append(medicion)
    return mediciones

# =====================================================================
# 2. CÁLCULO DE TIEMPOS ACUMULADOS (LÓGICA ESCALONADA)
# =====================================================================
def calcular_tiempo_foxfet(nro_postrad):
    tiempo = 0
    for i in range(1, nro_postrad + 1):
        if i <= 32: tiempo += 10
        elif i <= 44: tiempo += 15
        elif i <= 47: tiempo += 20
        elif i <= 50: tiempo += 25
        elif i <= 52: tiempo += 30
        elif i <= 53: tiempo += 35
        else: tiempo += 10
    return tiempo

def calcular_tiempo_fg(nro_postrad):
    tiempo = 0
    for i in range(1, nro_postrad + 1):
        if i <= 9: tiempo += 10
        elif i <= 21: tiempo += 15
        elif i <= 24: tiempo += 20
        elif i <= 27: tiempo += 25
        elif i <= 29: tiempo += 30
        elif i <= 30: tiempo += 35
        else: tiempo += 10
    return tiempo

# =====================================================================
# 3. EXTRACCIÓN DE PUNTOS CLAVE e INTERPOLACIÓN
# =====================================================================
def procesar_dispositivo(nombre_base, tipo):
    tiempos = []
    valores = []
    
    # Buscamos un rango amplio de postrads (ej: del 0 al 100) para cubrir el ensayo
    for nro in range(0, 100):
        # Probamos primero si existe la versión de medición M2, si no, buscamos M1
        archivo_encontrado = None
        for m_ver in ["M2", "M1"]:
            sufijo = ".ri" if tipo == "FG_tanda1" else ("_2.ri" if tipo == "FG_tanda2" else ".ri")
            nombre_buscar = f"{nombre_base}_postrad{nro}_{m_ver}{sufijo}"
            
            datos = matchear_archivos(nombre_buscar)
            if datos:  # Si la lista no está vacía, encontramos el archivo
                archivo_encontrado = datos[0] # Tomamos la matriz numérica
                break # Cortamos el búscador de M1/M2 si ya hallamos uno
        
        if archivo_encontrado is not None:
            # Calculamos el tiempo real de este paso
            t = calcular_tiempo_foxfet(nro) if tipo == "FOXFET" else calcular_tiempo_fg(nro)
            
            voltajes = archivo_encontrado[:, 0]
            corrientes = archivo_encontrado[:, 1]
            
            if tipo == "FOXFET":
                # Buscamos tensión interpolada a corriente constante de 10 uA (1e-5 A)
                corrientes_abs = np.abs(corrientes)
                # np.interp requiere que el eje X (corrientes) esté ordenado de menor a mayor
                indices_orden = np.argsort(corrientes_abs)
                v_interp = np.interp(1e-5, corrientes_abs[indices_orden], voltajes[indices_orden])
                valores.append(v_interp)
                tiempos.append(t)
            else:
                # Buscamos corriente de drenaje a voltaje constante de -4.5 V
                # Redondeamos a 1 decimal para evitar problemas de precisión flotante
                idx = np.where(np.round(voltajes, 1) == -4.5)[0]
                if len(idx) > 0:
                    corriente_ua = np.abs(corrientes[idx[0]] * 1e6)
                    valores.append(corriente_ua)
                    tiempos.append(t)
                    
    # Sincronización final: ordenamos por tiempo por si las carpetas se leyeron desordenadas
    if tiempos:
        indices_finales = np.argsort(tiempos)
        tiempos = np.array(tiempos)[indices_finales].tolist()
        valores = np.array(valores)[indices_finales].tolist()
        
    return tiempos, valores

# =====================================================================
# 4. FUNCIÓN SIMPLE DE GRAFICADO
# =====================================================================
def graficar_grupo(titulo, ylabel, lista_dispositivos, tipo_tanda):
    fig, ax = plt.subplots(figsize=(10, 5))
    hay_datos = False
    
    for disp in lista_dispositivos:
        tiempos, valores = procesar_dispositivo(disp, tipo_tanda)
        if tiempos:
            ax.plot(tiempos, valores, "o--", label=disp)
            hay_datos = True
            
    if hay_datos:
        ax.set_title(titulo)
        ax.set_xlabel("Tiempo Acumulado [min]")
        ax.set_ylabel(ylabel)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig)
    plt.close(fig)

# =====================================================================
# 5. FLUJO PRINCIPAL DE STREAMLIT
# =====================================================================
if __name__ == "__main__":
    st.title("Panel Simplificado de Ensayos de Radiación")
    st.write("Procesando archivos en tiempo real usando búsqueda iterativa...")

    # 1. Graficar Floating Gates - Tanda 1
    graficar_grupo(
        titulo="Evolución Floating Gates Tanda 1 (I @ V = -4.5 V)",
        ylabel=r"$I_D$ [$\mu$A]",
        lista_dispositivos=["PFGIW1", "PFGIW2", "PFGIW3"],
        tipo_tanda="FG_tanda1"
    )

    # 2. Graficar Floating Gates - Tanda 2
    graficar_grupo(
        titulo="Evolución Floating Gates Tanda 2 (I @ V = -4.5 V)",
        ylabel=r"$I_D$ [$\mu$A]",
        lista_dispositivos=["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"],
        tipo_tanda="FG_tanda2"
    )

    # 3. Graficar FOXFETs
    graficar_grupo(
        titulo="Evolución FOXFETs (Tensión interpolada @ I = 10 uA)",
        ylabel="Tensión [V]",
        lista_dispositivos=["FFC1", "FFC2", "FFC3", "FFL", "FFS"],
        tipo_tanda="FOXFET"
    )
