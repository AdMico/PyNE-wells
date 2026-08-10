"""
Brought to PyNE-wells v2.0.0 on Thu Apr 30 2026 by APM

@developers: Adam Micolich & Jan Gluschke

Main software for running assays.

Adam's to do list follows -- Updated APM 28JUL26
* Code up gate voltage and current monitoring properly.
* Consider ability to functionally switch the gate and hold setup if VHold is always zero.
* Fix the Ag/AgCl electrode information line in the log file.
"""

from TeensyInterface_Gen6 import TeensyMUX
from ConfigInterpreter_Gen6 import ConfigInterp
import GlobalMeasID as ID
from Config_Gen6 import Instruments,VSource,VGate,VHold,ItersAR,WaitAR,basePath,GuiUpdateMode,GateModeExt,ScanDir,PlotTwoMode
from SeabornInit import dataInit,dataReset
from USB6216Out import USB6216Out
from USB6216InSB import USB6216InSB
from Keithley2401 import Keithley2401
from MCC152Out import MCC152Out
from MCC128InSB import MCC128InSB
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
Ig = pd.DataFrame(np.zeros((nBits,nWords), dtype='float'),columns=WordList2,index=BitList) # Made a default for Gen 6 -- 09Aug26 APM
Vg = pd.DataFrame(np.zeros((nBits,nWords), dtype='float'),columns=WordList2,index=BitList) # Made a default for Gen 6 -- 09Aug26 APM
RD = np.zeros(1459)
SBStart = np.zeros((nBits,nWords),dtype='float') # For use in determining time taken to obtain measurements from USB6216/MCC128
SBEnd = np.zeros((nBits,nWords),dtype='float') # For use in determining time taken to obtain measurements from USB6216/MCC128
SBTime = np.zeros((nBits,nWords),dtype='float') # For use in determining time taken to obtain measurements from USB6216/MCC128
SBElapsed = np.zeros(ItersAR,dtype='float') # For use in determining time taken to obtain measurements from USB6216/MCC128
SBAverage = np.zeros(ItersAR,dtype='float') # For use in determining time taken to obtain measurements from USB6216/MCC128
GrabStart = np.zeros(ItersAR,dtype='float') # For use in determining time taken to run a grab
GrabEnd = np.zeros(ItersAR,dtype='float') # For use in determining time taken to run a grab
GrabTime = np.zeros(ItersAR,dtype='float') # for use in determining time taken to run a grab
GrabTime[:] = np.nan
#---- Run Configuration Interpreter to get missing configuration parameters -- Added 09Aug26 APM
SourcePol,HoldPol = ConfigInterp.Polarities()
Source = ConfigInterp.Source()
Hold = ConfigInterp.Hold()
Drain = ConfigInterp.Drain()
Gate = ConfigInterp.Gate()
SR = ConfigInterp.SR()
SpC = ConfigInterp.SpC()
P1Gain = ConfigInterp.P1Gain()
P2Gain = ConfigInterp.P2Gain()
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
               'Preamp 1 gain: ' + str(P1Gain) + '\n' +
               'Preamp 2 gain: ' + str(P2Gain) + '\n' +
               'Source Voltage: ' + str(VSource) + ' V' + '\n' +
               'Hold Voltage: ' + str(VHold) + ' V' + '\n' +
               'Gate Voltage: ' + str(VGate) + ' V' + '\n' +
               'ADC Sample Rate: ' + str(SR) + ' Hz' + '\n' +
               'ADC Samples per Channel: ' + str(SpC) + '\n' +
               'Number of Grabs: ' + str(ItersAR) + '\n' +
               'Time between Grabs: ' + str(WaitAR) + ' s' + '\n' +
               'Scan direction: ' + ScanDir + '\n' +
               'Instrument set: ' + Instruments + '\n' +
               'Ag/AgCl electrode on: ' + Gate + '\n \n'
               )

#---- Initialization of instruments
print ('Initialise instruments') ## Keep for diagnostics; Off from 17JAN24 APM
# ---- Raspberry Pi --------------
CtrlTy = TeensyMUX()
CtrlTy.SysInit()  # Initialises the multiplexer for running a measurement (including setting which line is connected to AO0 and preamp)
#---- External Instrument Initialisation
if Instruments == 'External':
    #---- NIDAQ Output Port for Source --------------
    daqout_S = USB6216Out(0)
    daqout_S.setOptions({"feedBack":"Int","scaleFactor":1})
    #---- NIDAQ Output Port for Source --------------
    daqout_H = USB6216Out(1)
    daqout_H.setOptions({"feedBack":"Int","scaleFactor":1})
    #---- NIDAQ Input Port for Drain running PairBurst on USB6216 --------------
    daqin_D = USB6216InSB(0)
    daqin_D.setOptions({"scaleFactor":1})
    #---- Code for Keithley 2401 initialisation for Ag/AgCl electrode control -- Added 30Oct25 APM
    if GateModeExt == 'K2401':
        daqin_G = Keithley2401(27)
        daqin_G.setOptions({"beepEnable":False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05e-4,"compliance":1.0e-4,"scaleFactor":1})
    elif GateModeExt == 'USB6216':
        daqin_G = USB6216InSB(1)
        daqin_G.setOptions({"scaleFactor": 1})
#---- Internal Instrument Initialisation
elif Instruments == 'Internal':
    # ---- MCC152 Output Port for Source --------------
    daqout_S = MCC152Out(0)
    daqout_S.setOptions({"scaleFactor": 1})
    # ---- MCC152 Output Port for Hold --------------
    daqout_H = MCC152Out(1)
    daqout_H.setOptions({"scaleFactor": 1})
    # ---- MCC128 Input Port for Drain --------------
    daqin_D = MCC128InSS(0)
    daqin_D.setOptions({"scaleFactor": 1})
    # ---- MCC128 Input Port for Gate --------------
    daqin_G = MCC128InSS(1)
    daqin_G.setOptions({"scaleFactor": 1})

def mapper(j): # Generates a k for dataframes running A-& from a j for dataframes running A-O -- last edited APM 11Nov25
    map = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,26,25,24,23,22,21,20,19,18,17,16,15,14])
    k = map[j]
    return k

def createFigL(): # Creates the left plot -- last edited APM 06Nov25
    global Dt,figL
    figL = plt.figure(figsize=(7.5, 7))
    axL = figL.subplots()
    sns.heatmap(Dt, cmap='Spectral', linewidths=0.5, ax=axL)
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
    run = tk.Label(root, text=('Run Number: '+str(nRun)),bg="seagreen")
    run.grid(row=1,column=0,padx=5,pady=5)
    grabNum = tk.Label(root, text=('Grab Number: '+str(nGrab+1)),bg="seagreen")
    grabNum.grid(row=3,column=0,padx=5,pady=5)
    grabTot = tk.Label(root, text=('of total grabs: '+str(ItersAR)),bg="seagreen")
    grabTot.grid(row=4,column=0,padx=5,pady=5)
    redrawFigL()
    redrawFigR()
    root.update()

def grabStart(): # Operates the Grab Start button in the GUI
    global Dt,dD,nGrab
    nGrab = 0
    Dt,dD = dataReset()
    updateGUI()
    # Resets the code used to end a grab before quitting program -- added APM 25Nov25
    stopText = """If you want to stop the program, simply replace this text with 'stop' and save it."""  # Resets the code used to end a grab before quitting program
    with open('stop.txt', 'w') as fStop:  # Initialise stop button
        fStop.write(stopText)
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
    if GateModeExt == 'K2401':
        daqin_G.goTo(0.0,delay=0.0)  # Run the gate up to specified voltage
    CtrlTy.SysReset()
    ID.increaseID()

def grab(nGrab): # Code to implement a single grab of all the devices on a chip -- last edited APM 31Oct25
    global nRun,RD
    print('Grab: ',nGrab+1)
    updateGUI()
    with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('Grab: '+str(nGrab+1)+' started: '+str(datetime.now())+'\n')
#    print('Start of grab: ',nGrab+1) ## Keep for diagnostics; Off from 18JAN24 APM
#    print('Set DAC Voltage')  ## Keep for diagnostics; Off from 17JAN24 APM
    daqout_S.goTo(VSource,delay=0.0)  # Run the source up to specified voltage
    daqout_H.goTo(VHold,delay=0.0)  # Run the source up to specified voltage
    if (GateModeExt == 'K2401' and VGate != 0.0):
        daqin_G.goTo(VGate,delay=0.0)  # Run the gate up to specified voltage if it's a Keithley and VGate is non-zero -- edited 09AUG26 APM
    RD[0]=nGrab+1
    print('Measuring...')
    if ScanDir == 'Horizontal': # Implements data pull by scanning along bitlines starting from 1
        for i in range(nBits):
            for j in range(nWords):
                k = mapper(j)
#                print('Measuring: ',WordList[k],BitList[i]) ## Keep for diagnostics; On from 16Oct25 APM
                # ---- Set multiplexer to given device
                CtrlTy.nodeToMeasure(k+1,i+1)
#                time.sleep(10)
                SBStart[i,j] = time.time()
                #---- Grab device data from NIDAQ
                Drain = daqin_D.get('inputLevel')
                # ---- Calculate conductance values and uncertainties
#               print("input: ",Drain[0],Drain[1]) ## Keep for diagnostics; Off from 18SEP25 APM
                Dt.iloc[i,j] = ((Drain[0]/(VSource*P1Gain))/1e-6)  ## Updated to Conductance in microsiemens for V1.1.3 30Oct25 APM
                Dterr.iloc[i,j] = (Drain[1]/Drain[0])*Dt.iloc[i,j]
#               print(f'Dt = {Dt.iloc[i,j]:.2f} +/- {Dterr.iloc[i,j]:.2f} uS') ## Keep for diagnostics; Off from 15JAN24 APM
                # ---- Generate the Ag/AgCl electrode data arrays -- edited for all options 09AUG26 APM
                if GateModeExt == 'K2401':
                    AgCl = daqin_G.get('senseLevel')
                    Ig.iloc[i,j] = AgCl[0]
                    Vg.iloc[i,j] = AgCl[1]
                else: # Whether USB6216 or MCC128 it should still work
                    Ig.iloc[i,j] = daqin_G.get('inputLevel')
                    Vg.iloc[i,j] = 0.0
                CtrlTy.nodeToHold(k+1,i+1)
                if GuiUpdateMode == 'point':  # Update the GUI every datapair from the NIDAQ
                    updateGUI()
    elif ScanDir == 'Vertical': # implements scan along wordlines starting from A
        for j in range(nWords):
            for i in range(nBits):
                k = mapper(j)
                print('Measuring: ',WordList[k],BitList[i])  ## Keep for diagnostics; On from 16Oct25 APM
                # ---- Set multiplexer to given device
                CtrlTy.nodeToMeasure(k+1,i+1)
                SBStart[i,j] = time.time()
                # ---- Grab device data from NIDAQ
                Drain = daqin_D.get('inputLevel')
                # ---- Calculate conductance values and uncertainties
#               print("input: ",Drain[0],Drain[1]) ## Keep for diagnostics; Off from 18SEP25 APM
                Dt.iloc[i,j] = ((Drain[0]/(VSource*P1Gain))/1e-6)  ## Updated to Conductance in microsiemens for V1.1.3 30Oct25 APM
                Dterr.iloc[i,j] = (Drain[1]/Drain[0])*Dt.iloc[i,j]
#               print(f'Dt = {Dt.iloc[i,j]:.2f} +/- {Dterr.iloc[i,j]:.2f} uS') ## Keep for diagnostics; Off from 15JAN24 APM
                # ---- Generate the Ag/AgCl electrode data arrays -- edited for all options 09AUG26 APM
                if GateModeExt == 'K2401':
                    AgCl = daqin_G.get('senseLevel')
                    Ig.iloc[i,j] = AgCl[0]
                    Vg.iloc[i,j] = AgCl[1]
                else: # Whether USB6216 or MCC128 it should still work
                    Ig.iloc[i,j] = daqin_G.get('inputLevel')
                    Vg.iloc[i,j] = 0.0
                CtrlTy.nodeToHold(k+1,i+1)
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
                writer.writerow([str(nGrab+1),str(Dt.iloc[i,j]),str(Dterr.iloc[i,j]),str(Ig.iloc[i,j]),str(Vg.iloc[i,j]),str(datetime.now().strftime("%H:%M:%S"))])
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
    if (GateModeExt == 'K2401' and VGate != 0.0):
        daqin_G.goTo(0.0,delay=0.0)  # Run the gate up to specified voltage
    # ---- Switch Multiplexer to off state.
    CtrlTy.SysReset()
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
                writer.writerow(['Grab','Conductance (uS)','Uncertainty (uS)','Ig (A)','Vg (V)','timestamp'])
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
    CtrlTy.SysReset()
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