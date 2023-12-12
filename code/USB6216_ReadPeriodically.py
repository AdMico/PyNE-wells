"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

Program for using NIDAQ USB-6216 for full control of a transistor characterisation.
DAQ AO0 on source, DAQ AO1 on gate, Drain feeds a Femto, which feeds AI0.
This program runs Vg and Vsd to specified values, then does a time sweep for a given length
of time, then ramps Vg and Vsd back. 
"""

import os
os.chdir('..\Data')
from Imports import *

# Setpoints here as some need to be fed to instruments
Vsd = 0.5 #Volts
Vg = 0.0 #Volts
TimeStep = 0.1 #Seconds
TimeStop = 180 #Seconds

# 1) Initialize Instruments
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

#---- NIDAQ Input Port for Drain-Left --------------
daqin_DL = USB6216In(0)
daqin_DL.setOptions({
#    "inputRange":10, ## APM to delete in a later update -- not defined in instrument itself.
    "scaleFactor":1
})

#---- NIDAQ Input Port for Drain-Right --------------
daqin_DR = USB6216In(1)
daqin_DR.setOptions({
#    "inputRange":10, ## APM to delete in a later update -- not defined in instrument itself.
    "scaleFactor":1
})

#---- Time Step Instrument --------------
time1 = TimeMeas(0.1) #Note! GPIB number serves instead as wait time interval for TimeMeas.py. Do not make this huge or you will wait forever.
time1.setOptions({
    "timeInterval":0
})

[basePath,fileName] = fileDialog()

print('Ensure Outputs Zero') #Optional, but use unless you trust to be zero.

daqout_SL.goTo(0.0,delay=0.0)
daqout_SR.goTo(0.0,delay=0.0)

print('Array definition')

#time array
tset = np.arange(0.0,TimeStop,TimeStep)
inputPoints = product(tset)

print('Sweep sequence')

print('Set outputs')

daqout_SL.goTo(Vsd,delay=0.0)
daqout_SR.goTo(Vsd,delay=0.0)

#-------------- Sweep Id vs Vsd at single Vg
inputHeaders = ["Time"]
inputSetters = [time1]
outputHeaders = ["I_dl","I_dr"]
outputReaders = [daqin_DL,daqin_DR]
sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders,
        plotParams = ["Time","I_dl","I_dr"]
)
    
print('Return outputs to zero')
    
daqout_SL.goTo(0.0,delay=0.0)
daqout_SR.goTo(0.0,delay=0.0)

closeInstruments(inputSetters,outputReaders)