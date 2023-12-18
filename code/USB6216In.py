"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

This module does the input handling for the USB-6216, which is effectively a pair of analog outputs
and a set of 8 analog inputs. The output handling is done by a separate .py. 
"""

import Instrument
import nidaqmx
import nidaqmx as nmx
import numpy as np
import time
from nidaqmx import stream_readers
from nidaqmx.stream_readers import (AnalogSingleChannelReader, AnalogMultiChannelReader)
from nidaqmx.stream_writers import (AnalogSingleChannelWriter, AnalogMultiChannelWriter)

@Instrument.enableOptions
class USB6216In(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultInput = "inputLevel"
    defaultOutput = "None"

    def __init__(self, address):
        super(USB6216In, self).__init__()
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
        
    @Instrument.addOptionGetter("inputLevel")
    def _getInputLevel(self):
        with nmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(self.port)
            tempData = task.read()
        measInput = float(tempData)/self.scaleFactor        
        return measInput

    #@Instrument.addOptionGetter("inputBurst") ## New Routine to get averaged/stdev data point
    #def _getInputLevel(self):
        #nmx.constants.ADCTimingMode(16097)
        #nmx.constants.AcquisitionType(10123)
        #nmx.constance.Coupling(10050)
    #    with nmx.Task() as task:
    #        task.ai_channels.add_ai_voltage_chan(self.port)
    #        tempData = task.read()
    #    measInput = float(tempData) / self.scaleFactor
    #    return measInput

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

class AnalogInStream(nidaqmx.Task):
    def __init__(self, device, channels, nr_samples):
        nidaqmx.Task.__init__(self)
        for ch in channels:
            self.ai_channels.add_ai_voltage_chan("Dev1/ai"+str(ch))
        self.nr_channels = len(channels)
        self.nr_samples = nr_samples
        self.acq_data = np.zeros((self.nr_channels, self.nr_samples), dtype = np.float64)
        self.reader = AnalogMultiChannelReader(self.in_stream)

    def configure_clock(self, sample_rate, device):
        try:
            self.timing.cfg_samp_clk_timing(sample_rate, source='/Dev1/ao/SampleClock',samps_per_chan=self.nr_samples)
        except NameError:
            pass

    def acquire_data(self):
        self.reader.read_many_sample(self.acq_data, number_of_samples_per_channel=self.nr_samples)

class AnalogOutStream(nmx.Task):
    def __init__(self, device, channel, nr_samples):
        nmx.Task.__init__(self)
        self.ao_channels.add_ao_voltage_chan("Dev1/ao"+str(channel))
        self.nr_channels = 1
        self.nr_samples = nr_samples
        self.writer = AnalogSingleChannelWriter(self.out_stream)
        self.write_data = np.zeros(nr_samples)
        self.change_flag = True

    def configure_clock(self, sample_rate):
        self.timing.cfg_samp_clk_timing(sample_rate, samps_per_chan=self.nr_samples)

    def update_data(self, data):
        self.write_data = data
        self.change_flag = True

    def perform_write(self):
        if self.change_flag:
            self.writer.write_many_sample(self.write_data)
            self.change_flag = False
        self.start()

def gaussian(x, mu, sig):
    return 1./(np.sqrt(2.*np.pi)*sig)*np.exp(-np.power((x-mu)/sig, 2.)/2)

if __name__ == "__main__":  # execute only if this script is run, not when it's being imported
    data = np.linspace(0,1,2000)
#    data = gaussian(x, 0.2, 0.01) + gaussian(x,0.8,0.01)
#    data /= data.max()
#    data *= 5

    scan_time = 1e-2
    sample_rate = int(len(data)/scan_time)
    print(f'sample rate = {sample_rate/1e6:.1f} MHz')

    dev = nmx.system.Device(name = 'Dev1')
    ao = AnalogOutStream(dev, 0, len(data))
    ai = AnalogInStream(dev, [0,1], len(data))
    ai.configure_clock(sample_rate, ao.devices[0])
    ao.configure_clock(sample_rate)
    ao.update_data(data)

    nr_loops = 1000
    timing = np.zeros(nr_loops)
    buffer = np.zeros((2, 2000), dtype=np.float64)
    with nidaqmx.Task() as task:
        reader = stream_readers.AnalogMultiChannelReader(task.in_stream)
    for idx in range(nr_loops):
        start = time.time()
        ai.start()
        ao.perform_write()
        #ai.acquire_data()
        reader.read_many_sample(buffer, 2000)
#        output[idx] = np.mean(buffer,axis=0)
        ai.stop()
        ao.stop()
        stop = time.time()
        timing[idx] = stop-start

    print(f'executed in {timing.mean():.2e} +/- {timing.std():.2e} s')
    print(f'output is {output.mean():.2e} +/- {output.std():.2e} V')

    ai.close()
    ao.close()

    ## Old Code for Test
    #with nmx.Task() as task:
    #    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    #    tempData = task.read()
    #measInput = float(tempData)
    #print(measInput)