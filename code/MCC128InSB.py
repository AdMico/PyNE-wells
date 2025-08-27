"""
Brought to PyNE-wells v2.0.0 on Fri Aug 15 2025 by APM

@developers: Adam Micolich

This module does the input handling for the MCC128, in single channel burst mode, returning average and standard deviation.
The output handling is done by a separate .py.
"""

import Instrument
from daqhats import mcc128,HatIDs,AnalogInputMode,AnalogInputRange,OptionFlags
from daqhats_utils import select_hat_device,chan_list_to_mask
from Config import SR_Gen6,SpC_Gen6

@Instrument.enableOptions
class MCC128InSB(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultInput = "inputLevel"
    defaultOutput = "None"

    def __init__(self, address):
        super(MCC128InSB, self).__init__()
        self.port = address
        self.type ="MCC128"  #We can check each instrument for its type and react accordingly
        self.name = "MCC128"
        self.address=select_hat_device(HatIDs.MCC_128)
        self.hat=mcc128(self.address)
        input_mode=AnalogInputMode.SE
        input_range=AnalogInputRange.BIP_10V
        self.hat.a_in_mode_write(input_mode)
        self.hat.a_in_range_write(input_range)
        self.hat.a_in_scan_cleanup()
        channels=[self.port]
        self.channel_mask=chan_list_to_mask(channels)
        self.options=OptionFlags.DEFAULT
        
    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name
        
    @Instrument.addOptionGetter("inputLevel")
    def _getInputLevel(self):
        self.hat.a_in_scan_start(self.channel_mask,SpC_Gen6,SR_Gen6,self.options)
        buffer = self.hat.a_in_scan_read_numpy(SpC_Gen6,-1)
        tempData = buffer.data
        Dav = tempData.mean()/self.scaleFactor
        Derr = tempData.std()/self.scaleFactor
        self.hat.a_in_scan_stop()
        self.hat.a_in_scan_cleanup()
        return [Dav,Derr]  # Drops values as an array, that you can strip out as s[0] and s[1]

    @Instrument.addOptionGetter("scaleFactor")
    def _getScaleFactor(self):
        return self.scaleFactor
    
    @Instrument.addOptionSetter("scaleFactor")
    def _setScaleFactor(self,scaleFactor):
        self.scaleFactor = scaleFactor
            
    def goTo(self,target,stepsize=0.01,delay=0.0):
        pass
            
    def close(self):
        pass