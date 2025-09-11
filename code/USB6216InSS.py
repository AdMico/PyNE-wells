"""
Brought to PyNE-wells v1.2.0 on Thu Sep 11 2025 by APM

@developers: Adam Micolich & Jan Gluschke

This module does the input handling for the USB-6216, which is effectively a pair of analog outputs
and a set of 8 analog inputs. The output handling is done by a separate .py.

APM 19DEC23 -- Renamed as USB6216InSS.py and dedicated as a single channel and single-shot reader option for the USB-6216 device.
This enables us to preserve old usages, e.g., in IV generation, but build in the new 'pair burst' functionality in USB6216InPB.py.
"""

import Instrument
import nidaqmx as nmx

@Instrument.enableOptions
class USB6216InSS(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultInput = "inputLevel"
    defaultOutput = "None"

    def __init__(self, address):
        super(USB6216InSS, self).__init__()
        self.dev = address
        self.type ="USB6216"  #We can check each instrument for its type and react accordingly
        self.name = "USB6216"
        if self.dev == 0:
            self.port = "Dev1/ai0"
        elif self.dev == 1:
            self.port = "Dev1/ai1"
        elif self.dev == 2:
            self.port = "Dev1/ai2"
        elif self.dev == 3:
            self.port = "Dev1/ai3"
        elif self.dev == 4:
            self.port = "Dev1/ai4"
        elif self.dev == 5:
            self.port = "Dev1/ai5"
        elif self.dev == 6:
            self.port = "Dev1/ai6"
        elif self.dev == 7:
            self.port = "Dev1/ai7"
        
    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name
        
    @Instrument.addOptionGetter("inputLevel")  ## This is the old single channel singleshot read routine (preserved)
    def _getInputLevel(self):
        with nmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(self.port)
            tempData = task.read()
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