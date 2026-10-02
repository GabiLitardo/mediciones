from pynanolab.instrument import Keithley2600
from pynanolab.data_processing.storage import save_data, save_plot
from pynanolab.data_processing.misc import set_source_range
import numpy as np
from pandas import DataFrame
import time
import signal
import matplotlib.pyplot as plt


# ------------------------------------------------
# -             Script Parameters                -
# ------------------------------------------------
# Output File Reference
measurement_reference = 'FG_PULSES_DIE4_PFGIW1'

# v_rest: Tensión de reposo u OFF
# v_pulse: Tensión activa de pulso u ON
v_rest      = 0.0
v_pulse     = -5.0
num_pulses  = 10          # Cantidad de pulsos en la ráfaga
t_on        = 0.3         # Tiempo de pulso activo
t_off       = 0.3         # Tiempo de reposo entre pulsos

vg_rangev   = 20
vg_limiti   = 1e-3
vg_rangei   = None # AUTORANGE_ON

# Drain Voltage  [SMU_25.CHB]
vd_meas     = -4.5     # Tensión de Drain de medción
vd_rangev   = 20
vd_limiti   = 1e-3
vd_rangei   = None # AUTORANGE_ON

# Source Voltage Sweep [SMU_26.CHA]
vs_rangev   = 200e-3
vs_limiti   = 10e-3
vs_rangei   = None # AUTORANGE_ON

# Bulk Voltage Sweep [SMU_26.CHB]
vb_rangev   = 200e-3
vb_limiti   = 10e-3
vb_rangei   = None # AUTORANGE_ON

# ------------------------------------------------
# -             Creating System                   -
# ------------------------------------------------
k1 = Keithley2600(address='GPIB0::25::INSTR')
k2 = Keithley2600(address='GPIB0::26::INSTR')

# ------------------------------------------------
# -             Exception Handling                -
# ------------------------------------------------
def sigint_handler(SignalNumber, Frame):
    raise Exception('Program was interrupted by the User')

signal.signal(signal.SIGINT, sigint_handler)

try:
    # ------------------------------------------------
    # -             Configuring Device                -
    # ------------------------------------------------
    k1.smua.reset()
    k1.smub.reset()
    k2.smua.reset()
    k2.smub.reset()

    k1.config_display_amperimeter()
    k2.config_display_amperimeter()

    # --- smu.measure configuration ---
    k1.smua.configure_simple_amperimeter(
        rangei  = vg_rangei,
    )
    k1.smub.configure_simple_amperimeter(
        rangei  = vd_rangei,
    )
    k2.smua.configure_simple_amperimeter(
        rangei  = vs_rangei,
    )
    k2.smub.configure_simple_amperimeter(
        rangei  = vb_rangei,
    )

    # --- smu.source configuration ---
    k1.smua.configure_simple_voltage_source(
        levelv  = 0,
        limiti  = vg_limiti,
        rangev  = vg_rangev,
        offmode = k1.smua.OUTPUT_NORMAL
    )
    k1.smub.configure_simple_voltage_source(
        levelv  = 0,
        limiti  = vd_limiti,
        rangev  = vd_rangev,
        offmode = k1.smub.OUTPUT_NORMAL
    )
    k2.smua.configure_simple_voltage_source(
        levelv  = 0,
        limiti  = vs_limiti,
        rangev  = vs_rangev,
        offmode = k2.smua.OUTPUT_NORMAL
    )
    k2.smub.configure_simple_voltage_source(
        levelv  = 0,
        limiti  = vb_limiti,
        rangev  = vb_rangev,
        offmode = k2.smub.OUTPUT_NORMAL
    )

    # Turn on all outputs
    k1.smua.source.output = k1.smua.OUTPUT_ON
    k1.smub.source.output = k1.smub.OUTPUT_ON
    k2.smua.source.output = k2.smua.OUTPUT_ON
    k2.smub.source.output = k2.smub.OUTPUT_ON

    # ------------------------------------------- #
    #               k1.smua = Injector            #
    #               k1.smub = Drain               #
    #               k2.smua = Source              #
    #               k2.smub = Bulk                #
    # ------------------------------------------- #

    # Wait for both SMUs to be ready
    k1.wait_opc()
    k2.wait_opc()

    # ==========================================================
    # -                     Pre Pulses                         -
    # ==========================================================
    k2.smua.source.levelv = '0.000000'
    k1.smua.source.levelv = '0.000000'
    k1.smub.source.levelv = f'{vd_meas:.6f}'
    k1.wait_opc()
    k2.wait_opc()
    time.sleep(0.2) # Initial transient estabilization

    id_initial = float(k1.smub.measure.i())
    k1.wait_opc()
    print(f"Initial Id: {id_initial:.6e} A")

    # ==========================================================
    # -                        Pulses                          -
    # ==========================================================
    print(f"Burst of {num_pulses} pulses...")

    # Initial rest config
    k2.smua.source.levelv = f'{v_rest:.6f}' # Source to v_rest
    k1.smub.source.levelv = f'{v_rest:.6f}' # Drain to v_rest
    k1.smua.source.levelv = f'{v_rest:.6f}' # Injector to v_rest
    k1.wait_opc()
    k2.wait_opc()
    time.sleep(t_off)

    for p in range(num_pulses):
        print(f"Pulse {p}/{num_pulses}.")
        # ON State
        k1.smua.source.levelv = f'{v_pulse:.6f}'
        k1.wait_opc()
        time.sleep(t_on)

        # OFF State
        k1.smua.source.levelv = f'{v_rest:.6f}'
        k1.wait_opc()
        time.sleep(t_off)

    print("Burst done.")

    # ==========================================================
    # -                     Post Pulses                       -
    # ==========================================================
    print("Reading...")
    k1.smua.source.levelv = '0.000000'       # Injector to 0V
    k2.smua.source.levelv = '0.000000'       # Source to 0V
    k1.smub.source.levelv = f'{vd_meas:.6f}' # Drain to vd_meas
    k1.wait_opc()
    k2.wait_opc()
    time.sleep(0.2) # Initial transient estabilization

    id_final = float(k1.smub.measure.i())
    k1.wait_opc()
    print(f"Final Id: {id_final:.6e} A")

    delta_id = id_final - id_initial
    print(f"Delta Id: {delta_id:.6e} A")

    df = DataFrame({
        'Inicial_Id': [id_initial],
        'Final_Id': [id_final],
        'Delta_Id': [delta_id]
    })

    # ==========================================================
    # -                     Save results                       -
    # ==========================================================
    save_data(data = df, name = measurement_reference)
    print("Measurement done.")

except Exception as ex:
    # We turn all sources off
    k1.smua.source.output = k1.smua.OUTPUT_OFF
    k1.smub.source.output = k1.smub.OUTPUT_OFF
    k2.smua.source.output = k2.smua.OUTPUT_OFF
    k2.smub.source.output = k2.smub.OUTPUT_OFF
    raise ex