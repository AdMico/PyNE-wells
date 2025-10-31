"""
Brought to PyNE-wells v1.2.0 on Thu Aug 07 2025 by APM

@developers: Adam Micolich & Jan Gluschke

Main software for running assays.
"""

from PiControlGen5 import PiMUX
import GlobalMeasID as ID
from Config import PiBox,P1Gain,VSource,VGate,VHold,ItersAR,WaitAR,zeroThres,basePath,SR,SpC,GuiUpdateMode,GateMode
from USB6216Out import USB6216Out
from USB6216InSB import USB6216InSB
#from USB6216InSS import USB6216InSS
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
import random

#---- Initialization of data structures
nWords = 27
nBits = 27
nDev = nWords*nBits
devices = np.zeros(nWords*nBits)
WordList = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','&','Z','Y','X','W','V','U','T','S','R','Q','P','O']
BitList = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27']
Dt = pd.DataFrame(np.zeros((nWords,nBits),dtype='float'),columns=WordList,index=BitList)
D0 = pd.DataFrame(np.zeros((nWords,nBits),dtype='float'),columns=WordList,index=BitList)
dD = pd.DataFrame(np.zeros((nWords,nBits),dtype='float'),columns=WordList,index=BitList)
Dterr = pd.DataFrame(np.zeros((nWords,nBits),dtype='float'),columns=WordList,index=BitList)
if GateMode == 'K2401':
    Ig = pd.DataFrame(np.zeros((nWords,nBits), dtype='float'),columns=WordList,index=BitList)
    Vg = pd.DataFrame(np.zeros((nWords,nBits), dtype='float'),columns=WordList,index=BitList)
RD = np.zeros(1459)
SBStart = np.zeros((nWords,nBits),dtype='float') # For use in determining time taken to obtain measurements from USB6216
SBEnd = np.zeros((nWords,nBits),dtype='float') # For use in determining time taken to obtain measurements from USB6216
SBTime = np.zeros((nWords,nBits),dtype='float') # For use in determining time taken to obtain measurements from USB6216
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
               'Ag/AgCl electrode on: ' + GateMode + '\n \n'
               )

#---- Temporary: Preinitialise the dataframes for GUI testing
for i in range(nWords):
    for j in range(nBits):
        Dt.iloc[i,j] = 1000.0 + 200.0*(random.uniform(-1,1))
        dD.iloc[i,j] = 0.0 + 10*(random.uniform(-1,1))

#---- Initialization of instruments
print ('Initialise instruments') ## Keep for diagnostics; Off from 17JAN24 APM
# ---- Raspberry Pi --------------
CtrlPi = PiMUX()
CtrlPi.SysInit()  # Initialises the multiplexer for running a measurement
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

def updateGUI(): # Updates the data in the GUI -- last edited APM 31Oct25
    global nGrab
#    SNS_plotL.close()
#    SNS_plotR.close()
    left_figure = Frame(root)
    left_figure.grid(row=1, column=1, rowspan=6, padx=5, pady=5, sticky='nsew')
    right_figure = Frame(root)
    right_figure.grid(row=1, column=2, rowspan=6, padx=5, pady=5, sticky='nsew')
#    SNS_plotL = plt.figure(figsize=(7, 7))
    axL = SNS_plotL.subplots()
    sns.heatmap(Dt, cmap='magma', linewidths=0.5, ax=axL)
    cbarL = axL.collections[0].colorbar
    cbarL.set_label('Conductance(uS)', labelpad=20)
    axL.xaxis.tick_top()
    axL.xaxis.set_label_position('top')
    axL.set_title('Current grab conductance', y=1.07)
    canvasL = FigureCanvasTkAgg(SNS_plotL, master=left_figure)
#    SNS_plotR = plt.figure(figsize=(7, 7))
    axR = SNS_plotR.subplots()
    sns.heatmap(dD, cmap='coolwarm', linewidths=0.5, ax=axR)
    cbarR = axR.collections[0].colorbar
    cbarR.set_label('Conductance change (uS)', labelpad=20)
    axR.xaxis.tick_top()
    axR.xaxis.set_label_position('top')
    axR.set_title('Conductance change since first grab', y=1.07)
    canvasR = FigureCanvasTkAgg(SNS_plotR, master=right_figure)
#    canvasL.draw()
    canvasL.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
#    canvasR.draw()
    canvasR.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    assay = tk.Label(root, text=('Assay Number: '+t+'_'+measurementName),bg="seagreen")
    assay.grid(row=0,column=0,padx=5,pady=5)
    run = tk.Label(root, text=('Run Number: ' + str(nRun)),bg="seagreen")
    run.grid(row=1,column=0,padx=5,pady=5)
    grabNum = tk.Label(root, text=('Grab Number: '+str(nGrab+1)),bg="seagreen")
    grabNum.grid(row=3,column=0,padx=5,pady=5)
    grabTot = tk.Label(root, text=('of total grabs: '+ str(ItersAR)),bg="seagreen")
    grabTot.grid(row=4,column=0,padx=5,pady=5)
    root.update()

def grabStart(): # Operates the Grab Start button in the GUI
    updateThread = threading.Thread(target=measLoop)
    updateThread.daemon = True
    updateThread.start()

def stop(): # Operates mechanism to complete grab before ending program -- last edited APM 17Jan24
    with open('stop.txt', 'w') as fStop:
        fStop.write('stop')

def end(): # Operates mechanism to end the program entirely
    with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('End: ' + str(datetime.now()) + '\n')
    ID.increaseID()

def grab(nGrab,zeroThres): # Code to implement a single grab of all the devices on a chip -- last edited APM 31Oct25
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
    time.sleep(0.5) # Give time for MUXes to properly run up.
    RD[0]=nGrab+1
    for i in range(nWords):
        for j in range(nBits):
            nWord = i+1
            nBit = j+1
            print('Word = ',WordList[i],'Bit = ',BitList[j]) ## Keep for diagnostics; On from 16Oct25 APM
            # ---- Set multiplexer to given device
            CtrlPi.SysDevOn(nWord,nBit)
            SBStart[i,j] = time.time()
            #---- Grab device data from NIDAQ
            time.sleep(3) ## Allows pause at where the current would be read for stability checking
            Drain = daqin_Drain.get('inputLevel')
            # ---- Grab Ag/AgCl electrode information if K2401 is being used
            if GateMode == 'K2401':
                AgCl = keithley.get('senseLevel')
            # ---- Calculate conductance values and uncertainties
            print("input: ",Drain[0],Drain[1]) ## Keep for diagnostics; Off from 18SEP25 APM
            Dt.iloc[i,j] = ((Drain[0]/(VSource*P1Gain))/1e-6)  ## Updated to Conductance in microsiemens for V1.1.3 30Oct25 APM
            Dterr.iloc[i,j] = (Drain[1]/Drain[0])*Dt.iloc[i,j]
            if nGrab == 0: # Populate the starting conductance dataframe on the first grab
                D0.iloc[i,j] = Dt.iloc[i,j]
            else: # Calculate the conductance difference dataframe on any subsequent grab
                dD.iloc[i,j] = Dt.iloc[i,j] - D0.iloc[i,j]
#            print(f'Dt = {Dt.iloc[i,j]:.2f} +/- {Dterr.iloc[i,j]:.2f} uS') ## Keep for diagnostics; Off from 15JAN24 APM
            # ---- Create the Ag/AgCl electrode data arrays if using K2401
            if GateMode == 'K2401':
                Ig.iloc[i,j] = AgCl[0]
                Vg.iloc[i,j] = AgCl[1]
            CtrlPi.SysDevOff(nWord,nBit)
            # ---- Make the Megatable Information
            RD[54*(nWord-1)+2*(nBit-1)+1] = round(Dt.iloc[i,j],3)
            RD[54*(nWord-1)+2*(nBit-1)+2] = round(Dterr.iloc[i,j],3)
            # ---- send data from this grab to file
            with open(runPath + '/' + t + '_' + measurementName + '_G' + str(nRun) + '_Dev' + str(WordList[i]) + str(BitList[j]) + '.csv','a',newline='') as f:
                writer = csv.writer(f)
                if GateMode == 'K2401':
                    writer.writerow([str(nGrab+1),str(Dt.iloc[i,j]),str(Dterr.iloc[i,j]),str(Ig.iloc[i,j]),str(Vg.iloc[i,j]),str(datetime.now().strftime("%H:%M:%S"))])
                else:
                    writer.writerow([str(nGrab+1),str(Dt.iloc[i,j]),str(Dterr.iloc[i,j]),str(datetime.now().strftime("%H:%M:%S"))])
            # ---- Decision tree below implements GuiUpdateMode switching of GUI updating from config.py -- New 11Sep25 APM
            if GuiUpdateMode == 'point':  # Update the GUI every datapair from the NIDAQ
                updateGUI()
            elif GuiUpdateMode == 'grab' and i == (nWords-1) and j == (nBits-1):  # Update the GUI only at the end of the grab
                print('Update GUI')
                updateGUI()
            #---- End of row timing
            SBEnd[i,j] = time.time()
            SBTime[i,j] = SBEnd[i,j]-SBStart[i,j]
            SBElapsed[nGrab] = SBEnd[nWord-1,nBit-1]-SBStart[0,0]
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
        for i in range(nWords):
            for j in range(nBits):
                MegatableHeader.append('G_'+WordList[i]+BitList[j])
                MegatableHeader.append('dG_'+WordList[i]+BitList[j])
        writer.writerow(MegatableHeader)
    for i in range(nWords):
        for j in range(nBits):
            with open(runPath+'/'+t+'_'+measurementName+'_G'+str(nRun)+'_Dev'+WordList[i]+BitList[j]+'.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                if GateMode == 'K2401':
                    writer.writerow(['Grab','Conductance (uS)','Uncertainty (uS)','Ig (A)','Vg (V)','timestamp'])
                else:
                    writer.writerow(['Grab','Conductance (uS)','Uncertainty (uS)','timestamp'])
    for i in range(ItersAR):
        nGrab = i
        GrabStart[i] = time.time()
        grab(nGrab,zeroThres)
        GrabEnd[i] = time.time()
        GrabTime[i] = GrabEnd[i] - GrabStart[i]
#        print('WaitAR=',WaitAR) ## Keep for diagnostics; Off from 11Sep25 APM
#        print('GrabTime=',GrabTime[i]) ## Keep for diagnostics; Off from 11Sep25 APM
#        print('GT= ',GT) ## Keep for diagnostics; Off from 11Sep25 APM
        #---- check for grab-stop signal
        with open('stop.txt', 'r') as fStop:
            r = fStop.read()
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
    # GUI Code
    nGrab = 0
    root = tk.Tk()
    root.title("Live Measurement GUI")
    root.geometry('1700x850')  # Values set to prevent GUI crash 16Sep25 APM
    root.config(bg="seagreen")
    left_figure = Frame(root)
    left_figure.grid(row=1,column=1,rowspan=6,padx=5,pady=5,sticky='nsew')
    right_figure = Frame(root)
    right_figure.grid(row=1,column=2,rowspan=6,padx=5,pady=5,sticky='nsew')
    SNS_plotL = plt.figure(figsize=(7,7))
    axL = SNS_plotL.subplots()
    sns.heatmap(Dt,cmap='magma',linewidths=0.5,ax=axL)
    cbarL = axL.collections[0].colorbar
    cbarL.set_label('Conductance(uS)', labelpad=20)
    axL.xaxis.tick_top()
    axL.xaxis.set_label_position('top')
    axL.set_title('Current grab conductance',y=1.07)
    canvasL = FigureCanvasTkAgg(SNS_plotL,master=left_figure)
    SNS_plotR = plt.figure(figsize=(7,7))
    axR = SNS_plotR.subplots()
    sns.heatmap(dD,cmap='coolwarm',linewidths=0.5,ax=axR)
    cbarR = axR.collections[0].colorbar
    cbarR.set_label('Conductance change (uS)',labelpad=20)
    axR.xaxis.tick_top()
    axR.xaxis.set_label_position('top')
    axR.set_title('Conductance change since first grab',y=1.07)
    canvasR = FigureCanvasTkAgg(SNS_plotR,master=right_figure)
    canvasL.draw()
    canvasL.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)
    canvasR.draw()
    canvasR.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)
    assay = tk.Label(root, text=('Assay Number: ' + t + '_' + measurementName), bg="seagreen")
    assay.grid(row=0,column=0,padx=5,pady=5)
    run = tk.Label(root, text=('Run Number: ' + str(nRun)), bg="seagreen")
    run.grid(row=1,column=0,padx=5,pady=5)
    start_button = tk.Button(root, text='Start Run', command=lambda: grabStart())
    start_button.grid(row=2,column=0,padx=5,pady=5)
    grabNum = tk.Label(root, text=('Grab Number: ' + str(nGrab + 1)), bg="seagreen")
    grabNum.grid(row=3,column=0,padx=5,pady=5)
    grabTot = tk.Label(root, text=('of total grabs: ' + str(ItersAR)), bg="seagreen")
    grabTot.grid(row=4,column=0,padx=5,pady=5)
    stop_button = tk.Button(root, text='Last Grab', command=lambda: stop())
    stop_button.grid(row=5,column=0,padx=5,pady=5)
    exit_button = tk.Button(root, text='End Program', command=lambda: [end(), root.quit()])
    exit_button.grid(row=6,column=0,padx=5,pady=5)
    root.mainloop()