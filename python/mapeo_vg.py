from pathlib import Path
import numpy as np

def obtener_vg_por_corriente(dispositivo, corriente_buscada):
    # Selección de archivo según la geometría W/L declarada para cada referencia
    if dispositivo in ["PFGIW1", "PFGIP2"]:
        nombre_archivo = "MOSISV72M_DIE4_PMOS_STD1_IV_VD=-4.5V_M1.ri"
    elif dispositivo == "PFGIW2":
        nombre_archivo = "MOSISV72M_DIE4_PMOS_STD2_IV_VD=-4.5V_M1.ri"
    else:
        raise ValueError("Dispositivo no válido. Elegir entre PFGIW1, PFGIW2 o PFGIP2.")

    # Búsqueda del archivo subiendo un nivel desde raíz/python y barriendo carpetas por fecha
    raiz = Path(__file__).resolve().parent.parent
    lista_rutas = list(raiz.glob(f"*/{nombre_archivo}"))
    
    if not lista_rutas:
        raise FileNotFoundError(f"No se encontró el archivo {nombre_archivo} en ninguna carpeta de mediciones.")
    
    ruta_archivo = lista_rutas[0]
    
    # Carga y procesamiento de datos numéricos
    datos = np.genfromtxt(ruta_archivo, skip_header=2, usecols=(0, 1), encoding="cp1252")
    voltajes_g = datos[:, 0]
    corrientes_d = np.abs(datos[:, 1])  # Trabajamos con valores absolutos para evitar problemas de signo

    # Para np.interp el eje X de interpolación (corrientes) debe estar estrictamente creciente
    indices_ordenados = np.argsort(corrientes_d)
    corrientes_ord = corrientes_d[indices_ordenados]
    voltajes_ord = voltajes_g[indices_ordenados]

    # Interpolación unidimensional
    vg_interpolado = np.interp(corriente_buscada, corrientes_ord, voltajes_ord)
    return vg_interpolado

# --- Ejemplo de uso interno para testeo ---
if __name__ == "__main__":
    try:
        # Ejemplo buscando la tensión para una corriente de 10 uA (1e-5 A) en el PFGIW1
        corriente_test = 1e-5
        vg_resultado = obtener_vg_por_corriente("PFGIW1", corriente_test)
        print(f"Para una corriente de {corriente_test} A, el Vg asociado es: {vg_resultado:.4f} V")
    except Exception as e:
        print(f"Error: {e}")
