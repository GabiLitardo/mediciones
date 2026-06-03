from lantz import Feat, Q_, Action, LOGGER
from keithley617 import Keithley617 #Electrometro
from keithley705 import Keithley705 # Scanner
from hp8112a import HP8112A # Generador de pulsos
import matplotlib.pyplot as plt
import csv
import tkinter as tk
from tkinter import Entry, Button, font, Checkbutton, BooleanVar
from time import sleep
from datetime import datetime
import threading # permite correr procesos en paralelo
import numpy as np
import argparse
import pyvisa

from lantz.log import log_to_screen, DEBUG

# fh = logging.FileHandler('C:\lantz\error.log')
# fh.setLevel(logging.DEBUG)
# LOGGER.addHandler(fh)

#log_to_screen(DEBUG) # esto solo si quiero que me muestre la tx/rx de mensajes

# Programa para inyección de floating gate con uno o más pulsos fijos con condición de corte

# Unidades
ampere=Q_(1,'A')
volt=Q_(1,'V')
millisec=Q_(1,'ms')
sec=Q_(1,'s')

########################## Instrumentos ##########################

# Instrumentos
gen_pulsos = HP8112A('GPIB0::11::INSTR')
electrometro_727 = Keithley617('GPIB0::27::INSTR')
scanner = Keithley705('GPIB0::29::INSTR')

# Inicializo instrumentos
scanner.initialize()
gen_pulsos.initialize()
electrometro_727.initialize()

# Configuro instrumentos

# K705 (Scanner)
# Channel: (col, fila)
# (2,2) --> conecta electrometro 727 (V source) con source
# (2,3) --> conecta electrometro 727 (V source) con drain
# (D y S conectados entre sí y al electrometro 727)
def matriz_estado_pulso():
    scanner.reset()
    for channel in [(2,2),(2,3)]:
        scanner.close(channel)
# (2,2) --> conecta electrometro 727 (V source) con source
# (1,3) --> conecta electrometro 727 con drain
# (D y S conectados entre sí y al electrometro 727)
def matriz_estado_medir_corriente():
    scanner.reset()
    for channel in [(2,2),(1,3)]:
        scanner.close(channel)

# HP8112A (generador de pulsos)
gen_pulsos.enable=False # inicialmente habilitado
gen_pulsos.period = 2*gen_pulsos.width # duty cycle 50%
# Seteo trigger ya para external burst así el programa no arranca con pulsos
# (recordar que generador de pulsos ya va a estar conectado al gate)
gen_pulsos.trigger_mode = 'external_burst' # M5
gen_pulsos.trigger_control = 'positive' # positive


# K617 (mide corriente)
electrometro_727.function='amps'
electrometro_727.zero_check = False
electrometro_727.zero_correct = False
electrometro_727.range = 'auto'
electrometro_727.vsource_operate = True # habilito fuente de tensión
electrometro_727.voltage = 0 * volt # en principio seteo 0V

# Cuando recién arranca el programa seteo matriz para medir corriente para ver cómo está ahora el FG
matriz_estado_medir_corriente()

########################## Plot y archivo csv ##########################

window = tk.Tk()

# Contenedores vacíos
x_data = []
current_data = []
pulse_data = []

# Archivo CSV
parser = argparse.ArgumentParser()
parser.add_argument('-archivo','--filename', required=True)
args = parser.parse_args()

csv_filename = args.filename + ".csv"

csvfile = open(csv_filename, 'w', newline='')

csv_writer = csv.writer(csvfile)
csv_writer.writerow([datetime.now()])
csv_writer.writerow(['segundo','ampere','volt','segundo','volt','volt'])
csv_writer.writerow(['Tiempo', 'Corriente', 'Pulso', 'AnchoPulso', 'Tension fija','Vsd']) # Header

########################## Medicion ##########################

class Medicion:
    def __init__(self, pulse_high_level, pulse_low_level, pulse_width):
        self.pulse_high_level = pulse_high_level
        self.pulse_low_level = pulse_low_level
        self.pulse_width = pulse_width
        self.sample_time = self.pulse_width/100 # fijar valor
        self.number_of_pulses = 1
        self.measured_current = 0
        self.number_of_pulses_sent_so_far = 0



        self.target_current = 0
        self.time_between_pulse_update_in_sec = 4 
        self.time_counter = self.time_between_pulse_update_in_sec
        self.max_current = 1e-3 # 1 mA

        # Estados para ejecución del programa
        self.medicion_iniciada = False # 
        self.estado_run = False
        self.begin_pulses = False
        self.estado_enviando_pulsos = False
        self.flag_enviar_pulso = False
        self.signo_pulso = False
        self.v_ds = 0
        # self.transistor_canal_n = True

        gen_pulsos.high_level = (self.pulse_high_level / 2) * volt
        gen_pulsos.low_level = (self.pulse_low_level / 2) * volt
        gen_pulsos.width = self.pulse_width * sec
        gen_pulsos.period = 2*gen_pulsos.width
    
    def iniciar(self):
        if self.v_ds != 0 and self.target_current != 0:
            label_set_v_ds.config(text="")
            if self.estado_run != True:
                self.estado_run = True
                run_thread = threading.Thread(target=self.run)
                run_thread.start()
                self.medicion_iniciada = True
        else:
            label_set_v_ds.config(text="Antes de iniciar la medición fije un valor de VDS y de corriente de corte.")

    def stop(self):
        self.estado_run = False
        self.plot()

    def plot(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8))
        fig.canvas.manager.set_window_title('Metodo2 - Pulsos fijos con condición de corte') # Nombre de la figura
        ax1.set_xlabel('Tiempo')
        ax1.set_ylabel('Corriente')
        ax2.set_xlabel('Tiempo')
        ax2.set_ylabel('Pulso')
        print(len(x_data))
        print(len(current_data))
        ax1.plot(x_data,current_data)
        ax1.grid(True)
        print("\n")
        print(len(x_data))
        print(len(pulse_data))
        ax2.plot(x_data,pulse_data)
        ax2.grid(True)
        plt.show()

    def run(self):
        while self.estado_run:

            if len(x_data) != 0:
                x_value = x_data[-1] + 1
            else:
                x_value = 0
            
            electrometro_727.voltage = self.v_ds * volt	
            x_data.append(x_value)
            
            current_value = electrometro_727.measure_current # valor con unidades
            
            self.measured_current = current_value.to('A').magnitude
            current_data.append(self.measured_current)
            screen_label.config(text="Corriente medida: " + str("{:.3e}".format(self.measured_current)) + "A")

            pulse_value = 0
            pulse_data.append(pulse_value)

            csv_writer.writerow([x_value, self.measured_current, pulse_value, 0,0,self.v_ds])

            if((self.measured_current >= self.target_current * 0.9) and ((self.measured_current <= self.target_current * 1.1))) :
                self.stop()

            if(self.measured_current > self.max_current):
                self.stop()

            sleep(1)

            if(self.flag_enviar_pulso):
                self.enviar_pulsos()
                self.begin_pulses = True
                while(self.estado_enviando_pulsos):
                    pass
                self.flag_enviar_pulso = False

            if((self.time_counter == 0) and (self.begin_pulses)):
                if(self.signo_pulso):
                    # Pulsos positivos
                    self.update_pulse_high_level(self.pulse_high_level + 0.1)
                else:
                    # Pulsos negativos
                    self.update_pulse_low_level(self.pulse_low_level - 0.1)
                self.time_counter = self.time_between_pulse_update_in_sec
                self.enviar_pulsos()
                while(self.estado_enviando_pulsos):
                    pass

            self.time_counter = self.time_counter - 1
			
    def update_pulse_high_level(self,new_high_level):
        self.pulse_high_level = new_high_level
        gen_pulsos.high_level = (self.pulse_high_level / 2) * volt
        add_label_set_pulse_high_level.config(text="High level: " + str("{:.2f}".format(self.pulse_high_level)) + "V")

    def update_pulse_low_level(self,new_low_level):
        self.pulse_low_level = new_low_level
        gen_pulsos.low_level = (self.pulse_low_level / 2) * volt
        add_label_set_pulse_low_level.config(text="Low level: " + str("{:.2f}".format(self.pulse_low_level)) + "V")
        
    def set_pulse_high_level(self):
        try:
            new_high_level = float(entrada_nuevo_valor_alto_pulso.get())
            if new_high_level >= -15 and new_high_level <= 16:
                self.update_pulse_high_level()
            else:
                add_label_set_pulse_high_level.config(text="High level: error")
            entrada_nuevo_valor_alto_pulso.delete(0, tk.END)
        except ValueError:
            pass

    def set_pulse_low_level(self):
        try:
            new_low_level = float(entrada_nuevo_valor_bajo_pulso.get())
            if new_low_level >= -16 and new_low_level <= 15:
                self.update_pulse_low_level(new_low_level)
            else:
                add_label_set_pulse_low_level.config(text="Low level: error")
            entrada_nuevo_valor_bajo_pulso.delete(0, tk.END)
        except ValueError:
            pass

    def set_pulse_width(self):
        try:
            new_width = float(entrada_nuevo_ancho_pulso.get())
            if new_width > 10e-9 and new_width <= 475e-3: # 475e-3 porque duty cycle es 50%
                self.pulse_width = new_width
                gen_pulsos.width = self.pulse_width * sec
                gen_pulsos.period = 2*gen_pulsos.width
                add_label_set_pulse_width.config(text="Ancho del pulso: " + str(self.pulse_width))
            else:
                add_label_set_pulse_width.config(text="Ancho del pulso: error")
            entrada_nuevo_ancho_pulso.delete(0, tk.END)
        except ValueError:
            pass

    def set_number_of_pulses(self):
        try:
            new_number_of_pulses = int(entrada_cant_pulsos.get())
            if new_number_of_pulses >= 1 and new_number_of_pulses <= 1999: 
                self.number_of_pulses = new_number_of_pulses
                add_label_set_cant_pulsos.config(text="Cantidad de pulsos: " + str(self.number_of_pulses))
            else:
                add_label_set_cant_pulsos.config(text="Cantidad de pulsos: error")
            entrada_cant_pulsos.delete(0, tk.END)
        except ValueError:
            pass

    def set_v_ds(self):
        try:
            self.v_ds = float(entrada_nuevo_valor_v_ds.get())
            add_label_set_v_ds.config(text="Tensión VSD: " + str(self.v_ds))
            entrada_nuevo_valor_v_ds.delete(0, tk.END)
            self.set_signo_pulso()
        except ValueError:
            pass

    def set_target_current(self):
        try:
            self.target_current = float(entrada_nuevo_valor_target_current.get())
            add_label_set_target_current.config(text="Corriente de corte: " + str(self.target_current) + " A")
            entrada_nuevo_valor_target_current.delete(0, tk.END)
        except ValueError:
            pass
    
    def graficar_pulsos(self):
        x_values = np.arange(0,self.pulse_width+self.sample_time,self.sample_time)

        a = 1 # constante para complementar pulso o no

        if(self.signo_pulso == False):
            a = -1

        y_values = [a * (abs(self.pulse_high_level) + abs(self.pulse_low_level))] * (round(len(x_values)))

        n = self.number_of_pulses

        for i in range(0,n):
            pulse_data.extend(y_values)    

        while n != 0:
            for i in range(0,len(x_values)):
                x_value = x_data[-1] + self.sample_time
                x_data.append(x_value)
                current_data.append(current_data[-1])
                csv_writer.writerow([x_value,current_data[-1],y_values[i],self.pulse_width,0,self.v_ds])
                sleep(self.sample_time) # muestreo
                print("Graficando...")
            n = n-1

        x_data.append(x_data[-1]+self.sample_time)
        current_data.append(current_data[-1])
        pulse_data.append(0)
        csv_writer.writerow([x_data[-1]+self.sample_time,current_data[-1],0,self.pulse_width,0,self.v_ds])
        
        self.estado_enviando_pulsos = False

    def set_flag_enviar_pulsos(self):
        self.flag_enviar_pulso = True

    def enviar_pulsos(self):
        if self.medicion_iniciada:
            self.estado_enviando_pulsos = True

            gen_pulsos.enable = True		

            N = self.number_of_pulses

            matriz_estado_pulso()

            if self.signo_pulso:
                electrometro_727.voltage = self.pulse_high_level * volt
            else:
                electrometro_727.voltage = self.pulse_low_level * volt

            plot_thread = threading.Thread(target=self.graficar_pulsos)
            plot_thread.start()

            gen_pulsos.burst(N)
            gen_pulsos.group_execute_trigger()

            print("----------------------------")
            print("Cantidad de pulsos: ",N)
            print("Ancho: ",gen_pulsos.width)
            print("Max: ",gen_pulsos.high_level * 2)
            print("Min: ",gen_pulsos.low_level * 2)
            print("----------------------------")
            sleep(N*self.pulse_width*2)	
		    
            sleep(1)
			
            electrometro_727.voltage = 0 * volt	
            
            sleep(1)	
			
            matriz_estado_medir_corriente()
            
            sleep(1)
			
            electrometro_727.voltage = self.v_ds * volt

            sleep(1)
			
            gen_pulsos.enable = False
            # self.estado_run = True
            sleep(1)

            self.number_of_pulses_sent_so_far = self.number_of_pulses_sent_so_far + N
            label_pulsos_aplicados.config(text="Cantidad de pulsos enviados: " + str(self.number_of_pulses_sent_so_far))
        else:
            print("Iniciar medición antes de enviar pulsos")

    def set_signo_pulso(self):
        estado = signo_pulso.get()
        self.signo_pulso = estado
        if(estado == True):
            gen_pulsos.complement = False
            self.update_pulse_high_level(1)
            self.update_pulse_low_level(0)
        else:
            gen_pulsos.complement = True
            self.update_pulse_low_level(-1)
            self.update_pulse_high_level(0)


medicion = Medicion(0,0,0.3)

window.title("Prueba")

i = 0

# window.geometry("500x300")
label_font = font.Font(size=10)
bold_font = font.Font(size=10, weight="bold")

boton_iniciar = Button(window, text="Iniciar", command=medicion.iniciar, bg='#ffb3fe', font=label_font)
boton_iniciar.grid(row=i,column=0,columnspan=2,pady=15)

i += 1

label_set_v_ds = tk.Label(window, text="", font=label_font)
label_set_v_ds.grid(row=i,column=0,columnspan=2,pady=5)

i += 1

add_label_cant_pulsos = tk.Label(window, text="Cantidad de pulsos", font=bold_font)
add_label_cant_pulsos.grid(row=i,column=0,padx=5)
i += 1
entrada_cant_pulsos = Entry(window, justify="center", font=label_font)
entrada_cant_pulsos.grid(row=i,column=0,padx=5)
i += 1
add_label_set_cant_pulsos = tk.Label(window, text="Cantidad de pulsos: " + str(medicion.number_of_pulses), font=label_font)
add_label_set_cant_pulsos.grid(row=i,column=0,padx=5)
i += 1
boton_cant_pulsos = Button(window, text="Enter", command=medicion.set_number_of_pulses, font=label_font)
boton_cant_pulsos.grid(row=i,column=0,padx=5)

i += 1

add_label_pulse_width = tk.Label(window, text="Ancho del pulso\n(Mín: 10e-9 | Máx: 475e-3)", font=bold_font)
add_label_pulse_width.grid(row=i,column=0,padx=5)
i += 1
entrada_nuevo_ancho_pulso = Entry(window, justify="center", font=label_font)
entrada_nuevo_ancho_pulso.grid(row=i,column=0,padx=5)
i += 1
add_label_set_pulse_width = tk.Label(window, text="Ancho del pulso: " + str(medicion.pulse_width), font=label_font)
add_label_set_pulse_width.grid(row=i,column=0,padx=5)
i += 1
boton_set_pulse_width = Button(window, text="Enter", command=medicion.set_pulse_width, font=label_font)
boton_set_pulse_width.grid(row=i,column=0,padx=5)

add_label_pulse_high_level = tk.Label(window, text="Valor máximo del pulso\n(Mín: -15 | Máx: 16)", font=bold_font)
add_label_pulse_high_level.grid(row=2,column=1,padx=5)
entrada_nuevo_valor_alto_pulso = Entry(window, justify="center", font=label_font)
entrada_nuevo_valor_alto_pulso.grid(row=3,column=1,padx=5)
add_label_set_pulse_high_level = tk.Label(window, text="High level: " + str(medicion.pulse_high_level), font=label_font)
add_label_set_pulse_high_level.grid(row=4,column=1,padx=5)
boton_set_pulse_high_level = Button(window, text="Enter", command=medicion.set_pulse_high_level, font=label_font)
boton_set_pulse_high_level.grid(row=5,column=1,padx=5)

add_label_pulse_low_level = tk.Label(window, text="Valor mínimo del pulso\n(Mín: -16 | Máx: 15)", font=bold_font)
add_label_pulse_low_level.grid(row=6,column=1,padx=5)
entrada_nuevo_valor_bajo_pulso = Entry(window, justify="center", font=label_font)
entrada_nuevo_valor_bajo_pulso.grid(row=7,column=1,padx=5)
add_label_set_pulse_low_level = tk.Label(window, text="Low level: " + str(medicion.pulse_low_level), font=label_font)
add_label_set_pulse_low_level.grid(row=8,column=1,padx=5)
boton_set_pulse_low_level = Button(window, text="Enter", command=medicion.set_pulse_low_level, font=label_font)
boton_set_pulse_low_level.grid(row=9,column=1,padx=5)

add_label_v_ds = tk.Label(window, text="Tensión VSD:", font=bold_font)
add_label_v_ds.grid(row=10,column=0,columnspan=2,padx=5)
entrada_nuevo_valor_v_ds = Entry(window, justify="center", font=label_font)
entrada_nuevo_valor_v_ds.grid(row=11,column=0,columnspan=2,padx=5)
add_label_set_v_ds = tk.Label(window, text="Tensión VSD: " + str(medicion.v_ds), font=label_font)
add_label_set_v_ds.grid(row=12,column=0,columnspan=2,padx=5)
boton_set_set_v_ds = Button(window, text="Enter", command=medicion.set_v_ds, font=label_font)
boton_set_set_v_ds.grid(row=13,column=0,columnspan=2,padx=5)

add_label_set_target_current = tk.Label(window, text="Corriente de corte: ", font=bold_font)
add_label_set_target_current.grid(row=14,column=0,columnspan=2,padx=5)
entrada_nuevo_valor_target_current = Entry(window, justify="center", font=label_font)
entrada_nuevo_valor_target_current.grid(row=15,column=0,columnspan=2,padx=5)
add_label_set_target_current = tk.Label(window, text="Corriente de corte: " + str(medicion.target_current), font=label_font)
add_label_set_target_current.grid(row=16,column=0,columnspan=2,padx=5)
boton_set_set_target_current = Button(window, text="Enter", command=medicion.set_target_current, font=label_font)
boton_set_set_target_current.grid(row=17,column=0,columnspan=2,padx=5)

boton_enviar_pulsos = Button(window, text="Enviar pulsos", command=medicion.set_flag_enviar_pulsos, font=label_font)
boton_enviar_pulsos.grid(row=18,column=0,columnspan=2,pady=10)

signo_pulso = BooleanVar()
pulso_positivo = tk.Radiobutton(window,text="Positivo",variable=signo_pulso,value=True, command=medicion.set_signo_pulso)
pulso_positivo.grid(row=19, column=0, columnspan=2,padx=10)
pulso_negativo = tk.Radiobutton(window,text="Negativo",variable=signo_pulso,value=False, command=medicion.set_signo_pulso)
pulso_negativo.grid(row=19, column=1, columnspan=2,padx=10)

screen_label = tk.Label(window, text="Corriente medida: " + str("{:.3e}".format(medicion.measured_current)) + "A", width=30, height=4, bg="black", fg="white", font=("Arial", 12))
screen_label.grid(row=20, column=0, columnspan=2, pady=2)

label_pulsos_aplicados = tk.Label(window, text="Cantidad de pulsos enviados: " + str(medicion.number_of_pulses_sent_so_far), font=label_font)
label_pulsos_aplicados.grid(row=21, column=0, columnspan=2, pady=2)

boton_stop = Button(window, text="Stop", command=medicion.stop, bg='#748570', font=label_font)
boton_stop.grid(row=22,column=0,columnspan=2,pady=10)

add_label_instruc = tk.Label(window, text="Después de Stop:\n 1- Cerrar primero ventana del plot\n2- Cerrar ventana Tkinter", font=label_font)
add_label_instruc.grid(row=23,column=0,columnspan=2,pady=15)

window.mainloop()

medicion.estado_run = False

electrometro_727.voltage = 0 * volt
csvfile.close()
scanner.reset()
gen_pulsos.finalize()
scanner.finalize()
electrometro_727.finalize()