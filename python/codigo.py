import os
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as str  # Se cambia el alias para evitar colisión con el tipo str nativo


class AnalizadorRadiacion:
    """Clase para el procesamiento y visualización de datos de irradiación

    en dispositivos Floating Gate (FG) y FOXFET.
    """

    def __init__(self, ruta_base="./", intervalo_minutos=10):
        self.ruta_base = ruta_base
        self.intervalo_minutos = intervalo_minutos
        self.config_dispositivos = {
            "FG_tanda1": {
                "nombres": ["PFGIW1", "PFGIW2", "PFGIW3"],
                "target_val": -4.5,
                "modo": "corriente",
                "marker": "o",
                "titulo": "Evolución Floating Gates Tanda 1 (I @ V = -4.5 V)",
                "ylabel": r"$I_D$ [$\mu$A]",
                "factores_wl": {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0},
                "sufijo_archivo": ".ri",
            },
            "FG_tanda2": {
                "nombres": ["PFGIW1", "PFGIW2", "PFGIW3", "PFGIP2"],
                "target_val": -4.5,
                "modo": "corriente",
                "marker": "v",
                "titulo": "Evolución Floating Gates Tanda 2 (I @ V = -4.5 V)",
                "ylabel": r"$I_D$ [$\mu$A]",
                "factores_wl": {"PFGIW1": 4.0, "PFGIW2": 1.0, "PFGIW3": 56.0, "PFGIP2": 1.0},
                "sufijo_archivo": "_2.ri",
            },
            "FOXFET": {
                "nombres": ["FFC1", "FFC2", "FFC3", "FFL", "FFS"],
                "target_val": 1e-5,
                "modo": "tension",
                "marker": "s",
                "titulo": r"Evolución FOXFETs (Tensión interpolada @ I = 10 $\mu$A)",
                "ylabel": "Tensión [V]",
            },
        }
        self.resultados = self._inicializar_estructuras()

    def _inicializar_estructuras(self):
        estructuras = {}
        for tipo, conf in self.config_dispositivos.items():
            for disp in conf["nombres"]:
                estructuras[f"{tipo}_{disp}"] = {"tiempos": [], "valores": []}
        return estructuras

    def _calcular_tiempo_acumulado_foxfet(self, nro_postrad):
        tiempo = 0
        for i in range(1, nro_postrad + 1):
            if i <= 32:
                tiempo += 10
            elif i <= 44:
                tiempo += 15
            else:
                tiempo += 20
        return tiempo

    def procesar_carpetas(self, fechas=None):
        """Ejecuta la extracción de datos detectando automáticamente las carpetas de fechas."""
        if not os.path.exists(self.ruta_base):
            return

        patron_fecha = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        todas_las_carpetas = os.listdir(self.ruta_base)
        fechas_detectadas = [
            f
            for f in todas_las_carpetas
            if patron_fecha.match(f)
            and os.path.isdir(os.path.join(self.ruta_base, f))
        ]
        fechas_ordenadas = sorted(fechas_detectadas)

        for fecha in fechas_ordenadas:
            ruta_carpeta = os.path.join(self.ruta_base, fecha)
            archivos = os.listdir(ruta_carpeta)

            for tipo, conf in self.config_dispositivos.items():
                for disp in conf["nombres"]:
                    mapeo_prioridad = {}
                    for f in archivos:
                        if disp in f and "postrad" in f:
                            if tipo == "FG_tanda1" and f.endswith("_2.ri"):
                                continue
                            if tipo == "FG_tanda2" and not f.endswith("_2.ri"):
                                continue

                            match = re.search(r"postrad(\d+)_M(\d+)", f)
                            if match:
                                nro = int(match.group(1))
                                m_version = int(match.group(2))

                                if nro not in mapeo_prioridad:
                                    mapeo_prioridad[nro] = (m_version, f)
                                else:
                                    if m_version > mapeo_prioridad[nro][0]:
                                        mapeo_prioridad[nro] = (m_version, f)

                    for nro in sorted(mapeo_prioridad.keys()):
                        nombre_f = mapeo_prioridad[nro][1]
                        self._extraer_punto_operacion(
                            os.path.join(ruta_carpeta, nombre_f),
                            disp,
                            nro,
                            conf,
                            tipo,
                        )

    def _extraer_punto_operacion(self, ruta_completa, disp, nro, conf, tipo_disp):
        try:
            df = pd.read_csv(
                ruta_completa,
                skiprows=4,
                sep=r"\s+",
                names=["V", "I", "C3", "C4", "C5"],
                encoding="latin-1",
            )
            df["V"] = pd.to_numeric(df["V"], errors="coerce")
            df["I"] = pd.to_numeric(df["I"], errors="coerce")
            df = df.dropna(subset=["V", "I"]).sort_values(by="I")

            if tipo_disp == "FOXFET":
                tiempo_acumulado = self._calcular_tiempo_acumulado_foxfet(nro)
            else:
                tiempo_acumulado = nro * self.intervalo_minutos

            if conf["modo"] == "corriente":
                fila = df[(df["V"].round(1) == conf["target_val"])]
                if not fila.empty:
                    corriente_ua = abs(fila["I"].values[0] * 1e6)
                    self.resultados[f"{tipo_disp}_{disp}"]["valores"].append(corriente_ua)
                    self.resultados[f"{tipo_disp}_{disp}"]["tiempos"].append(tiempo_acumulado)
            else:
                corrientes_medidas = df["I"].abs().values
                tensiones_medidas = df["V"].values
                tension_interpolada = np.interp(
                    conf["target_val"], corrientes_medidas, tensiones_medidas
                )
                self.resultados[f"{tipo_disp}_{disp}"]["valores"].append(tension_interpolada)
                self.resultados[f"{tipo_disp}_{disp}"]["tiempos"].append(tiempo_acumulado)
        except Exception:
            pass

    def generar_graficos_dinamica_fg(self):
        """Calcula la derivada temporal de la corriente normalizada para ambas tandas

        y las renderiza en la interfaz web de Streamlit.
        """
        for tanda in ["FG_tanda1", "FG_tanda2"]:
            conf = self.config_dispositivos[tanda]
            fig_mpl, ax = plt.subplots(figsize=(10, 6))
            fig_ply = go.Figure()
            hay_datos = False

            for disp in conf["nombres"]:
                tiempos = np.array(self.resultados[f"{tanda}_{disp}"]["tiempos"])
                corrientes = np.array(self.resultados[f"{tanda}_{disp}"]["valores"])

                if len(corrientes) < 2:
                    continue

                factor = conf["factores_wl"][disp]
                corrientes_norm = corrientes / factor

                d_corriente = np.abs(np.diff(corrientes_norm))
                d_tiempo = np.diff(tiempos)

                derivadas = d_corriente / d_tiempo
                corrientes_promedio = (
                    corrientes_norm[:-1] + corrientes_norm[1:]
                ) / 2.0

                ax.plot(
                    corrientes_promedio,
                    derivadas,
                    marker=conf["marker"],
                    label=f"{disp} (Normalizado)",
                    linestyle="-",
                )

                fig_ply.add_trace(
                    go.Scatter(
                        x=corrientes_promedio,
                        y=derivadas,
                        mode="lines+markers",
                        name=f"{disp} (Normalizado)",
                    )
                )
                hay_datos = True

            if hay_datos:
                titulo_grafico = f"Dinámica de Degradación ({tanda.replace('_', ' ').title()}): $dI/dt$ vs Corriente Normalizada"
                ax.set_title(titulo_grafico)
                ax.set_xlabel(r"Corriente Normalizada I [$\mu$A]")
                ax.set_ylabel(r"$dI/dt$ [$\mu$A/min]")
                ax.legend()
                ax.grid(True, linestyle=":", alpha=0.6)
                plt.savefig(f"grafico_derivada_{tanda}.png")
                
                # Renderizado en Streamlit
                str.subheader(f"Dinámica diferencial - {tanda.replace('_', ' ').title()}")
                str.pyplot(fig_mpl)

                fig_ply.update_layout(
                    title=titulo_grafico.replace("$", ""),
                    xaxis_title="Corriente Normalizada I [uA]",
                    yaxis_title="dI/dt [uA/min]",
                    template="plotly_white",
                )
                fig_ply.write_html(f"grafico_derivada_{tanda}_interactivo.html")
                str.plotly_chart(fig_ply, use_container_width=True)
                plt.close(fig_mpl)

    def generar_graficos(self):
        """Renderiza y exporta las figuras estáticas e interactivas originales."""
        for tipo, conf in self.config_dispositivos.items():
            if tipo == "FG_tanda1" or tipo == "FG_tanda2":
                self._graficar_floating_gates(tipo, conf)
            else:
                self._graficar_foxfets(conf)

    def _graficar_floating_gates(self, tipo_tanda, conf):
        fig_mpl, ax = plt.subplots(figsize=(10, 6))
        fig_ply = go.Figure()
        hay_datos = False
        for disp in conf["nombres"]:
            if self.resultados[f"{tipo_tanda}_{disp}"]["tiempos"]:
                ax.plot(
                    self.resultados[f"{tipo_tanda}_{disp}"]["tiempos"],
                    self.resultados[f"{tipo_tanda}_{disp}"]["valores"],
                    conf["marker"],
                    label=disp,
                    linestyle="--",
                )
                fig_ply.add_trace(
                    go.Scatter(
                        x=self.resultados[f"{tipo_tanda}_{disp}"]["tiempos"],
                        y=self.resultados[f"{tipo_tanda}_{disp}"]["valores"],
                        mode="lines+markers",
                        name=disp,
                    )
                )
                hay_datos = True

        if hay_datos:
            ax.set_title(conf["titulo"])
            ax.set_xlabel("Tiempo [min]")
            ax.set_ylabel(conf["ylabel"])
            ax.legend()
            ax.grid(True, linestyle=":", alpha=0.6)
            plt.savefig(f"grafico_corriente_{tipo_tanda}.png")
            
            str.subheader(conf["titulo"])
            str.pyplot(fig_mpl)

            fig_ply.update_layout(
                title=conf["titulo"],
                xaxis_title="Tiempo [min]",
                yaxis_title="Corriente [uA]",
                template="plotly_white",
            )
            fig_ply.write_html(f"grafico_corriente_{tipo_tanda}_interactivo.html")
            str.plotly_chart(fig_ply, use_container_width=True)
            plt.close(fig_mpl)

    def _graficar_foxfets(self, conf):
        from plotly.subplots import make_subplots

        fig_mpl, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14))
        fig_ply = make_subplots(
            rows=3,
            cols=1,
            subplot_titles=[
                "Dispositivo FFC1",
                "Dispositivos FFC2 y FFC3",
                "Dispositivos FFL y FFS",
            ],
            vertical_spacing=0.08,
        )
        hay_datos = False

        if self.resultados["FOXFET_FFC1"]["tiempos"]:
            ax1.plot(
                self.resultados["FOXFET_FFC1"]["tiempos"],
                self.resultados["FOXFET_FFC1"]["valores"],
                conf["marker"],
                label="FFC1",
                color="red",
                linestyle="--",
            )
            fig_ply.add_trace(
                go.Scatter(
                    x=self.resultados["FOXFET_FFC1"]["tiempos"],
                    y=self.resultados["FOXFET_FFC1"]["valores"],
                    mode="lines+markers",
                    name="FFC1",
                    line=dict(color="red"),
                ),
                row=1,
                col=1,
            )
            hay_datos = True

        for disp in ["FFC2", "FFC3"]:
            if self.resultados[f"FOXFET_{disp}"]["tiempos"]:
                ax2.plot(
                    self.resultados[f"FOXFET_{disp}"]["tiempos"],
                    self.resultados[f"FOXFET_{disp}"]["valores"],
                    conf["marker"],
                    label=disp,
                    linestyle="--",
                )
                fig_ply.add_trace(
                    go.Scatter(
                        x=self.resultados[f"FOXFET_{disp}"]["tiempos"],
                        y=self.resultados[f"FOXFET_{disp}"]["valores"],
                        mode="lines+markers",
                        name=disp,
                    ),
                    row=2,
                    col=1,
                )
                hay_datos = True

        for disp in ["FFL", "FFS"]:
            if self.resultados[f"FOXFET_{disp}"]["tiempos"]:
                ax3.plot(
                    self.resultados[f"FOXFET_{disp}"]["tiempos"],
                    self.resultados[f"FOXFET_{disp}"]["valores"],
                    conf["marker"],
                    label=disp,
                    linestyle="--",
                )
                fig_ply.add_trace(
                    go.Scatter(
                        x=self.resultados[f"FOXFET_{disp}"]["tiempos"],
                        y=self.resultados[f"FOXFET_{disp}"]["valores"],
                        mode="lines+markers",
                        name=disp,
                    ),
                    row=3,
                    col=1,
                )
                hay_datos = True

        for idx, ax in enumerate([ax1, ax2, ax3], start=1):
            ax.set_ylabel(conf["ylabel"])
            ax.set_xlabel("Tiempo acumulado [min]")
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend()

            lineas = ax.get_lines()
            if lineas:
                todos_los_v = [
                    val for linea in lineas for val in linea.get_ydata()
                ]
                ax.set_ylim(min(todos_los_v) - 0.2, max(todos_los_v) + 0.2)

            fig_ply.update_xaxes(
                title_text="Tiempo acumulado [min]", row=idx, col=1
            )
            fig_ply.update_yaxes(title_text="Tensión [V]", row=idx, col=1)

        if hay_datos:
            plt.subplots_adjust(hspace=0.5)
            plt.suptitle(conf["titulo"], fontsize=16, y=0.95)
            plt.savefig(f"grafico_{conf['modo']}_FOXFET.png")
            
            str.subheader(conf["titulo"])
            str.pyplot(fig_mpl)

            fig_ply.update_layout(
                title_text=conf["titulo"],
                height=900,
                width=1000,
                template="plotly_white",
            )
            fig_ply.write_html(f"grafico_{conf['modo']}_FOXFET_interactivo.html")
            str.plotly_chart(fig_ply, use_container_width=True)
            plt.close(fig_mpl)


if __name__ == "__main__":
    str.title("Panel de Control de Ensayos de Radiación")
    str.sidebar.markdown("### Configuración de Datos")
    str.sidebar.info("El script está analizando la raíz del repositorio en busca de carpetas con formato YYYY-MM-DD.")
    
    analizador = AnalizadorRadiacion(ruta_base="./")
    analizador.procesar_carpetas()
    analizador.generar_graficos_dinamica_fg()
    analizador.generar_graficos()
