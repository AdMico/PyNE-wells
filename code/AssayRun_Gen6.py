"""
Brought to PyNE-wells v2.0.0 on Thu Apr 30 2026 by APM

@developers: Adam Micolich & Jan Gluschke

Main software for running assays.

Adam's to do list follows -- Updated APM 26Aug26
* Consider ability to functionally switch the gate and hold setup if VHold is always zero.
"""

from TeensyInterface_Gen6 import TeensyMUX
from ConfigInterpreter_Gen6 import ConfigInterp
import GlobalMeasID as ID
from Config_Gen6 import SourceInst,DrainInst,HoldInst,GateInst,VSource,VGate,VHold,ItersAR,WaitAR,basePath,GuiUpdateMode,DrainExt,GateExt,ScanDir
from Config_Gen6 import PlotTwoMode,SourceCurrMode,HoldCurrMode,DrainType,Operation
from SeabornInit import dataInit,dataReset
from Keithley2401 import Keithley2401
from MCC152Out import MCC152Out
from MCC128InSB import MCC128InSB
from MCC128InSS import MCC128InSS
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
Is = pd.DataFrame(np.zeros((nBits,nWords), dtype='float'),columns=WordList2,index=BitList) # New for source current measurement for Gen 6 -- 12Aug26 APM
Ih = pd.DataFrame(np.zeros((nBits,nWords), dtype='float'),columns=WordList2,index=BitList) # New for hold current measurement for Gen 6 -- 12Aug26 APM
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
SourceOut = ConfigInterp.SourceVoltage()
HoldOut = ConfigInterp.HoldVoltage()
DrainIn = ConfigInterp.DrainCurrent()
GateIn = ConfigInterp.GateCurrent()
SourceIn = ConfigInterp.SourceCurrent()
HoldIn = ConfigInterp.HoldCurrent()
SR = ConfigInterp.SR()
SpC = ConfigInterp.SpC()
PDGain = ConfigInterp.PDGain()
PGGain = ConfigInterp.PGGain()
PSGain = ConfigInterp.PSGain()
PHGain = ConfigInterp.PHGain()
PDRange = ConfigInterp.PDRange()
PGRange = ConfigInterp.PGRange()
PSRange = ConfigInterp.PSRange()
PHRange = ConfigInterp.PHRange()
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
               'ADC Sample Rate: ' + str(SR) + ' Hz' + '\n' +
               'ADC Samples per Channel: ' + str(SpC) + '\n' +
               'Number of Grabs: ' + str(ItersAR) + '\n' +
               'Time between Grabs: ' + str(WaitAR) + ' s' + '\n' +
               'Scan direction: ' + ScanDir + '\n' +
               'Source Instrument Mode: ' + SourceInst + '\n' +
               'Source Voltage on: ' + SourceOut + '\n' +
               'Source Voltage: ' + str(VSource) + ' V' + '\n' +
               'Hold Instrument Mode: ' + HoldInst + '\n' +
               'Hold Voltage on: ' + HoldOut + '\n' +
               'Hold Voltage: ' + str(VHold) + ' V' + '\n' +
               'Drain Instrument Mode: ' + DrainInst + '\n' +
               'Drain Current on: ' + DrainIn + '\n' +
               'Ag/AgCl Instrument Mode: ' + GateInst + '\n' +
               'Ag/AgCl electrode on: ' + GateIn + '\n' +
               'Gate Voltage: ' + str(VGate) + ' V' + '\n' +
               'Source Current on: ' + SourceIn + '\n' +
               'Hold Current on: ' + HoldIn + '\n' +
               'Drain Preamp gain: ' + str(PDGain) + '\n' +
               'Gate Preamp gain: ' + str(PGGain) + '\n' +
               'Source Preamp gain: ' + str(PSGain) + '\n' +
               'Hold Preamp gain: ' + str(PHGain) + '\n' +
               'Drain Preamp range: ' + PDRange + '\n' +
               'Gate Preamp range: ' + PGRange + '\n' +
               'Source Preamp range: ' + PSRange + '\n' +
               'Hold Preamp range: ' + PHRange + '\n\n'
               )

#---- Initialization of instruments
print ('Initialise instruments') ## Keep for diagnostics
# ---- Raspberry Pi --------------
CtrlTy = TeensyMUX()
CtrlTy.SysInit()  # Initialises the multiplexer system for running a measurement
#---- Source instrument Initialisation
if SourceInst == 'External':
    # ---- Keithley2401 for Source Voltage --------------
    daqout_S = Keithley2401(1)
    daqout_S.setOptions({"beepEnable":False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05E-2,"compliance":20.0E-3,"scaleFactor":1})
    if SourceCurrMode == "Active":
        daqin_S = Keithley2401(1)
        daqin_S.setOptions({"beepEnable":False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05E-2,"compliance":20.0E-3,"scaleFactor":1})
elif SourceInst == 'Internal':
    # ---- MCC152 Output Port for Source Voltage --------------
    daqout_S = MCC152Out(0)
    daqout_S.setOptions({"scaleFactor":1})
    if SourceCurrMode == 'Active':
        # ---- MCC128 Input Port for Source Current Measurement --------------
        daqin_S = MCC128InSS(4,PSRange)
        daqin_S.setOptions({"scaleFactor":1})
#---- Drain Instrument Initialisation
if DrainInst == 'External':
    # ---- Keithley2401 for Drain Current --------------
    daqin_D = Keithley2401(2)
    daqin_D.setOptions({"beepEnable":False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05E-2,"compliance":20.0E-3,"scaleFactor":1})
elif DrainInst == 'Internal':
    # ---- MCC128 Input Port for Drain Current --------------
    if DrainType == 'Burst':
        daqin_D = MCC128InSB(0,PDRange)
        daqin_D.setOptions({"scaleFactor":1})
    elif DrainType == 'Single':
        daqin_D = MCC128InSS(0,PDRange)
        daqin_D.setOptions({"scaleFactor":1})
#---- Hold Instrument Initialisation
if HoldInst == 'External':
    # ---- Keithley2401 for Drain Current --------------
    daqout_H = Keithley2401(3)
    daqout_H.setOptions({"beepEnable":False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05E-2,"compliance":20.0E-3,"scaleFactor":1})
    if HoldCurrMode == "Active":
        daqin_H = Keithley2401(3)
        daqin_H.setOptions({"beepEnable":False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05E-2,"compliance":20.0E-3,"scaleFactor":1})
elif HoldInst == 'Internal':
    # ---- MCC152 Output Port for Hold Voltage --------------
    daqout_H = MCC152Out(1)
    daqout_H.setOptions({"scaleFactor":1})
    if HoldCurrMode == 'Active':
        # ---- MCC128 Input Port for Hold Current Measurement --------------
        daqin_H = MCC128InSS(5,PHRange)
        daqin_H.setOptions({"scaleFactor":1})
#---- Gate Instrument Initialisation
if GateInst == 'External':
    #---- Keithley 2401 or MCC128 Input Port for Femto for Ag/AgCl electrode current measurement --------------
    if GateExt == 'K2401':
        daqout_G = Keithley2401(4)
        daqout_G.setOptions({"beepEnable": False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05E-4,"compliance":1.0E-4,"scaleFactor":1})
        daqin_G = Keithley2401(4)
        daqin_G.setOptions({"beepEnable":False,"sourceMode":"voltage","sourceRange":10,"senseRange":1.05E-4,"compliance":1.0E-4,"scaleFactor":1})
    elif GateExt == 'Femto':
        daqin_G = MCC128InSS(3)
        daqin_G.setOptions({"scaleFactor": 1})
elif GateInst == 'Internal':
    # ---- MCC128 Input Port for Ag/AgCl electrode current Measurement --------------
    daqin_G = MCC128InSS(1,PGRange)
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
    daqout_S.goTo(0.0,delay=0.0)  # Run the source line back to zero
    daqout_H.goTo(0.0,delay=0.0)  # Run the hold line back to zero
    if (GateInst == "External" and GateExt == 'K2401'):
        daqout_G.goTo(0.0,delay=0.0)  # Run the gate line back to zero if using a K2401
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
    daqout_S.goTo(abs(VSource),delay=0.0)  # Run the source line up to specified voltage -- Edited to abs() 02SEP26 APM to deal with unipolarity of MCC152
    daqout_H.goTo(abs(VHold),delay=0.0)  # Run the hold line up to specified voltage -- Edited to abs() 02SEP26 APM to deal with unipolarity of MCC152
    if (GateInst == 'External' and GateExt == 'K2401' and VGate != 0.0):
        daqout_G.goTo(VGate,delay=0.0)  # Run the gate up to specified voltage if it's a Keithley and VGate is non-zero -- edited 09AUG26 APM
    RD[0]=nGrab+1
    print('Measuring...')
    if ScanDir == 'Horizontal': # Implements data pull by scanning along bitlines starting from 1
        for i in range(nBits):
            for j in range(nWords):
                k = mapper(j)
                # print('Measuring: ',WordList[k],BitList[i]) ## Keep for diagnostics; Off from 26AUG26 APM
                if (i == 0 and j == 0): # If this is the first node, then switch that node to measure
                    CtrlTy.nodeToMeasure(k+1,i+1)
                # ---- Set given device to measure
                SBStart[i,j] = time.time()
                #---- Grab device data
                if DrainInst == 'External':
                    Drain = daqin_D.get('senseLevel')
                elif DrainInst == 'Internal':
                    Drain = daqin_D.get('inputLevel')
                # ---- Calculate conductance values and uncertainties
                if Operation == 'Verbose':
                    if DrainInst == 'Internal':
                        if DrainType == 'Burst':
                            print (i,j,Drain[0],Drain[1],VSource,PDGain)
                        elif DrainType == 'Single':
                            print(i, j, Drain, VSource, PDGain)
                        time.sleep(10)
                    elif DrainInst == 'External':
                        print(i,j,Drain[0],Drain[1],VSource,PDGain)
                        time.sleep(10)
                if DrainInst == 'External':
                    Dt.iloc[i,j] = abs((Drain[0]/(VSource*PDGain))/1e-6)  ## Updated to Conductance in microsiemens -- 30Oct25 APM
                    Dterr.iloc[i, j] = 0.0
                elif DrainInst == 'Internal':
                    if DrainType == 'Burst':
                        Dt.iloc[i,j] = abs((Drain[0]/(VSource*PDGain))/1e-6)  ## Updated to Conductance in microsiemens -- 30Oct25 APM
                        Dterr.iloc[i,j] = abs((Drain[1]/Drain[0])*Dt.iloc[i,j])
                    elif DrainType == 'Single':
                        Dt.iloc[i,j] = abs((Drain/(VSource*PDGain))/1e-6)  ## Updated to Conductance in microsiemens -- 30Oct25 APM
                        Dterr.iloc[i,j] = 0.0
                # ---- Generate the Ag/AgCl electrode data arrays -- edited for all options 09AUG26 APM
                if GateInst == 'Internal':
                    Ig.iloc[i, j] = daqin_G.get('inputLevel')
                elif GateInst == 'External':
                    if GateExt == 'K2401':
                        AgCl = daqin_G.get('senseLevel')
                        Ig.iloc[i,j] = AgCl[0]
                    else:
                        Ig.iloc[i,j] = daqin_G.get('inputLevel')
                # ---- If Instruments in Internal Mode and SourceHoldCurrent is Active get the source and hold currents -- Added 12AUG26 APM
                if SourceCurrMode == 'Active':
                    if SourceInst == 'Internal':
                        Is.iloc[i,j] = daqin_S.get('inputLevel')
                    elif SourceInst == 'External':
                        SC = daqin_S.get('senseLevel')
                        Is.iloc[i,j] = SC[0]
                if HoldCurrMode == 'Active':
                    if HoldInst == 'Internal':
                        Ih.iloc[i,j] = daqin_H.get('inputLevel')
                    elif HoldInst == 'External':
                        HC = daqin_H.get('senseLevel')
                        Ih.iloc[i,j] = HC[0]
                if (j == (nWords-1)): # if the end of the bit line then
                    if (i == (nBits-1)): # check if this is the last bit line
                        CtrlTy.nodeToHold(k+1,i+1) # Set node back to hold because that's the end of the array
                    else:
                        CtrlTy.wordShift(k+1,1) # Shift the word line back to the first row
                        CtrlTy.bitShift(i+1,i+2) # Shift to the next bit line
                else: # if this isn't the end of the bit line
                    kNext = mapper(j+1) # Work out the next word line, bearing in mind wordline mapping
                    CtrlTy.wordShift(k+1,kNext+1) # Shift to next word line
                if GuiUpdateMode == 'point':  # Update the GUI after each device in the array (n.b. much much slower)
                    updateGUI()
    elif ScanDir == 'Vertical': # implements scan along wordlines starting from A
        for j in range(nWords):
            for i in range(nBits):
                k = mapper(j)
                # print('Measuring: ', WordList[k], BitList[i])  ## Keep for diagnostics; Off from 27Aug26 APM
                if (i == 0 and j == 0): # If this is the first node, then switch that node to measure
                    CtrlTy.nodeToMeasure(k+1,i+1)
                SBStart[i,j] = time.time()
                # ---- Grab device data
                if DrainInst == 'External':
                    Drain = daqin_D.get('senseLevel')
                elif DrainInst == 'Internal':
                    Drain = daqin_D.get('inputLevel')
                # ---- Calculate conductance values and uncertainties
                if Operation == 'Verbose':
                    if DrainInst == 'Internal':
                        if DrainType == 'Burst':
                            print (i,j,Drain[0],Drain[1],VSource,PDGain)
                        elif DrainType == 'Single':
                            print(i,j,Drain,VSource,PDGain)
                        time.sleep(10)
                    elif DrainInst == 'External':
                        print(i,j,Drain[0],Drain[1],VSource,PDGain)
                        time.sleep(10)
                if DrainInst == 'External':
                    Dt.iloc[i,j] = abs((Drain[0]/(VSource*PDGain))/1e-6)  ## Updated to Conductance in microsiemens -- 30Oct25 APM
                    Dterr.iloc[i, j] = 0.0
                elif DrainInst == 'Internal':
                    if DrainType == 'Burst':
                        Dt.iloc[i,j] = abs((Drain[0]/(VSource*PDGain))/1e-6)  ## Updated to Conductance in microsiemens -- 30Oct25 APM
                        Dterr.iloc[i,j] = abs((Drain[1]/Drain[0])*Dt.iloc[i,j])
                    elif DrainType == 'Single':
                        Dt.iloc[i,j] = abs((Drain/(VSource*PDGain))/1e-6)  ## Updated to Conductance in microsiemens -- 30Oct25 APM
                        Dterr.iloc[i,j] = 0.0
                # ---- Generate the Ag/AgCl electrode data arrays -- edited for all options 09AUG26 APM
                if GateInst == 'Internal':
                    Ig.iloc[i, j] = daqin_G.get('inputLevel')
                elif GateInst == 'External':
                    if GateExt == 'K2401':
                        AgCl = daqin_G.get('senseLevel')
                        Ig.iloc[i,j] = AgCl[0]
                    else:
                        Ig.iloc[i,j] = daqin_G.get('inputLevel')
                # ---- If Instruments in Internal Mode and SourceHoldCurrent is Active get the source and hold currents -- Added 12AUG26 APM
                if SourceCurrMode == 'Active':
                    if SourceInst == 'Internal':
                        Is.iloc[i,j] = daqin_S.get('inputLevel')
                    elif SourceInst == 'External':
                        SC = daqin_S.get('senseLevel')
                        Is.iloc[i,j] = SC[0]
                if HoldCurrMode == 'Active':
                    if HoldInst == 'Internal':
                        Ih.iloc[i,j] = daqin_H.get('inputLevel')
                    elif HoldInst == 'External':
                        HC = daqin_H.get('senseLevel')
                        Ih.iloc[i,j] = HC[0]
                if (i == (nBits-1)): # if the end of the word line then
                    if (j == (nWords-1)): # check if this is the last word line
                        CtrlTy.nodeToHold(k+1,i+1) # Set node back to hold because that's the end of the array
                    else:
                        CtrlTy.bitShift(i+1,1) # Shift the bit line back to the first row
                        kNext = mapper(j+1)  # Work out the next word line, bearing in mind wordline mapping
                        CtrlTy.wordShift(k+1,kNext+1) # Shift to the next word line
                else: # if this isn't the end of the word line
                    CtrlTy.bitShift(i+1,i+2) # Shift to next word line
                if GuiUpdateMode == 'point':  # Update the GUI after each device in the array (n.b. much much slower)
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
                if (SourceCurrMode == 'Active' and HoldCurrMode == 'Active'):
                    writer.writerow([str(nGrab+1),str(Dt.iloc[i,j]),str(Dterr.iloc[i,j]),str(Ig.iloc[i,j]),str(Is.iloc[i,j]),str(Ih.iloc[i,j]),str(datetime.now().strftime("%H:%M:%S"))])
                elif (SourceCurrMode == 'Active' and HoldCurrMode == 'Inactive'):
                    writer.writerow([str(nGrab+1),str(Dt.iloc[i,j]),str(Dterr.iloc[i,j]),str(Ig.iloc[i,j]),str(Is.iloc[i,j]),str(datetime.now().strftime("%H:%M:%S"))])
                elif (SourceCurrMode == 'Inactive' and HoldCurrMode == 'Active'):
                    writer.writerow([str(nGrab+1),str(Dt.iloc[i,j]),str(Dterr.iloc[i,j]),str(Ig.iloc[i,j]),str(Ih.iloc[i,j]),str(datetime.now().strftime("%H:%M:%S"))])
                else: # Include Drain and Gate information only.
                    writer.writerow([str(nGrab+1),str(Dt.iloc[i,j]),str(Dterr.iloc[i,j]),str(Ig.iloc[i,j]),str(datetime.now().strftime("%H:%M:%S"))])
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
    if (GateInst == 'External' and GateExt == 'K2401' and VGate != 0.0):
        daqout_G.goTo(0.0,delay=0.0)
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
                if (SourceCurrMode == 'Active' and HoldCurrMode == 'Active'):
                    writer.writerow(['Grab','Conductance (uS)','Uncertainty (uS)','Ig (A)','Is (A)','Ih (A)','timestamp'])
                elif (SourceCurrMode == 'Active' and HoldCurrMode == 'Inactive'):
                    writer.writerow(['Grab','Conductance (uS)','Uncertainty (uS)','Ig (A)','Is (A)','timestamp'])
                elif (SourceCurrMode == 'Inactive' and HoldCurrMode == 'Active'):
                    writer.writerow(['Grab','Conductance (uS)','Uncertainty (uS)','Ig (A)','Ih (A)','timestamp'])
                else:
                    writer.writerow(['Grab','Conductance (uS)','Uncertainty (uS)','Ig (A)','timestamp'])
    for i in range(ItersAR):
        nGrab = i
        GrabStart[i] = time.time()
        grab(nGrab)
        GrabEnd[i] = time.time()
        GrabTime[i] = GrabEnd[i] - GrabStart[i]
        GT = WaitAR - GrabTime[i]
        print(f'WaitAR = {WaitAR:.2f} s') ## Keep for diagnostics
        print(f'Grab Time = {GrabTime[i]:.2f} s') ## Keep for diagnostics
        print(f'Pause = {GT:.2f} s') ## Keep for diagnostics
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
    print('Finish Set-up')  ## Keep for diagnostics
    # ---- Reset the switch box to defaults.
    CtrlTy.SysReset()

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