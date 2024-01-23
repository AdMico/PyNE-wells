"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

For debugging hardware setup
"""

from Pi_control import PiMUX
from Imports import *
from Config import P1Gain, P2Gain, VSource
import pandas as pd
import time
from datetime import datetime
from tkinter import *
import tkinter as tk
from pandastable import Table, TableModel
import pandastable as pdtb
import threading

# Initialisation APM 19DEC23
nRows=26
nDev=2*nRows
devices=np.zeros(nDev)
testGUIFrameL = pd.DataFrame(np.zeros((nRows, 4)), columns=['Device ID', 'Resistance', 'Uncertainty', 'Timestamp'], dtype='object')
testGUIFrameR = pd.DataFrame(np.zeros((nRows, 4)), columns=['Device ID', 'Resistance', 'Uncertainty', 'Timestamp'], dtype='object')
zeroThres = float(1e-2)
start = np.zeros(nRows,float)
end = np.zeros(nRows,float)
timing = np.zeros(nRows,float)
stop_text = """If you want to stop the program, simply replace this text with 'stop' and save it."""

def updateDF():
    table_L.updateModel(TableModel(testGUIFrameL))
    table_R.updateModel(TableModel(testGUIFrameR))
    table_L.redraw()
    table_R.redraw()

def stop():
    with open('stop.txt', 'w') as f:
        f.write('stop')

def measLoop():

    # Initialise stop button
    with open('stop.txt', 'w') as f:
        f.write(stop_text)

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

    print('Set NIDAQ Voltage')
    daqout_S.goTo(VSource,delay=0.0)

    print ('Do a DAQ Read Series -- pairburst, full set')
    for i in range(nRows):
        Row = i+1
        print('Row = ',Row)
        DevL = i+1
        DevR = 52-i
        print('Device Left =', DevL ,'Device Right =', DevR)
        CtrlPi.setMuxToOutput(i+1)
        start[i]=time.time()
        Drain=daqin_Drain.get('inputLevel')

        if Drain[0] > zeroThres:
            DL=((VSource*P1Gain)/Drain[0])
            DLerr=(Drain[1]/Drain[0])*DL
        else:
            DL = 0.0
            DLerr = 0.0
        if Drain[2] > zeroThres:
            DR = ((VSource * P2Gain) / Drain[2])
            DRerr = (Drain[3] / Drain[2]) * DR
        else:
            DR = 0.0
            DRerr = 0.0

#        print(f'DL = {DL:.2f} +/- {DLerr:.2f} ohms') ## Keep for diagnostics; Off from 15JAN24 APM
#        print(f'DR = {DR:.2f} +/- {DRerr:.2f} ohms') ## Keep for diagnostics; Off from 15JAN24 APM

        #testGUIFrame.iloc[DevL-1] = [int(DevL), round(DL,2), round(DLerr,2), datetime.now().strftime("%H:%M:%S")]
        #testGUIFrame.iloc[DevR-1] = [int(DevR), round(DR,2), round(DRerr,2), datetime.now().strftime("%H:%M:%S")]
        testGUIFrameL.iloc[i] = [int(DevL), round(DL,2), round(DLerr,2), datetime.now().strftime("%H:%M:%S")]
        testGUIFrameR.iloc[nRows-i-1] = [int(DevR), round(DR,2), round(DRerr,2), datetime.now().strftime("%H:%M:%S")]
        if __name__ == "__main__":
            updateDF()

        end[i]=time.time()
        timing[i] = end[i]-start[i]

        with open('stop.txt', 'r') as f:
            r = f.read()
        if r == 'stop':
            print('stopped safely after repeat')
            break

    print()
    print(f'Time elapsed = {end[nRows - 1] - start[0]:.2f} s')
    print(f'Average time = {timing.mean():.2f} s')

    print('Finish Set-up')
    daqout_S.goTo(0.0,delay=0.0)
    CtrlPi.setMuxToOutput(0)
    print()
    print ('Measurement Daemon Completed Successfully')
    root.quit() ## remove this line for the program to not quit at the end

if __name__ == "__main__":

    #GUI Code
    root = tk.Tk()
    root.title("Live Measurement GUI")
    root.maxsize(1200,800)
    root.config(bg="skyblue")
    left_table = Frame(root)
    left_table.grid(row=0, column=1, padx=5, pady=5)
    right_table = Frame(root)
    right_table.grid(row=0, column =2, padx=5, pady=5)
    table_L = Table(left_table, showtoolbar=True, showstatusbar=True, width=350, height=590)
    options_L = {'align':'w', 'cellwidth': 80, 'floatprecision': 2,'font': 'Arial', 'fontsize': 12, 'linewidth': 1, 'rowheight': 22}
    pdtb.config.apply_options(options_L,table_L)
    table_L.updateModel(TableModel(testGUIFrameL))
    table_R = Table(right_table, showtoolbar=True, showstatusbar=True, width=350, height=590)
    options_R = {'align':'w', 'cellwidth': 80, 'floatprecision': 2,'font': 'Arial', 'fontsize': 12, 'linewidth': 1, 'rowheight': 22}
    pdtb.config.apply_options(options_R,table_R)
    table_R.updateModel(TableModel(testGUIFrameR))
    table_L.show()
    table_R.show()
    updateDF()
    updateThread = threading.Thread(target=measLoop)
    updateThread.daemon = True
#    tk.Button(root, text='STOP Button', command=lambda *args: stop()).grid(row=0, column=0, padx=5, pady=5) ## Remove in future version 15JAN24 APM
    stop_button = tk.Button(root, text='STOP Button', command=lambda *args: stop())
    stop_button.grid(row=0, column=0, padx=5, pady=5)
    exit_button = tk.Button(root, text='Close GUI', command=root.quit)
    exit_button.grid(row=1, column=0, padx=5, pady=5)
    updateThread.start()
    root.mainloop()