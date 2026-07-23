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
                    if not lista_datos:
                        nombre_buscar = f"*_UTN_DIE4_{disp}_{corr}u_{temp}_{m_ver}.csv"
                        lista_datos = matchear_archivos(nombre_buscar, tipo_medicion="temperatura")
                    
                    if lista_datos:
                        archivo_encontrado = lista_datos[0]
                        break
                
                if archivo_encontrado is not None:
                    v_drain = archivo_encontrado[:, 0]
                    i_drain = archivo_encontrado[:, 1]
                    
                    # Buscamos el índice más cercano a VD = -4.5V
                    idx_vd = np.argmin(np.abs(v_drain - (-4.5)))
                    
                    # Guardamos el valor absoluto en uA
                    i_en_v5 = np.abs(i_drain[idx_vd]) * 1e6
                    
                    temps_aux.append(float(temp))
                    corrientes_aux.append(i_en_v5)
            
            if temps_aux:
                # 1. Nos aseguramos de ordenar los vectores de menor a mayor temperatura
                indices_orden = np.argsort(temps_aux)
                x_ordenado = np.array(temps_aux)[indices_orden]
                y_ordenado = np.array(corrientes_aux)[indices_orden]
                
                # 2. Calculamos el coeficiente térmico (pendiente de la recta) con los datos ordenados
                coefs = np.polyfit(x_ordenado, y_ordenado, deg=1)
                
                resultado[disp][corr] = {
                    "x": x_ordenado,
                    "y": y_ordenado,
                    "alpha": coefs[0]  # Coeficiente térmico absoluto (uA/°C)
                }
                
    return resultado
