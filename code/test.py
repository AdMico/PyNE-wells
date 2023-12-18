"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

For debugging hardware setup
"""

from Pi_control import PiMUX
from Imports import *
import pandas as pd
import numpy as np
import nidaqmx
import nidaqmx as nmx
from nidaqmx import constants
from nidaqmx import stream_readers
from nidaqmx import stream_writers

print ('Initialise instruments')
#---- Raspberry Pi --------------
CtrlPi = PiMUX()
CtrlPi.setMuxToOutput(0) # Sets multiplexer to state with all outputs off

#---- NIDAQ Output Port for Source --------------
daqout_S = USB6216Out(0)
daqout_S.setOptions({
    "feedBack":"Int",
    "extPort":6, # Can be any number 0-7 if in 'Int'
    "scaleFactor":1
})

#---- NIDAQ Input Port for Drain-Left --------------
daqin_DL = USB6216In(0)
daqin_DL.setOptions({"scaleFactor":1})

#---- NIDAQ Input Port for Drain-Right --------------
daqin_DR = USB6216In(1)
daqin_DR.setOptions({"scaleFactor":1})

print('MUX to a given row')
CtrlPi.setMuxToOutput(2)

print('Set NIDAQ Voltage')
daqout_S.goTo(0.5,delay=0.0)

print ('Do a DAQ Read -- standard')
n = 10
s = pd.Series()
for i in range(n):
    s[i] = daqin_DL.get('inputLevel')
    print('Run',i,s[i])
print('Average',s.mean())
print('StDev',s.std())

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan(physical_channel='Dev1/ai0', min_val=-10, max_val=10)
    task.ai_channels.add_ai_voltage_chan(physical_channel='Dev1/ai1', min_val=-10, max_val=10)
    task.timing.cfg_samp_clk_timing(rate=1e5, sample_mode=constants.AcquisitionType.CONTINUOUS, samps_per_chan=2000)
    samples_per_buffer = 2000
    reader = stream_readers.AnalogMultiChannelReader(task.in_stream)
    writer = stream_writers.AnalogMultiChannelWriter(task.out_stream)
    buffer = np.zeros((2, 2000), dtype=np.float64)
    reader.read_many_sample(buffer, 2000, timeout=constants.WAIT_INFINITELY)
    data = buffer.T.astype(np.float64)
    print(data)
    #def reading_task_callback(task_idx, event_type, num_samples, callback_data=None):
     #   buffer = np.zeros((num_channels, num_samples), dtype=np.float32)
      #  reader.read_many_sample(buffer, num_samples, timeout=constants.WAIT_INFINITELY)
       # data = buffer.T.astype(np.float32)
        #return 0

#task.register_every_n_samples_acquired_into_buffer_event(samples_per_buffer, reading_task_callback)