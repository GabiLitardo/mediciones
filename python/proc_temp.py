import numpy as np
from lector_archivos import matchear_archivos

def obtener_datos_I_vs_T(lista_dispositivos, corrientes_nominales, lista_temperaturas):
    """
    Busca archivos de medición de temperatura, extrae la corriente de drenaje 
    a VD = -5V y calcula el coeficiente térmico absoluto (alpha) en uA/°C.
    """
    resultado = {}

    for disp in lista_dispositivos:
        resultado[disp] = {}
        
        for corr in corrientes_nominales:
            temps_aux = []
            corrientes_aux = []
            
            for temp in lista_temperaturas:
                archivo_encontrado = None
                
                # Búsqueda sistemática priorizando la versión de medición más alta (M10 a M1)
                for m_ver in ["M10", "M9", "M8", "M7", "M6", "M5", "M4", "M3", "M2", "M1"]:
                    nombre_buscar = f"*UTN_DIE4{disp}{corr}uA{temp}_{m_ver}.csv"
                    archivos_encontrados = matchear_archivos(nombre_buscar, tipo_medicion="temperatura")
                    
                    if not archivos_encontrados:
                        nombre_buscar = f"*UTN_DIE4{disp}{corr}u{temp}_{m_ver}.csv"
                        archivos_encontrados = matchear_archivos(nombre_buscar, tipo_medicion="temperatura")
                        
                    if archivos_encontrados:
                        archivo_encontrado = archivos_encontrados[0]
                        break
                        
                if archivo_encontrado is not None:
                    v_drain = archivo_encontrado[:, 0]
                    i_drain = archivo_encontrado[:, 1]
                    
                    # Identificar el índice de tensión más cercano a VD = -5.0V
                    idx_vd = np.argmin(np.abs(v_drain - (-5.0)))
                    
                    # Convertir la corriente a valor absoluto en uA
                    i_en_v5 = np.abs(i_drain[idx_vd]) * 1e6
                    
                    temps_aux.append(float(temp))
                    corrientes_aux.append(i_en_v5)
            
            if temps_aux:
                # Asegurar el ordenamiento de menor a mayor temperatura
                indices_orden = np.argsort(temps_aux)
                x_ordenado = np.array(temps_aux)[indices_orden]
                y_ordenado = np.array(corrientes_aux)[indices_orden]
                
                # Cálculo de la pendiente (coeficiente térmico alpha) mediante ajuste lineal
                coefs = np.polyfit(x_ordenado, y_ordenado, deg=1)
                
                resultado[disp][corr] = {
                    "x": x_ordenado,
                    "y": y_ordenado,
                    "alpha": coefs[0]  # Coeficiente térmico absoluto (uA/°C)
                }
                
    return resultado
