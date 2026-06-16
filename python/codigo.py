import os
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.signal import savgol_filter


class AnalizadorRadiacion:
    """Clase para el procesamiento y visualización de datos de irradiación
    en dispositivos Floating Gate (FG) y FOXFET.
    """

    def __init__(self, ruta_base="./", intervalo_minutos=10):
        self.ruta_base = ruta_base
        self.intervalo_minutos = intervalo_minutos
        self.config_dispositivos = {
            "FG_tanda1": {
                "nombres": [["PFGIW1", "PFGIW2", "PFGIW3"]],
                "target_val": -4.5,
                "modo": "corriente",
                "marker": "o",
                "titulo": "Evolución Floating Gates Tanda 1 (I @ V = -4.5 V)",
                "ylabel": r"$I_D$ [$\mu$A]",
                "factores_wl": {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0},
                "sufijo_archivo": ".ri",
            },
            "FG_tanda2": {
                "nombres": [["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"]],
                "target_val": -4.5,
                "modo": "corriente",
                "marker": "v",
                "titulo": "Evolución Floating Gates Tanda 2 (I @ V = -4.5 V)",
                "ylabel": r"$I_D$ [$\mu$A]",
                "factores_wl": {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0},
                "sufijo_archivo": "_2.ri",
            },
            "FOXFET": {
                "nombres": [["FOXFET_W1L1", "FOXFET_W2L1", "FOXFET_W4L1", "FOXFET_W10L1"]],
                "target_val": 1e-5,
                "modo": "tension",
                "marker": "s",
                "titulo": "Evolución FOXFET (V @ I = 10 \muA)",
                "ylabel": "Tensión [V]",
                "sufijo_archivo": ".ri",
            },
        }

    def _calcular_tiempo_acumulado_foxfet(self, nro_paso):
        """Calcula el tiempo acumulado dinámico basado en el paso físico para FOXFET."""
        tiempo = 0
        for i in range(1, nro_paso + 1):
            if i <= 32:
                tiempo += 10
            elif i <= 44:
                tiempo += 15
            elif i <= 47:
                tiempo += 20
            elif i <= 50:
                tiempo += 25
            elif i <= 52:
                tiempo += 30
            elif i == 53:
                tiempo += 35
            else:
                tiempo += 10
        return tiempo

    def _calcular_tiempo_acumulado_fg(self, nro_paso):
        """Calcula el tiempo acumulado dinámico basado en el paso físico para Floating Gates."""
        tiempo = 0
        for i in range(1, nro_paso + 1):
            if i <= 9:
                tiempo += 10
            elif i <= 21:
                tiempo += 15
            elif i <= 24:
                tiempo += 20
            elif i <= 27:
                tiempo += 25
            elif i <= 29:
                tiempo += 30
            elif i <= 30:
                tiempo += 35
            else:
                tiempo += 10
        return tiempo

    def _extraer_punto_operacion(self, ruta_archivo, conf, nro_paso, disp_nombre):
        """Parsea un archivo individual e interactúa/interpola según el modo operativo."""
        try:
            with open(ruta_archivo, "r") as f:
                lineas = f.readlines()

            datos = []
            comenzar = False
            for linea in lineas:
                if "V" in linea and "I" in linea:
                    comenzar = True
                    continue
                if comenzar:
                    partes = linea.strip().split()
                    if len(partes) >= 2:
                        try:
                            datos.append([float(partes[0]), float(partes[1])])
                        except ValueError:
                            continue

            if not datos:
                return None

            df = pd.DataFrame(datos, columns=["V", "I"])
            df = df.dropna(subset=["V", "I"]).sort_values(by="I")

            if conf["modo"] == "corriente":
                fila = df[(df["V"].round(1) == conf["target_val"])]
                if not fila.empty:
                    val_ia = abs(fila["I"].values[0]) * 1e6  # Normalizado a uA
                    t_acum = self._calcular_tiempo_acumulado_fg(nro_paso)
                    return t_acum, val_ia
            else:
                # Modo Tensión (FOXFET): interpolación lineal sub-paso
                v_vector = df["V"].values
                i_vector = df["I"].values
                if min(i_vector) <= conf["target_val"] <= max(i_vector):
                    v_interp = np.interp(conf["target_val"], i_vector, v_vector)
                    t_acum = self._calcular_tiempo_acumulado_foxfet(nro_paso)
                    return t_acum, v_interp

        except Exception as e:
            st.error(f"Error procesando {ruta_archivo}: {e}")
        return None

    def procesar_carpetas(self, clave_dispositivo):
        """Escanea el directorio, prioriza réplicas M2 > M1 y realiza el ordenamiento global."""
        conf = self.config_dispositivos[clave_dispositivo]
        patron_carpeta = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        patron_archivo = re.compile(r"postrad(\d+)_M(\d+)" + re.escape(conf["sufijo_archivo"]) + "$")

        base_datos = {disp: [] for disp in conf["nombres"][0]}
        carpetas = [c for c in os.listdir(self.ruta_base) if os.path.isdir(os.path.join(self.ruta_base, c)) and patron_carpeta.match(c)]

        for carpeta in carpetas:
            ruta_carp = os.path.join(self.ruta_base, carpeta)
            for disp in conf["nombres"][0]:
                ruta_disp = os.path.join(ruta_carp, disp)
                if not os.path.exists(ruta_disp):
                    continue

                archivos_por_paso = {}
                for arch in os.listdir(ruta_disp):
                    match = patron_archivo.match(arch)
                    if match:
                        nro_paso = int(match.group(1))
                        m_val = int(match.group(2))
                        if nro_paso not in archivos_por_paso or m_val > archivos_por_paso[nro_paso]["m"]:
                            archivos_por_paso[nro_paso] = {"arch": arch, "m": m_val}

                for nro_paso, info in archivos_por_paso.items():
                    ruta_final_arch = os.path.join(ruta_disp, info["arch"])
                    resultado = self._extraer_punto_operacion(ruta_final_arch, conf, nro_paso, disp)
                    if resultado:
                        base_datos[disp].append(resultado)

        # Ordenamiento Global via np.argsort() para resolver desajustes temporales
        for disp in conf["nombres"][0]:
            if base_datos[disp]:
                base_datos[disp] = sorted(base_datos[disp], key=lambda x: x[0])

        return base_datos

    def generar_graficos_evolucion(self, clave_dispositivo, datos):
        """Genera y despliega las salidas de evolución temporal acumulada (Matplotlib + Plotly)."""
        conf = self.config_dispositivos[clave_dispositivo]
        fig_mpl, ax_mpl = plt.subplots(figsize=(10, 6))
        fig_ply = go.Figure()

        hay_datos = False
        for disp in conf["nombres"][0]:
            if disp in datos and datos[disp]:
                hay_datos = True
                tiempos = [x[0] for x in datos[disp]]
                valores = [x[1] for x in datos[disp]]

                ax_mpl.plot(tiempos, valores, marker=conf["marker"], label=disp)
                fig_ply.add_trace(go.Scatter(x=tiempos, y=valores, mode="lines+markers", name=disp))

        if hay_datos:
            ax_mpl.set_title(conf["titulo"])
            ax_mpl.set_xlabel("Tiempo acumulado [min]")
            ax_mpl.set_ylabel(conf["ylabel"])
            ax_mpl.grid(True)
            ax_mpl.legend()
            plt.savefig(f"grafico_{clave_dispositivo}.png")

            st.subheader(conf["titulo"])
            st.pyplot(fig_mpl)

            fig_ply.update_layout(
                title=conf["titulo"],
                xaxis_title="Tiempo acumulado [min]",
                yaxis_title=conf["ylabel"].replace("$", ""),
                template="plotly_white",
            )
            fig_ply.write_html(f"grafico_{clave_dispositivo}_interactivo.html")
            st.plotly_chart(fig_ply, use_container_width=True)
            plt.close(fig_mpl)

    def generar_graficos_dinamica_fg(self, datos_t1, datos_t2):
        """Calcula el análisis diferencial (dIn/dt) respecto a la corriente promedio.
        Mapea las dinámicas intrínsecas y grafica salidas estándar y NUEVAS salidas suavizadas.
        """
        # =====================================================================
        # BLOQUE ORIGINAL (SIN MODIFICACIONES)
        # =====================================================================
        fig_mpl, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig_ply = go.Figure()

        def procesar_tanda_grafico(datos, conf, ax, prefijo_ply):
            hay_datos_tanda = False
            for disp in conf["nombres"][0]:
                if disp in datos and len(datos[disp]) > 1:
                    hay_datos_tanda = True
                    tiempos = np.array([x[0] for x in datos[disp]])
                    valores = np.array([x[1] for x in datos[disp]])

                    factor = conf["factores_wl"].get(disp, 1.0)
                    corrientes_norm = valores / factor

                    d_corriente = np.abs(np.diff(corrientes_norm))
                    d_tiempo = np.diff(tiempos)
                    d_tiempo = np.where(d_tiempo == 0, 1, d_tiempo)

                    derivadas = d_corriente / d_tiempo
                    corriente_promedio = (corrientes_norm[:-1] + corrientes_norm[1:]) / 2.0

                    ax.plot(corriente_promedio, derivadas, marker=conf["marker"], label=disp)
                    fig_ply.add_trace(
                        go.Scatter(
                            x=corriente_promedio,
                            y=derivadas,
                            mode="lines+markers",
                            name=f"{prefijo_ply} - {disp}",
                        )
                    )
            if hay_datos_tanda:
                ax.set_title(conf["titulo"].replace("Evolución", "Dinámica"))
                ax.set_xlabel(r"Corriente Normalizada $I_D / (W/L)$ [$\mu$A]")
                ax.set_ylabel(r"$|d(I_D/(W/L)) / dt|$ [$\mu$A/min]")
                ax.grid(True)
                ax.legend()

        procesar_tanda_grafico(datos_t1, self.config_dispositivos["01_FG_tanda1"] if "01_FG_tanda1" in self.config_dispositivos else self.config_dispositivos["FG_tanda1"], ax1, "Tanda 1")
        procesar_tanda_grafico(datos_t2, self.config_dispositivos["02_FG_tanda2"] if "02_FG_tanda2" in self.config_dispositivos else self.config_dispositivos["FG_tanda2"], ax2, "Tanda 2")

        plt.suptitle("Análisis Diferencial de Degradación (Lógica por Defecto)", fontsize=14)
        plt.savefig("grafico_dinamica_FG_ORIGINAL.png")

        st.subheader("Dinámica de Degradación de Floating Gates (Original)")
        st.pyplot(fig_mpl)

        fig_ply.update_layout(
            title="Dinámica de Degradación Interactiva (Original)",
            xaxis_title="Corriente Normalizada ID / (W/L) [uA]",
            yaxis_title="|d(ID/(W/L)) / dt| [uA/min]",
            template="plotly_white",
        )
        fig_ply.write_html("grafico_dinamica_FG_ORIGINAL_interactivo.html")
        st.plotly_chart(fig_ply, use_container_width=True)
        plt.close(fig_mpl)

        # =====================================================================
        # NUEVO BLOQUE ADICIONAL (SUAVIZADO MEDIANTE SAVITZKY-GOLAY)
        # =====================================================================
        fig_mpl_suav, (ax1_s, ax2_s) = plt.subplots(1, 2, figsize=(16, 6))
        fig_ply_suav = go.Figure()

        def procesar_tanda_suavizada(datos, conf, ax, prefijo_ply):
            hay_datos_tanda = False
            for disp in conf["nombres"][0]:
                if disp in datos and len(datos[disp]) > 4:  # Requiere ventana mínima para SavGol
                    hay_datos_tanda = True
                    tiempos = np.array([x[0] for x in datos[disp]])
                    valores = np.array([x[1] for x in datos[disp]])

                    factor = conf["factores_wl"].get(disp, 1.0)
                    corrientes_norm = valores / factor

                    # Filtro Savitzky-Golay aplicado a la corriente previo a derivar
                    # Ventana de 5 puntos, polinomio de grado 2 (elimina ruido de cuantización)
                    corrientes_suavizadas = savgol_filter(corrientes_norm, window_length=5, polyorder=2)

                    d_corriente = np.abs(np.diff(corrientes_suavizadas))
                    d_tiempo = np.diff(tiempos)
                    d_tiempo = np.where(d_tiempo == 0, 1, d_tiempo)

                    derivadas_filtradas = d_corriente / d_tiempo
                    corriente_promedio = (corrientes_suavizadas[:-1] + corrientes_suavizadas[1:]) / 2.0

                    ax.plot(corriente_promedio, derivadas_filtradas, marker=conf["marker"], label=disp)
                    fig_ply_suav.add_trace(
                        go.Scatter(
                            x=corriente_promedio,
                            y=derivadas_filtradas,
                            mode="lines+markers",
                            name=f"{prefijo_ply} - {disp} (Suavizado)",
                        )
                    )
            if hay_datos_tanda:
                ax.set_title(conf["titulo"].replace("Evolución", "Dinámica Suavizada"))
                ax.set_xlabel(r"Corriente Normalizada $I_D / (W/L)$ [$\mu$A]")
                ax.set_ylabel(r"$|d(I_{suav}/(W/L)) / dt|$ [$\mu$A/min]")
                ax.grid(True)
                ax.legend()

        procesar_tanda_suavizada(datos_t1, self.config_dispositivos["01_FG_tanda1"] if "01_FG_tanda1" in self.config_dispositivos else self.config_dispositivos["FG_tanda1"], ax1_s, "Tanda 1")
        procesar_tanda_suavizada(datos_t2, self.config_dispositivos["02_FG_tanda2"] if "02_FG_tanda2" in self.config_dispositivos else self.config_dispositivos["FG_tanda2"], ax2_s, "Tanda 2")

        plt.suptitle("Análisis Diferencial con Filtro Savitzky-Golay (Ventana=5, Grado=2)", fontsize=14)
        plt.savefig("grafico_dinamica_FG_SUAVIZADO.png")

        st.subheader("Dinámica de Degradación de Floating Gates (Filtro Anti-Ruido Adicional)")
        st.pyplot(fig_mpl_suav)

        fig_ply_suav.update_layout(
            title="Dinámica de Degradación Interactiva (Filtrada / Suave)",
            xaxis_title="Corriente Normalizada ID / (W/L) [uA]",
            yaxis_title="|d(ID_suav/(W/L)) / dt| [uA/min]",
            template="plotly_white",
        )
        fig_ply_suav.write_html("grafico_dinamica_FG_SUAVIZADO_interactivo.html")
        st.plotly_chart(fig_ply_suav, use_container_width=True)
        plt.close(fig_mpl_suav)

    def generar_graficos_foxfet(self, datos):
        """Genera gráficos para los FOXFET separando por curvas individuales."""
        conf = self.config_dispositivos["FOXFET"]
        fig_mpl, ejes = plt.subplots(2, 2, figsize=(14, 10))
        ejes = ejes.flatten()

        fig_ply = go.Figure()

        hay_datos = False
        for idx, disp in enumerate(conf["nombres"][0]):
            if disp in datos and datos[disp]:
                hay_datos = True
                tiempos = [x[0] for x in datos[disp]]
                valores = [x[1] for x in datos[disp]]

                ax = ejes[idx]
                ax.plot(tiempos, valores, marker=conf["marker"], color=f"C{idx}", label=disp)
                ax.set_title(f"Dispositivo: {disp}")
                ax.set_xlabel("Tiempo [min]")
                ax.set_ylabel("Tensión [V]")
                ax.grid(True)
                ax.legend()

                fig_ply.add_trace(go.Scatter(x=tiempos, y=valores, mode="lines+markers", name=disp))

        if hay_datos:
            plt.subplots_adjust(hspace=0.4, wspace=0.3)
            plt.suptitle(conf["titulo"], fontsize=16, y=0.95)
            plt.savefig("grafico_FOXFET.png")

            st.subheader(conf["titulo"])
            st.pyplot(fig_mpl)

            fig_ply.update_layout(
                title=conf["titulo"],
                xaxis_title="Tiempo acumulado [min]",
                yaxis_title="Tensión [V]",
                template="plotly_white",
            )
            fig_ply.write_html("grafico_FOXFET_interactivo.html")
            st.plotly_chart(fig_ply, use_container_width=True)
            plt.close(fig_mpl)


if __name__ == "__main__":
    st.title("Panel de Control de Ensayos de Radiación")
    st.sidebar.markdown("### Configuración de Datos")
    st.sidebar.info("El script está analizando la raíz del directorio actual (./)")

    analizador = AnalizadorRadiacion()

    st.header("1. Ejecución de Pipeline de Carga")
    with st.spinner("Procesando archivos de datos experimentales..."):
        datos_t1 = analizador.procesar_carpetas("FG_tanda1")
        datos_t2 = analizador.procesar_carpetas("FG_tanda2")
        datos_foxfet = analizador.procesar_carpetas("FOXFET")
    st.success("¡Pipeline completado con éxito! Estructuras ordenadas globalmente.")

    st.header("2. Curvas de Evolución Temporal")
    analizador.generar_graficos_evolucion("FG_tanda1", datos_t1)
    analizador.generar_graficos_evolucion("FG_tanda2", datos_t2)
    analizador.generar_graficos_foxfet(datos_foxfet)

    st.header("3. Análisis de Sensibilidad y Dinámicas")
    analizador.generar_graficos_dinamica_fg(datos_t1, datos_t2)
