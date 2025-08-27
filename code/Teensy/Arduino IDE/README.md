**Note:** These are the .ino files to upload to Teensy4.1 using the Arduino IDE for use with the software. Each are described in detail below.

**Written by:** Adam Micolich

**10xRed5.ino:** Very basic algorithm that lights every second LED one by one then turns them off again. Relies on 10xLED chip with LEDs connected to Teensy4.1 pins 14-18, each with 220 ohm resistors in series to ground. Has no interaction with other `PyNE-wells` code, it's purely for hardware test.

**TeensyBasicCommsTest.ino:** For use with `TeensyBasicCommsTest.py` only. Code will allow you to send a string to the Teensy, which will echo the string back to you. End loop using 'exit'. Code is purely for serial byte traffic check.

**TeensyGPIOTest.ino:** Designed for use with `TeensyBasicCommsTest.py` or `MCCBasicFunctionChecks.py` and offers full GPIO set functionality. For use with `TeensyBasicCommsTest.py`, send commands such as 14:1 or 16:0 to turn the respective LEDs on/off. For use with `MCCBasicFunctionChecks.py`, the program will automatically run a 5-iteration loop that turns a LED on, runs a voltage ramp on AO0 and AO1 to +2.0V and back, turns the LED off, then moves to the next LED on each subsequent iteration.

