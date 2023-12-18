"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

Program for using NIDAQ USB-6216 for full control of a transistor characterisation.
DAQ AO0 on source, DAQ AO1 on gate, Drain feeds a Femto, which feeds AI0.
This program runs Vg and Vsd to specified values, then does a time sweep for a given length
of time, then ramps Vg and Vsd back. 
"""

import SweepFunction as SF
import Utils as U
import pandas as pd
import easygui
from datetime import datetime
from Pi_control import PiMUX
import collections.abc
collections.Iterable = collections.abc.Iterable
from Imports import *

def micr_measure(deviceList=1,
                 fileName='test',
                 Vsd=0.5,
                 Vg=0.0,
                 timeStart=0.0,
                 timeStop=180.0,
                 timeStep=10.0,
                 preampGain=1E3,
                 comment='no comment'):

    # Using old stop button setup for now -- APM 13DEC23
    print ('Resetting Stop Button')
    stop_text = """If you want to stop the program, simply replace this text with 'stop' and save it."""
    with open('stop.txt', 'w') as f:
        f.write(stop_text)
    # os.system('stop_button.py') -- Deactivated for now APM 13DEC23

    # Do array build -- APM 13DEC23
    print ('Build Array')
    start_stop_step = [timeStart, timeStop, timeStep]
    timeAxis = U.targetArray([timeStart,timeStop],stepsize=timeStep)

    # Datafile Setup -- APM 13DEC23
    print ('Datafile setup')
    basePath = easygui.diropenbox().replace('\\','/') #Opens window to select folder where data is saved
    with open(basePath + '/comments.txt', 'w') as f:
        f.write('start: ' + str(datetime.now()) + '\n' +
                'Filename: ' + fileName + '\n' +
                'Pi IP: ' + PiBox + '\n' +
                'Preamp Gain: ' + str(preampGain) + '\n' +
                'Time start, stop, step = ' + str(start_stop_step) + '\n' +
                'Source voltage = ' + str(Vsd) + '\n' +
                'Data at: ' + basePath + '\n \n' +
                'Comment: ' + comment + '\n \n'
                )

    # Initialize Instruments -- APM 13DEC23
    print ('Initialise instruments')
    #---- Raspberry Pi --------------
    CtrlPi = PiMUX()
    CtrlPi.setMuxToOutput(0) # Sets multiplexer to state with all outputs off

    #---- Time Step Instrument --------------
    time1 = TimeMeas(timeStep) #Note! GPIB number serves instead as wait time interval for TimeMeas.py. Do not make this huge or you will wait forever.
    time1.setOptions({
        "timeInterval":timeStep
    })

    #---- NIDAQ Output Port for Source --------------
    daqout_S = USB6216Out(0)
    daqout_S.setOptions({
        "feedBack":"Int",
        "extPort":6, # Can be any number 0-7 if in 'Int'
        "scaleFactor":1
    })

    print('Ensure NIDAQ Output Zero') #Optional, but use unless you trust to be zero -- Remove in future version APM 13DEC23
    daqout_S.goTo(0.0,delay=0.0)

    #---- NIDAQ Input Port for Drain-Left --------------
    daqin_DL = USB6216In(0)
    daqin_DL.setOptions({"scaleFactor":1})

    #---- NIDAQ Input Port for Drain-Right --------------
    daqin_DR = USB6216In(1)
    daqin_DR.setOptions({"scaleFactor":1})

    # Setup Dictionary for the Sweep File
    print ('Sweep initialisation')
    Dct = {} # sets up timesweep including where to save the files.
    Dct['basePath'] = basePath + '/t'
    Dct['fileName'] = fileName
    Dct['setters'] = {time1: 'time'}
    Dct['readers'] = {daqin_DL: 'I_DL', daqin_DR: 'I_DR'}
    Dct['sweepArray'] = timeAxis

    # Jan's Dataframe handling, decide later to keep or kill -- APM 13DEC23
    MasterDF = pd.DataFrame(columns=['ID','time','datetime', 'device', 'V_SD', 'I_SD', 'G', 'Std_Dev']) # Sets up results table
    t0 = time.time()

    # Set Multiplexer to Row 1
    CtrlPi.setMuxToOutput(1)

    # Set NIDAQ outputs to operating values -- APM 13DEC23
    print('Set NIDAQ outputs for sweep')
    daqout_S.goTo(Vsd,delay=0.0)

    # Run Sweep
    print ('Run the actual sweep')
    SF.sweepAndSave(Dct) # Perform timesweep using PyNE NIDAQ module

    # Set NIDAQ output back to zero and switch MUX off
    print('Return output to zero')
    daqout_S.goTo(0.0,delay=0.0)
    print('MUX off')
    CtrlPi.setMuxToOutput(0)

    #Data save to file
    #MasterDF.to_csv(basePath + '/' + fileName + '.csv') # Save results table
    #MasterDF.to_csv(basePath + '/' + fileName + str(Params['ID']) + '.csv') # Save final results table with ID of the last sweep
    with open(basePath + '/comments.txt', 'a') as f:
        f.write('Measurement finished at: ' + str(datetime.now()))

    return MasterDF, basePath

# Code for direct run
if __name__ == '__main__':
    Comment = 'test'
    t0 = time.time()
    df, basePath = micr_measure(comment=Comment)
    t1 = time.time()
    print('Time elapsed: ' + str(t1-t0) + 'seconds')
