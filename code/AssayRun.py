"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

For debugging hardware setup
"""

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

def initialise(): # Initialises the software and the instruments -- last edited APM 17Jan24
    nRows = int(26)
    nDev = 2*nRows
    devices = np.zeros(nDev)
    GUIFrameL = pd.DataFrame(np.zeros((nRows,4),columns = ['Device ID', 'Resistance', 'Uncertainty', 'Timestamp'], dtype = 'object'))
    GUIFrameR = pd.DataFrame(np.zeros((nRows,4),columns = ['Device ID', 'Resistance', 'Uncertainty', 'Timestamp'], dtype = 'object'))
    DL = pd.DataFrame(np.zeros(nDev,ItersAR),dtype='float')
    DLerr = pd.DataFrame(np.zeros(nDev,ItersAR),dtype='float')
    DR = pd.DataFrame(np.zeros(nDev,ItersAR),dtype='float')
    DRerr = pd.DataFrame(np.zeros(nDev,ItersAR),dtype='float')
    PBStart = pd.DataFrame(np.zeros(nRows),dtype='float') # For use in determining time taken to obtain measurements from USB6216
    PBEnd = pd.DataFrame(np.zeros(nRows),dtype='float') # For use in determining time taken to obtain measurements from USB6216
    PBTime = pd.DataFrame(np.zeros(nRows),dtype='float') # For use in determining time taken to obtain measurements from USB6216
    stopText = """If you want to stop the program, simply replace this text with 'stop' and save it.""" # Resets the code used to end a grab before quitting program
    with open('stop.txt', 'w') as f: # Initialise stop button
        f.write(stopText)
#    print ('Initialise instruments') ## Keep for diagnostics; Off from 17JAN24 APM
    # ---- Raspberry Pi --------------
    CtrlPi = PiMUX()
    CtrlPi.setMuxToOutput(0)  # Sets multiplexer to state with all outputs off
    #---- NIDAQ Output Port for Source --------------
    daqout_S = USB6216Out(0)
    daqout_S.setOptions({"feedBack":"Int","scaleFactor":1})
    #---- NIDAQ Input Port for Drain running PairBurst on USB6216 --------------
    daqin_Drain = USB6216InPB()
    daqin_Drain.setOptions({"scaleFactor":1})
    #    print('Set NIDAQ Voltage') ## Keep for diagnostics; Off from 17JAN24 APM
    daqout_S.goTo(VSource, delay=0.0) # Run the source up to specified voltage

def finishOff(): # Ends the software -- last edited APM 17Jan24
#    print('Finish Set-up') ## Keep for diagnostics; Off from 17JAN24 APM
    #---- Run source voltage back to zero
    daqout_S.goTo(0.0, delay=0.0)
    #---- Switch Multiplexer to off state.
    CtrlPi.setMuxToOutput(0)

def updateDF(): # Updates the dataframes for the GUI -- last edited APM 17Jan24
    GUI_tableL.updateModel(TableModel(GUIFrameL))
    GUI_tableR.updateModel(TableModel(GUIFrameR))
    GUI_tableL.redraw()
    GUI_tableR.redraw()

def stop(): # Operates mechanism to complete grab before ending program -- last edited APM 17Jan24
    with open('stop.txt', 'w') as f:
        f.write('stop')

def grab(nGrab): # Code to implement a single grab of all the devices on a chip -- last edited APM 17Jan24
    print('Start of grab: ',nGrab)
    for i in range(nRows):
        nRow = i + 1
#        print('Row = ',nRow) ## Keep for diagnostics; Off from 15JAN24 APM
        nDevL = i + 1
        nDevR = 52 - i
#        print('Device Left =', nDevL ,'Device Right =', nDevR) ## Keep for diagnostics; Off from 15JAN24 APM
        #---- Set Multiplexer
        CtrlPi.setMuxToOutput(nRow)
        PBStart[i,nGrab] = time.time()
        #---- Grab row data from NIDAQ
        Drain = daqin_Drain.get('inputLevel')
        if Drain[0] > zeroThres: # Converts to resistance and sets open circuit to zero for left-bank devices
            DL[i,nGrab] = ((VSource*P1Gain)/Drain[0])
            DLerr[i,nGrab] = (Drain[1]/Drain[0])*DL
        else:
            DL[i,nGrab] = 0.0
            DLerr[i,nGrab] = 0.0
        if Drain[2] > zeroThres: # Converts to resistance and sets open circuit to zero for right-bank devices
            DR[i,nGrab] = ((VSource*P2Gain)/Drain[2])
            DRerr[i,nGrab] = (Drain[3]/Drain[2])*DR
        else:
            DR[i,nGrab] = 0.0
            DRerr[i,nGrab] = 0.0
#        print(f'DL = {DL:.2f} +/- {DLerr:.2f} ohms') ## Keep for diagnostics; Off from 15JAN24 APM
#        print(f'DR = {DR:.2f} +/- {DRerr:.2f} ohms') ## Keep for diagnostics; Off from 15JAN24 APM
        #---- Update data for the GUI
        GUIFrameL.iloc[nRow-1] = [nDevL,round(DL,2),round(DLerr,2),datetime.now().strftime("%H:%M:%S")]
        GUIFrameR.iloc[nRows-nRow] = [nDevR,round(DR,2),round(DRerr,2),datetime.now().strftime("%H:%M:%S")]
        updateDF()
        #---- End of row timing
        PBEnd[i,nGrab] = time.time()
        PBTime[i,nGrab] = PBEnd[i,nGrab]-PBStart[i,nGrab]
        PBElapsed[nGrab] = PBEnd[nRows-1]-PBStart[0]
        PBAverage[nGrab] = PBTime.mean()

    return PBElapsed,PBAverage

def measLoop():
    #---- Currently the main program
    #---- Initialise everything
    initialise()
    for i in range(ItersAR):
        nGrab = i







    with open('stop.txt', 'r') as f:
        r = f.read()
        if r == 'stop':
            print('stopped safely after repeat')
            break

    print()
    print(f'Time elapsed = {end[nRows - 1] - start[0]:.2f} s')
    print(f'Average time = {timing.mean():.2f} s')











    finishOff()
    print()
    print('Measurement Daemon Completed Successfully')
    #root.quit() ## remove this line for the program to not quit at the end

if __name__ == "__main__":
    # GUI Code
    root = tk.Tk()
    root.title("Live Measurement GUI")
    root.maxsize(1200,800)
    root.config(bg="skyblue")
    left_table = Frame(root)
    left_table.grid(row=0,column=1,padx=5,pady=5)
    right_table = Frame(root)
    right_table.grid(row=0,column=2,padx=5,pady=5)
    table_L = Table(left_table,showtoolbar=True,showstatusbar=True,width=350,height=590)
    options_L = {'align':'w','cellwidth':80,'floatprecision':2,'font':'Arial','fontsize':12,'linewidth':1,'rowheight':22}
    pdtb.config.apply_options(options_L,table_L)
    table_L.updateModel(TableModel(GUIFrameL))
    table_R = Table(right_table,showtoolbar=True,showstatusbar=True,width=350,height=590)
    options_R = {'align':'w','cellwidth':80,'floatprecision':2,'font':'Arial','fontsize':12,'linewidth':1,'rowheight':22}
    pdtb.config.apply_options(options_R,table_R)
    table_R.updateModel(TableModel(GUIFrameR))
    table_L.show()
    table_R.show()
    updateDF()
    updateThread = threading.Thread(target=measLoop)
    updateThread.daemon = True
    stop_button = tk.Button(root, text='STOP Button', command=lambda *args: stop())
    stop_button.grid(row=0,column=0,padx=5,pady=5)
    exit_button = tk.Button(root, text='Close GUI', command=root.quit)
    exit_button.grid(row=1,column=0,padx=5,pady=5)
    updateThread.start()
    root.mainloop()