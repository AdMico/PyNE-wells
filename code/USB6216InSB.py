"""
Brought to PyNE-wells v1.2.0 on Thu Aug 07 2025 by APM

@developers: Adam Micolich & Jan Gluschke

This module does the input handling for the USB-6216, which is effectively a pair of analog outputs
and a set of 8 analog inputs. The output handling is done by a separate .py.

APM 19DEC23 -- Renamed as USB6216InSB.py and dedicated as a single channel and burst reader option for the USB-6216 device.
This enables us to preserve old usages, e.g., in IV generation, but build in the new 'burst' functionality for more accurate reads.
Pulls NIDAQ information (e.g., sample rate and samples per channel) from Config.py. The rest works as usual (address = port)

APM 09SEP25 -- This routine gets used exclusively in Gen5, so I've set the config.py calls specifically to Gen5.
If implemented elsewhere, change the calls. To be made more robust in a later version.

APM 16OCT25 -- Edited this routine to look more like USB6216InPB.py for use in AssayRunGen5.py. If it breaks stuff, I might need two SB routines with different naming.
"""

import Instrument
import numpy as np
import pandas as pd
import nidaqmx as nmx
from nidaqmx import constants
from nidaqmx import stream_readers
from Config import Drain_Gen5, SR, SpC

pd.set_option('future.no_silent_downcasting',True) ## Uncomment and run if getting downcasting error, then recomment when fixed.

@Instrument.enableOptions
class USB6216InSB(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultInput = "inputLevel"
    defaultOutput = "None"

    def __init__(self):
        super(USB6216InSB, self).__init__()
        self.type ="USB6216"  #We can check each instrument for its type and react accordingly
        self.name = "USB6216"
        self.burstVolume = SpC  # initialise burstVolume to the Samples per Chanel - Sample rate still fixed!!!!
        self.port = Drain_Gen5

    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name

    @Instrument.addOptionSetter("burstVolume")
    def _setBurstVolume(self, vol):
        self.burstVolume = vol

    @Instrument.addOptionGetter("burstVolume")
    def _getBurstVolume(self):
        return self.burstVolume

    @Instrument.addOptionGetter("inputLevel")  ## This is the new burst read routine but single channel - Updated for Gen 5 APM 16Oct25
    def _getInputLevel(self):
        with nmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(self.port)
            task.timing.cfg_samp_clk_timing(rate=SR, sample_mode=constants.AcquisitionType.CONTINUOUS, samps_per_chan=self.burstVolume)
            reader = stream_readers.AnalogSingleChannelReader(task.in_stream)
            buffer = np.zeros((self.burstVolume), dtype=np.float64)
            reader.read_many_sample(buffer, self.burstVolume, timeout=constants.WAIT_INFINITELY)
            data = buffer.T.astype(np.float64)/self.scaleFactor
#            measInput = data.mean() ## Current version only returns the average, we can add error return later if needed APM 19DEC23 -- Deactivated APM 16Oct25
            D = data[:]
            Dav = D.mean()
            Derr = D.std()
        return [Dav,Derr]

    @Instrument.addOptionGetter("scaleFactor")
    def _getScaleFactor(self):
        return self.scaleFactor
    
    @Instrument.addOptionSetter("scaleFactor")
    def _setScaleFactor(self,scaleFactor):
        self.scaleFactor = scaleFactor

    @Instrument.addOptionGetter("SpC")
    def _getSpC(self):
        return self.SpC

    @Instrument.addOptionSetter("SpC")
    def _setSpC(self, SpC):
        self.SpC = SpC

    def goTo(self,target,stepsize=0.01,delay=0.0):
        pass
            
    def close(self):
        pass