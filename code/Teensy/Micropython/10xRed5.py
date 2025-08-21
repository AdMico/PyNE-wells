"""
Brought to PyNE-wells v2.0.0 on Wed Aug 20 2025 by APM

@developers: Adam Micolich

Very basic algorithm that lights every second LED one by one then turns them off again.
Relies on 10xLED chip with LEDs connected to Teensy4.1 pins 14-18, each with 220 ohm resistors in series to ground.
Has no interaction with other PyNE-wells code, it's purely for hardware test.
"""

from machine import Pin
import time

p14 = Pin('D14',Pin.OUT)
p15 = Pin('D15',Pin.OUT)
p16 = Pin('D16',Pin.OUT)
p17 = Pin('D17',Pin.OUT)
p18 = Pin('D18',Pin.OUT)

def main_loop():
    while True:
        p14.on()
        time.sleep_ms(500)
        p15.on()
        time.sleep_ms(500)
        p16.on()
        time.sleep_ms(500)
        p17.on()
        time.sleep_ms(500)
        p18.on()
        time.sleep_ms(500)
        p14.off()
        time.sleep_ms(500)
        p15.off()
        time.sleep_ms(500)
        p16.off()
        time.sleep_ms(500)
        p17.off()
        time.sleep_ms(500)
        p18.off()
        time.sleep_ms(500)

main_loop()