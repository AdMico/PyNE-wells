"""
Brought to PyNE-wells v2.0.0 on Fri Aug 15 2025 by APM

@developers: Adam Micolich

Very basic test program for MCC128/MCC152 DAQ HATs
"""

from MCC128InSS import MCC128InSS
from MCC152Out import MCC152Out
import serial

# Setup Teensy 4.1 Comms
teensy = serial.Serial(
    port="/dev/ttyACM0",  # Change this to your Teensy's port
    baudrate=9600, # Or your configured baudrate
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1 # Timeout in seconds
)

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

#---- MCC128 Input Port for AI0 --------------
daqin_AI0 = MCC128InSS(0)
daqin_AI0.setOptions({
    "scaleFactor":1
})

#---- MCC128 Input Port for AI1 --------------
daqin_AI1 = MCC128InSS(1)
daqin_AI1.setOptions({
    "scaleFactor":1
})

for i in range(5):
    print('Start Loop: ',i+1)
    print('LED on')
    send(str(14+i)+":1\n")
    msg = receive()
    print(msg)
    V_AI0 = daqin_AI0._getInputLevel()
    V_AI1 = daqin_AI1._getInputLevel()
    print('Start = ',V_AI0,V_AI1)
    daqout_AO0.goTo(AO0GoTo,stepsize=0.01,delay=0.01)
    daqout_AO1.goTo(AO1GoTo,stepsize=0.01,delay=0.01)
    V_AI0 = daqin_AI0._getInputLevel()
    V_AI1 = daqin_AI1._getInputLevel()
    print('Middle = ',V_AI0,V_AI1)
    daqout_AO0.goTo(0.0,stepsize=0.01,delay=0.01)
    daqout_AO1.goTo(0.0,stepsize=0.01,delay=0.01)
    V_AI0 = daqin_AI0._getInputLevel()
    V_AI1 = daqin_AI1._getInputLevel()
    print('End = ',V_AI0,V_AI1)
    print('LED off')
    send(str(14 + i) + ":0\n")
    msg = receive()
    print(msg)
    print('End loop: ',i+1)
    print('')