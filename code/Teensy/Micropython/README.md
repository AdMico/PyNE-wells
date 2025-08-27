**Note:** These are the .py files to upload to Teensy4.1 using micropython for use with the software. Of these, only 10xRed5.py actually functions correctly at present. UART comms seem to work terribly on micropython, the comms are inconsistent/irreproducible, so bugging has been almost impossible. This part of the project has been abandoned for another attempt at a much later date. Please use the Arduino IDE version instead until then.

Each file is described in detail below.

**Written by:** Adam Micolich

**10xRed5.py:** Very basic algorithm that lights every second LED one by one then turns them off again. Relies on 10xLED chip with LEDs connected to Teensy4.1 pins 14-18, each with 220 ohm resistors in series to ground. Has no interaction with other `PyNE-wells` code, it's purely for hardware test.

**TeensyBasicCommsTest.py:** For use with `TeensyBasicCommsTest.py` only. Code will allow you to send a string to the Teensy, which will echo the string back to you. End loop using 'exit'. Code is purely for serial byte traffic check.

**TeensyGPIOTest.py:** Designed for use with `TeensyBasicCommsTest.py` or `MCCBasicFunctionChecks.py` and offers full GPIO set functionality. For use with `TeensyBasicCommsTest.py`, send commands such as 14:1 or 16:0 to turn the respective LEDs on/off. For use with `MCCBasicFunctionChecks.py`, the program will automatically run a 5-iteration loop that turns a LED on, runs a voltage ramp on AO0 and AO1 to +2.0V and back, turns the LED off, then moves to the next LED on each subsequent iteration.

**print_platform.py:** Just makes Teensy send a message back to micropython REPL.