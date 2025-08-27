"""
Brought to PyNE-wells v2.0.0 on Wed Aug 20 2025 by APM

@developers: Adam Micolich

For use with TeensyBasicCommsTest_MPY.py only.
Code will allow you to send a string to the Teensy, which will echo the string back to you.
End loop using 'exit'. Code is purely for serial byte traffic check.
"""

from machine import UART
import time

teensy = UART(1,9600)
teensy.init(9600,bits=8,parity=None,stop=1)

def main_loop():
    while True:
        if teensy.any():
            rec = teensy.readline()
            if rec:
                teensy.write(rec)
        time.sleep(0.1)

if __name__ == "__main__":
    main_loop()