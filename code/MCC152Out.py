"""
Brought to PyNE-wells v2.0.0 on Fri Aug 15 2025 by APM

@developer: Adam Micolich

This module does the output voltage handling for the Pi-HAT MCC152, which has a pair of analog outputs.
The input handling is done by a separate .py. Unlike the USB-6216, there is no voltage feedback.
Accuracy relies on having a very good ground reference to the Raspberry Pi ground.
"""

import Instrument
from daqhats import mcc152,HatIDs
from daqhats_utils import select_hat_device
import time
import numpy as np

@Instrument.enableOptions
class MCC152Out(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultInput = "outputLevel"
    defaultOutput = "outputLevel"

    def __init__(self, address):
        super(MCC152Out, self).__init__()
        self.port = address
        self.type ="MCC152"  #We can check each instrument for its type and react accordingly
        self.name = "MCC152"
        self.address = select_hat_device(HatIDs.MCC_152)
        self.hat = mcc152(self.address)
        self.hat.a_out_write(self.port, 0.0) # Initialises voltage to zero if it's not -- consider improved set-up in full Gen 6 dev APM 15AUG25
        self.currentOutput = 0.0 # Possibly make a read from MCC128 at init in future -- consider at full Gen 6 dev APM 15AUG25
        
    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name

    @Instrument.addOptionSetter("outputLevel")
    def _setOutputLevel(self,outputLevel):
        if (5.0 >= outputLevel and outputLevel >= 0.0):
            self.output = outputLevel
            self.currentOutput = self.output
            self.hat.a_out_write(self.port,outputLevel)
        else:
            raise ValueError("Output outside 0-5V range available".format(outputLevel))
                
    @Instrument.addOptionGetter("outputLevel")
    def _getOutputLevel(self):
        pass

    @Instrument.addOptionGetter("scaleFactor")
    def _getScaleFactor(self):
        return self.scaleFactor
    
    @Instrument.addOptionSetter("scaleFactor")
    def _setScaleFactor(self,scaleFactor):
        self.scaleFactor = scaleFactor
            
    def goTo(self,target,stepsize = 0.01,delay = 0.0): # Modified from usual as APM likes linspace better
        count = int(abs(target-self.currentOutput)/stepsize) + 1
        sweepArray = np.linspace(self.currentOutput,target,count,endpoint=True)
        if count < 3: #Option to avoid pointless sweeps, if you're close enough, just go direct
            self.hat.a_out_write(self.port,target)
        else:
            for point in sweepArray:
                self.hat.a_out_write(self.port,point)
                time.sleep(delay)
            self.hat.a_out_write(self.port,target)
            self.currentOutput = target
            
    def close(self):
        self.goTo(0.0, stepsize=0.01, delay=0.01)