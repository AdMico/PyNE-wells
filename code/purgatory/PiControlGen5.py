"""
Brought to PyNE-wells v2.0.0 on Thu Apr 30 2026 by APM

@developers: Adam Micolich & Jan Gluschke

This class sets up the Pi to be controlled remotely. The truth table is that of the multiplexer.
"""

from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from Config import PiBox,MuxMode_Gen5,ScanDir_Gen5
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
        self.WordList = ['OFF','A','B','C','D','E','F','G','H','I','J','K','L','M','N',
                           '&','Z','Y','X','W','V','U','T','S','R','Q','P','O']
        self.BitList = ['OFF','1','2','3','4','5','6','7','8','9','10','11','12','13','14',
                           '15','16','17','18','19','20','21','22','23','24','25','26','27']
        self.RelayTime = 0.01

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

        # Define what GPIO pins are connected to the selector pins on the MUX
        # This is the GPIO number not the 40 pin cable number
        # GPIO 0, 1, 14, 15 not use as protected for EEPROM/UART

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

    def setWMuxToOutput(self,desiredOutput): #Controls output to WMUXes
        for index, item in enumerate(self.WMUXPins):
            if self.WordTable[desiredOutput][index]:
                item.on()
            else:
                item.off()

    def setBMuxToOutput(self,desiredOutput): #Controls output to BMUXes
        for index, item in enumerate(self.BMUXPins):
            if self.BitTable[desiredOutput][index]:
                item.on()
            else:
                item.off()

    def setPiPowerToOn(self): # Switches power supply to the RPi -- APM 09SEP25
        self.PiPowerOn_pin.on()
        time.sleep(self.RelayTime) # Tested at 1ms wait being ok APM 26Feb24
        self.PiPowerOn_pin.off()

    def setBatteryToOn(self): # Switches power supply to the battery -- APM 09SEP25
        self.BatteryOn_pin.on()
        time.sleep(self.RelayTime) # Tested at 1ms wait being ok APM 26Feb24
        self.BatteryOn_pin.off()

    def setBattLPRToOff(self): # Connects battery regulator circuit to ground -- APM 09SEP25
        self.BattLPROff_pin.on()
        time.sleep(self.RelayTime) # Tested at 1ms wait being ok APM 26Feb24
        self.BattLPROff_pin.off()

    def setBattLPRToOn(self): # Connects battery regulator circuit to battery -- APM 09SEP25
        self.BattLPROn_pin.on()
        time.sleep(self.RelayTime) # Tested at 1ms wait being ok APM 26Feb24
        self.BattLPROn_pin.off()

    def setToBiasBits(self): # Connects the source AO0 to Meas-B -- APM 09SEP25
        self.BiasBits_pin.on()
        time.sleep(self.RelayTime) # Tested at 1ms wait being ok APM 26Feb24
        self.BiasBits_pin.off()

    def setToBiasWords(self): # Connects the source AO0 to Meas-W -- APM 09SEP25
        self.BiasWords_pin.on()
        time.sleep(self.RelayTime) # Tested at 1ms wait being ok APM 26Feb24
        self.BiasWords_pin.off()

    def setWordToOff(self): # Connects the given word line back to hold -- APM 09SEP25
        self.WordOff_pin.on()
        time.sleep(self.RelayTime) # Tested at 1ms wait being ok APM 26Feb24
        self.WordOff_pin.off()

    def setWordToOn(self): # Connects the given word line to Meas-W -- APM 09SEP25
        self.WordOn_pin.on()
        time.sleep(self.RelayTime) # Tested at 1ms wait being ok APM 26Feb24
        self.WordOn_pin.off()

    def setBitToOff(self): # Connects the given bit line back to hold -- APM 09SEP25
        self.BitOff_pin.on()
        time.sleep(self.RelayTime) # Tested at 1ms wait being ok APM 26Feb24
        self.BitOff_pin.off()

    def setBitToOn(self): # Connects the given bit line to Meas-B -- APM 09SEP25
        self.BitOn_pin.on()
        time.sleep(self.RelayTime) # Tested at 1ms wait being ok APM 26Feb24
        self.BitOn_pin.off()

    def SysInit(self):  # Runs a sequence to initialise all the relays at start -- APM 09SEP25
        if MuxMode_Gen5 == 'Battery':
            self.setBatteryToOn() # Sets MUX power to Battery
            self.setBattLPRToOn() # Connects battery to LPR to power MUXes
        elif MuxMode_Gen5 == 'Pi-power':
            self.setPiPowerToOn() # Sets MUX power to Pi +5V line
            self.setBattLPRToOff() # Connects LPR circuit to ground
        if ScanDir_Gen5 == 'Horizontal':
            self.setToBiasWords()
        elif ScanDir_Gen5 == 'Vertical':
            self.setToBiasBits()
        for i in range(27): # Sets all word/bit lines to hold
            self.setWMuxToOutput(i+1)
            self.setWordToOff()
            self.setBMuxToOutput(i+1)
            self.setBitToOff()
        self.setWMuxToOutput(0) # Switches word MUXes off
        self.setBMuxToOutput(0) # Switches bit MUXes off

    def SysReset(self):  # Runs a sequence to reset all the relays for next run -- APM 09SEP25
        for i in range(27): # Sets all word/bit lines to hold
            self.setWMuxToOutput(i+1)
            self.setWordToOff()
            self.setBMuxToOutput(i+1)
            self.setBitToOff()
        self.setWMuxToOutput(0) # Switches word MUXes off
        self.setBMuxToOutput(0) # Switches bit MUXes off

    def SysSoftShutdown(self):  # Runs a sequence to setup for shutdown but leave MUXes powered -- APM 09SEP25
        for i in range(27): # Sets all word/bit lines to hold
            self.setWMuxToOutput(i+1)
            self.setWordToOff()
            self.setBMuxToOutput(i+1)
            self.setBitToOff()
        self.setWMuxToOutput(0) # Switches word MUXes off
        self.setBMuxToOutput(0) # Switches bit MUXes off

    def SysHardShutdown(self):  # Runs a sequence to setup for shutdown including depowering the MUXes -- APM 09SEP25
        for i in range(27): # Sets all word/bit lines to hold
            self.setWMuxToOutput(i+1)
            self.setWordToOff()
            self.setBMuxToOutput(i+1)
            self.setBitToOff()
        self.setWMuxToOutput(0) # Switches word MUXes off
        self.setBMuxToOutput(0) # Switches bit MUXes off
        self.setBatteryToOn() # Ensures MUXes powered by Battery
        self.setBattLPRToOff() # Connects ground to LPR to power down MUXes

    def WordRelayTest(self,bias,HoldTime):
        if bias == 'S':
            self.setToBiasWords()
        elif bias == 'D':
            self.setToBiasBits()
        print('Prepare to test Word:',self.WordList[1],' in 1 seconds.')
        time.sleep(1)
        for i in range(27):
            if i == 14:
                time.sleep(3) # Added to allow for realising you need to jump to & from N -- APM 30Sep25
            print ('Wordline: ',self.WordList[i+1],' to Hold for ',HoldTime,' seconds.')
            self.setWMuxToOutput(i+1)
            self.setWordToOff()
            time.sleep(HoldTime)
            print('Wordline: ',self.WordList[i+1],' to ',bias,' for ',HoldTime,' seconds.')
            self.setWMuxToOutput(i+1)
            self.setWordToOn()
            time.sleep(HoldTime)
            print('Wordline: ',self.WordList[i+1],' to Hold for ',HoldTime,' seconds.')
            self.setWMuxToOutput(i+1)
            self.setWordToOff()
            time.sleep(HoldTime)
            if i < 26:
                print('Prepare to test Word:',self.WordList[i+2],' in 1 second.')
                time.sleep(1)
            else:
                print('Finished Test.')
                print()
                time.sleep(3)

    def BitRelayTest(self,bias,HoldTime):
        if bias == 'S':
            self.setToBiasBits()
        elif bias == 'D':
            self.setToBiasWords()
        print('Prepare to test Bit:',self.BitList[1],' in 1 seconds')
        time.sleep(1)
        for i in range(27):
            print ('Bitline: ',self.BitList[i+1],' to Hold for ',HoldTime,' seconds.')
            self.setBMuxToOutput(i+1)
            self.setBitToOff()
            time.sleep(HoldTime)
            print('Bitline: ',self.BitList[i+1],' to ',bias,' for ',HoldTime,' seconds.')
            self.setBMuxToOutput(i+1)
            self.setBitToOn()
            time.sleep(HoldTime)
            print('Bitline: ',self.BitList[i+1],' to Hold for ',HoldTime,' seconds.')
            self.setBMuxToOutput(i+1)
            self.setBitToOff()
            time.sleep(HoldTime)
            if i < 26:
                print('Prepare to test Bit:',self.BitList[i+2],' in 1 second.')
                time.sleep(1)
            else:
                print('Finished Test.')
                print()
                time.sleep(3)

    def SysTestSingle(self,word,bit,wait): # Switches a given device over to connection for a specified time -- APM 10SEP25
        self.setWMuxToOutput(word)
        self.setWordToOn()
        self.setBMuxToOutput(bit)
        self.setBitToOn()
        print('Testing: ', self.WordList[word], self.BitList[bit])
        time.sleep(wait)
        self.setBMuxToOutput(bit)
        self.setBitToOff()
        self.setWMuxToOutput(word)
        self.setWordToOff()

    def SysTestFull(self,wait): # Switches each node on for a specified time in sequence -- APM 10SEP25
        for i in range(27):
            self.setWMuxToOutput(i+1)
            self.setWordToOn()
            for j in range(27):
                self.setBMuxToOutput(j+1)
                self.setBitToOn()
                print('Testing: ',self.WordList[i+1],self.BitList[j+1])
                time.sleep(wait)
                self.setBMuxToOutput(j+1)
                self.setBitToOff()
            self.setWMuxToOutput(i+1)
            self.setWordToOff()

    def SysTest4x4(self,wait): # Switches each node on for a specified time in sequence -- APM 10SEP25
        for i in range(4):
            self.setWMuxToOutput(i+1)
            self.setWordToOn()
            for j in range(4):
                self.setBMuxToOutput(j+1)
                self.setBitToOn()
                print('Testing: ',self.WordList[i+1],self.BitList[j+1])
                time.sleep(wait)
                self.setBMuxToOutput(j+1)
                self.setBitToOff()
            self.setWMuxToOutput(i+1)
            self.setWordToOff()

    def SysDevOn(self,i,j): # Switches a given device on for AssayRunGen5.py -- APM 16Oct25
        self.setWMuxToOutput(i)
        self.setWordToOn()
        self.setBMuxToOutput(j)
        self.setBitToOn()

    def SysDevOff(self,i,j): # Switches a given device off for AssayRunGen5.py -- APM 16Oct25
        self.setBMuxToOutput(j)
        self.setBitToOff()
        self.setWMuxToOutput(i)
        self.setWordToOff()

if __name__ == "__main__": # execute only if this script is run, not when it's being imported
    my_pi = PiMUX()
    my_pi.SysInit() # Running as main will initialise system -- APM 09SEP25
#    my_pi.WordRelayTest('S',1.5)
#    my_pi.BitRelayTest('D',1.5)
#    my_pi.SysTestSingle(3,3,10) # Will connect to device A1 for 10 sec -- APM 10SEP25
#    my_pi.SysTest4x4(20) # Runs a test using the 4x4 board -- APM 30SEP25
#    my_pi.SysTestFull(0.1) # Will connect to each device for 0.1 sec -- APM 10SEP25
    my_pi.SysReset() # Runs a reset -- APM 10SEP25