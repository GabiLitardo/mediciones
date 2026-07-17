import numpy as np
from proc_evo import obtener_datos_crudos_tanda

# Factores fijos de escalado para normalizar las corrientes según el dispositivo
FACTORES_NORM = {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0}

def calcular_fit_polinomico(tiempos_list, corrientes_list):
    """Calcula los coeficientes del polinomio de grado 4."""
    coeficientes = np.polyfit(tiempos_list, corrientes_list, deg=4)
    return coeficientes.tolist()

def procesar_sensibilidad(lista_dispositivos, tipo_tanda, normalizado=True):
    """Calcula la tasa de cambio de corriente (sensibilidad) de forma continua y discreta."""
    datos_crudos = obtener_datos_crudos_tanda(lista_dispositivos, tipo_tanda)
    resultado_fit = {}
    resultado_discreto = {}

    for disp, datos in datos_crudos.items():
        tiempos = datos["tiempos"]
        corrientes = datos["valores"]
        
        factor = FACTORES_NORM.get(disp, 1.0)
        corrientes_norm = corrientes / factor
        corrientes_proc = corrientes_norm if normalizado else corrientes

        # --- Cálculo Ajuste Continuo (Derivada analítica del polinomio g4) ---
        a_y, b_y, c_y, d_y, e_y = calcular_fit_polinomico(tiempos.tolist(), corrientes_proc.tolist())
        a_x, b_x, c_x, d_x, e_x = calcular_fit_polinomico(tiempos.tolist(), corrientes_norm.tolist())
        
        t_cont = np.linspace(tiempos.min(), tiempos.max(), 200)
        
        # Derivada analítica: |4at³ + 3bt² + 2ct + d|
        eje_y_cont = np.abs(4 * a_y * (t_cont ** 3) + 3 * b_y * (t_cont ** 2) + 2 * c_y * t_cont + d_y)
        eje_x_cont = a_x * (t_cont ** 4) + b_x * (t_cont ** 3) + c_x * (t_cont ** 2) + d_x * t_cont + e_x
        
        resultado_fit[disp] = {"x": eje_x_cont, "y": eje_y_cont}

        # --- Cálculo Discreto (Diferencias finitas punto a punto) ---
        eje_x_disc, eje_y_disc = [], []
        for k in range(len(corrientes_proc) - 1):
            dt = tiempos[k+1] - tiempos[k]
            tasa = np.abs(corrientes_proc[k+1] - corrientes_proc[k]) / dt
            promedio = (corrientes_norm[k+1] + corrientes_norm[k]) / 2.0
            
            eje_y_disc.append(tasa)
            eje_x_disc.append(promedio)

        resultado_discreto[disp] = {"x": np.array(eje_x_disc), "y": np.array(eje_y_disc)}

    return [resultado_fit, resultado_discreto]
