"""
Brought to PyNE-wells v1.2.0 on Thu Aug 07 2025 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

This class sets up the Pi to be controlled remotely. The truth table is that of the multiplexer.
"""
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from Config import PiBox
import time

class PiMUX:

    def __init__(self):
        if PiBox == 'MeasureOne':
            IP = '149.171.105.34' #IP changed for Lowy APM 25MAR24, was 129.94.163.203 on VLAN334 (Physics)
        if PiBox == 'MeasureTwo':
            IP = '129.94.163.167'
        if PiBox == 'MeasureThree':
            IP = '129.94.163.75'
        self.IP = IP
        #print(IP) -- For PiBox testing
        self.PiFactory = PiGPIOFactory(host=self.IP)

        #WordTable format: Device: [W-A3,W-A2,W-A1,W-A0,W-EN1,W-EN2], #MUX <number> Pin <number> (Mx <number> out of 16)
        self.WordTable = {0: [0, 0, 0, 0, 0, 0],  # OFF state
                            1: [0, 0, 0, 0, 1, 0],  # W-MUX 1/3 Pin 19 (Mx1)
                            2: [0, 0, 0, 1, 1, 0],  # W-MUX 1/3 Pin 20 (Mx2)
                            3: [0, 0, 1, 0, 1, 0],  # W-MUX 1/3 Pin 21 (Mx3)
                            4: [0, 0, 1, 1, 1, 0],  # W-MUX 1/3 Pin 22 (Mx4)
                            5: [0, 1, 0, 0, 1, 0],  # W-MUX 1/3 Pin 23 (Mx5)
                            6: [0, 1, 0, 1, 1, 0],  # W-MUX 1/3 Pin 24 (Mx6)
                            7: [0, 1, 1, 0, 1, 0],  # W-MUX 1/3 Pin 25 (Mx7)
                            8: [0, 1, 1, 1, 1, 0],  # W-MUX 1/3 Pin 26 (Mx8)
                            9: [1, 0, 0, 0, 1, 0],  # W-MUX 1/3 Pin 11 (Mx9)
                            10: [1, 0, 0, 1, 1, 0],  # W-MUX 1/3 Pin 10 (Mx10)
                            11: [1, 0, 1, 0, 1, 0],  # W-MUX 1/3 Pin 9 (Mx11)
                            12: [1, 0, 1, 1, 1, 0],  # W-MUX 1/3 Pin 8 (Mx12)
                            13: [1, 1, 0, 0, 1, 0],  # W-MUX 1/3 Pin 7 (Mx13)
                            14: [1, 1, 0, 1, 1, 0],  # W-MUX 1/3 Pin 6 (Mx14)
                            15: [0, 0, 0, 0, 0, 1],  # W-MUX 2/4 Pin 19 (Mx1)
                            16: [0, 0, 0, 1, 0, 1],  # W-MUX 2/4 Pin 20 (Mx2)
                            17: [0, 0, 1, 0, 0, 1],  # W-MUX 2/4 Pin 21 (Mx3)
                            18: [0, 0, 1, 1, 0, 1],  # W-MUX 2/4 Pin 22 (Mx4)
                            19: [0, 1, 0, 0, 0, 1],  # W-MUX 2/4 Pin 23 (Mx5)
                            20: [0, 1, 0, 1, 0, 1],  # W-MUX 2/4 Pin 24 (Mx6)
                            21: [0, 1, 1, 0, 0, 1],  # W-MUX 2/4 Pin 25 (Mx7)
                            22: [0, 1, 1, 1, 0, 1],  # W-MUX 2/4 Pin 26 (Mx8)
                            23: [1, 0, 0, 0, 0, 1],  # W-MUX 2/4 Pin 11 (Mx9)
                            24: [1, 0, 0, 1, 0, 1],  # W-MUX 2/4 Pin 10 (Mx10)
                            25: [1, 0, 1, 0, 0, 1],  # W-MUX 2/4 Pin 9 (Mx11)
                            26: [1, 0, 1, 1, 0, 1],  # W-MUX 2/4 Pin 8 (Mx12)
                            27: [1, 1, 0, 0, 0, 1]}  # W-MUX 2/4 Pin 7 (Mx13)

        #BitTable format: Device: [B-A3,B-A2,B-A1,B-A0,B-EN1,B-EN2], #MUX <number> Pin <number> (Mx <number> out of 16)
        self.BitTable = {0: [0, 0, 0, 0, 0, 0],  # OFF state
                            1: [0, 0, 0, 0, 1, 0],  # B-MUX 1/3 Pin 19 (Mx1)
                            2: [0, 0, 0, 1, 1, 0],  # B-MUX 1/3 Pin 20 (Mx2)
                            3: [0, 0, 1, 0, 1, 0],  # B-MUX 1/3 Pin 21 (Mx3)
                            4: [0, 0, 1, 1, 1, 0],  # B-MUX 1/3 Pin 22 (Mx4)
                            5: [0, 1, 0, 0, 1, 0],  # B-MUX 1/3 Pin 23 (Mx5)
                            6: [0, 1, 0, 1, 1, 0],  # B-MUX 1/3 Pin 24 (Mx6)
                            7: [0, 1, 1, 0, 1, 0],  # B-MUX 1/3 Pin 25 (Mx7)
                            8: [0, 1, 1, 1, 1, 0],  # B-MUX 1/3 Pin 26 (Mx8)
                            9: [1, 0, 0, 0, 1, 0],  # B-MUX 1/3 Pin 11 (Mx9)
                            10: [1, 0, 0, 1, 1, 0],  # B-MUX 1/3 Pin 10 (Mx10)
                            11: [1, 0, 1, 0, 1, 0],  # B-MUX 1/3 Pin 9 (Mx11)
                            12: [1, 0, 1, 1, 1, 0],  # B-MUX 1/3 Pin 8 (Mx12)
                            13: [1, 1, 0, 0, 1, 0],  # B-MUX 1/3 Pin 7 (Mx13)
                            14: [1, 1, 0, 1, 1, 0],  # B-MUX 1/3 Pin 6 (Mx14)
                            15: [0, 0, 0, 0, 0, 1],  # B-MUX 2/4 Pin 19 (Mx1)
                            16: [0, 0, 0, 1, 0, 1],  # B-MUX 2/4 Pin 20 (Mx2)
                            17: [0, 0, 1, 0, 0, 1],  # B-MUX 2/4 Pin 21 (Mx3)
                            18: [0, 0, 1, 1, 0, 1],  # B-MUX 2/4 Pin 22 (Mx4)
                            19: [0, 1, 0, 0, 0, 1],  # B-MUX 2/4 Pin 23 (Mx5)
                            20: [0, 1, 0, 1, 0, 1],  # B-MUX 2/4 Pin 24 (Mx6)
                            21: [0, 1, 1, 0, 0, 1],  # B-MUX 2/4 Pin 25 (Mx7)
                            22: [0, 1, 1, 1, 0, 1],  # B-MUX 2/4 Pin 26 (Mx8)
                            23: [1, 0, 0, 0, 0, 1],  # B-MUX 2/4 Pin 11 (Mx9)
                            24: [1, 0, 0, 1, 0, 1],  # B-MUX 2/4 Pin 10 (Mx10)
                            25: [1, 0, 1, 0, 0, 1],  # B-MUX 2/4 Pin 9 (Mx11)
                            26: [1, 0, 1, 1, 0, 1],  # B-MUX 2/4 Pin 8 (Mx12)
                            27: [1, 1, 0, 0, 0, 1]}  # B-MUX 2/4 Pin 7 (Mx13)

        #Define what GPIO pins are connected to the selector pins on the MUX
        #This is the GPIO number not the 40 pin cable number
        #GPIO 0, 1, 14, 15 not use as protected for EEPROM/UART

        self.WEN1_pin = LED(2, pin_factory=self.PiFactory)
        self.WEN2_pin = LED(3, pin_factory=self.PiFactory)
        self.WA0_pin = LED(4, pin_factory=self.PiFactory)
        self.WA1_pin = LED(5, pin_factory=self.PiFactory)
        self.WA2_pin = LED(6, pin_factory=self.PiFactory)
        self.WA3_pin = LED(7, pin_factory=self.PiFactory)

        self.BEN1_pin = LED(8, pin_factory=self.PiFactory)
        self.BEN2_pin = LED(9, pin_factory=self.PiFactory)
        self.BA0_pin = LED(10, pin_factory=self.PiFactory)
        self.BA1_pin = LED(11, pin_factory=self.PiFactory)
        self.BA2_pin = LED(12, pin_factory=self.PiFactory)
        self.BA3_pin = LED(13, pin_factory=self.PiFactory)

        self.PiPowerOn_pin = LED(16, pin_factory=self.PiFactory)
        self.BatteryOn_pin = LED(17, pin_factory=self.PiFactory)
        self.BattLPROff_pin = LED(18, pin_factory=self.PiFactory)
        self.BattLPROn_pin = LED(19, pin_factory=self.PiFactory)

        self.BiasBits_pin = LED(20, pin_factory=self.PiFactory)
        self.BiasWords_pin = LED(21, pin_factory=self.PiFactory)

        self.WordOff_pin = LED(22, pin_factory=self.PiFactory)
        self.WordOn_pin = LED(23, pin_factory=self.PiFactory)
        self.BitOff_pin = LED(24, pin_factory=self.PiFactory)
        self.BitOn_pin = LED(25, pin_factory=self.PiFactory)

        self.WMUXPins = [self.WA3_pin,self.WA2_pin,self.WA1_pin,self.WA0_pin,self.WEN1_pin,self.WEN2_pin]
        self.BMUXPins = [self.BA3_pin,self.BA2_pin,self.BA1_pin,self.BA0_pin,self.BEN1_pin,self.BEN2_pin]

        #Uses truthtables to set GPIO pin voltages to activate desired output.

    def setWMuxToOutput(self, desiredOutput): #Controls output to WMUXes

        for index, item in enumerate(self.WMUXPins):
            if self.WordTable[desiredOutput][index]:
                item.on()
            else:
                item.off()

    def setBMuxToOutput(self, desiredOutput): #Controls output to BMUXes

        for index, item in enumerate(self.BMUXPins):
            if self.BitTable[desiredOutput][index]:
                item.on()
            else:
                item.off()

    def setPiPowerToOn(self): # Switches power supply to the RPi -- APM 09SEP25
        self.PiPowerOn_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.PiPowerOn_pin.off()

    def setBatteryToOn(self): # Switches power supply to the battery -- APM 09SEP25
        self.BatteryOn_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.BatteryOn_pin.off()

    def setBattLPRToOff(self): # Connects battery regulator circuit to ground -- APM 09SEP25
        self.BattLPROff_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.BattLPROff_pin.off()

    def setBattLPRToOn(self): # Connects battery regulator circuit to battery -- APM 09SEP25
        self.BattLPROn_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.BattLPROn_pin.off()

    def setToBiasBits(self): # Connects the source AO0 to Meas-B -- APM 09SEP25
        self.BiasBits_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.BiasBits_pin.off()

    def setToBiasWords(self): # Connects the source AO0 to Meas-W -- APM 09SEP25
        self.BiasWords_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.BiasWords_pin.off()

    def setWordToOff(self): # Connects the given word line back to hold -- APM 09SEP25
        self.WordOff_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.WordOff_pin.off()

    def setWordToOn(self): # Connects the given word line to Meas-W -- APM 09SEP25
        self.WordOn_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.WordOn_pin.off()

    def setBitToOff(self): # Connects the given bit line back to hold -- APM 09SEP25
        self.BitOff_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.BitOff_pin.off()

    def setBitToOn(self): # Connects the given bit line to Meas-B -- APM 09SEP25
        self.BitOn_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.BitOn_pin.off()

    def SysInit(self):  # Runs a sequence to initialise all the relays at start -- APM 09SEP25
        self.setBatteryToOn() # Ensures MUXes powered by Battery
        self.setBattLPRToOn() # Connects battery to LPR to power MUXes
        self.setToBiasWords()
        for i in range(27): # Sets all word/bit lines to hold
            self.setWMuxToOutput(i+1)
            self.setWordToOff()
            self.setBMuxToOutput(i+1)
            self.setBitToOff()
        self.setWMuxToOutput(0) # Switches word MUXes off
        self.setBMuxToOutput(0) # Switches bit MUXes off

    def SysReset(self):  # Runs a sequence to reset all the relays for next run -- APM 09SEP25
        self.setToBiasWords()
        for i in range(27): # Sets all word/bit lines to hold
            self.setWMuxToOutput(i+1)
            self.setWordToOff()
            self.setBMuxToOutput(i+1)
            self.setBitToOff()
        self.setWMuxToOutput(0) # Switches word MUXes off
        self.setBMuxToOutput(0) # Switches bit MUXes off

    def SysShutdown(self):  # Runs a sequence to setup for shutdown -- APM 09SEP25
        self.setToBiasWords()
        for i in range(27): # Sets all word/bit lines to hold
            self.setWMuxToOutput(i+1)
            self.setWordToOff()
            self.setBMuxToOutput(i+1)
            self.setBitToOff()
        self.setWMuxToOutput(0) # Switches word MUXes off
        self.setBMuxToOutput(0) # Switches bit MUXes off
        self.setBatteryToOn() # Ensures MUXes powered by Battery
        self.setBattLPRToOff() # Connects ground to LPR to power down MUXes

    def SysTest(self,word,bit,time): # Switches a given bit over to connection for a specified time -- APM 10SEP25
        self.setToBiasWords()
        self.setWMuxToOutput(word)
        self.setWordToOn()
        self.setBMuxToOutput(bit)
        self.setBitToOn()
        time.sleep(time)
        self.setWMuxToOutput(word)
        self.setWordToOff()
        self.setBMuxToOutput(bit)
        self.setBitToOff()

if __name__ == "__main__": # execute only if this script is run, not when it's being imported
    my_pi = PiMUX()
    my_pi.SysInit() # Running as main will initialise system -- APM 09SEP25
#    my_pi.SysTest(1,1,30) # Will connect to device A1 for 30 sec -- APM 10SEP25
#    my_pi.SysReset() # Runs a reset -- APM 10SEP25