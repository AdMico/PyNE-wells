"""
Brought to PyNE-wells v2.0.0 on Wed Aug 20 2025 by APM

@developers: Adam Micolich

Very basic algorithm that lights every second LED one by one then turns them off again.
Relies on 10xLED chip with LEDs connected to Teensy4.1 pins 14-18, each with 220 ohm resistors in series to ground.
Has no interaction with other PyNE-wells code, it's purely for hardware test.
"""

import sys

print ("Hello from (Micro)Python! I am running on the following platform:", sys.platform)
