"""
Brought to PyNE-wells v1.2.0 on Thu Aug 07 2025 by APM

@developers: Adam Micolich & Jan Gluschke

Version of AssayRunGen5.py where the hardware lines are all stripped out so it can
be run on machines outside the lab to test aspects of the GUI code.
"""

import GlobalMeasID as ID
from Config import PiBox,P1Gain,VSource,VGate,VHold,ItersAR,WaitAR,zeroThres,basePath,SR,SpC,GuiUpdateMode,GateMode
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import time
from datetime import datetime,date
from tkinter import *
import tkinter as tk
import threading
import os
import csv
import random
global Dt,D0,dD

#---- Initialization of data structures
nWords = 27
nBits = 27
nDev = nWords*nBits
devices = np.zeros(nBits*nWords)
WordList = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','&','Z','Y','X','W','V','U','T','S','R','Q','P','O']
BitList = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27']
Dt = pd.DataFrame(np.zeros((nBits,nWords),dtype='float'),columns=WordList,index=BitList)
D0 = pd.DataFrame(np.zeros((nBits,nWords),dtype='float'),columns=WordList,index=BitList)
dD = pd.DataFrame(np.zeros((nBits,nWords),dtype='float'),columns=WordList,index=BitList)
Dterr = pd.DataFrame(np.zeros((nBits,nWords),dtype='float'),columns=WordList,index=BitList)
if GateMode == 'K2401':
    Ig = pd.DataFrame(np.zeros((nBits,nWords), dtype='float'),columns=WordList,index=BitList)
    Vg = pd.DataFrame(np.zeros((nBits,nWords), dtype='float'),columns=WordList,index=BitList)
RD = np.zeros(1459)
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
for i in range(nBits):
    for j in range(nWords):
        D0.iloc[i,j] = 1000.0
        Dt.iloc[i,j] = D0.iloc[i,j]
        dD.iloc[i,j] = 0.0
Dt.iloc[0,0] = 900.0
Dt.iloc[0,26] = 950.0
Dt.iloc[26,0] = 1050.0
Dt.iloc[26,26] = 1100.0
dD.iloc[0,0] = -10.0
dD.iloc[0,26] = -5.0
dD.iloc[26,0] = 5.0
dD.iloc[26,26] = 10.0

#---- Initialization of instruments
print ('Initialise instruments') ## Keep for diagnostics; Off from 17JAN24 APM
# ---- Raspberry Pi --------------
# Hardware Lines Stripped
#---- NIDAQ Output Port for Source --------------
# Hardware Lines Stripped
#---- NIDAQ Output Port for Source --------------
# Hardware Lines Stripped
#---- NIDAQ Input Port for Drain running PairBurst on USB6216 --------------
# Hardware Lines Stripped
#---- Code for instrument initialisation for Ag/AgCL electrode control -- New 30Oct25 APM
# Hardware Lines Stripped

def createFigL(): # Creates the left plot
    global Dt,figL
    figL = plt.figure(figsize=(7, 7))
    axL = figL.subplots()
    sns.heatmap(Dt, cmap='magma', linewidths=0.5, ax=axL)
    cbarL = axL.collections[0].colorbar
    cbarL.set_label('Conductance(uS)', labelpad=20)
    axL.xaxis.tick_top()
    axL.xaxis.set_label_position('top')
    axL.set_title('Current grab conductance', y=1.07)
    return figL

def createFigR(): # Creates the right plot
    global dD,figR
    figR = plt.figure(figsize=(7, 7))
    axR = figR.subplots()
    sns.heatmap(dD, cmap='coolwarm', linewidths=0.5, ax=axR)
    cbarR = axR.collections[0].colorbar
    cbarR.set_label('Conductance change (uS)', labelpad=20)
    axR.xaxis.tick_top()
    axR.xaxis.set_label_position('top')
    axR.set_title('Conductance change since first grab', y=1.07)
    return figR

def redrawFigL():
    global figL
    plt.close(figL)
#    figL.clf()
    figL = createFigL()
    canvasL.figure = figL
    canvasL.draw()

def redrawFigR():
    global figR
    plt.close(figR)
#    figR.clf()
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
# Hardware Lines Stripped
    time.sleep(0.5) # Give time for MUXes to properly run up.
    RD[0]=nGrab+1
    for i in range(nBits):
        for j in range(nWords):
            nBit = i+1
            nWord = j+1
            print('Word = ',WordList[j],'Bit = ',BitList[i]) ## Keep for diagnostics; On from 16Oct25 APM
            # ---- Set multiplexer to given device
            # Hardware Lines Stripped
            #---- Grab device data from NIDAQ
            time.sleep(0.001) ## Allows pause at where the current would be read for stability checking
            # Hardware Lines Stripped
            # ---- Grab Ag/AgCl electrode information if K2401 is being used
            # Hardware Lines Stripped
            # ---- Calculate conductance values and uncertainties
#            print("input: ",Drain[0],Drain[1]) ## Keep for diagnostics; Off from 18SEP25 APM
            Dt.iloc[i,j] = 1000.0 - (nGrab * 100.0) + 200.0*(random.uniform(-1,1))  ## Goes to random to fake data pull
            Dterr.iloc[i,j] = 1.0 + 1.0*(random.uniform(-1,1)) ## Goes to random to fake data pull
            if nGrab == 0: # Populate the starting conductance dataframe on the first grab
                D0.iloc[i,j] = Dt.iloc[i,j]
            else: # Calculate the conductance difference dataframe on any subsequent grab
                dD.iloc[i,j] = Dt.iloc[i,j] - D0.iloc[i,j]
#            print(f'Dt = {Dt.iloc[i,j]:.2f} +/- {Dterr.iloc[i,j]:.2f} uS') ## Keep for diagnostics; Off from 15JAN24 APM
            # ---- Create the Ag/AgCl electrode data arrays if using K2401
            # Hardware Lines Stripped
            # ---- Make the Megatable Information
            RD[54*(nWord-1)+2*(nBit-1)+1] = round(Dt.iloc[i,j],3)
            RD[54*(nWord-1)+2*(nBit-1)+2] = round(Dterr.iloc[i,j],3)
            # ---- Decision tree below implements GuiUpdateMode switching of GUI updating from config.py -- New 11Sep25 APM
            if GuiUpdateMode == 'point':  # Update the GUI every datapair from the NIDAQ
                updateGUI()
            elif GuiUpdateMode == 'grab' and i == (nBits-1) and j == (nWords-1):  # Update the GUI only at the end of the grab
                print('Update GUI')
                updateGUI()
    for i in range(nBits): # Send data to file outside the acquisition loop to speed it up
        for j in range(nWords):
            # ---- send data from this grab to file
            with open(runPath + '/' + t + '_' + measurementName + '_G' + str(nRun) + '_Dev' + str(WordList[j]) + str(BitList[i]) + '.csv','a',newline='') as f:
                writer = csv.writer(f)
                if GateMode == 'K2401':
                    writer.writerow([str(nGrab+1),str(Dt.iloc[i,j]),str(Dterr.iloc[i,j]),str(Ig.iloc[i,j]),str(Vg.iloc[i,j]),str(datetime.now().strftime("%H:%M:%S"))])
                else:
                    writer.writerow([str(nGrab+1),str(Dt.iloc[i,j]),str(Dterr.iloc[i,j]),str(datetime.now().strftime("%H:%M:%S"))])
    #---- Drop all device data to megatable at end of grab
    with open(runPath+'/'+t+'_'+measurementName+'_G'+str(nRun)+'.csv','a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(RD[:])
    # ---- Run source voltage back to zero
    # Hardware Lines Stripped
    # ---- Run hold voltage back to zero
    # Hardware Lines Stripped
    # ---- Run Ag/AgCl electrode back to zero
    # Hardware Lines Stripped
    # ---- Switch Multiplexer to off state.
    # Hardware Lines Stripped
#    print('End of grab: ',nGrab+1) ## Keep for diagnostics; Off from 18JAN24 APM

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
                MegatableHeader.append('G_'+WordList[j]+BitList[i])
                MegatableHeader.append('dG_'+WordList[j]+BitList[i])
        writer.writerow(MegatableHeader)
    for i in range(nBits):
        for j in range(nWords):
            with open(runPath+'/'+t+'_'+measurementName+'_G'+str(nRun)+'_Dev'+WordList[j]+BitList[i]+'.csv', 'w', newline='') as f:
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
        GT = WaitAR-GrabTime[i]
        print(f'WaitAR = {WaitAR:.2f} s') ## Keep for diagnostics; Off from 11Sep25 APM
        print(f'GrabTime = {GrabTime[i]:.2f} s') ## Keep for diagnostics; Off from 11Sep25 APM
        print(f'GT = {GT:.2f} s') ## Keep for diagnostics; Off from 11Sep25 APM
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
    # Hardware Lines Stripped
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
    # Populates the sidebar
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
    # Creates the two frames needed for the figures
    left_figure = Frame(root)
    left_figure.grid(row=1,column=1,rowspan=6,padx=5,pady=5,sticky='nsew')
    right_figure = Frame(root)
    right_figure.grid(row=1,column=2,rowspan=6,padx=5,pady=5,sticky='nsew')
    # Generates the starting figures and assigns them to their frames
    figL = createFigL()
    canvasL = FigureCanvasTkAgg(figL,master=left_figure)
    figR = createFigR()
    canvasR = FigureCanvasTkAgg(figR,master=right_figure)
    # Draws the two plots into the GUI
    canvasL.draw()
    canvasL.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)
    canvasR.draw()
    canvasR.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)
    root.mainloop()