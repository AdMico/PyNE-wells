"""
Testing uncertainties from different burst lengths

@developers: Adam Micolich, Sam Shelton
"""
import matplotlib.pyplot as plt

from Imports import *
from Pi_control import PiMUX
import GlobalMeasID as ID
from Config import P1Gain, P2Gain, VSource, ItersAR, WaitAR, zeroThres, basePath, SR, SpC
import pandas as pd

##--------------------------------------------------------------------------------------------------------------------
##  Initialisation

debugPrints = True

# Device to run testing on - expand later?
test_device = 14

# Length of Bursts to test in Seconds
burst_min = 0.01
burst_max = 1
datapoints = 5

# Comment out one of these to change linear/log - does not effect graph
#burst_lengths = np.logspace(np.log10(burst_min), np.log10(burst_max), num=datapoints)   # Burst time in S
burst_lengths = np.linspace(burst_min, burst_max, num=datapoints)                      # Burst time in S

burst_volumes = (burst_lengths*SR).astype(int)         # Burst measurements (int)

if debugPrints: print("Configuring Devices...")
#---- Initialisation of instruments - ripped from assay run
CtrlPi = PiMUX()
CtrlPi.setMuxToOutput(0)  # Sets multiplexer to state with all outputs off
daqout_S = USB6216Out(0)
daqout_S.setOptions({"feedBack":"Int","scaleFactor":1})

#---- NIDAQ Input Port for Drain running PairBurst on USB6216 --------------
daqin_Drain = USB6216InPB()
daqin_Drain.setOptions({"scaleFactor":1})


##--------------------------------------------------------------------------------------------------------------------
##  Data Gathering

# Setting DAQ output to config, setting MUX to test device
daqout_S.goTo(VSource, delay=0.0)
CtrlPi.setMuxToOutput(test_device)

# Temporary pandas arrays to avoid annoying pandas indexing
temp1 = np.zeros(datapoints); temp2 = np.zeros(datapoints); temp3 = np.zeros(datapoints)

if debugPrints: print("Taking Measurements...")
for index, vol in enumerate(burst_volumes):

    daqin_Drain.setOptions({"burstVolume":vol}) # Set the Burst Volume
    start = time.time()
    Drain = daqin_Drain.get('inputLevel') # Read Measurement
    end = time.time()

    temp1[index] = Drain[0]; temp2[index] = Drain[1]; temp3[index] = end - start
    time.sleep(0.100)                ## Wait a little before the next loop

Results_Array = pd.DataFrame({'Expected Sample Time (s)':burst_lengths, 'Samples':burst_volumes, \
                              'Resistance (Ohm)':temp1, 'Uncertainty (Ohm)':temp2, 'Measured Sample Time (s)':temp3})

# Turn everything back to Zero
daqout_S.goTo(0.0, delay=0.0)
CtrlPi.setMuxToOutput(0)

if debugPrints: print("Finished Gathering Data")

##--------------------------------------------------------------------------------------------------------------------
##  Data Analysis

print(Results_Array)

fig, ax1 = plt.subplots(1)
ax1.plot(Results_Array['Expected Sample Time (s)'], Results_Array['Uncertainty (Ohm)'], marker='x', linestyle='')

ax2 = ax1.twiny()
ax2.plot(Results_Array['Samples'], Results_Array['Uncertainty (Ohm)'], marker='', linestyle='')
ax2.set_xlabel('Number of Samples per Chanel / $n$')

ax1.set_xlabel('"Ideal" Double Burst Sample Time / $s$')
ax1.set_ylabel('Resistance Uncertainty / $\Omega$')

plt.tight_layout()
plt.show()


