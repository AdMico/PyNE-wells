"""
Brought to PyNE-wells v1.2.0 on Thu Nov 06 2025 by APM

@developers: Adam Micolich & Jan Gluschke

Initialisation data for the two Seaborn plots in AssayRunGen5.py
"""

import numpy as np
import pandas as pd

nWords = 27
nBits = 27
WordList = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','&','Z','Y','X','W','V','U','T','S','R','Q','P','O']
WordList2 = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','&']
BitList = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27']
Dt = pd.DataFrame(np.zeros((nBits,nWords),dtype='float'),columns=WordList2,index=BitList)
dD = pd.DataFrame(np.zeros((nBits,nWords),dtype='float'),columns=WordList2,index=BitList)

def dataInit(): # Generates the initialisation data for the two Seaborn plots
    global Dt,dD
    DtCentre = 1000.0
    DtSpread = 100.0
    dDCentre = 0.0
    dDSpread = 10.0
    for i in range(nBits): # Generate central value for colour scale
        for j in range(nWords):
            Dt.iloc[i,j] = DtCentre
            dD.iloc[i,j] = dDCentre
    # Dt Map-out, 4x cardinals then word 'hello'
    # Cardinals
    Dt.iloc[0,0] = DtCentre-DtSpread
    Dt.iloc[0,26] = DtCentre-(DtSpread/2.0)
    Dt.iloc[26,0] = DtCentre+(DtSpread/2.0)
    Dt.iloc[26,26] = DtCentre+DtSpread
    # H
    Dt.iloc[11,4] = DtCentre-DtSpread
    Dt.iloc[12,4] = DtCentre-DtSpread
    Dt.iloc[13,4] = DtCentre-DtSpread
    Dt.iloc[14,4] = DtCentre-DtSpread
    Dt.iloc[15,4] = DtCentre-DtSpread
    Dt.iloc[13,5] = DtCentre-DtSpread
    Dt.iloc[11,6] = DtCentre-DtSpread
    Dt.iloc[12,6] = DtCentre-DtSpread
    Dt.iloc[13,6] = DtCentre-DtSpread
    Dt.iloc[14,6] = DtCentre-DtSpread
    Dt.iloc[15,6] = DtCentre-DtSpread
    # E
    Dt.iloc[11,8] = DtCentre-DtSpread
    Dt.iloc[12,8] = DtCentre-DtSpread
    Dt.iloc[13,8] = DtCentre-DtSpread
    Dt.iloc[14,8] = DtCentre-DtSpread
    Dt.iloc[15,8] = DtCentre-DtSpread
    Dt.iloc[11,9] = DtCentre-DtSpread
    Dt.iloc[13,9] = DtCentre-DtSpread
    Dt.iloc[15,9] = DtCentre-DtSpread
    Dt.iloc[11,10] = DtCentre-DtSpread
    Dt.iloc[15,10] = DtCentre-DtSpread
    # L
    Dt.iloc[11,12] = DtCentre-DtSpread
    Dt.iloc[12,12] = DtCentre-DtSpread
    Dt.iloc[13,12] = DtCentre-DtSpread
    Dt.iloc[14,12] = DtCentre-DtSpread
    Dt.iloc[15,12] = DtCentre-DtSpread
    Dt.iloc[15,13] = DtCentre-DtSpread
    Dt.iloc[15,14] = DtCentre-DtSpread
    # L
    Dt.iloc[11,16] = DtCentre-DtSpread
    Dt.iloc[12,16] = DtCentre-DtSpread
    Dt.iloc[13,16] = DtCentre-DtSpread
    Dt.iloc[14,16] = DtCentre-DtSpread
    Dt.iloc[15,16] = DtCentre-DtSpread
    Dt.iloc[15,17] = DtCentre-DtSpread
    Dt.iloc[15,18] = DtCentre-DtSpread
    # O
    Dt.iloc[11,20] = DtCentre-DtSpread
    Dt.iloc[12,20] = DtCentre-DtSpread
    Dt.iloc[13,20] = DtCentre-DtSpread
    Dt.iloc[14,20] = DtCentre-DtSpread
    Dt.iloc[15,20] = DtCentre-DtSpread
    Dt.iloc[11,21] = DtCentre-DtSpread
    Dt.iloc[15,21] = DtCentre-DtSpread
    Dt.iloc[11,22] = DtCentre-DtSpread
    Dt.iloc[12,22] = DtCentre-DtSpread
    Dt.iloc[13,22] = DtCentre-DtSpread
    Dt.iloc[14,22] = DtCentre-DtSpread
    Dt.iloc[15,22] = DtCentre-DtSpread
    # dD Map-out, 4x cardinals then word 'user'
    # Cardinals
    dD.iloc[0,0] = dDCentre-dDSpread
    dD.iloc[0,26] = dDCentre-(dDSpread/2.0)
    dD.iloc[26,0] = dDCentre+(dDSpread/2.0)
    dD.iloc[26,26] = dDCentre+dDSpread
    # U
    dD.iloc[11,6] = dDCentre-dDSpread
    dD.iloc[12,6] = dDCentre-dDSpread
    dD.iloc[13,6] = dDCentre-dDSpread
    dD.iloc[14,6] = dDCentre-dDSpread
    dD.iloc[15,6] = dDCentre-dDSpread
    dD.iloc[15,7] = dDCentre-dDSpread
    dD.iloc[11,8] = dDCentre-dDSpread
    dD.iloc[12,8] = dDCentre-dDSpread
    dD.iloc[13,8] = dDCentre-dDSpread
    dD.iloc[14,8] = dDCentre-dDSpread
    dD.iloc[15,8] = dDCentre-dDSpread
    # S
    dD.iloc[11,10] = dDCentre-dDSpread
    dD.iloc[12,10] = dDCentre-dDSpread
    dD.iloc[13,10] = dDCentre-dDSpread
    dD.iloc[15,10] = dDCentre-dDSpread
    dD.iloc[11,11] = dDCentre-dDSpread
    dD.iloc[13,11] = dDCentre-dDSpread
    dD.iloc[15,11] = dDCentre-dDSpread
    dD.iloc[11,12] = dDCentre-dDSpread
    dD.iloc[13,12] = dDCentre-dDSpread
    dD.iloc[14,12] = dDCentre-dDSpread
    dD.iloc[15,12] = dDCentre-dDSpread
    # E
    dD.iloc[11,14] = dDCentre-dDSpread
    dD.iloc[12,14] = dDCentre-dDSpread
    dD.iloc[13,14] = dDCentre-dDSpread
    dD.iloc[14,14] = dDCentre-dDSpread
    dD.iloc[15,14] = dDCentre-dDSpread
    dD.iloc[11,15] = dDCentre-dDSpread
    dD.iloc[13,15] = dDCentre-dDSpread
    dD.iloc[15,15] = dDCentre-dDSpread
    dD.iloc[11,16] = dDCentre-dDSpread
    dD.iloc[15,16] = dDCentre-dDSpread
    # R
    dD.iloc[11,18] = dDCentre-dDSpread
    dD.iloc[12,18] = dDCentre-dDSpread
    dD.iloc[13,18] = dDCentre-dDSpread
    dD.iloc[14,18] = dDCentre-dDSpread
    dD.iloc[15,18] = dDCentre-dDSpread
    dD.iloc[11,19] = dDCentre-dDSpread
    dD.iloc[13,19] = dDCentre-dDSpread
    dD.iloc[11,20] = dDCentre-dDSpread
    dD.iloc[13,20] = dDCentre-dDSpread
    dD.iloc[14,20] = dDCentre-dDSpread
    dD.iloc[11,21] = dDCentre-dDSpread
    dD.iloc[12,21] = dDCentre-dDSpread
    dD.iloc[13,21] = dDCentre-dDSpread
    dD.iloc[15,21] = dDCentre-dDSpread
    return Dt,dD

def dataReset(): # Generates the reset data for the two Seaborn plots
    global Dt,dD
    DtCentre = 1000.0
    DtSpread = 100.0
    dDCentre = 0.0
    dDSpread = 10.0
    for i in range(nBits): # Generate central value for colour scale
        for j in range(nWords):
            Dt.iloc[i,j] = DtCentre
            dD.iloc[i,j] = dDCentre
    # Dt Map-out, 4x cardinals then word 'hello'
    # Cardinals
    Dt.iloc[0,0] = DtCentre-DtSpread
    Dt.iloc[0,26] = DtCentre-(DtSpread/2.0)
    Dt.iloc[26,0] = DtCentre+(DtSpread/2.0)
    Dt.iloc[26,26] = DtCentre+DtSpread
    # R
    Dt.iloc[11,3] = DtCentre-DtSpread
    Dt.iloc[12,3] = DtCentre-DtSpread
    Dt.iloc[13,3] = DtCentre-DtSpread
    Dt.iloc[14,3] = DtCentre-DtSpread
    Dt.iloc[15,3] = DtCentre-DtSpread
    Dt.iloc[11,4] = DtCentre-DtSpread
    Dt.iloc[13,4] = DtCentre-DtSpread
    Dt.iloc[11,5] = DtCentre-DtSpread
    Dt.iloc[13,5] = DtCentre-DtSpread
    Dt.iloc[14,5] = DtCentre-DtSpread
    Dt.iloc[11,6] = DtCentre-DtSpread
    Dt.iloc[12,6] = DtCentre-DtSpread
    Dt.iloc[13,6] = DtCentre-DtSpread
    Dt.iloc[15,6] = DtCentre-DtSpread
    # E
    Dt.iloc[11,8] = DtCentre-DtSpread
    Dt.iloc[12,8] = DtCentre-DtSpread
    Dt.iloc[13,8] = DtCentre-DtSpread
    Dt.iloc[14,8] = DtCentre-DtSpread
    Dt.iloc[15,8] = DtCentre-DtSpread
    Dt.iloc[11,9] = DtCentre-DtSpread
    Dt.iloc[13,9] = DtCentre-DtSpread
    Dt.iloc[15,9] = DtCentre-DtSpread
    Dt.iloc[11,10] = DtCentre-DtSpread
    Dt.iloc[15,10] = DtCentre-DtSpread
    # S
    Dt.iloc[11,12] = DtCentre-DtSpread
    Dt.iloc[12,12] = DtCentre-DtSpread
    Dt.iloc[13,12] = DtCentre-DtSpread
    Dt.iloc[15,12] = DtCentre-DtSpread
    Dt.iloc[11,13] = DtCentre-DtSpread
    Dt.iloc[13,13] = DtCentre-DtSpread
    Dt.iloc[15,13] = DtCentre-DtSpread
    Dt.iloc[11,14] = DtCentre-DtSpread
    Dt.iloc[13,14] = DtCentre-DtSpread
    Dt.iloc[14,14] = DtCentre-DtSpread
    Dt.iloc[15,14] = DtCentre-DtSpread
    # E
    Dt.iloc[11,16] = DtCentre-DtSpread
    Dt.iloc[12,16] = DtCentre-DtSpread
    Dt.iloc[13,16] = DtCentre-DtSpread
    Dt.iloc[14,16] = DtCentre-DtSpread
    Dt.iloc[15,16] = DtCentre-DtSpread
    Dt.iloc[11,17] = DtCentre-DtSpread
    Dt.iloc[13,17] = DtCentre-DtSpread
    Dt.iloc[15,17] = DtCentre-DtSpread
    Dt.iloc[11,18] = DtCentre-DtSpread
    Dt.iloc[15,18] = DtCentre-DtSpread
    # T
    Dt.iloc[11,20] = DtCentre-DtSpread
    Dt.iloc[11,21] = DtCentre-DtSpread
    Dt.iloc[12,21] = DtCentre-DtSpread
    Dt.iloc[13,21] = DtCentre-DtSpread
    Dt.iloc[14,21] = DtCentre-DtSpread
    Dt.iloc[15,21] = DtCentre-DtSpread
    Dt.iloc[11,22] = DtCentre-DtSpread
    # dD Map-out, 4x cardinals then word 'user'
    # Cardinals
    dD.iloc[0,0] = dDCentre-dDSpread
    dD.iloc[0,26] = dDCentre-(dDSpread/2.0)
    dD.iloc[26,0] = dDCentre+(dDSpread/2.0)
    dD.iloc[26,26] = dDCentre+dDSpread
    # R
    dD.iloc[11,3] = dDCentre-dDSpread
    dD.iloc[12,3] = dDCentre-dDSpread
    dD.iloc[13,3] = dDCentre-dDSpread
    dD.iloc[14,3] = dDCentre-dDSpread
    dD.iloc[15,3] = dDCentre-dDSpread
    dD.iloc[11,4] = dDCentre-dDSpread
    dD.iloc[13,4] = dDCentre-dDSpread
    dD.iloc[11,5] = dDCentre-dDSpread
    dD.iloc[13,5] = dDCentre-dDSpread
    dD.iloc[14,5] = dDCentre-dDSpread
    dD.iloc[11,6] = dDCentre-dDSpread
    dD.iloc[12,6] = dDCentre-dDSpread
    dD.iloc[13,6] = dDCentre-dDSpread
    dD.iloc[15,6] = dDCentre-dDSpread
    # E
    dD.iloc[11,8] = dDCentre-dDSpread
    dD.iloc[12,8] = dDCentre-dDSpread
    dD.iloc[13,8] = dDCentre-dDSpread
    dD.iloc[14,8] = dDCentre-dDSpread
    dD.iloc[15,8] = dDCentre-dDSpread
    dD.iloc[11,9] = dDCentre-dDSpread
    dD.iloc[13,9] = dDCentre-dDSpread
    dD.iloc[15,9] = dDCentre-dDSpread
    dD.iloc[11,10] = dDCentre-dDSpread
    dD.iloc[15,10] = dDCentre-dDSpread
    # S
    dD.iloc[11,12] = dDCentre-dDSpread
    dD.iloc[12,12] = dDCentre-dDSpread
    dD.iloc[13,12] = dDCentre-dDSpread
    dD.iloc[15,12] = dDCentre-dDSpread
    dD.iloc[11,13] = dDCentre-dDSpread
    dD.iloc[13,13] = dDCentre-dDSpread
    dD.iloc[15,13] = dDCentre-dDSpread
    dD.iloc[11,14] = dDCentre-dDSpread
    dD.iloc[13,14] = dDCentre-dDSpread
    dD.iloc[14,14] = dDCentre-dDSpread
    dD.iloc[15,14] = dDCentre-dDSpread
    # E
    dD.iloc[11,16] = dDCentre-dDSpread
    dD.iloc[12,16] = dDCentre-dDSpread
    dD.iloc[13,16] = dDCentre-dDSpread
    dD.iloc[14,16] = dDCentre-dDSpread
    dD.iloc[15,16] = dDCentre-dDSpread
    dD.iloc[11,17] = dDCentre-dDSpread
    dD.iloc[13,17] = dDCentre-dDSpread
    dD.iloc[15,17] = dDCentre-dDSpread
    dD.iloc[11,18] = dDCentre-dDSpread
    dD.iloc[15,18] = dDCentre-dDSpread
    # T
    dD.iloc[11,20] = dDCentre-dDSpread
    dD.iloc[11,21] = dDCentre-dDSpread
    dD.iloc[12,21] = dDCentre-dDSpread
    dD.iloc[13,21] = dDCentre-dDSpread
    dD.iloc[14,21] = dDCentre-dDSpread
    dD.iloc[15,21] = dDCentre-dDSpread
    dD.iloc[11,22] = dDCentre-dDSpread
    return Dt,dD