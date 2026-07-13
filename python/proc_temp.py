import numpy as np
from lector_archivos import matchear_archivos

def obtener_datos_I_vs_T(lista_dispositivos, corrientes_nominales, lista_temperaturas):
    resultado = {}
    
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            temps_aux = []
            corrientes_aux = []
            
            for temp in lista_temperaturas:
                archivo_encontrado = None
                
                # Buscamos sistemáticamente priorizando la versión de medición más alta
                for m_ver in ["M10", "M9", "M8", "M7", "M6", "M5", "M4", "M3", "M2", "M1"]:
                    nombre_buscar = f"*_UTN_DIE4_{disp}_{corr}uA_{temp}_{m_ver}.csv"
                    lista_datos = matchear_archivos(nombre_buscar, tipo_medicion="temperatura")
                    
                    if lista_datos:
                        archivo_encontrado = lista_datos[0]
                        break
                
                if archivo_encontrado is not None:
                    # Al usar tipo_medicion="temperatura", la columna 0 es vd (3) y la columna 1 es id (4)
                    v_drain = archivo_encontrado[:, 0]
                    i_drain = archivo_encontrado[:, 1]
                    
                    # Buscamos el índice más cercano a VD = -5.0V
                    idx_vd = np.argmin(np.abs(v_drain - (-5.0)))
                    
                    # Guardamos el valor absoluto en uA (multiplicamos por 1e6 ya que viene en Amperes nativos)
                    i_en_v5 = np.abs(i_drain[idx_vd]) * 1e6
                    
                    temps_aux.append(float(temp))
                    corrientes_aux.append(i_en_v5)
            
            if temps_aux:
                # Nos aseguramos de que queden ordenados de menor a mayor temperatura
                indices_orden = np.argsort(temps_aux)
                resultado[disp][corr] = {
                    "x": np.array(temps_aux)[indices_orden],
                    "y": np.array(corrientes_aux)[indices_orden]
                }
                
    return resultado
