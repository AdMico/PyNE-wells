"""
Brought to PyNE-wells v2.0.0 on Fri Aug 15 2025 by APM

@developers: Adam Micolich

This module does the input handling for the MCC128, in basic single shot measurement mode.
The output handling is done by a separate .py.
"""

import Instrument
from daqhats import mcc128,HatIDs,AnalogInputMode,AnalogInputRange
from daqhats_utils import select_hat_device

@Instrument.enableOptions
class MCC128InSS(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultInput = "inputLevel"
    defaultOutput = "None"

    def __init__(self, address):
        super(MCC128InSS, self).__init__()
        self.port = address
        self.type ="MCC128"  #We can check each instrument for its type and react accordingly
        self.name = "MCC128"
        self.address=select_hat_device(HatIDs.MCC_128)
        self.hat=mcc128(self.address)
        input_mode = AnalogInputMode.SE
        input_range = AnalogInputRange.BIP_10V
        self.hat.a_in_mode_write(input_mode)
        self.hat.a_in_range_write(input_range)
        
    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name
        
    @Instrument.addOptionGetter("inputLevel")  ## This is the old single channel singleshot read routine (preserved)
    def _getInputLevel(self):
        tempData = self.hat.a_in_read(self.port)
        measInput = float(tempData)/self.scaleFactor        
        return measInput

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