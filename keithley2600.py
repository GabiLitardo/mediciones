from pynanolab.instrument.generic import Instrument
import pandas as pd
import numpy as np
from time import sleep

class Buffer:
    '''
    Supported instructions:

        - mybuffer.clear()
        - mybuffer.collectsourcevalues = 1
        - mybuffer.appendmode = 1
        - mybuffer.fillmode = smu.FILL_ONCE / smu.FILL_WINDOW
        - mybuffer.fillcount = 100
        - mybuffer.collecttimestamps = 1
        - mybuffer.timestampresolution = 0.000001

    Documentation available from page 147.

    Note that Buffers should be deleted after they were used. This could be done by deleting the instance with the 'del' keyword.
    '''
    def __init__(self, link: Instrument, name: str):
        self.link = link
        self.name = name

        # Internal values
        self._collectsourcevalues   = '?'
        self._appendmode            = '?'
        self._fillmode              = '?'
        self._fillcount             = '?'
        self._collecttimestamps     = '?'
        self._timestampresolution   = '?'

    def get_methods(self):
        all_methods = dir(Measure)
        return [method for method in all_methods if '__' not in method]
    
    def __str__(self) -> str:
        return self.name
    
    def __del__(self):
        try:
            self.link.write_cmd(f'{self.name} = nil')
            self.link.write_cmd(f'collectgarbage()')
            print(f'"{self.name}" buffer was deleted')
        except Exception as ex:
            raise RuntimeError(f'Error while trying to end program. "{self.name}" should have been destroyed before leaving the program!')

    def create(self, smu: str, size: int):
        self.link.write_cmd(f'{self.name} = {smu}.makebuffer({size})')

    def clear(self):
        self.link.write_cmd(f'{self.name}.clear()')

    def read(self):
        return np.fromstring(self.link.query(f'printbuffer(1,{self.name}.n,{self.name}.readings)'),sep=',')

    @property
    def collectsourcevalues(self):
        return self._collectsourcevalues

    @collectsourcevalues.setter
    def collectsourcevalues(self, value):
        self._collectsourcevalues = value
        self.link.write_cmd(f'{self.name}.collectsourcevalues = {value}')

    @property
    def appendmode(self):
        return self._appendmode

    @appendmode.setter
    def appendmode(self, value):
        self._appendmode = value
        self.link.write_cmd(f'{self.name}.appendmode = {value}')

    @property
    def fillmode(self):
        return self._fillmode

    @fillmode.setter
    def fillmode(self, value):
        self._fillmode = value
        self.link.write_cmd(f'{self.name}.fillmode = {value}')

    @property
    def fillcount(self):
        return self._fillcount

    @fillcount.setter
    def fillcount(self, value):
        self._fillcount = value
        self.link.write_cmd(f'{self.name}.fillcount = {value}')

    @property
    def collecttimestamps(self):
        return self._collecttimestamps

    @collecttimestamps.setter
    def collecttimestamps(self, value):
        self._collecttimestamps = value
        self.link.write_cmd(f'{self.name}.collecttimestamps = {value}')

    @property
    def timestampresolution(self):
        return self._timestampresolution

    @timestampresolution.setter
    def timestampresolution(self, value):
        self._timestampresolution = value
        self.link.write_cmd(f'{self.name}.timestampresolution = {value}')

class NVBuffer:
    # TODO: Heredar de Buffer
    '''
    Supported instructions:

        - smua.nvbuffer1.clear()
        - smua.nvbuffer1.collectsourcevalues = 1
        - smua.nvbuffer1.appendmode = 1

    Documentation available in page 570.
    '''
    def __init__(self, link: Instrument, smu: str, number: int):
        self.link = link
        self.smu = smu

        if number!=1 and number!=2: 
            raise ValueError('NVBuffer number must be either 1 or 2.')
        self.name = smu+'.nvbuffer'+str(number)

        # Internal values
        self._collectsourcevalues   = '?'
        self._appendmode            = '?'

    def get_methods(self):
        all_methods = dir(Measure)
        return [method for method in all_methods if '__' not in method]
    
    def __str__(self) -> str:
        return self.name

    @property
    def collectsourcevalues(self):
        return self._collectsourcevalues

    @collectsourcevalues.setter
    def collectsourcevalues(self, value):
        self._collectsourcevalues = value
        self.link.write_cmd(f'{self.smu}.{self.name}.collectsourcevalues = {value}')

    @property
    def appendmode(self):
        return self._appendmode

    @appendmode.setter
    def appendmode(self, value):
        self._appendmode = value
        self.link.write_cmd(f'{self.smu}.{self.name}.appendmode = {value}')


    def clear(self):
        self.link.write_cmd(f'{self.smu}.{self.name}.clear()')  

class Measure:
    '''
    Supported instructions:
        - smuX.measure.nplc = nplc_value
    
        - smuX.measure.autorangei = smuX.AUTORANGE_ON
        - smuX.measure.autorangev = smuX.AUTORANGE_ON
        - smuX.measure.autorangei = smuX.AUTORANGE_OFF
        - smuX.measure.autorangev = smuX.AUTORANGE_OFF

        - smuX.measure.rangei = rangeval
        - smuX.measure.rangev = rangeval
        
        - reading = smuX.measure.i(buffer)
        - reading = smuX.measure.v(buffer)
        - reading = smuX.measure.r(buffer)
        - reading = smuX.measure.p(buffer)
        - iReading, vReading = smuX.measure.iv(buffer1,buffer2)
    '''
    # TODO: Ver se si se puede sacar el setter y reemplazarlo por el self.autorangei en el __init__

    def __init__(self, link: Instrument, smu: str):
        self.link = link
        self.smu = smu

        # Internal values
        self._autorangei    = '?'
        self._autorangev    = '?'
        self._rangei        = '?'
        self._rangev        = '?'
        self._nplc          = '?'


    def get_methods(self):
        all_methods = dir(Measure)
        return [method for method in all_methods if '__' not in method]

    @property
    def nplc(self):
        return self._nplc

    @nplc.setter
    def nplc(self, value):
        self._nplc = value
        self.link.write_cmd(f'{self.smu}.measure.nplc = {value}')

    @property
    def autorangei(self):
        return self._autorangei

    @autorangei.setter
    def autorangei(self, value):
        self._autorangei = value
        self.link.write_cmd(f'{self.smu}.measure.autorangei = {self.smu}.{value}')

    @property
    def autorangev(self):
        return self._autorangev

    @autorangev.setter
    def autorangev(self, value):
        self._autorangev = value
        self.link.write_cmd(f'{self.smu}.measure.autorangev = {self.smu}.{value}')

    @property
    def rangei(self):
        return self._rangei

    @rangei.setter
    def rangei(self, value):
        self._rangei = value
        self.link.write_cmd(f'{self.smu}.measure.rangei = {value}')

    @property
    def rangev(self):
        return self._rangev

    @rangev.setter
    def rangev(self, value):
        self._rangev = value
        self.link.write_cmd(f'{self.smu}.measure.rangev = {value}')

    def i(self, buffer=None):
        if buffer:
            self.link.write_cmd(f'{self.smu}.measure.i({buffer})')
        else:
            return self.link.query(f'print({self.smu}.measure.i())')
        
    def v(self, buffer=None):
        if buffer:
            self.link.write_cmd(f'{self.smu}.measure.v({buffer})')
        else:
            return self.link.query(f'print({self.smu}.measure.v())')
        
    def r(self, buffer=None):
        if buffer:
            self.link.write_cmd(f'{self.smu}.measure.r({buffer})')
        else:
            return self.link.query(f'print({self.smu}.measure.r())')
        
    def p(self, buffer=None):
        if buffer:
            self.link.write_cmd(f'{self.smu}.measure.p({buffer})')
        else:
            return self.link.query(f'print({self.smu}.measure.p())')
    
    def iv(self, buffer1=None, buffer2=None):
        if (buffer1 and not buffer2) or (buffer2 and not buffer1): raise ValueError('measure.iv() expects either both buffers or none.')
        if buffer1 and buffer2:
            self.link.write_cmd(f'{self.smu}.measure.iv({buffer1}, {buffer2})')
        else:
            return self.link.query(f'print({self.smu}.measure.iv())')

class Source:
    '''
    Supported instructions:

        - smuX.source.autorangei = smuX.AUTORANGE_ON
        - smuX.source.autorangev = smuX.AUTORANGE_ON
        - smuX.source.autorangei = smuX.AUTORANGE_OFF
        - smuX.source.autorangev = smuX.AUTORANGE_OFF

        - smuX.source.rangei = rangeval
        - smuX.source.rangev = rangeval

        - smuX.source.func = smuX.OUTPUT_DCVOLTS
        - smuX.source.func = smuX.OUTPUT_DCAMPS

        - smuX.source.leveli = sourceval
        - smuX.source.levelv = sourceval

        - smuX.source.limiti = level
        - smuX.source.limitv = level
        - smuX.source.limitp = level

        - smuX.source.output = smuX.OUTPUT_ON
        - smuX.source.output = smuX.OUTPUT_OFF

        - smuX.source.offmode = smuX.OUTPUT_NORMAL
        - smuX.source.offmode = smuX.OUTPUT_HIGH_Z
        - smuX.source.offmode = smuX.OUTPUT_ZERO

    '''


    def __init__(self, link: Instrument, smu: str):
        self.link = link
        self.smu = smu

        # Internal values
        self._autorangei    = '?'
        self._autorangev    = '?'
        self._rangei        = '?'
        self._rangev        = '?'
        self._func          = '?'
        self._leveli        = '?'
        self._levelv        = '?'
        self._limiti        = '?'
        self._limitv        = '?'
        self._limitp        = '?'
        self._output        = '?'
        self._offmode       = '?'

    def get_methods(self):
        all_methods = dir(Source)
        return [method for method in all_methods if '__' not in method]


    @property
    def autorangei(self):
        return self._autorangei

    @autorangei.setter
    def autorangei(self, value):
        self._autorangei = value
        self.link.write_cmd(f'{self.smu}.source.autorangei = {self.smu}.{value}')

    @property
    def autorangev(self):
        return self._autorangev

    @autorangev.setter
    def autorangev(self, value):
        self._autorangev = value
        self.link.write_cmd(f'{self.smu}.source.autorangev = {self.smu}.{value}')

    @property
    def rangei(self):
        return self._rangei

    @rangei.setter
    def rangei(self, value):
        self._rangei = value
        self.link.write_cmd(f'{self.smu}.source.rangei = {value}')

    @property
    def rangev(self):
        return self._rangev

    @rangev.setter
    def rangev(self, value):
        self._rangev = value
        self.link.write_cmd(f'{self.smu}.source.rangev = {value}')

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, value):
        self._func = value
        self.link.write_cmd(f'{self.smu}.source.func = {self.smu}.{value}')

    @property
    def leveli(self):
        return self._leveli

    @leveli.setter
    def leveli(self, value):
        self._leveli = value
        self.link.write_cmd(f'{self.smu}.source.leveli = {value}')

    @property
    def levelv(self):
        return self._levelv

    @levelv.setter
    def levelv(self, value):
        self._levelv = value
        self.link.write_cmd(f'{self.smu}.source.levelv = {value}')

    @property
    def limiti(self):
        return self._limiti

    @limiti.setter
    def limiti(self, value):
        self._limiti = value
        self.link.write_cmd(f'{self.smu}.source.limiti = {value}')

    @property
    def limitv(self):
        return self._limitv

    @limitv.setter
    def limitv(self, value):
        self._limitv = value
        self.link.write_cmd(f'{self.smu}.source.limitv = {value}')

    @property
    def limitp(self):
        return self._limitp

    @limitp.setter
    def limitp(self, value):
        self._limitp = value
        self.link.write_cmd(f'{self.smu}.source.limitp = {value}')

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        self._output = value
        self.link.write_cmd(f'{self.smu}.source.output = {self.smu}.{value}')

    @property
    def offmode(self):
        return self._offmode

    @offmode.setter
    def offmode(self, value):
        self._offmode = value
        self.link.write_cmd(f'{self.smu}.source.offmode = {self.smu}.{value}')

class SMU:
    # -------- Constants --------
    # measure
    AUTORANGE_ON    = 'AUTORANGE_ON'
    AUTORANGE_OFF   = 'AUTORANGE_OFF'

    # source
    OUTPUT_DCVOLTS  = 'OUTPUT_DCVOLTS'
    OUTPUT_DCAMPS   = 'OUTPUT_DCAMPS'
    OUTPUT_ON       = 'OUTPUT_ON'
    OUTPUT_OFF      = 'OUTPUT_OFF'
    OUTPUT_NORMAL   = 'OUTPUT_NORMAL'
    OUTPUT_HIGH_Z   = 'OUTPUT_HIGH_Z'
    OUTPUT_ZERO     = 'OUTPUT_ZERO'

    # sense
    SENSE_LOCAL     = 'SENSE_LOCAL'
    SENSE_REMOTE    = 'SENSE_REMOTE'

    ## Buffers
    FILL_ONCE       = 0
    FILL_WINDOW     = 0

    # -------- -------- --------

    def __init__(self, link: Instrument, letter : str):
        self.link = link

        if letter != 'a' and letter != 'b': 
            raise ValueError('letter must be either "a" or "b".')
        self.smu = 'smu'+letter


        # Public elements
        self.measure = Measure(self.link, self.smu)
        self.source = Source(self.link, self.smu)

        self.nvbuffer1 = NVBuffer(self.link, self.smu, number = 1)
        self.nvbuffer2 = NVBuffer(self.link, self.smu, number = 2)

        # "Private" elements
        self._sense = '?'


    def reset(self):
        self.link.write_cmd(f'{self.smu}.reset()')


    @property
    def sense(self):
        return self._sense

    @sense.setter
    def sense(self, value):
        '''
        smuX.sense = smuX.SENSE_LOCAL
        smuX.sense = smuX.SENSE_REMOTE
        '''
        self.link.write_cmd(f'{self.smu}.sense = {self.smu}.{value}')


    def configure_simple_voltage_source(self, levelv, limiti = None, rangev = None, offmode = None):
        '''
        Configura el SMU.source como una fuente de tensión simple. 

        @param levelv: int.         Nivel de tensión de la fuente.

        @param limiti: int.         Corriente máxima por la fuente.

        @param rangev: int.         Rango en el cual se configura la fuente. Si no se pasa, se asume AUTORANGE (recomendado).

        @param offmode: str.        Valor por default en modo OUTPUT_OFF. Ver página 100 del manual - 'Output-off states'.
                                    Si no se ingresa nada no se modificará el parámetro. Por default se encuentra en smu.OUTPUT_NORMAL.
                                    Los valores posibles son: {smu.OUTPUT_NORMAL, smu.OUTPUT_ZERO, smu.OUTPUT_HIGH_Z}
        
        Return: None.
        '''
        self.source.func         = self.OUTPUT_DCVOLTS
        self.source.levelv       = levelv

        if limiti:
            self.source.limiti   = limiti

        if rangev:
            self.source.rangev = rangev
        else:
            self.source.autorangev = self.AUTORANGE_ON

        if offmode:
            self.source.offmode  = offmode
            
            
    def configure_simple_current_source(self, leveli, limitv = None, rangei = None, offmode = None):
        '''
        Configura el SMU.source como una fuente de corriente simple. 

        @param leveli: int.         Nivel de corriente de la fuente.

        @param limitv: int.         Tensión máxima por la fuente.

        @param rangei: int.         Rango en el cual se configura la fuente. Si no se pasa, se asume AUTORANGE (recomendado).

        @param offmode: str.        Valor por default en modo OUTPUT_OFF. Ver página 100 del manual - 'Output-off states'.
                                    Si no se ingresa nada no se modificará el parámetro. Por default se encuentra en smu.OUTPUT_NORMAL.
                                    Los valores posibles son: {smu.OUTPUT_NORMAL, smu.OUTPUT_ZERO, smu.OUTPUT_HIGH_Z}
        
        Return: None.
        '''
        self.source.func         = self.OUTPUT_DCAMPS
        self.source.leveli       = leveli

        if limitv:
            self.source.limitv   = limitv

        if rangei:
            self.source.rangei = rangei
        else:
            self.source.autorangei = self.AUTORANGE_ON

        if offmode:
            self.source.offmode  = offmode

    def configure_simple_amperimeter(self, rangei = None, nplc = None):
        '''
        Configura el SMU.measure como un amperímetro simple.

        @param rangei: int.         Rango en el cual se configura el amperímetro. Si no se pasa, se asume AUTORANGE (recomendado).

        @param nplc: int.           Ventana de integración para la medición.
        
        Return: None.
        '''
        if rangei:
            self.measure.rangei = rangei
        else:
            self.measure.autorangei = self.AUTORANGE_ON

        if nplc:
            self.measure.nplc = nplc
        else:
            self.measure.nplc = 5 #100ms con plc=50
        
    def configure_simple_voltimeter(self, rangev = None, nplc = None):
        '''
        Configura el SMU.measure como un voltímetro simple.

        @param rangev: int.         Rango en el cual se configura el voltímetro. Si no se pasa, se asume AUTORANGE (recomendado).

        @param nplc: int.           Ventana de integración para la medición.
        
        Return: None.
        '''
        if rangev:
            self.measure.rangev = rangev
        else:
            self.measure.autorangev = self.AUTORANGE_ON

        if nplc:
            self.measure.nplc = nplc
        else:
            self.measure.nplc = 5 #100ms con plc=50

    
    def create_buffer(
        self,
        name: str,
        size: int,
        collectsourcevalues: int = None,
        appendmode: int = None,
        fillmode: str = None,
        fillcount: int = None,
        collecttimestamps: int = None,
        timestampresolution: float = None):
        '''
        Crea un buffer dinámico. Se le pueden asignar algunos parámetros para su configuración. 
        Los parámetros estan descriptos en la página 147 del manual.

        @param name: str.                   Nombre del buffer.

        @param size: int.                   Tamaño del buffer.

        @param collectsourcevalues: int.    Configura si el buffer va a almacenar las mediciones de la fuente o no. Por default es False.

        @param appendmode: int.             Configura el modo append. Por default es False.

        @param fillmode: str.               Configura el fillmode. Por default es FILL_ONCE.

        @param fillcount: int.              Configura la cantidad de muestras antes de reiniciar el index, cuando fillmode = FILL_WINDOW.

        @param collecttimestamps: int.      Configura si el buffer va a almacenar los timestamp de las mediciones o no. Por default es 1us.

        @param timestampresolution: float.  Resolución utilizada por los timestamp. Por default es 1us.


        
        Return: Devuelve un Buffer donde ya se han configurado todos los parámetros especificados.
        '''
        buf = Buffer(self.link, name)
        buf.create(self.smu, size)
        buf.clear()

        if collectsourcevalues:
            buf.collectsourcevalues = collectsourcevalues

        if appendmode:
            buf.appendmode = appendmode

        if fillmode:
            buf.fillmode = fillmode

        if fillcount:
            if fillmode == self.FILL_WINDOW:
                buf.fillcount = fillcount
            else:
                del buf
                raise ValueError('Buffer fillcount attribute should only be used when fillmode=FILL_WINDOW. See user manual, page 363.')

        if collecttimestamps:
            buf.collecttimestamps = collecttimestamps

        if timestampresolution:
            buf.timestampresolution = timestampresolution

        return buf

    def source_zerov(self):
        self.source.func        = self.OUTPUT_DCVOLTS
        self.source.levelv      = 0
        self.source.offmode     = self.OUTPUT_NORMAL
        self.source.output      = self.OUTPUT_ON

class Keithley2600(Instrument):
    '''
    Keithley2600

    TODO: Mejorar la documentación de las clases. Ver qué formato queremos utilizar para la documentación inline.
    '''
    def __init__(self, address = None, name = None, backend='/usr/lib/x86_64-linux-gnu/libivivisa.so.7.0.0'):
        super().__init__(backend=backend)
        self.set_name(name)
        self.selected_device = None

        if address:
            try:
                self.connect(address)
            except Exception as ex:
                print('An error ocurred while trying to connect to the specified address.')
                print(ex)
            

            current_id = self.get_id()
            if 'Keithley' in current_id:
                self.selected_device = {
                    'addr' : address,
                    'id': current_id
                }
            else:
                raise RuntimeError('The selected address does not corresponds to a Keithley2600 intrument.')
            
        else:
            print('Scanning..')
            available_smus = self._scan()
            if len(available_smus) > 1:
                print(f'More than one Keithley was founded:\n {available_smus}')
                index = int(input('Select the one you want by the index (starting from 0):'))
            elif len(available_smus) == 0:
                raise RuntimeError('There are not devices available!')
            else: 
                index = 0
            
            self.selected_device = available_smus[index]
            self._reconnect()   # NOTE: selected_device should've been set before this step.

        print(f'Connected to: { self.selected_device["id"] }\n')
        self.smua = SMU(link=self, letter='a')
        self.smub = SMU(link=self, letter='b')

    def _reconnect(self):
        '''
        Intenta conectarse con el address almacenado en self.selected_device.
        '''
        try:
            self.connect(self.selected_device['addr'])
        except Exception as ex:
            print(ex)
            raise IOError('An error ocurred while trying to connect to the device.')
            
    def _scan(self):
        '''
        Busca automáticamente dispositivos Keithley2600.

        Devuelve una lista de diccionarios con los address y los id de cada dispositivo.
        '''
        dvs = self._get_available_devices()
        output_list = []
        for device_addr in dvs:
            try:
                self.connect(device_addr)
                current_id = self.get_id()

                if '2636B' in current_id: # Checks for Keithley model on ID

                    output_list.append(
                        {
                            'addr' : device_addr,
                            'id': current_id
                        }
                    )
                self.disconnect()

            except Exception as ex:
                pass    # NOTE: When the connection was not successful, we just ignore the error.

        return output_list

    def delay(self, time):
        self.write_cmd(f'delay({time})')
        sleep(time)

    def wait_opc(self):
        '''
        When *OPC is sent, the OPC bit in the Standard Event Register (see Status model (on page 5-15, on
        page E-1)) is set when all overlapped commands complete. The *OPC? command places an ASCII
        "1" in the output queue when all previous overlapped commands complete.
        '''
        self.query('*OPC?')

    def load_tsp(self, file, name='test'):
        '''
        Load a TSP script into the Instrument memory. 

        @param file: str.         Filepath to .lua script.

        @param name: str.         Script name. Default: 'test'
        
        Return: None.
        '''
        
        self.write_cmd(f'loadscript {name}')
        
        try:
            for line in open(file, mode='r'):
                self.write_cmd(line)
        except FileNotFoundError:
            print('ERROR: Could not find tsp script. Check path.')
            raise SystemExit
    
        self.write_cmd('endscript')
        print('----------------------------------------')
        print(f'Uploaded TSP script: {file} - Script Name: {name}')

    def runTSP(self, name='test'):
        '''
        Run a previously loaded TSP script. See Run Scripts (on page 6-5, on page 282))

        @param name: str.         Script name. Default: 'test'
        
        Return: None.
        '''

        self.write_cmd(f'{name}.run()')
        print('Measurement in progress...')

    def config_display_amperimeter(self):
        self.write_cmd('display.screen = display.SMUA_SMUB')
        self.write_cmd('display.smua.measure.func = display.MEASURE_DCAMPS')
        self.write_cmd('display.smub.measure.func = display.MEASURE_DCAMPS')

    def simple_i_measurement(self, smu: SMU, levelv, limiti, rangei = None, force_zeroV = False):
        '''
        Establece una comunicacion con el dispositivo para solicitar una medicion de corriente, inyectando tensión. 

        @param smu: SMU.    Canal del SMU en el que se realizará la medición.

        @param levelv: int. Nivel de tensión a utilizar para realizar la medición.

        @param limiti: int. Corriente máxima admitida para realizar la medición.

        @param rangei: int. Rango en el cual se espera encontrar la medición de corriente. Si no se pasa, se asume AUTORANGE.

        @param force_zeroV: bool.   Si TRUE se fuerza una tensión de 0V en lugar de apagar el output.


        Return: Devuelve un float con la medición de corriente.
        '''

        smu.reset()

        # Measure configuration
        smu.configure_simple_amperimeter(
            rangei  = rangei,
        )

        # Source configuration
        smu.configure_simple_voltage_source(
            levelv  = levelv,
            limiti  = limiti,
            rangev  = None,     # Utilizamos el autorange del source.
            offmode = smu.OUTPUT_ZERO if force_zeroV else smu.OUTPUT_NORMAL
        )

        # Running measurement
        smu.source.output = smu.OUTPUT_ON
        output = smu.measure.i()

        # Setting output off
        smu.source.output = smu.OUTPUT_OFF

        return output

    def single_smu_sweep(self, smu: SMU, v_values, limiti, rangei = None, force_zeroV = False):
        '''
        Realiza un barrido de tensión en un canal del Keithley. Se barre tensión y se mide corriente. 

        @param smu: SMU.            Canal del SMU en el que se realizará la medición.

        @param v_values: list.      Lista de valores de tensión para realizar el barrido.

        @param limiti: int.         Corriente máxima admitida para realizar la medición.

        @param rangei: int.         Rango en el cual se espera encontrar la medición de corriente. Si no se pasa, se asume AUTORANGE.

        @param force_zeroV: bool.   Si TRUE se fuerza una tensión de 0V en lugar de apagar el output.

        
        Return: Devuelve un pandas.DataFrame con las columnas ['v','i'].
        '''

        # Restore Series 2600B defaults.
        smu.reset()

        # nvBuffer configs
        smu.nvbuffer1.clear()
        smu.nvbuffer1.collectsourcevalues = 1
        smu.nvbuffer1.appendmode = 1

        # Measure configuration
        smu.configure_simple_amperimeter(
            rangei  = rangei,
        )

        # Source configuration
        smu.configure_simple_voltage_source(
            levelv  = 0,        # We don't want to set any particular voltage level yet.
            limiti  = limiti,
            rangev  = None,     # We use the autorange feature of the smu.source.
            offmode = smu.OUTPUT_ZERO if force_zeroV else smu.OUTPUT_NORMAL
        )
        
        # Setting output off
        smu.source.output = smu.OUTPUT_OFF

        # Generating output dataframe
        output = pd.DataFrame(columns=['v','i'])

        # Running sweep
        for v in v_values:
            # Set source
            smu.source.levelv = f'{v:.2f}'
            smu.source.output = smu.OUTPUT_ON
            # Wait for transient response
            self.delay(0.01)
            # Read measurement
            i_meas = float(smu.measure.i(smu.nvbuffer1))
            # Save values
            output.loc[len(output)] = [v,i_meas]

        # Setting output off
        smu.source.output = smu.OUTPUT_OFF

        # Exiting
        return output

    def double_smu_sweep(
        self,
        primary_smu: SMU,
        secondary_smu: SMU,
        v_values,
        limiti,
        rangei = None,
        force_zeroV = False):
        '''
        Realiza un doble barrido. El SMU primario genera el barrido más lento. Por ejemplo, para una curva de salida
        el SMU primario sería el correspondiente a la Vgs. Se toman mediciones de ambas corrientes por cada punto. 

        @param primary_smu: SMU.    Canal para realizar el barrido externo (Vgs).

        @param secondary_smu: SMU.  Canal para realizar el barrido interno (Vds).

        @param v_values: list.      Lista con dos listas de valores de tensión para realizar el barrido. El primer elemento es la lista para el smu primario.

        @param limiti: int.         Lista con dos corrientes máximas admitidas para realizar la medición. El primer elemento es la lista para el smu primario.

        @param rangei: int.         Lista con dos rangos de corriente. Si no se pasa, se asume AUTORANGE. El primer elemento es la lista para el smu primario.

        @param force_zeroV: bool.   Si TRUE se fuerza una tensión de 0V en lugar de apagar el output.

        
        Return: Devuelve un pandas.DataFrame con las columnas ['v1','i1','v2','i2'].
        '''
        # We check the inputs
        if not (isinstance(v_values, list) and len(v_values)==2): raise ValueError('v_values should be a list of 2 elements. Each element has to be a list with voltage values for the sweep.')
        if not (isinstance(limiti, list) and len(limiti)==2): raise ValueError('limiti should be a list of 2 elements. Each element has to be the max. current admited.')
        if rangei:
            if not (isinstance(rangei, list) and len(rangei)==2): raise ValueError('rangei should be a list of 2 elements. Each element has to be the range for the current measurement.')
        else:
            rangei = [None, None]   # FIXME: Find a better way to do the same.

        # Restore Series 2600B defaults.
        primary_smu.reset()
        secondary_smu.reset()

        # nvBuffer configs
        primary_smu.nvbuffer1.clear()
        primary_smu.nvbuffer1.collectsourcevalues = 1
        primary_smu.nvbuffer1.appendmode = 1
        secondary_smu.nvbuffer1.clear()
        secondary_smu.nvbuffer1.collectsourcevalues = 1
        secondary_smu.nvbuffer1.appendmode = 1

        # Measure configuration
        primary_smu.configure_simple_amperimeter(
            rangei  = rangei[0],
        )
        secondary_smu.configure_simple_amperimeter(
            rangei  = rangei[1],
        )

        # Source configuration
        primary_smu.configure_simple_voltage_source(
            levelv  = 0,        # We don't want to set any particular voltage level yet.
            limiti  = limiti[0],
            rangev  = None,     # We use the autorange feature of the smu.source.
            offmode = primary_smu.OUTPUT_ZERO if force_zeroV else primary_smu.OUTPUT_NORMAL
        )
        secondary_smu.configure_simple_voltage_source(
            levelv  = 0,        # We don't want to set any particular voltage level yet.
            limiti  = limiti[1],
            rangev  = None,     # We use the autorange feature of the smu.source.
            offmode = secondary_smu.OUTPUT_ZERO if force_zeroV else secondary_smu.OUTPUT_NORMAL
        )
        
        # Setting output off
        primary_smu.source.output = primary_smu.OUTPUT_OFF
        secondary_smu.source.output = secondary_smu.OUTPUT_OFF

        # Generating output dataframe
        output = pd.DataFrame(columns=['v1','i1','v2','i2'])

        # Running sweep
        for v1 in v_values[0]:
            # Set primary_smu source
            primary_smu.source.levelv = f'{v1:.2f}'
            primary_smu.source.output = primary_smu.OUTPUT_ON
            for v2 in v_values[1]:
                # Set secondary_smu source
                secondary_smu.source.levelv = f'{v2:.2f}'
                secondary_smu.source.output = secondary_smu.OUTPUT_ON

                # Wait for transient response
                # self.delay(0.01)
                
                # Read measurements
                i1 = float(primary_smu.measure.i(primary_smu.nvbuffer1))
                i2 = float(secondary_smu.measure.i(secondary_smu.nvbuffer1))
                # Save values
                output.loc[len(output)] = [v1,i1,v2,i2]

        # Setting output off
        primary_smu.source.output = primary_smu.OUTPUT_OFF
        secondary_smu.source.output = secondary_smu.OUTPUT_OFF

        # Exiting
        return output
