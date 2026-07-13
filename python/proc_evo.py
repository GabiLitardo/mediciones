# proc_evo.py
import numpy as np
from pathlib import Path
from lector_archivos import matchear_archivos

def calcular_tiempo_acumulado(nro, tipo_tanda):
    """Calcula el tiempo acumulado según el historial de intervalos de irradiación."""
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
        else:
            if i <= 9: t += 10
            elif i <= 21: t += 15
            elif i <= 24: t += 20
            elif i <= 27: t += 25
            elif i <= 29: t += 30
            elif i <= 30: t += 35
            else: t += 10
    return t

def obtener_vg_por_corriente(dispositivo, corriente_buscada):
    """Obtiene la tensión de Floating Gate equivalente a partir de las curvas de transferencia de los dispositivos estándar"""
    if dispositivo in ["PFGIW2", "PFGIP2"]:
        nombre_archivo = "MOSISV72M_DIE4_PMOS_STD1_IV_VD=-4.5V_M1.ri"
    elif dispositivo == "PFGIW1":
        nombre_archivo = "MOSISV72M_DIE4_PMOS_STD2_IV_VD=-4.5V_M1.ri"
    else:
        raise ValueError("Dispositivo no válido. Elegir entre PFGIW1, PFGIW2 o PFGIP2.")
    raiz = Path(__file__).resolve().parent.parent
    lista_rutas = list(raiz.glob(f"*/{nombre_archivo}"))
    if not lista_rutas:
        raise FileNotFoundError(f"No se encontró el archivo {nombre_archivo} en mediciones.")
    
    ruta_archivo = lista_rutas[0]
    datos = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
    tensiones_g = datos[:, 0]
    corrientes_d = np.abs(datos[:, 1])

    indices_ordenados = np.argsort(corrientes_d)
    return np.interp(corriente_buscada, corrientes_d[indices_ordenados], tensiones_g[indices_ordenados])

def obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda):
    """Barre los archivos del postrad0 al postrad100 y extrae los arrays de tiempos y valores (Corriente o Tensión)."""
    resultado = {}
    for disp in lista_dispositivos:
        tiempos, valores = [], []
        for nro in range(0, 100):
            if tipo_tanda == "FG_tanda1":
                sufijo = ".ri"; prefijo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_"
            elif tipo_tanda == "FG_tanda2":
                sufijo = "_2.ri"; prefijo = f"MOSISV72M_DIE4_{disp}_VG=0_postrad{nro}_"
            elif tipo_tanda == "FOXFET":
                sufijo = ".ri"; prefijo = f"MOSISV72M_DIE4_{disp}_IV_VD=5V_postrad{nro}_"
                
            archivo_encontrado = None    
            for m_ver in ["M2", "M1"]:#le doy prioridad a la última medición (M2 por sobre M1)
                nombre_buscar = f"{prefijo}{m_ver}{sufijo}"
                datos = matchear_archivos(nombre_buscar)
                if datos:
                    archivo_encontrado = datos[0]
                    break
            
            if archivo_encontrado is not None:
                t = calcular_tiempo_acumulado(nro, tipo_tanda)
                tensiones = archivo_encontrado[:, 0]
                corrientes = archivo_encontrado[:, 1]
                
                if tipo_tanda == "FOXFET":

                    corrientes_abs = np.abs(corrientes)

                    indices_orden = np.argsort(corrientes_abs)

                    v_interp = np.interp(1e-5, corrientes_abs[indices_orden], tensiones[indices_orden])

                    valores.append(v_interp)

                    tiempos.append(t)
                else:
                    idx = np.where(np.round(tensiones, 1) == -4.5)[0]
                    if len(idx) > 0:
                        valores.append(np.abs(corrientes[idx[0]] * 1e6))
                        tiempos.append(t)
                        
        if tiempos:
            indices = np.argsort(tiempos)
            resultado[disp] = {
                "tiempos": np.array(tiempos)[indices],
                "valores": np.array(valores)[indices]
            }
        if disp == "FFC1":
            print("A")
    return resultado

def obtener_datos_evolucion_vg(lista_dispositivos, tipo_tanda):
    """Genera la evolución temporal mapeada a la tensión equivalente V_FG."""
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda)
    resultado = {}
    for disp, datos in datos_crudos.items():
        tiempos_vg, tensiones_vg = [], []
        for t, corriente_ua in zip(datos["tiempos"], datos["valores"]):
            try:
                vg_val = obtener_vg_por_corriente(disp, corriente_ua * 1e-6)
                tensiones_vg.append(vg_val)
                tiempos_vg.append(t)
            except:
                continue
        if tiempos_vg:
            resultado[disp] = {"tiempos": np.array(tiempos_vg), "valores": np.array(tensiones_vg)}
    return resultado
