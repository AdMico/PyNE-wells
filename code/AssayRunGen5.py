"""
Brought to PyNE-wells v1.2.0 on Thu Aug 07 2025 by APM

@developers: Adam Micolich & Jan Gluschke

Main software for running assays.
"""

from PiControlGen5 import PiMUX
import GlobalMeasID as ID
from Config import P1Gain, VSource, ItersAR, WaitAR, zeroThres, basePath, SR, SpC
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time
from datetime import datetime,date
from tkinter import *
import tkinter as tk
from pandastable import Table, TableModel
import pandastable as pdtb
import threading
import os
import csv

#---- Initialization of data structures
nWords = 27
nBits = 27
nDev = nWords*nBits
devices = np.zeros(nWords*nBits)
DD = pd.DataFrame(np.zeros((nWords,nBits,ItersAR),dtype='float'))
DDerr = pd.DataFrame(np.zeros((nWords,nBits,ItersAR),dtype='float'))
GUIFrame = pd.DataFrame(np.zeros((nRows,4)),columns=['Device ID','Resistance','Uncertainty','Timestamp'],dtype='object')
RD = np.zeros(1459)
SBStart = np.zeros(nWords,nBits) # For use in determining time taken to obtain measurements from USB6216
SBEnd = np.zeros(nWords,nBits) # For use in determining time taken to obtain measurements from USB6216
SBTime = np.zeros(nWords,nBits) # For use in determining time taken to obtain measurements from USB6216
SBElapsed = np.zeros(ItersAR) # For use in determining time taken to obtain measurements from USB6216
SBAverage = np.zeros(ItersAR) # For use in determining time taken to obtain measurements from USB6216
GrabStart = np.zeros(ItersAR) # For use in determining time taken to run a grab
GrabEnd = np.zeros(ItersAR) # For use in determining time taken to run a grab
GrabTime = np.zeros(ItersAR) # for use in determining time taken to run a grab
GrabTime[:] = np.nan
WordList = ['OFF','A','B','C','D','E','F','G','H','I','J','K','L','M','N','&','Z','Y','X','W','V','U','T','S','R','Q','P','O']
BitList = ['OFF','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27']
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
               'NIDAQ Sample Rate: ' + str(SR) + ' Hz' + '\n' +
               'NIDAQ Samples per Channel: ' + str(SpC) + '\n' +
               'Number of Grabs: ' + str(ItersAR) + '\n' +
               'Time between Grabs: ' + str(WaitAR) + ' s' + '\n \n'
               )

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
daqin_Drain = USB6216InSB(0)
daqin_Drain.setOptions({"scaleFactor":1})

def updateGUI(): # Updates the data in the GUI -- last edited APM 19Jan24
    global nGrab
    GUI_table.updateModel(TableModel(GUIFrame))
    GUI_table.redraw()
    assay = tk.Label(root, text=('Assay Number: '+t+'_'+measurementName),bg="skyblue")
    assay.grid(row=0,column=0,padx=5,pady=5)
    run = tk.Label(root, text=('Run Number: ' + str(nRun)),bg="skyblue")
    run.grid(row=1,column=0,padx=5,pady=5)
    grabNum = tk.Label(root, text=('Grab Number: '+str(nGrab+1)),bg="skyblue")
    grabNum.grid(row=3,column=0,padx=5,pady=5)
    grabTot = tk.Label(root, text=('of total grabs: '+ str(ItersAR)),bg="skyblue")
    grabTot.grid(row=4,column=0,padx=5,pady=5)
    root.update_idletasks()

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

def grab(nGrab,zeroThres): # Code to implement a single grab of all the devices on a chip -- last edited APM 17Jan24
    global nRun,RD
    print('Grab: ',nGrab+1)
    with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('Grab: '+str(nGrab+1)+' started: '+str(datetime.now())+'\n')
#    print('Start of grab: ',nGrab+1) ## Keep for diagnostics; Off from 18JAN24 APM
#    print('Set NIDAQ Voltage')  ## Keep for diagnostics; Off from 17JAN24 APM
    daqout_S.goTo(VSource, delay=0.0)  # Run the source up to specified voltage
    time.sleep(0.5) # Give time for MUXes to properly run up.
    RD[0]=nGrab+1
    for i in range(nWords):
        for j in range(nBits):
            nWord = i+1
            nBit = j+1
            print('Word = ',WordList[nWord],'Bit = ',BitList[nBit]) ## Keep for diagnostics; On from 16Oct25 APM
            # ---- Set multiplexer to given device
            CtrlPi.SysDevOn(nWord,nBit)
            SBStart[i,j] = time.time()
            #---- Grab device data from NIDAQ
            Drain = daqin_Drain.get('inputLevel')
            if Drain[0] > zeroThres: # Converts to resistance and sets open circuit to zero for left-bank devices
                DD.iloc[i,j,nGrab] = ((VSource*P1Gain)/Drain[0])
                DDerr.iloc[i,j,nGrab] = (Drain[1]/Drain[0])*DD.iloc[i,j,nGrab]
            else:
                DD.iloc[i,j,nGrab] = 0.0
                DDerr.iloc[i,j,nGrab] = 0.0
        #        print(f'DD = {DD.iloc[i,j,nGrab]:.2f} +/- {DDerr.iloc[i,j,nGrab]:.2f} ohms') ## Keep for diagnostics; Off from 15JAN24 APM
            CtrlPi.SysDevOff(nWord,nBit)
            RD[54*(nWord-1)+2*(nBit-1)] = round(DD.iloc[i,j,nGrab],3)
            RD[54*(nWord-1)+2*(nBit-1)+1] = round(DDerr.iloc[i,j,nGrab],3)
            # ---- send data to file
            with open(runPath + '/' + t + '_' + measurementName + '_R' + str(nRun) + '_Dev' + str(WordList[nWord]) + str(BitList[nBit]) + '.csv','a',newline='') as f:
                writer = csv.writer(f)
                writer.writerow([str(nGrab+1),str(DD.iloc[i,j,nGrab]),str(DDerr.iloc[i,j,nGrab]),str(datetime.now().strftime("%H:%M:%S"))])
            #---- Update data for the GUI
#            GUIFrame.iloc[nRow-1] = [nDevL,round(DL.iloc[i,nGrab],2),round(DLerr.iloc[i,nGrab],2),datetime.now().strftime("%H:%M:%S")] -- Commented until solved APM 16Oct25
            updateGUI()
            #---- End of row timing
            SBEnd[i,j] = time.time()
            SBTime[i,j] = SBEnd[i,j]-SBStart[i,j]
            SBElapsed[nGrab] = SBEnd[nWord-1,nBit-1]-SBStart[0,0]
            SBAverage[nGrab] = SBTime.mean()
    #---- Drop all device data to megatable at end of grab
    with open(runPath+'/'+t+'_'+measurementName+'_R'+str(nRun)+'.csv','a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(RD[:])
    # ---- Run source voltage back to zero
    daqout_S.goTo(0.0, delay=0.0)
    # ---- Switch Multiplexer to off state.
    CtrlPi.SysReset()
#    print('End of grab: ', nGrab+1) ## Keep for diagnostics; Off from 18JAN24 APM
    return SBElapsed,SBAverage

def measLoop():
    global measurementName,nRun,runPath,nGrab
    #---- Currently the main program
    with open(dataPath+'/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('Measurement '+measurementName+'R'+str(nRun)+' started at: '+str(datetime.now())+'\n')
    runPath = dataPath+'/'+t+'_'+measurementName+'_R'+str(nRun)
    if not os.path.exists(runPath):
        os.makedirs(runPath)
    with open(runPath+'/'+t+'_'+measurementName+'_R'+str(nRun)+'.csv','w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['Grab','R1','dR1','R2','dR2','R3','dR3','R4','dR4','R5','dR5','R6','dR6','R7','dR7','R8','dR8','R9','dR9','R10','dR10',
                         'R11','dR11','R12','dR12','R13','dR13','R14','dR14','R15','dR15','R16','dR16','R17','dR17','R18','dR18','R19','dR19','R20','dR20',
                         'R21','dR21','R22','dR22','R23','dR23','R24','dR24','R25','dR25','R26','dR26','R27','dR27','R28','dR28','R29','dR29','R30','dR30',
                         'R31','dR31','R32','dR32','R33','dR33','R34','dR34','R35','dR35','R36','dR36','R37','dR37','R38','dR38','R39','dR39','R40','dR40',
                         'R41','dR41','R42','dR42','R43','dR43','R44','dR44','R45','dR45','R46','dR46','R47','dR47','R48','dR48','R49','dR49','R50','dR50',
                         'R51','dR51','R52','dR52'])
    for i in range(nDev):
        with open(runPath+'/'+t+'_'+measurementName+'_R'+str(nRun)+'_Dev'+str(i+1)+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Grab','Resistance (ohms)','Uncertainty (ohms)','timestamp'])
    for i in range(ItersAR):
        nGrab = i
        GrabStart[i] = time.time()
        grab(nGrab,zeroThres)
        GrabEnd[i] = time.time()
        GrabTime[i] = GrabEnd[i] - GrabStart[i]
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
    # ---- Run source voltage back to zero
    daqout_S.goTo(0.0, delay=0.0)
    # ---- Switch Multiplexer to off state.
    CtrlPi.setMuxToOutput(0)
    CtrlPi.setRelayToOff()  # Switches multiplexer power off
    #root.quit() ## remove this line for the program to not quit at the end

if __name__ == "__main__":
    # GUI Code
    nGrab=0
    root = tk.Tk()
    root.title("Live Measurement GUI")
    root.geometry('1100x650')
#    root.maxsize(1200,800)
    root.config(bg="skyblue")
    left_table = Frame(root)
    left_table.grid(row=0,column=1,rowspan=7,padx=5,pady=5)
    right_table = Frame(root)
    right_table.grid(row=0,column=2,rowspan=7,padx=5,pady=5)
    GUI_tableL = Table(left_table,showtoolbar=False,showstatusbar=False,width=365,height=590)
    GUI_optionsL = {'align':'w','cellwidth':85,'floatprecision':2,'font':'Arial','fontsize':12,'linewidth':1,'rowheight':22}
    pdtb.config.apply_options(GUI_optionsL,GUI_tableL)
    GUI_tableR = Table(right_table,showtoolbar=False,showstatusbar=False,width=365,height=590)
    GUI_optionsR = {'align':'w','cellwidth':85,'floatprecision':2,'font':'Arial','fontsize':12,'linewidth':1,'rowheight':22}
    pdtb.config.apply_options(GUI_optionsR,GUI_tableR)
    GUI_tableL.show()
    GUI_tableR.show()
    GUI_tableL.updateModel(TableModel(GUIFrameL))
    GUI_tableR.updateModel(TableModel(GUIFrameR))
    assay = tk.Label(root,text=('Assay Number: '+t+'_'+measurementName),bg="skyblue")
    assay.grid(row=0,column=0,padx=5,pady=5)
    run = tk.Label(root, text=('Run Number: '+str(nRun)),bg="skyblue")
    run.grid(row=1, column=0, padx=5, pady=5)
    start_button = tk.Button(root, text='Start Run',command=lambda:grabStart())
    start_button.grid(row=2,column=0,padx=5,pady=5)
    grabNum = tk.Label(root, text=('Grab Number: '+str(nGrab+1)),bg="skyblue")
    grabNum.grid(row=3, column=0, padx=5, pady=5)
    grabTot = tk.Label(root, text=('of total grabs: '+str(ItersAR)),bg="skyblue")
    grabTot.grid(row=4, column=0, padx=5, pady=5)
    stop_button = tk.Button(root,text='Last Grab',command=lambda:stop())
    stop_button.grid(row=5,column=0,padx=5,pady=5)
    exit_button = tk.Button(root,text='End Program',command=lambda:[end(),root.quit()])
    exit_button.grid(row=6,column=0,padx=5,pady=5)
    root.mainloop()