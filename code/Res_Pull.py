"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

For debugging hardware setup
"""

from Imports import *
from Pi_control import PiMUX
import GlobalMeasID as ID
from Config import P1Gain, P2Gain, VSource, ItersAR, WaitAR, zeroThres, basePath, SR, SpC
import pandas as pd
import time
from datetime import datetime,date
from tkinter import *
import tkinter as tk
from pandastable import Table, TableModel
import pandastable as pdtb
import threading
import os
import csv

nRows = 26
nDev = 2*nRows
DL = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))
DLerr = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))
DR = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))
DRerr = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))

#---- NIDAQ Input Port for Drain running PairBurst on USB6216 --------------
daqin_Drain = USB6216InPB()
daqin_Drain.setOptions({"scaleFactor":1})

# ---- Grab row data from NIDAQ
nGrab=1
for i in range(nRows):
    Drain = daqin_Drain.get('inputLevel')
    if Drain[0] > zeroThres:  # Converts to resistance and sets open circuit to zero for left-bank devices
        DL.iloc[i, nGrab] = ((VSource * P1Gain) / Drain[0])
        DLerr.iloc[i, nGrab] = (Drain[1] / Drain[0]) * DL.iloc[i, nGrab]
    else:
        DL.iloc[i, nGrab] = 0.0
        DLerr.iloc[i, nGrab] = 0.0
    if Drain[2] > zeroThres:  # Converts to resistance and sets open circuit to zero for right-bank devices
        DR.iloc[i, nGrab] = ((VSource * P2Gain) / Drain[2])
        DRerr.iloc[i, nGrab] = (Drain[3] / Drain[2]) * DR.iloc[i, nGrab]
    else:
        DR.iloc[i, nGrab] = 0.0
        DRerr.iloc[i, nGrab] = 0.0
    print('Run: ',i+1)
    print(f'DL = {DL.iloc[i, nGrab]:.2f} +/- {DLerr.iloc[i, nGrab]:.2f} ohms')  ## Keep for diagnostics; Off from 15JAN24 APM
    print(f'DR = {DR.iloc[i, nGrab]:.2f} +/- {DRerr.iloc[i, nGrab]:.2f} ohms')  ## Keep for diagnostics; Off from 15JAN24 APM