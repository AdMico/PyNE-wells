"""
Brought to PyNE-wells v2.0.0 on Wed Aug 20 2025 by APM

@developers: Adam Micolich

Designed for use with TeensyBasicCommsTest.py or Control - MCC_BasicFunctionChecks.py and offers full GPIO set functionality.
For use with TeensyBasicCommsTest.py, send commands such as 14:1 or 16:0 to turn the respective LEDs on/off.
For use with Control - MCC_BasicFunctionChecks.py, the program will automatically run a 5-iteration loop that turns a LED on,
runs a voltage ramp on AO0 and AO1 to +2.0V and back, turns the LED off, then moves to the next LED on each subsequent iteration.
"""

from machine import UART
from machine import Pin

teensy = UART(1,9600)
teensy.init(9600,bits=8,parity=None,stop=1)

p14 = Pin('D14',Pin.OUT)
p15 = Pin('D15',Pin.OUT)
p16 = Pin('D16',Pin.OUT)
p17 = Pin('D17',Pin.OUT)
p18 = Pin('D18',Pin.OUT)

def main_loop():
    while True:
        if (teensy.any() > 0):
            comm = teensy.readline()
            command = comm.strip()
            commandIndex = command.index(":")  # Find a delimiter (e.g., semicolon) to split the string
            if (commandIndex != -1):
                PinStr = command[0,commandIndex]
                SetStr = command[commandIndex+1, commandIndex+2]
                Pin = int(PinStr)
                Set = int(SetStr)
                if ((Pin >= 14) and (Pin <= 18) and ((Set == 0) or (Set == 1))):
                    if (Pin == 14):
                        p14.value(Set)
                    elif (Pin == 15):
                        p15.value(Set)
                    elif (Pin == 16):
                        p16.value(Set)
                    elif (Pin == 17):
                        p17.value(Set)
                    elif (Pin == 18):
                        p18.value(Set)
#                    teensy.write("GPIO Set OK")
#                else:
#                    teensy.write("GPIO Set Fail: Outside bounds")
#            else:
#                teensy.write("GPIO Set Fail: No delimiter found")

main_loop()