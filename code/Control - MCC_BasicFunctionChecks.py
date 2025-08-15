"""
Brought to PyNE-wells v2.0.0 on Fri Aug 15 2025 by APM

@developers: Adam Micolich

Very basic test program for MCC128/MCC152 DAQ HATs
"""

from MCC128InSS import MCC128InSS
from MCC152Out import MCC152Out

AO0GoTo = 2.0
AO1GoTo = 2.0

# 1) Initialize Instruments
#---- MCC152 Output Port for AO0 --------------
daqout_AO0 = MCC152Out(0)
daqout_AO0.setOptions({
    "scaleFactor":1
})

#---- MCC152 Output Port for AO1 --------------
daqout_AO1 = MCC152Out(1)
daqout_AO1.setOptions({
    "scaleFactor":1
})

#---- MCC128 Input Port for AI0 --------------
daqin_AI0 = MCC128InSS(0)
daqin_AI0.setOptions({
    "scaleFactor":1
})

#---- MCC128 Input Port for AI1 --------------
daqin_AI1 = MCC128InSS(1)
daqin_AI1.setOptions({
    "scaleFactor":1
})

V_AI0 = daqin_AI0._getInputLevel()
V_AI1 = daqin_AI1._getInputLevel()
print('start = ',V_AI0,V_AI1)
daqout_AO0.goTo(AO0GoTo,stepsize=0.01,delay=0.01)
daqout_AO1.goTo(AO1GoTo,stepsize=0.01,delay=0.01)
V_AI0 = daqin_AI0._getInputLevel()
V_AI1 = daqin_AI1._getInputLevel()
print('middle = ',V_AI0,V_AI1)
daqout_AO0.goTo(0.0,stepsize=0.01,delay=0.01)
daqout_AO1.goTo(0.0,stepsize=0.01,delay=0.01)
V_AI0 = daqin_AI0._getInputLevel()
V_AI1 = daqin_AI1._getInputLevel()
print('end = ',V_AI0,V_AI1)