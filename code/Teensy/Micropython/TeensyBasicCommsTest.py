"""
Brought to PyNE-wells v2.0.0 on Wed Aug 20 2025 by APM

@developers: Adam Micolich

For use with TeensyBasicCommsTest_MPY.py only.
Code will allow you to send a string to the Teensy, which will echo the string back to you.
End loop using 'exit'. Code is purely for serial byte traffic check.
"""

from machine import UART

teensy = UART(1,9600)
teensy.init(9600,bits=8,parity=None,stop=1)

def main_loop():
    val=""
    while True:
        if (teensy.any() > 0):
            val = teensy.readline()
        if (val != ""):
            teensy.write(val)
            if (val == 'exit'):
                return
            val = ""

main_loop()