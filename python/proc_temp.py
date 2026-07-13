import numpy as np
import re
from pathlib import Path
from lector_archivos import matchear_archivos

def obtener_datos_corriente_vs_temp(lista_dispositivos, corrientes_nominales):
    resultado = {}
    for disp in lista_dispositivos:
        resultado[disp] = {}
        for corr in corrientes_nominales:
            nombre_generico = f"*_UTN_DIE4_{disp}_{corr}uA_*_M1.csv"
            
            directorio_base = Path(".")
            lista_de_rutas = directorio_base.glob("**/" + nombre_generico)
            
            temps_aux = []
            corrientes_aux = []
            
            for ruta in lista_de_rutas:
                nombre_archivo = ruta.name
                match = re.search(f"_UTN_DIE4_{disp}_{corr}uA_(-?\d+)_M1\.csv", nombre_archivo)
                if match:
                    temp_valor = float(match.group(1))
                    
                    lista_datos = matchear_archivos(nombre_archivo, tipo_medicion="temperatura")
                    
                    if lista_datos:
                        datos = lista_datos[0]
                        v_drain = datos[:, 0]
                        i_drain = datos[:, 1]
                        
                        # Buscamos 5.0V positivo ya que el SMU barrió de 0 a 6V
                        idx_vd = np.argmin(np.abs(v_drain - 5.0))
                        
                        # Guardamos la corriente directamente (ya viene en uA)
                        i_en_v5 = np.abs(i_drain[idx_vd])
                        
                        temps_aux.append(temp_valor)
                        corrientes_aux.append(i_en_v5)
            
            if temps_aux:
                indices_orden = np.argsort(temps_aux)
                resultado[disp][corr] = {
                    "x": np.array(temps_aux)[indices_orden],
                    "y": np.array(corrientes_aux)[indices_orden]
                }
    return resultado
