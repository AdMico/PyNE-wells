"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

For debugging hardware setup
"""
import numpy as np

from Pi_control import PiMUX
from Imports import *
from Config import P1Gain, P2Gain, VSource, ItersAR, WaitAR, zeroThres
import pandas as pd
import time
from datetime import datetime
from tkinter import *
import tkinter as tk
from pandastable import Table, TableModel
import pandastable as pdtb
import threading

#---- Definition of the data structures
nRows = 26
nDev = 2*nRows
devices = np.zeros(nDev)
DL = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))
DLerr = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))
DR = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))
DRerr = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))
GUIFrameL = pd.DataFrame(np.zeros((nRows,4)),columns=['Device ID','Resistance','Uncertainty','Timestamp'],dtype='object')
GUIFrameR = pd.DataFrame(np.zeros((nRows,4)),columns=['Device ID','Resistance','Uncertainty','Timestamp'],dtype='object')
PBStart = np.zeros(nRows) # For use in determining time taken to obtain measurements from USB6216
PBEnd = np.zeros(nRows) # For use in determining time taken to obtain measurements from USB6216
PBTime = np.zeros(nRows) # For use in determining time taken to obtain measurements from USB6216
PBElapsed = np.zeros(ItersAR) # For use in determining time taken to obtain measurements from USB6216
PBAverage = np.zeros(ItersAR) # For use in determining time taken to obtain measurements from USB6216
GrabStart = np.zeros(ItersAR) # For use in determining time taken to run a grab
GrabEnd = np.zeros(ItersAR) # For use in determining time taken to run a grab
GrabTime = np.zeros(ItersAR) # for use in determining time taken to run a grab
GrabTime[:] = np.nan
stopText = """If you want to stop the program, simply replace this text with 'stop' and save it.""" # Resets the code used to end a grab before quitting program
with open('stop.txt', 'w') as f: # Initialise stop button
    f.write(stopText)
print ('Initialise instruments') ## Keep for diagnostics; Off from 17JAN24 APM
# ---- Raspberry Pi --------------
CtrlPi = PiMUX()
CtrlPi.setMuxToOutput(0)  # Sets multiplexer to state with all outputs off
#---- NIDAQ Output Port for Source --------------
daqout_S = USB6216Out(0)
daqout_S.setOptions({"feedBack":"Int","scaleFactor":1})
#---- NIDAQ Input Port for Drain running PairBurst on USB6216 --------------
daqin_Drain = USB6216InPB()
daqin_Drain.setOptions({"scaleFactor":1})

def updateDF(): # Updates the dataframes for the GUI -- last edited APM 17Jan24
    GUI_tableL.updateModel(TableModel(GUIFrameL))
    GUI_tableR.updateModel(TableModel(GUIFrameR))
    GUI_tableL.redraw()
    GUI_tableR.redraw()

def stop(): # Operates mechanism to complete grab before ending program -- last edited APM 17Jan24
    with open('stop.txt', 'w') as f:
        f.write('stop')

def grab(nGrab,zeroThres): # Code to implement a single grab of all the devices on a chip -- last edited APM 17Jan24
    print('Grab: ',nGrab+1)
#    print('Start of grab: ',nGrab+1) ## Keep for diagnostics; Off from 18JAN24 APM
#    print('Set NIDAQ Voltage')  ## Keep for diagnostics; Off from 17JAN24 APM
    daqout_S.goTo(VSource, delay=0.0)  # Run the source up to specified voltage

    for i in range(nRows):
        nRow = i+1
#        print('Row = ',nRow) ## Keep for diagnostics; Off from 15JAN24 APM
        nDevL = i+1
        nDevR = 52-i
#        print('Device Left =', nDevL ,'Device Right =', nDevR) ## Keep for diagnostics; Off from 15JAN24 APM
        #---- Set Multiplexer
        CtrlPi.setMuxToOutput(nRow)
        PBStart[i] = time.time()
        #---- Grab row data from NIDAQ
        Drain = daqin_Drain.get('inputLevel')
        if Drain[0] > zeroThres: # Converts to resistance and sets open circuit to zero for left-bank devices
            DL.iloc[i,nGrab] = ((VSource*P1Gain)/Drain[0])
            DLerr.iloc[i,nGrab] = (Drain[1]/Drain[0])*DL.iloc[i,nGrab]
        else:
            DL.iloc[i,nGrab] = 0.0
            DLerr.iloc[i,nGrab] = 0.0
        if Drain[2] > zeroThres: # Converts to resistance and sets open circuit to zero for right-bank devices
            DR.iloc[i,nGrab] = ((VSource*P2Gain)/Drain[2])
            DRerr.iloc[i,nGrab] = (Drain[3]/Drain[2])*DR.iloc[i,nGrab]
        else:
            DR.iloc[i,nGrab] = 0.0
            DRerr.iloc[i,nGrab] = 0.0
#        print(f'DL = {DL.iloc[i,nGrab]:.2f} +/- {DLerr.iloc[i,nGrab]:.2f} ohms') ## Keep for diagnostics; Off from 15JAN24 APM
#        print(f'DR = {DR.iloc[i,nGrab]:.2f} +/- {DRerr.iloc[i,nGrab]:.2f} ohms') ## Keep for diagnostics; Off from 15JAN24 APM
        #---- Update data for the GUI
        GUIFrameL.iloc[nRow-1] = [nDevL,round(DL.iloc[i,nGrab],2),round(DLerr.iloc[i,nGrab],2),datetime.now().strftime("%H:%M:%S")]
        GUIFrameR.iloc[nRows-nRow] = [nDevR,round(DR.iloc[i,nGrab],2),round(DRerr.iloc[i,nGrab],2),datetime.now().strftime("%H:%M:%S")]
        updateDF()
        #---- End of row timing
        PBEnd[i] = time.time()
        PBTime[i] = PBEnd[i]-PBStart[i]
        PBElapsed[nGrab] = PBEnd[nRows-1]-PBStart[0]
        PBAverage[nGrab] = PBTime.mean()

#    print('End of grab: ', nGrab+1) ## Keep for diagnostics; Off from 18JAN24 APM
    # ---- Run source voltage back to zero
    daqout_S.goTo(0.0, delay=0.0)
    # ---- Switch Multiplexer to off state.
    CtrlPi.setMuxToOutput(0)

    return PBElapsed,PBAverage

def measLoop():
    #---- Currently the main program
    for i in range(ItersAR):
        nGrab = i
        GrabStart[i] = time.time()
        grab(nGrab,zeroThres)
        GrabEnd[i] = time.time()
        GrabTime[i] = GrabEnd[i] - GrabStart[i]
        #---- check for grab-stop signal
        with open('stop.txt', 'r') as f:
            r = f.read()
            if r == 'stop':
                print('Stopped safely after completed grab: ',nGrab+1)
                break
        GT = WaitAR-GrabTime[i]
        #---- wait for the next scheduled grab
        if nGrab+1 < ItersAR:
            time.sleep(GT)
    print()
    print(f'Time elapsed = {(GrabEnd[i] - GrabStart[0]):.2f} s')
    print(f'Average time per grab = {np.nanmean(GrabTime):.2f} s')
    print()
    print('Measurement Daemon Completed Successfully')
    print('Finish Set-up')  ## Keep for diagnostics; Off from 17JAN24 APM
    # ---- Run source voltage back to zero
    daqout_S.goTo(0.0, delay=0.0)
    # ---- Switch Multiplexer to off state.
    CtrlPi.setMuxToOutput(0)
    #root.quit() ## remove this line for the program to not quit at the end

if __name__ == "__main__":
    # GUI Code
    root = tk.Tk()
    root.title("Live Measurement GUI")
    root.geometry('1100x750')
#    root.maxsize(1200,800)
    root.config(bg="skyblue")
    left_table = Frame(root)
    left_table.grid(row=0,column=1,padx=5,pady=5)
    right_table = Frame(root)
    right_table.grid(row=0,column=2,padx=5,pady=5)
    GUI_tableL = Table(left_table,showtoolbar=True,showstatusbar=True,width=350,height=590)
    GUI_optionsL = {'align':'w','cellwidth':85,'floatprecision':2,'font':'Arial','fontsize':12,'linewidth':1,'rowheight':22}
    pdtb.config.apply_options(GUI_optionsL,GUI_tableL)
    GUI_tableL.updateModel(TableModel(GUIFrameL))
    GUI_tableR = Table(right_table,showtoolbar=True,showstatusbar=True,width=350,height=590)
    GUI_optionsR = {'align':'w','cellwidth':85,'floatprecision':2,'font':'Arial','fontsize':12,'linewidth':1,'rowheight':22}
    pdtb.config.apply_options(GUI_optionsR,GUI_tableR)
    GUI_tableR.updateModel(TableModel(GUIFrameR))
    GUI_tableL.show()
    GUI_tableR.show()
#    updateDF() # Switching this off seems to stabilise the GUI -- to retest/remove at future version APM 18Jan24
    updateThread = threading.Thread(target=measLoop)
    updateThread.daemon = True
    stop_button = tk.Button(root, text='STOP Button', command=lambda *args: stop())
    stop_button.grid(row=0,column=0,padx=5,pady=5)
    exit_button = tk.Button(root, text='Close GUI', command=root.quit)
    exit_button.grid(row=1,column=0,padx=5,pady=5)
    updateThread.start()
    root.mainloop()