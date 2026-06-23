from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# =====================================================================
# 1. UNICA FUNCIÓN OBLIGATORIA (PARA CARGAR LOS ARCHIVOS)
# =====================================================================
def matchear_archivos(nombre_archivo_generico):
    directorio_base = Path(".")
    lista_de_rutas = directorio_base.glob("**/" + nombre_archivo_generico)
    mediciones = []
    for ruta_archivo in lista_de_rutas:
        medicion = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
        mediciones.append(medicion)
    return mediciones

# =====================================================================
# 2. FUNCIÓN DE PROCESAMIENTO Y GRAFICADO (TODO EN UNO)
# =====================================================================
def graficar_dispositivos(titulo, ylabel, lista_dispositivos, tipo_tanda):
    fig, ax = plt.subplots(figsize=(10, 5))
    hay_datos = False    
    
    # Diccionario con los factores de normalización específicos para cada FG
    factores_normalizacion = {
        "PFGIW1": 4.0,
        "PFGIW2": 1.0,
        "PFGIW3": 56.0,
        "PFGIP2": 1.0
    }
    
    for disp in lista_dispositivos:
        tiempos = []
        valores = []
        
        # Iteramos de forma directa por los números de postrad del ensayo
        for nro in range(0, 100):
            if tipo_tanda == "FG_tanda1":
                sufijo = ".ri"
                prefijo_archivo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_"
            elif tipo_tanda == "FG_tanda2":
                sufijo = "_2.ri"
                prefijo_archivo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_"
            elif tipo_tanda == "FOXFET":
                sufijo = ".ri"
                prefijo_archivo = f"MOSISV72M_DIE4_{disp}_IV_VD=5V_postrad{nro}_"
                
            archivo_encontrado = None    
            
            # Buscamos dándole prioridad a M2 sobre M1
            for m_ver in ["M2", "M1"]:
                nombre_buscar = f"{prefijo_archivo}{m_ver}{sufijo}"
                
                datos = matchear_archivos(nombre_buscar)
                if datos:
                    archivo_encontrado = datos[0]
                    break
            
            if archivo_encontrado is not None:
                # -----------------------------------------------------
                # A) CÁLCULO DE TIEMPO ACUMULADO (LÓGICA ESCALONADA)
                # -----------------------------------------------------
                t = 0
                for i in range(1, nro + 1):
                    if tipo_tanda == "FOXFET":
                        if i <= 32: t += 10
                        elif i <= 44: t += 15
                        elif i <= 47: t += 20
                        elif i <= 50: t += 25
                        elif i <= 52: t += 30
                        elif i <= 53: t += 35
                        else: t += 10
                    else: # Floating Gates
                        if i <= 9: t += 10
                        elif i <= 21: t += 15
                        elif i <= 24: t += 20
                        elif i <= 27: t += 25
                        elif i <= 29: t += 30
                        elif i <= 30: t += 35
                        else: t += 10
                
                # -----------------------------------------------------
                # B) EXTRACCIÓN DEL PUNTO OPERATIVO
                # -----------------------------------------------------
                voltajes = archivo_encontrado[:, 0]
                corrientes = archivo_encontrado[:, 1]
                
                if tipo_tanda == "FOXFET":
                    corrientes_abs = np.abs(corrientes)
                    indices_orden = np.argsort(corrientes_abs)
                    v_interp = np.interp(1e-5, corrientes_abs[indices_orden], voltajes[indices_orden])
                    valores.append(v_interp)
                    tiempos.append(t)
                else:
                    idx = np.where(np.round(voltajes, 1) == -4.5)[0]
                    if len(idx) > 0:
                        corriente_ua = np.abs(corrientes[idx[0]] * 1e6)
                        valores.append(corriente_ua)
                        tiempos.append(t)
                        
        # Si se recolectaron datos para este dispositivo, los ordenamos cronológicamente
        if tiempos:
            indices_finales = np.argsort(tiempos)
            tiempos_ordenados = np.array(tiempos)[indices_finales]
            valores_ordenados = np.array(valores)[indices_finales]
            
            # -----------------------------------------------------
            # C) CÁLCULO DE SENSIBILIDAD REAL PARA FLOATING GATES
            # -----------------------------------------------------
            if tipo_tanda.startswith("FG"):
                # 1. Normalizar la corriente por el factor asignado a este dispositivo
                factor = factores_normalizacion.get(disp, 1.0)
                corrientes_norm = valores_ordenados / factor
                
                eje_x_promedios = []
                eje_y_tasas = []
                
                # 2. Iterar punto a punto calculando las tasas entre irradiaciones sucesivas
                for k in range(len(corrientes_norm) - 1):
                    dt = tiempos_ordenados[k+1] - tiempos_ordenados[k]
                    
                    if dt > 0:  # Evitamos división por cero si hubiera tiempos duplicados
                        # Diferencia de corriente normalizada en módulo dividido tiempo de exposición
                        tasa = np.abs(corrientes_norm[k+1] - corrientes_norm[k]) / dt
                        # Promedio de las dos corrientes originales (sin normalizar)
                        promedio_i = (valores_ordenados[k+1] + valores_ordenados[k]) / 2.0
                        
                        eje_y_tasas.append(tasa)
                        eje_x_promedios.append(promedio_i)
                
                # Reemplazamos los arreglos para graficar Tasa vs Corriente Promedio
                x_graficar = eje_x_promedios
                y_graficar = eje_y_tasas
            else:
                # Si es FOXFET, el gráfico sigue siendo tradicional: Tiempo (X) vs Tensión (Y)
                x_graficar = tiempos_ordenados
                y_graficar = valores_ordenados
            
            if len(x_graficar) > 0:
                ax.plot(x_graficar, y_graficar, "o--", label=disp)
                hay_datos = True
            
    if hay_datos:
        ax.set_title(titulo)
        # Cambiamos las etiquetas dinámicamente según el tipo de gráfico generado
        if tipo_tanda.startswith("FG"):
            ax.set_xlabel("Corriente Promedio $I_D$ [$\mu$A]")
        else:
            ax.set_xlabel("Tiempo Acumulado [min]")
            
        ax.set_ylabel(ylabel)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig)
    plt.close(fig)

# =====================================================================
# 3. EJECUCIÓN SECUENCIAL DIRECTA (SIN NINGUN MAIN)
# =====================================================================
st.title("Panel Simplificado de Ensayos de Radiación")
st.write("Generando gráficos secuenciales de forma directa...")

# 1. Gráfico Sensibilidad Floating Gates Tanda 1
graficar_dispositivos(
    titulo="Sensibilidad Floating Gates Tanda 1 (Tasa de Cambio vs $I_D$ Promedio)",
    ylabel="Tasa de Cambio [$\mu$A/min]",
    lista_dispositivos=["PFGIW1", "PFGIW2", "PFGIW3"],
    tipo_tanda="FG_tanda1"
)

# 2. Gráfico Sensibilidad Floating Gates Tanda 2
graficar_dispositivos(
    titulo="Sensibilidad Floating Gates Tanda 2 (Tasa de Cambio vs $I_D$ Promedio)",
    ylabel="Tasa de Cambio [$\mu$A/min]",
    lista_dispositivos=["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"],
    tipo_tanda="FG_tanda2"
)

# 3. Gráfico FOXFETs (Valores absolutos tradicionales)
graficar_dispositivos(
    titulo="Evolución FOXFETs (Tensión interpolada @ I = 10 uA)",
    ylabel="Tensión [V]",
    lista_dispositivos=["FFC1", "FFC2", "FFC3", "FFL", "FFS"],
    tipo_tanda="FOXFET"
)
