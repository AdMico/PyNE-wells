"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima
"""

import numpy as np
import random
import matplotlib.pyplot as plt

def rand_split(l, ratio=[0.8, 0.1, 0.1]):
    l1, l2, l3 = [], [], []
    for e in l:
        val = random.random()
        if val <= ratio[0]:
            l1.append(e)
        elif val <= ratio[1]+ratio[0]:
            l2.append(e)
        else:
            l3.append(e)
    return l1, l2, l3

def generate_data(device_list=np.array([i for i in range(1, 46)]),
                  repeats=50,
                  event_repeat=25,
                  percent_drop=0.1,
                  percent_rise=0.2,
                  drop_vs_rise=0.8,
                  plot=False,
                  print_Gf=False):

    l1, l2, l3 = rand_split(device_list)
    device_list = np.array(device_list)

    # Generate G1
    G1 = np.zeros(device_list.shape[0])
    for i, e in enumerate(device_list):
        if e in l1 or e in l2:
            G1[i] = 0.02 * np.random.randn(1) + 0.1
        else:
            G1[i] = 0

    # Generate G2
    G2 = np.zeros(device_list.shape[0])
    for i, e in enumerate(device_list):
        if e in l1:
            G2[i] = G1[i] - (0.005 * np.random.randn(1) + 0.15*G1[i])
        elif e in l2:
            G2[i] = G1[i] + (0.005 * np.random.randn(1) + 0.09*G1[i])
        else:
            G2[i] = 0

    Gf = np.zeros((device_list.shape[0], repeats))

    # Generate repeats
    for j in range(repeats):
        for i, e in enumerate(device_list):
            if j < event_repeat:
                Gf[i-1,j] = 0.0001 * np.random.randn(1) + G1[i-1]
            else:
                Gf[i-1, j] = 0.0001 * np.random.randn(1) + G2[i-1]

    if plot:
        x = np.arange(len(device_list))
        for i,e in enumerate(device_list):
            plt.plot([r for r in range(repeats)],Gf[i-1])

    if print_Gf:
        print(Gf)

    return Gf

def generate_IV(G, V_SD):
    V_SD = np.array(V_SD)
    noise = np.random.randn(V_SD.shape[0])
    I = V_SD*G*(1+0.01*noise)
    return I

if __name__ == '__main__':
    deviceList = [i for i in range(4, 12)]
    repeats = 10
    event_repeat = 5
    G_data = generate_data(device_list=deviceList, repeats=repeats, event_repeat=event_repeat, plot=True)
    I_SD = generate_IV(1, [1, 2, 3])
