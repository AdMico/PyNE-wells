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

#---- NIDAQ Output Port for Source-Left --------------
daqout_SL = USB6216Out(0)
daqout_SL.setOptions({
    "feedBack":"Int",
    "extPort":6, # Can be any number 0-7 if in 'Int'
    "scaleFactor":1
})

#---- NIDAQ Output Port for Source-Right --------------
daqout_SR = USB6216Out(1)
daqout_SR.setOptions({
    "feedBack":"Int",
    "extPort":7, # Can be any number 0-7 if in 'Int'
    "scaleFactor":1
})

print('MUX to Row 1')
CtrlPi.setMuxToOutput(0)

print('Set NIDAQ Voltages')
daqout_SL.goTo(0.0,delay=0.0)
daqout_SR.goTo(0.0,delay=0.0)
