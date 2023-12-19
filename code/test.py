"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

For debugging hardware setup
"""

from Pi_control import PiMUX
from Imports import *

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

#---- NIDAQ Input Port for Drain --------------
daqin_Drain = USB6216InPB()
daqin_Drain.setOptions({"scaleFactor":1})

print('MUX to a given row')
CtrlPi.setMuxToOutput(5)

print('Set NIDAQ Voltage')
daqout_S.goTo(0.5,delay=0.0)

print ('Do a DAQ Read -- pairburst')
start=time.time()
Drain=daqin_Drain.get('inputLevel')
print(Drain)
print('Average DL = ',Drain[0], 'StDev = ', Drain[1])
print('Average DR = ',Drain[2], 'StDev = ', Drain[3])
stop=time.time()
print('Time elapsed = ',stop-start, ' s')

### Old Test Code APM 19DEC23

#print ('Do a DAQ Read -- standard')
#n = 200
#s1 = pd.Series()
#s2 = pd.Series()
#timing = np.zeros(n)
#start_a = time.time()
#for i in range(n):
#    start = time.time()
#    s1[i] = daqin_DL.get('inputLevel')
#    s2[i] = daqin_DR.get('inputLevel')
#    print('Run',i,s[i])
#    stop = time.time()
#    timing[i] = stop-start
#print('Average DL = ',s1.mean(), 'StDev = ', s1.std())
#print('Average DR = ',s2.mean(), 'StDev = ', s2.std())
#end_a = time.time()
#print(f'executed in {timing.mean():.2e} +/- {timing.std():.2e} s per step')
#print('All 200 took: ', (end_a-start_a), 's total')

#with nidaqmx.Task() as task:
#    start = time.time()
#    task.ai_channels.add_ai_voltage_chan(physical_channel='Dev1/ai0', min_val=-10, max_val=10)
#    task.ai_channels.add_ai_voltage_chan(physical_channel='Dev1/ai1', min_val=-10, max_val=10)
#    task.timing.cfg_samp_clk_timing(rate=2e5, sample_mode=constants.AcquisitionType.CONTINUOUS, samps_per_chan=200000)
#    #samples_per_buffer = 200000
#    reader = stream_readers.AnalogMultiChannelReader(task.in_stream)
#    #writer = stream_writers.AnalogMultiChannelWriter(task.out_stream)
#    buffer = np.zeros((2, 200000), dtype=np.float64)
#    reader.read_many_sample(buffer, 200000, timeout=constants.WAIT_INFINITELY)
#    data = buffer.T.astype(np.float64)
#    data1,data2 = data[:,0], data[:,1]
#    print('Average DL =', data1.mean(), 'Error = ', data1.std())
#    print('Average DR =', data2.mean(), 'Error = ', data2.std())
#    stop = time.time()
#    print(f'all 200000 executed in {(stop-start):.2e} s')