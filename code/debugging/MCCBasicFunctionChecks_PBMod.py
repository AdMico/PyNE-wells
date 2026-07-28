"""
Brought to PyNE-wells v2.0.0 on Fri Aug 15 2025 by APM

@developers: Adam Micolich

Very basic test program for MCC128/MCC152 DAQ HATs using MCC128 PairBurst option
"""

from MCC128InPB import MCC128InPB
from MCC152Out import MCC152Out
import serial

# Setup Teensy 4.1 Comms
port = "/dev/ttyACM0"
baudrate = 9600
teensy = serial.Serial(port, baudrate)

# Function for sending commands to Teensy'
def send(command):
    command = command + '\n'
    cmd = command.encode('ascii') # encode and send
    teensy.write(cmd)

# Function for Teensy to be able to send status information back (test only)
def receive():
    msg = teensy.read_until() # read until a new line
    received = msg.decode('ascii')  # decode and return
    return received

# Values for outputs to run to in testing
AO0GoTo = 2.0
AO1GoTo = 2.0

# 1) Initialize Instruments
#---- MCC152 Output Port for AO0 --------------
daqout_AO0 = MCC152Out(0)
daqout_AO0.setOptions({
    "scaleFactor":1
})

#---- MCC152 Output Port for AO1 --------------
daqout_AO1 = MCC152Out(1)
daqout_AO1.setOptions({
    "scaleFactor":1
})

#---- MCC128 Input Port for AI0,AI1 --------------
daqin_AI = MCC128InPB(0,1)
daqin_AI.setOptions({
    "scaleFactor":1
})

for i in range(5):
    print('Start Loop: ',i+1)
    print('LED on')
    send(str(14+i)+":1\n")
    msg = receive()
    print(msg)
    V_AI = daqin_AI._getInputLevel()
    print('Start = ',V_AI[0],V_AI[1],V_AI[2],V_AI[3])
    daqout_AO0.goTo(AO0GoTo,stepsize=0.01,delay=0.01)
    daqout_AO1.goTo(AO1GoTo,stepsize=0.01,delay=0.01)
    V_AI = daqin_AI._getInputLevel()
    print('Middle = ',V_AI[0],V_AI[1],V_AI[2],V_AI[3])
    daqout_AO0.goTo(0.0,stepsize=0.01,delay=0.01)
    daqout_AO1.goTo(0.0,stepsize=0.01,delay=0.01)
    V_AI = daqin_AI._getInputLevel()
    print('End = ',V_AI[0],V_AI[1],V_AI[2],V_AI[3])
    print('LED off')
    send(str(14+i)+":0\n")
    msg = receive()
    print(msg)
    print('End loop: ',i+1)
    print('')