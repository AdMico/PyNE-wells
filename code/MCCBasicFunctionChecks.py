"""
Brought to PyNE-wells v2.0.0 on Fri Aug 15 2025 by APM

@developers: Adam Micolich

Very basic test program for MCC128/MCC152 DAQ HATs
"""

from MCC128InSS import MCC128InSS
from MCC128InSB import MCC128InSB
from MCC152Out import MCC152Out
import time

# Values for outputs to run to in testing
AO0GoTo = 1.0
AO1GoTo = 0.0

# 1) Initialize Instruments
#---- MCC152 Output Port for AO0 --------------
daqout_AO0 = MCC152Out(0)
daqout_AO0.setOptions({"scaleFactor":1})

#---- MCC152 Output Port for AO1 --------------
daqout_AO1 = MCC152Out(1)
daqout_AO1.setOptions({"scaleFactor":1})

#---- MCC128 Input Port for AI0 --------------
daqin_AI0 = MCC128InSB(0,"BIP_5V")
daqin_AI0.setOptions({"scaleFactor":1})

#---- MCC128 Input Port for AI1 --------------
daqin_AI1 = MCC128InSB(1,"BIP_5V")
daqin_AI1.setOptions({"scaleFactor":1})

daqout_AO0.goTo(AO0GoTo,stepsize=0.01,delay=0.01)

for i in range(5):
    print('Iteration: ',i+1)
    V_AI0 = daqin_AI0._getInputLevel()
    print (V_AI0)
    time.sleep(5)

daqout_AO0.goTo(0.0,stepsize=0.01,delay=0.01)
