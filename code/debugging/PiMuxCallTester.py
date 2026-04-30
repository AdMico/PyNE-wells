"""
Brought to PyNE-wells v2.0.0 on Thu Apr 30 2026 by APM

@developers: Adam Micolich

Program to test why AssayRunGen5.py is having problems on its bit lines
"""

from PiControlGen5 import PiMUX
import time

CtrlPi = PiMUX()
CtrlPi.SysInit()  # Initialises the multiplexer for running a measurement
CtrlPi.WordRelayTest('S',0.5)
CtrlPi.BitRelayTest('D',0.5)
#CtrlPi.SysTestSingle(1,1,10,'D')
#CtrlPi.SysDevOn(1,1)
#time.sleep(10)
#CtrlPi.SysDevOff(1,1)
CtrlPi.SysReset()