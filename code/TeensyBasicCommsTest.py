"""
Brought to PyNE-wells v2.1.0 on Wed Nov 18 2026 by APM

@developers: Adam Micolich

Python code handling basic serial comms to Teensy 4.1 to issue manual commands for Gen6 hardware debugging
"""

import serial

port = "/dev/ttyACM0" # put your port here
baudrate = 9600
ser = serial.Serial(port, baudrate)
flag = True
def tell(msg):
    msg = msg + '\n'
    x = msg.encode('ascii') # encode n send
    ser.write(x)

def hear():
    msg = ser.read_until() # read until a new line
#    msg = ser.read()
    mystring = msg.decode('ascii')  # decode n return
#    mystring = msg
    return mystring

while flag == True:
    val = input() # take user input
    if val=='exit':
        flag = False
    else:
        tell(val) # send it to Teensy
        var = hear() # listen to Teensy
        print(var) # print what Teensy sent

