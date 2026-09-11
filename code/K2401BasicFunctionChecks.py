"""
Brought to PyNE-wells v2.0.0 on Fri Aug 15 2025 by APM

@developers: Adam Micolich

Very basic test program for K2401s running by GPIB from Raspberry Pi
"""

from Keithley2401 import Keithley2401
import time

# Values for outputs to run to in testing
AO0GoTo = 1.0
AO1GoTo = -1.0

# 1) Initialize Instruments
#---- Keithley2401 Output Port for AO0 --------------
daqout_AO0 = Keithley2401(1)
daqout_AO0.setOptions({"beepEnable":False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05E-2,"compliance":50.0E-3,"scaleFactor":1})

#---- Keithley2401 Output Port for AO1 --------------
daqout_AO1 = Keithley2401(2)
daqout_AO1.setOptions({"beepEnable":False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05E-2,"compliance":50.0E-3,"scaleFactor":1})

#---- Keithley2401 Input Port for AI0 --------------
daqin_AI0 = Keithley2401(1)
daqin_AI0.setOptions({"beepEnable":False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05E-2,"compliance":50.0E-3,"scaleFactor":1})

#---- Keithley2401 Input Port for AI1 --------------
daqin_AI1 = Keithley2401(2)
daqin_AI1.setOptions({"beepEnable":False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05E-2,"compliance":50.0E-3,"scaleFactor":1})

daqout_AO0.goTo(AO0GoTo,stepsize=0.01,delay=0.01)
daqout_AO1.goTo(AO1GoTo,stepsize=0.01,delay=0.01)

for i in range(5):
    print('Iteration: ',i+1)
    V_AI0 = daqin_AI0.get('senseLevel')
    V_AI1 = daqin_AI1.get('senseLevel')
    print (V_AI0[0],V_AI0[1],V_AI1[0],V_AI1[1])
    time.sleep(5)

daqout_AO0.goTo(0.0,stepsize=0.01,delay=0.01)
daqout_AO1.goTo(0.0,stepsize=0.01,delay=0.01)