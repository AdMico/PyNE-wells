"""
Brought to PyNE-wells v1.0.0 on Tue Feb 6 2024 by SK

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

Contents: Monitoring Id with MUX
Note:
---Config.py: MuxMode = 'test'
"""

import pandas as pd
import os
from Pi_control import PiMUX
import collections.abc
collections.Iterable = collections.abc.Iterable # Quick and dirty fix for V4.0, implement properly later.
from Imports2 import *
import glob
import shutil

"""
Create folders
"""

print('Select directory to create two folders:1. Monitoring Id')

[basePath,fileName] = fileDialog()
list = ['Monitoring Id']

for items in list:
    os.mkdir(basePath + items)

print('1 folders have been created.')

# Define device/instruments
currentVoltagePreAmp_gain = 1E4
my_Pi = PiMUX()  # sets up raspberry pi
daqout_S = USB6216Out(0)  # sets up NIDAQ
daqout_S.setOptions({
        "feedBack": "Int",
        "extPort": 0,  # Can be any number 0-7 if in 'Int'
        "scaleFactor": 1
    })
daqin_D = USB6216In(0)  # sets up NIDAQ
daqin_D.set('scaleFactor', currentVoltagePreAmp_gain)  # sets up NIDAQ to work with the current preamp

my_Pi.setMuxToOutput(0)  # sets multiplexer to state with all outputs off

# ---Keithley Vg -----------
KVg = Keithley2401(27)
KVg.setOptions({
        "beepEnable": False,
        "sourceMode": "voltage",
        "sourceRange": 10,
        # "senseRange": 1.05e-6,
        # "compliance": 1.0E-2,
        "scaleFactor": 1
    })

"""
Monitoring Id
"""

print('Monitoring Id')

os.chdir(r"C:\Users\z5345591\PycharmProjects\Nanowells_4p0b\Code")

Vsd = -0.5
Vg = 0
daqout_S.goTo(Vsd, delay=0.001)
KVg.goTo(Vg, delay=0.001)
# Time
T = 1;
time = TimeMeas(
    T)  # Note! GPIB number serves instead as wait time interval for TimeMeas.py. Do not make this huge or you will wait forever.
time.setOptions({
    "timeInterval": 0
})

"""
Time setting
"""

ET = 10 # Measurement time [sec]
start = 0.0;
end = ET + 1;
step = 1.0  # Interval between measurements [sec]/Length of sweep is 100 times wait time. Program runs for a few seconds if wait time is zero.
t = np.arange(start, end, step)


# --------------Headers and setters for monitoring Id over time
inputHeaders = ["t [sec]/Vsd={}V & Vg={}V".format(Vsd,Vg)]
inputSetters = [time]
inputPoints = product(t)

####### Multiple device (52 devices) measurement

my_Pi.setMuxToOutput(52)  # sets multiplexer to the desired device
outputHeaders = ["Device#{}".format(52)]
outputReaders = [daqin_D]

n = 52  # number of devices
N = n - 1
for j in range(N):
    my_Pi.setMuxToOutput(n - (j + 1))
    # time.sleep(0.5)  # short wait to settle. May not be necessary. Can investigate later
    outputHeaders = ["Device#{}".format(n - (j + 1))] + outputHeaders
    outputReaders = [daqin_D] + outputReaders
########


print('Start monitoring Id for {} sec'.format(T * ET))
sweepAndSave(
        basePath + "Monitoring Id",
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable=True
    )

target_dir = basePath + "Monitoring Id"
file_names = os.listdir(basePath)
for file_name in file_names:
    if(file_name.startswith("Monitoring Id")):
        shutil.move(os.path.join(basePath, file_name), target_dir)

daqout_S.goTo(0, delay=0.001)
KVg.goTo(0, delay=0.001)
my_Pi.setMuxToOutput(0)  # sets multiplexer to 0

##plot
os.chdir(basePath + "Monitoring Id")
tsv_files = glob.glob('*.{}'.format('tsv'))
filteredResults = [i for i in tsv_files if "LOG" not in i]
# print(filteredResults)

Monitoring_Id  = pd.concat([pd.read_csv(f, sep='\t') for f in filteredResults])
# print(Monitoring_Id)
Monitoring_Id.to_csv('Monitoring_Id.csv', sep='\t')

dfs = {}
dfs = pd.read_csv('Monitoring_Id.csv', sep='\t',header=None)


# new_header = dfs.iloc[1] #grab the first row for the header
# dfs = dfs[2:] #take the data less the header row
# dfs.columns = new_header #set the header row as the df header
#
# print(dfs)

headers = dfs.iloc[1].values
dfs.columns = headers
# dfs.drop(index=0 and 1,inplace=True)
dfs = dfs[2:]



out = []

for col in dfs.columns.values:
    out.append(dfs[col].tolist())

for p in range(1, len(out)):

    x = out[0]
    x = np.array(x,dtype=float) #time unit: sec
    x = x/60 #time unit: min

    y = out[p]
    y = np.array(y,dtype=float)
    y = y * (1E6)

    if p in range (1,11):
     plt.plot(x, y, label="device#{}".format(p),linestyle='solid')
    elif p in range (11,21):
     plt.plot(x, y, label="device#{}".format(p), linestyle='dotted')
    elif p in range(21, 31):
     plt.plot(x, y, label="device#{}".format(p), linestyle='dashed')
    elif p in range(31, 41):
     plt.plot(x, y, label="device#{}".format(p), linestyle=(5, (10, 3))) #'long dash with offset'
    elif p in range(41, 51):
     plt.plot(x, y, label="device#{}".format(p), linestyle=(0, (5, 1)))  # 'densely dashed'
    elif p in range(51, 53):
     plt.plot(x, y, label="device#{}".format(p), linestyle=(0, (3, 1, 1, 1, 1, 1)))  # 'densely dashdotdotted'


# plt.xlabel("Elapsed Time [sec]", fontsize=20)
plt.xlabel("Elapsed Time [min]", fontsize=20)
plt.ylabel("Id [uA]",fontsize=20)
plt.gca().invert_yaxis()

# plt.legend(loc='best', fancybox=True, shadow=True)
plt.title('Monitoring Id/ Vsd={}[V] and Vg={}[V]'.format(Vsd,Vg),fontsize=20)
plt.legend(bbox_to_anchor=(1.1, 1),borderaxespad=0, ncol=2,handleheight=1.2, labelspacing=0.05)
fig = plt.gcf()
fig.set_size_inches(7, 7)
fig.tight_layout()

plt.show()

fig.savefig('Monitoring Id.png', dpi=100)


print("End of all processes =)")

