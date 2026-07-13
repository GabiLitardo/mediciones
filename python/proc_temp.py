import numpy as np
import re
import os
import glob
from lector_archivos import matchear_archivos

def obtener_datos_corriente_vs_temp(lista_dispositivos, corrientes_nominales, ruta_base="."):
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            patron = os.path.join(ruta_base, f"*_UTN_DIE4_{disp}_{corr}uA_*_M1.csv")
            archivos_encontrados = glob.glob(patron)
            
            temps_aux = []
            corrientes_aux = []
            
            for ruta_completa in archivos_encontrados:
                nombre_archivo = os.path.basename(ruta_completa)
                match = re.search(f"_UTN_DIE4_{disp}_{corr}uA_(-?\d+)_M1\.csv", nombre_archivo)
                if match:
                    temp_valor = float(match.group(1))
                    datos = matchear_archivos(nombre_archivo)[0]
                    
                    v_drain = datos[:, 0]
                    i_drain = datos[:, 1]
                    
                    idx_vd = np.argmin(np.abs(v_drain - (-5.0)))
                    i_en_v5 = np.abs(i_drain[idx_vd]) * 1e6
                    
                    temps_aux.append(temp_valor)
                    corrientes_aux.append(i_en_v5)
            
            if temps_aux:
                indices_orden = np.argsort(temps_aux)
                resultado[disp][corr] = {
                    "x": np.array(temps_aux)[indices_orden],
                    "y": np.array(corrientes_aux)[indices_orden]
                }
    return resultado
