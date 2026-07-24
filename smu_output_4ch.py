'''
Explicación del Ejemplo:

    En el presente ejemplo se mide la curva de salida con 4 canales.
    Para este ejemplo debemos disponer de dos dispositivos dual-channel.
'''
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
measurement_reference = 'OUTPUT_UBA_pmos_07'
# All measurements are stored in: ~/Desktop/mediciones

# Gate Voltage [SMU_25.CHA]
vg_values   = set_source_range(
    start   = -17.5,
    stop    = -17.7,
    step    = -50e-3,
)
vg_rangev   = 20
vg_limiti   = 1e-3
vg_rangei   = None # AUTORANGE_ON

# Drain Voltage  [SMU_25.CHB]
vd_values   = set_source_range(
    start   = 0,                    # NOTE: Vgs = Vg - Vs = [0:5]
    stop    = -300e-3,
    # points  = 200,
    step    = -20e-3,
)
vd_rangev   = 10
vd_limiti   = 1e-3
vd_rangei   = None # AUTORANGE_ON

# Source Voltage Sweep [SMU_26.CHA]
vs_values   = set_source_range(0)
vs_rangev   = 200e-3
vs_limiti   = 10e-3
vs_rangei   = None # AUTORANGE_ON

# Bulk Voltage Sweep [SMU_26.CHB]
vb_values   = set_source_range(0)
vb_rangev   = 200e-3
vb_limiti   = 10e-3
vb_rangei   = None # AUTORANGE_ON

# ------------------------------------------------
# -            Creating System                   -
# ------------------------------------------------
# For this example it is mandatory to know both SMUs addresses.
k1 = Keithley2600(address='GPIB0::25::INSTR')
k2 = Keithley2600(address='GPIB0::26::INSTR')

# ------------------------------------------------
# -            Exception Handling                -
# ------------------------------------------------
def sigint_handler(SignalNumber, Frame):
    raise Exception('Program was interrupted by the User')

signal.signal(signal.SIGINT, sigint_handler)

try:
    # ------------------------------------------------
    # -            Configuring Device                -
    # ------------------------------------------------
    k1.smua.reset()
    k1.smub.reset()
    k2.smua.reset()
    k2.smub.reset()

    k1.config_display_amperimeter()
    k2.config_display_amperimeter()

    # --- smu.measure configuration ---
    # Autorange is used for both amperimeters
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

    # Turn on Vs and Vd
    k1.smua.source.output = k1.smua.OUTPUT_ON 
    k1.smub.source.output = k1.smub.OUTPUT_ON 
    k2.smua.source.output = k2.smua.OUTPUT_ON
    k2.smub.source.output = k2.smub.OUTPUT_ON

    # ------------------------------------------------
    # -               Running Sweep                  -
    # ------------------------------------------------

    # --- Generating output dataframe ---
    results = DataFrame(columns=['vs','vg','vd','id'])

    # ------------------------------------------- #
    #               k1.smua = Gate                #
    #               k1.smub = Drain               #
    #               k2.smua = Source              #
    #               k2.smub = Bulk                #
    # ------------------------------------------- #
    def take_measurements():
        ## Only measure what we need - Id
        output = float(k1.smub.measure.i())
        k1.wait_opc()
        return output

    # --- Sweep ---
    # Wait for both SMUs to be ready
    k1.wait_opc()
    k2.wait_opc()

    # Starting loop
    outter_loop_st = time.time()
    index_colors = 0
    print('Vs       |Vg       |Vd')
    for vs in vs_values:
        print(f'{vs:.6f}')
        k2.smua.source.levelv = f'{vs:.6f}'
        k2.wait_opc()

        for vg in vg_values:
            print(f'          {vg:.6f}')
            k1.smua.source.levelv = f'{vg:.6f}'
            k1.wait_opc()

            for vd in vd_values:
                inner_loop_st = time.time()

                k1.smub.source.levelv = f'{vd:.6f}'
                k1.wait_opc()

                id_meas = take_measurements()
                results.loc[len(results)] = [vs,vg,vd, id_meas]

                print(f'                    {vd:.6f} - dt: {time.time() - inner_loop_st}')
            
            

    # End Of Sweep
    print(f'Loop finished. Total time: {time.time() - outter_loop_st}')
    k1.wait_opc()
    k2.wait_opc()

    # Turn off Vs and Vd
    k1.smua.source.output = k1.smua.OUTPUT_OFF
    k1.smub.source.output = k1.smub.OUTPUT_OFF
    k2.smua.source.output = k2.smua.OUTPUT_OFF 
    k2.smub.source.output = k2.smub.OUTPUT_OFF 


    # ------------------------------------------------
    # -            Save & Plot Results               -
    # ------------------------------------------------
    # We save the measurement and the plot
    save_data(data = results, name = measurement_reference)
    plt.show()
    

except Exception as ex:
    # We turn all sources off
    k1.smua.source.output = k1.smua.OUTPUT_OFF 
    k1.smub.source.output = k1.smub.OUTPUT_OFF 
    k2.smua.source.output = k2.smua.OUTPUT_OFF 
    k2.smub.source.output = k2.smub.OUTPUT_OFF 

    # Return 
    raise ex