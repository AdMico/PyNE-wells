"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

This module does the input handling for the USB-6216, which is effectively a pair of analog outputs
and a set of 8 analog inputs. The output handling is done by a separate .py.

APM 19DEC23 -- This is a new instrument functionality that enables hardware-buffered read from the USB-6216 for a pair of analog inputs.
The two buffers are averaged to return the value & error in a much faster way (by factor of 2000) than the single-shot routine.
Instrument will pull information from config.py
"""

import Instrument
import numpy as np
import pandas as pd
import nidaqmx
import nidaqmx as nmx
from nidaqmx import constants
from nidaqmx import stream_readers
from nidaqmx import stream_writers
from Config import DrainLeft, DrainRight, SR, SpC

pd.set_option('future.no_silent_downcasting',True)

@Instrument.enableOptions
class USB6216InPB(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultInput = "inputLevel"
    defaultOutput = "None"

    def __init__(self):
        super(USB6216InPB, self).__init__()
        self.type ="USB6216"  #We can check each instrument for its type and react accordingly
        self.name = "USB6216"
        self.port1 = DrainLeft
        self.port2 = DrainRight
        
    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name

    @Instrument.addOptionGetter("inputLevel") ## New routine to get averaged/stdev data for two channels
    def _getInputLevel(self):
        with nmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(self.port1)
            task.ai_channels.add_ai_voltage_chan(self.port2)
            task.timing.cfg_samp_clk_timing(rate=SR, sample_mode=constants.AcquisitionType.CONTINUOUS, samps_per_chan=SpC)
            reader = stream_readers.AnalogMultiChannelReader(task.in_stream)
            buffer = np.zeros((2, SpC), dtype = np.float64)
            reader.read_many_sample(buffer, SpC, timeout=constants.WAIT_INFINITELY)
            data = buffer.T.astype(np.float64)/self.scaleFactor
            DL, DR = data[:,0], data[:,1]
            DLav = DL.mean()
            DLerr = DL.std()
            DRav = DR.mean()
            DRerr = DR.std()
        return [DLav, DLerr, DRav, DRerr] # Drops values as an array, that you can strip out as s[0], s[1], s[2] and s[3]

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