"""
Brought to PyNE-wells v1.2.0 on Thu Aug 07 2025 by APM

@developers: Adam Micolich & Jan Gluschke

Main software for running assays.
"""

from PiControlGen5 import PiMUX
import GlobalMeasID as ID
from Config import PiBox,P1Gain,VSource,VGate,VHold,ItersAR,WaitAR,basePath,SR,SpC,GuiUpdateMode,GateMode,ScanDir_Gen5,PlotTwoMode
from SeabornInit import dataInit,dataReset
from USB6216Out import USB6216Out
from USB6216InSB import USB6216InSB
from Keithley2401 import Keithley2401
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from datetime import datetime,date
from tkinter import *
import tkinter as tk
import threading
import os
import csv
global Dt,D0,dD

#---- Initialization of data structures
nWords = 27
nBits = 27
nDev = nWords*nBits
devices = np.zeros(nWords*nBits)
WordList = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','&','Z','Y','X','W','V','U','T','S','R','Q','P','O']
WordList2 = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','&']
BitList = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27']
Dt = pd.DataFrame(np.zeros((nBits,nWords),dtype='float'),columns=WordList2,index=BitList)
D0 = pd.DataFrame(np.zeros((nBits,nWords),dtype='float'),columns=WordList2,index=BitList)
dD = pd.DataFrame(np.zeros((nBits,nWords),dtype='float'),columns=WordList2,index=BitList)
Dterr = pd.DataFrame(np.zeros((nBits,nWords),dtype='float'),columns=WordList2,index=BitList)
if GateMode == 'K2401':
    Ig = pd.DataFrame(np.zeros((nBits,nWords), dtype='float'),columns=WordList2,index=BitList)
    Vg = pd.DataFrame(np.zeros((nBits,nWords), dtype='float'),columns=WordList2,index=BitList)
RD = np.zeros(1459)
SBStart = np.zeros((nBits,nWords),dtype='float') # For use in determining time taken to obtain measurements from USB6216
SBEnd = np.zeros((nBits,nWords),dtype='float') # For use in determining time taken to obtain measurements from USB6216
SBTime = np.zeros((nBits,nWords),dtype='float') # For use in determining time taken to obtain measurements from USB6216
SBElapsed = np.zeros(ItersAR,dtype='float') # For use in determining time taken to obtain measurements from USB6216
SBAverage = np.zeros(ItersAR,dtype='float') # For use in determining time taken to obtain measurements from USB6216
GrabStart = np.zeros(ItersAR,dtype='float') # For use in determining time taken to run a grab
GrabEnd = np.zeros(ItersAR,dtype='float') # For use in determining time taken to run a grab
GrabTime = np.zeros(ItersAR,dtype='float') # for use in determining time taken to run a grab
GrabTime[:] = np.nan
#---- Initialization of files for data and control
stopText = """If you want to stop the program, simply replace this text with 'stop' and save it.""" # Resets the code used to end a grab before quitting program
with open('stop.txt', 'w') as fStop: # Initialise stop button
    fStop.write(stopText)
nRun=1
measurementName = str(ID.readCurrentSetup()) + str(ID.readCurrentID())
today = date.today()
t=today.strftime("%y%m%d")
dataPath = basePath + '/'+t+'_'+measurementName
if not os.path.exists(dataPath):
    os.makedirs(dataPath)
with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'w') as fLog:
    fLog.write('Start: '+str(datetime.now()) + '\n' +
               'Assay Number: ' + measurementName + '\n' +
               'Pi Box: ' + PiBox + '\n' +
               'Preamp 1 gain: ' + str(P1Gain) + '\n' +
               'Source Voltage: ' + str(VSource) + ' V' + '\n' +
               'Hold Voltage: ' + str(VHold) + ' V' + '\n' +
               'Gate Voltage: ' + str(VGate) + ' V' + '\n' +
               'NIDAQ Sample Rate: ' + str(SR) + ' Hz' + '\n' +
               'NIDAQ Samples per Channel: ' + str(SpC) + '\n' +
               'Number of Grabs: ' + str(ItersAR) + '\n' +
               'Time between Grabs: ' + str(WaitAR) + ' s' + '\n' +
               'Scan direction: ' + ScanDir_Gen5 + '\n' +
               'Ag/AgCl electrode on: ' + GateMode + '\n \n'
               )

#---- Initialization of instruments
print ('Initialise instruments') ## Keep for diagnostics; Off from 17JAN24 APM
# ---- Raspberry Pi --------------
CtrlPi = PiMUX()
CtrlPi.SysInit()  # Initialises the multiplexer for running a measurement (including setting which line is connected to AO0 and preamp)
#---- NIDAQ Output Port for Source --------------
daqout_S = USB6216Out(0)
daqout_S.setOptions({"feedBack":"Int","scaleFactor":1})
#---- NIDAQ Output Port for Source --------------
daqout_H = USB6216Out(1)
daqout_H.setOptions({"feedBack":"Int","scaleFactor":1})
#---- NIDAQ Input Port for Drain running PairBurst on USB6216 --------------
daqin_Drain = USB6216InSB()
daqin_Drain.setOptions({"scaleFactor":1})
#---- Code for instrument initialisation for Ag/AgCL electrode control -- New 30Oct25 APM
if GateMode == 'K2401':
    keithley = Keithley2401(27)
    keithley.setOptions({
        "beepEnable": False,
        "sourceMode": "voltage",
        "sourceRange": 10,
        "senseRange": 1.05e-4,
        "compliance": 1.0e-4,
        "scaleFactor": 1
    })

def mapper(j): # Generates a k for dataframes running A-& from a j for dataframes running A-O -- last edited APM 11Nov25
    map = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,26,25,24,23,22,21,20,19,18,17,16,15,14])
    k = map[j]
    return k

def createFigL(): # Creates the left plot -- last edited APM 06Nov25
    global Dt,figL
    figL = plt.figure(figsize=(7.5, 7))
    axL = figL.subplots()
    sns.heatmap(Dt, cmap='magma', linewidths=0.5, ax=axL)
    cbarL = axL.collections[0].colorbar
    cbarL.set_label('Conductance(uS)', labelpad=20)
    axL.xaxis.tick_top()
    axL.xaxis.set_label_position('top')
    axL.set_title('Current grab conductance', y=1.07)
    axL.text(x=7.5,y=28,s="Plot updates after first grab")
    return figL

def createFigR(): # Creates the right plot -- last edited APM 06Nov25
    global dD,figR
    figR = plt.figure(figsize=(7.5, 7))
    axR = figR.subplots()
    sns.heatmap(dD, cmap='coolwarm', linewidths=0.5, ax=axR)
    cbarR = axR.collections[0].colorbar
    cbarR.set_label('Conductance change (uS)', labelpad=20)
    axR.xaxis.tick_top()
    axR.xaxis.set_label_position('top')
    if PlotTwoMode == 'First':
        axR.set_title('Conductance change since first grab', y=1.07)
    elif PlotTwoMode == 'Last':
        axR.set_title('Conductance change since last grab', y=1.07)
    axR.text(x=7.5,y=28,s="Plot updates after second grab")
    return figR

def redrawFigL(): # Redraws the left plot -- last edited APM 06Nov25
    global figL
    plt.close(figL)
    figL = createFigL()
    canvasL.figure = figL
    canvasL.draw()

def redrawFigR(): # Redraws the right plot -- last edited APM 06Nov25
    global figR
    plt.close(figR)
    figR = createFigR()
    canvasR.figure = figR
    canvasR.draw()

def updateGUI(): # Updates the data in the GUI -- last edited APM 31Oct25
    global nGrab
    assay = tk.Label(root, text=('Assay Number: '+t+'_'+measurementName),bg="seagreen")
    assay.grid(row=0,column=0,padx=5,pady=5)
    run = tk.Label(root, text=('Run Number: ' + str(nRun)),bg="seagreen")
    run.grid(row=1,column=0,padx=5,pady=5)
    grabNum = tk.Label(root, text=('Grab Number: '+str(nGrab+1)),bg="seagreen")
    grabNum.grid(row=3,column=0,padx=5,pady=5)
    grabTot = tk.Label(root, text=('of total grabs: '+ str(ItersAR)),bg="seagreen")
    grabTot.grid(row=4,column=0,padx=5,pady=5)
    redrawFigL()
    redrawFigR()
    root.update()

def grabStart(): # Operates the Grab Start button in the GUI
    global Dt,dD
    Dt,dD = dataReset()
    redrawFigL()
    redrawFigR()
    updateThread = threading.Thread(target=measLoop)
    updateThread.daemon = True
    updateThread.start()

def stop(): # Operates mechanism to complete grab before ending program -- last edited APM 17Jan24
    with open('stop.txt', 'w') as fStop:
        fStop.write('stop')

def end(): # Operates mechanism to end the program entirely
    with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('End: ' + str(datetime.now()) + '\n')
    daqout_S.goTo(0.0,delay=0.0)  # Run the source up to specified voltage
    daqout_H.goTo(0.0,delay=0.0)  # Run the source up to specified voltage
    if GateMode == 'K2401':
        keithley.goTo(0.0,delay=0.0)  # Run the gate up to specified voltage
    CtrlPi.SysReset()
    ID.increaseID()

def grab(nGrab): # Code to implement a single grab of all the devices on a chip -- last edited APM 31Oct25
    global nRun,RD
    print('Grab: ',nGrab+1)
    with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('Grab: '+str(nGrab+1)+' started: '+str(datetime.now())+'\n')
#    print('Start of grab: ',nGrab+1) ## Keep for diagnostics; Off from 18JAN24 APM
#    print('Set NIDAQ Voltage')  ## Keep for diagnostics; Off from 17JAN24 APM
    daqout_S.goTo(VSource,delay=0.0)  # Run the source up to specified voltage
    daqout_H.goTo(VHold,delay=0.0)  # Run the source up to specified voltage
    if GateMode == 'K2401':
        keithley.goTo(VGate,delay=0.0)  # Run the gate up to specified voltage
    RD[0]=nGrab+1
    if ScanDir_Gen5 == 'Horizontal': # Implements data pull by scanning along bitlines starting from 1
        for i in range(nBits):
            for j in range(nWords):
                k = mapper(j)
                print('Measuring: ',WordList[k],BitList[i]) ## Keep for diagnostics; On from 16Oct25 APM
                # ---- Set multiplexer to given device
                CtrlPi.SysDevOn(k+1,i+1)
#                time.sleep(10)
                SBStart[i,j] = time.time()
                #---- Grab device data from NIDAQ
                Drain = daqin_Drain.get('inputLevel')
                # ---- Calculate conductance values and uncertainties
#               print("input: ",Drain[0],Drain[1]) ## Keep for diagnostics; Off from 18SEP25 APM
                Dt.iloc[i,j] = ((Drain[0]/(VSource*P1Gain))/1e-6)  ## Updated to Conductance in microsiemens for V1.1.3 30Oct25 APM
                Dterr.iloc[i,j] = (Drain[1]/Drain[0])*Dt.iloc[i,j]
#               print(f'Dt = {Dt.iloc[i,j]:.2f} +/- {Dterr.iloc[i,j]:.2f} uS') ## Keep for diagnostics; Off from 15JAN24 APM
                # ---- Create the Ag/AgCl electrode data arrays if using K2401
                if GateMode == 'K2401':
                    AgCl = keithley.get('senseLevel')
                    Ig.iloc[i,j] = AgCl[0]
                    Vg.iloc[i,j] = AgCl[1]
                CtrlPi.SysDevOff(k+1,i+1)
                if GuiUpdateMode == 'point':  # Update the GUI every datapair from the NIDAQ
                    updateGUI()
    elif ScanDir_Gen5 == 'Vertical': # implements scan along wordlines starting from A
        for j in range(nWords):
            for i in range(nBits):
                k = mapper(j)
                print('Measuring: ',WordList[k],BitList[i])  ## Keep for diagnostics; On from 16Oct25 APM
                # ---- Set multiplexer to given device
                CtrlPi.SysDevOn(k+1,i+1)
                SBStart[i,j] = time.time()
                # ---- Grab device data from NIDAQ
                Drain = daqin_Drain.get('inputLevel')
                # ---- Calculate conductance values and uncertainties
#               print("input: ",Drain[0],Drain[1]) ## Keep for diagnostics; Off from 18SEP25 APM
                Dt.iloc[i,j] = ((Drain[0]/(VSource*P1Gain))/1e-6)  ## Updated to Conductance in microsiemens for V1.1.3 30Oct25 APM
                Dterr.iloc[i,j] = (Drain[1]/Drain[0])*Dt.iloc[i,j]
#               print(f'Dt = {Dt.iloc[i,j]:.2f} +/- {Dterr.iloc[i,j]:.2f} uS') ## Keep for diagnostics; Off from 15JAN24 APM
                # ---- Create the Ag/AgCl electrode data arrays if using K2401
                if GateMode == 'K2401':
                    AgCl = keithley.get('senseLevel')
                    Ig.iloc[i,j] = AgCl[0]
                    Vg.iloc[i,j] = AgCl[1]
                CtrlPi.SysDevOff(k+1,i+1)
                if GuiUpdateMode == 'point':  # Update the GUI every datapair from the NIDAQ
                    updateGUI()
    # ---- Run a loop just to handle all the data management at the end of the grab
    for i in range(nBits):
        for j in range(nWords):
            # ---- Display GUI data management
            if nGrab >= 1: #Delay to second grab so all the dataframes below have data in them
                dD.iloc[i,j] = Dt.iloc[i,j] - D0.iloc[i,j]
            if PlotTwoMode == 'First': # Option for second Seaborn plot to be difference from first grab
                if nGrab == 0:  # Populate the starting conductance dataframe on the first grab
                    D0.iloc[i,j] = Dt.iloc[i,j]
            elif PlotTwoMode == 'Last': # Option for second Seaborn plot to be difference from preceding grab
                D0.iloc[i,j] = Dt.iloc[i,j]
            # ---- Make the Megatable Information
            RD[54*(i)+2*(j)+1] = round(Dt.iloc[i,j],3)
            RD[54*(i)+2*(j)+2] = round(Dterr.iloc[i,j],3)
            # ---- send data from this grab to file
            with open(runPath + '/' + t + '_' + measurementName + '_G' + str(nRun) + '_Dev' + str(WordList2[j]) + str(BitList[i]) + '.csv','a',newline='') as f:
                writer = csv.writer(f)
                if GateMode == 'K2401':
                    writer.writerow([str(nGrab+1),str(Dt.iloc[i,j]),str(Dterr.iloc[i,j]),str(Ig.iloc[i,j]),str(Vg.iloc[i,j]),str(datetime.now().strftime("%H:%M:%S"))])
                else:
                    writer.writerow([str(nGrab+1),str(Dt.iloc[i,j]),str(Dterr.iloc[i,j]),str(datetime.now().strftime("%H:%M:%S"))])
            #---- End of row timing
            SBEnd[i,j] = time.time()
            SBTime[i,j] = SBEnd[i,j]-SBStart[i,j]
            SBElapsed[nGrab] = SBEnd[i,j]-SBStart[0,0]
            SBAverage[nGrab] = SBTime.mean()
    #---- Drop all device data to megatable at end of grab
    with open(runPath+'/'+t+'_'+measurementName+'_G'+str(nRun)+'.csv','a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(RD[:])
    # ---- Run source voltage back to zero
    daqout_S.goTo(0.0,delay=0.0)
    # ---- Run hold voltage back to zero
    daqout_H.goTo(0.0,delay=0.0)
    # ---- Run Ag/AgCl electrode back to zero
    if GateMode == 'K2401':
        keithley.goTo(0.0,delay=0.0)  # Run the gate up to specified voltage
    # ---- Switch Multiplexer to off state.
    CtrlPi.SysReset()
    print('Update GUI')
    updateGUI()
#    print('End of grab: ',nGrab+1) ## Keep for diagnostics; Off from 18JAN24 APM
    return SBElapsed,SBAverage

def measLoop():
    global measurementName,nRun,runPath,nGrab
    #---- Currently the main program
    with open(dataPath+'/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('Measurement '+measurementName+'G'+str(nRun)+' started at: '+str(datetime.now())+'\n')
    runPath = dataPath+'/'+t+'_'+measurementName+'_G'+str(nRun)
    if not os.path.exists(runPath):
        os.makedirs(runPath)
    with open(runPath+'/'+t+'_'+measurementName+'_G'+str(nRun)+'.csv','w',newline='') as f:
        writer=csv.writer(f)
        MegatableHeader=[]
        MegatableHeader.append('Grab')
        for i in range(nBits):
            for j in range(nWords):
                k = mapper(j)
                MegatableHeader.append('G_'+WordList2[k]+BitList[i])
                MegatableHeader.append('dG_'+WordList2[k]+BitList[i])
        writer.writerow(MegatableHeader)
    for i in range(nBits):
        for j in range(nWords):
            k = mapper(j)
            with open(runPath+'/'+t+'_'+measurementName+'_G'+str(nRun)+'_Dev'+WordList2[k]+BitList[i]+'.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                if GateMode == 'K2401':
                    writer.writerow(['Grab','Conductance (uS)','Uncertainty (uS)','Ig (A)','Vg (V)','timestamp'])
                else:
                    writer.writerow(['Grab','Conductance (uS)','Uncertainty (uS)','timestamp'])
    for i in range(ItersAR):
        nGrab = i
        GrabStart[i] = time.time()
        grab(nGrab)
        GrabEnd[i] = time.time()
        GrabTime[i] = GrabEnd[i] - GrabStart[i]
        GT = WaitAR - GrabTime[i]
        print(f'WaitAR = {WaitAR:.2f} s') ## Keep for diagnostics; Off from 11Sep25 APM
        print(f'Grab Time = {GrabTime[i]:.2f} s') ## Keep for diagnostics; Off from 11Sep25 APM
        print(f'Pause = {GT:.2f} s') ## Keep for diagnostics; Off from 11Sep25 APM
        #---- check for grab-stop signal
        with open('stop.txt', 'r') as fStop:
            r = fStop.read()
            if r == 'stop':
                print('Stopped safely after completed grab: ',nGrab+1)
                break
        #---- wait for the next scheduled grab
        if nGrab+1 < ItersAR:
            time.sleep(GT)
    print()
    print(f'Time elapsed = {(GrabEnd[i] - GrabStart[0]):.2f} s')
    print(f'Average time per grab = {np.nanmean(GrabTime):.2f} s')
    print()
    print('Measurement Daemon Completed Successfully')
    with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('Measurement '+measurementName+'R'+str(nRun)+' finished at: '+str(datetime.now())+'\n'+
                   'with '+str(nGrab+1)+' of '+str(ItersAR)+' grabs completed.'+'\n \n'
                   )
    nRun += 1
    print('Finish Set-up')  ## Keep for diagnostics; Off from 17JAN24 APM
    # ---- Switch Multiplexer to off state.
    CtrlPi.SysReset()
    #root.quit() ## remove this line for the program to not quit at the end

if __name__ == "__main__":
    global figL,figR,canvasL,canvasR
    # GUI Code
    nGrab = 0
    # Generates the GUI Window
    root = tk.Tk()
    root.title("Live Measurement GUI")
    root.geometry('1700x850')  # Values set to prevent GUI crash 16Sep25 APM
    root.config(bg="seagreen")
    #Populates the sidebar
    assay = tk.Label(root, text=('Assay Number: ' + t + '_' + measurementName), bg="seagreen")
    assay.grid(row=0, column=0, padx=5, pady=5)
    run = tk.Label(root, text=('Run Number: ' + str(nRun)), bg="seagreen")
    run.grid(row=1, column=0, padx=5, pady=5)
    start_button = tk.Button(root, text='Start Run', command=lambda: grabStart())
    start_button.grid(row=2, column=0, padx=5, pady=5)
    grabNum = tk.Label(root, text=('Grab Number: ' + str(nGrab + 1)), bg="seagreen")
    grabNum.grid(row=3, column=0, padx=5, pady=5)
    grabTot = tk.Label(root, text=('of total grabs: ' + str(ItersAR)), bg="seagreen")
    grabTot.grid(row=4, column=0, padx=5, pady=5)
    stop_button = tk.Button(root, text='Last Grab', command=lambda: stop())
    stop_button.grid(row=5, column=0, padx=5, pady=5)
    exit_button = tk.Button(root, text='End Program', command=lambda: [end(), root.quit()])
    exit_button.grid(row=6, column=0, padx=5, pady=5)
    # Creates the two frames needed for the figures
    left_figure = Frame(root)
    left_figure.grid(row=1, column=1, rowspan=6, padx=5, pady=5, sticky='nsew')
    right_figure = Frame(root)
    right_figure.grid(row=1, column=2, rowspan=6, padx=5, pady=5, sticky='nsew')
    # Initialise Seaborn plot data
    Dt, dD = dataInit()
    # Generates the starting figures and assigns them to their frames
    figL = createFigL()
    canvasL = FigureCanvasTkAgg(figL, master=left_figure)
    figR = createFigR()
    canvasR = FigureCanvasTkAgg(figR, master=right_figure)
    # Draws the two plots into the GUI
    canvasL.draw()
    canvasL.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    canvasR.draw()
    canvasR.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    root.mainloop()