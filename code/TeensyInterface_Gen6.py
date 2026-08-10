"""
Brought to PyNE-wells v2.0.0 on Thu Apr 30 2026 by APM

@developer: Adam Micolich

This class sets up the Teensy to be controlled remotely. The truth table is now in the Teensy .ino file.
This code mostly just handles the serial interface from the Raspberry Pi to the Teensy in the Gen 6 boxes.
"""

from Config_Gen6 import Instruments,ScanDir,DrainGain,GateGain,DrainCirc,GateCirc,TeensyPort
from ConfigInterpreter_Gen6 import ConfigInterp
import serial
import time
from itertools import chain

class TeensyMUX:

    def __init__(self):
        self.port = TeensyPort
        self.teensy = serial.Serial(port,9600)
        self.ChipWordList = ['OFF','A','B','C','D','E','F','G','H','I','J','K','L','M','N',
                           '&','Z','Y','X','W','V','U','T','S','R','Q','P','O']
        self.ChipBitList = ['OFF','1','2','3','4','5','6','7','8','9','10','11','12','13','14',
                           '15','16','17','18','19','20','21','22','23','24','25','26','27']
        self.TeensyWordList = ['OFF','A','B','C','D','E','F','G','H','I','J','K','L','M','N',
                           'O','P','Q','R','S','T','U','V','W','X','Y','Z','&']
        self.TeensyBitList = ['OFF','A','B','C','D','E','F','G','H','I','J','K','L','M','N',
                           'O','P','Q','R','S','T','U','V','W','X','Y','Z','&']

        ## Useful mapping information follows below.
        # GPIO Mapping for Gen6 V1: W - EN1 = 1; W - EN2 = 2; W - A0 = 3; W - A1 = 4; W - A2 = 5;
        # W - A3 = 6; B - EN1 = 7; B - EN2 = 8; B - A0 = 9; B - A1 = 10; B - A2 = 11; B - A3 = 12;
        # Bias Words (def) = 13; Bias Bits = 14; Word On (def) = 15; Word Off = 16; Bit On (def) = 17;
        # Bit Off = 18; +5V GND (def) = 19; +5V Active = 20; Source Int (def) = 21; Source Ext = 22;
        # Drain Int (def) = 23; Drain Ext = 24; Hold Int (def) = 25; Hold Ext = 26; Gate Int(def) = 27;
        # Gate Ext = 28; V1 - Inv (def) = 29; V1 - NonInv = 30; V2 - Inv (def) = 31; V2 - NonInv = 32;
        # I1 - Lo (def) = 33; I1 - Hi = 34; I2 - Lo (def) = 35; I2 - Hi = 36; I1 - TIA (def) = 37;
        # I1 - CSA = 38, I2 - TIA (def) = 39; I2 - CSA = 40.
        #
        # Control Relay Commands: 01 = K-O; 02 = K-P; 03 = K-S; 04 = K-D; 05 = K-H; 06 = K-G;
        # 07 = K-V1, K-X1, K-I5; 08 = K-V2, K-X2, K-I6; 09 = K-I1; 10 = K-I2, 11 = K-I3, 12 = K-I4
        # A command sets to relay default, B command sets to relay non-default.

    def send(msg):
        msg = msg + '\n' #add newline to string
        command = msg.encode('ascii')  #encode to ascii
        teensy.write(command)

    def receive():
        msg = teensy.read_until()  #read until newline
        response = msg.decode('ascii')  #decode from ascii
        return response

    def setWordsAsSource(self): # Sets words as source and bits as drain -- APM 23JUL26
        self.send(A01)
        Err = self.receive()
        return Err

    def setBitsAsSource(self): # Sets bits as source and words as drain -- APM 23JUL26
        self.send(B01)
        Err = self.receive()
        return Err

    def setRelaysToOff(self): # Connects +5V power line to ground, disables all relays -- APM 23JUL26
        self.send(A02)
        Err = self.receive()
        return Err

    def setRelaysToOn(self): # Activates +5V power line, enables all relays -- APM 23JUL26
        self.send(B02)
        Err = self.receive()
        return Err

    def setSourceInt(self): # Connects source to MCC152 AO0 -- APM 23JUL26
        self.send(A03)
        Err = self.receive()
        return Err

    def setSourceExt(self): # Connects source to BNC -- APM 23JUL26
        self.send(B03)
        Err = self.receive()
        return Err

    def setDrainInt(self): # Connects drain to MCC128 CH0H -- APM 23JUL26
        self.send(A04)
        Err = self.receive()
        return Err

    def setDrainExt(self): # Connects drain to BNC -- APM 23JUL26
        self.send(B04)
        Err = self.receive()
        return Err

    def setHoldInt(self): # Connects hold to MCC152 AO1 -- APM 23JUL26
        self.send(A05)
        Err = self.receive()
        return Err

    def setHoldExt(self): # Connects hold to BNC -- APM 23JUL26
        self.send(B05)
        Err = self.receive()
        return Err

    def setGateInt(self): # Connects gate to MCC128 CH1H -- APM 23JUL26
        self.send(A06)
        Err = self.receive()
        return Err

    def setGateExt(self): # Connects gate to BNC -- APM 23JUL26
        self.send(B06)
        Err = self.receive()
        return Err

    def setPosSource(self): # Sets Source to positive voltage range -- APM 28JUL26
        self.send(A07)
        Err = self.receive()
        return Err

    def setPosHold(self): # Sets Hold to positive voltage range -- APM 28JUL26
        self.send(A08)
        Err = self.receive()
        return Err

    def setNegSource(self): # Sets Source to negative voltage range -- APM 28JUL26
        self.send(B07)
        Err = self.receive()
        return Err

    def setNegHold(self): # Sets Hold to negative voltage range -- APM 28JUL26
        self.send(B08)
        Err = self.receive()
        return Err

    def setDrainLowGain(self): # Sets drain to 10^3 V/A gain -- APM 23JUL26
        self.send(A09)
        Err = self.receive()
        return Err

    def setDrainHighGain(self): # Sets drain to 10^4 V/A gain -- APM 23JUL26
        self.send(B09)
        Err = self.receive()
        return Err

    def setGateLowGain(self): # Sets gate to 10^3 V/A gain -- APM 23JUL26
        self.send(A10)
        Err = self.receive()
        return Err

    def setGateHighGain(self): # Sets gate to 10^4 V/A gain -- APM 23JUL26
        self.send(B10)
        Err = self.receive()
        return Err

    def setDrainToTIA(self): # Routes the drain through the TIA circuit -- APM 23JUL26
        self.send(A11)
        Err = self.receive()
        return Err

    def setDrainToCSA(self): # Routes the drain through the CSA circuit -- APM 23JUL26
        self.send(B11)
        Err = self.receive()
        return Err

    def setGateToTIA(self): # Routes the gate through the TIA circuit -- APM 23JUL26
        self.send(A12)
        Err = self.receive()
        return Err

    def setGateToCSA(self): # Routes the gate through the CSA circuit -- APM 23JUL26
        self.send(B12)
        Err = self.receive()
        return Err

    def testRelaysFast(self): # Runs fast hardware test of all 54 device relays -- APM 23JUL26
        self.send(TFX)
        Err = self.receive()
        return Err

    def testRelaysSlow(self): # Runs slow hardware test of all 54 device relays -- APM 23JUL26
        self.send(TSX)
        Err = self.receive()
        return Err

    def resetAllToHold(self): # Resets all 54 device relays to hold state -- APM 23JUL26
        self.send(RXX)
        Err = self.receive()
        return Err

    def nodeToMeasure(self,word,bit): # Sets a given node to the Measure state -- APM 27JUL26
        cmd = 'M' + self.TeensyWordList[word] + self.TeensyBitList[bit]
        self.send(cmd)
        Err = self.receive()
        return Err

    def nodeToHold(self,word,bit): # Sets a given node to the Hold state -- APM 27JUL26
        cmd = 'H' + self.TeensyWordList[word] + self.TeensyBitList[bit]
        self.send(cmd)
        Err = self.receive()
        return Err

    def SysInit(self):  # Runs a sequence to initialise all the relays at start -- APM 23JUL26
        self.setRelaysToOn()
        if Instruments == 'Internal':
            self.setSourceInt()
            self.setDrainInt()
            self.setHoldInt()
            self.setGateInt()
        elif Instruments == 'External':
            self.setSourceExt()
            self.setDrainExt()
            self.setHoldExt()
            self.setGateExt()
        SourcePol, HoldPol = ConfigInterp.Polarities()
        if SourcePol == 'Positive':
            self.setPosSource()
        elif SourcePol == 'Negative':
            self.setNegSource()
        if HoldPol == 'Positive':
            self.setPosHold()
        elif HoldPol == 'Negative':
            self.setNegHold()
        if DrainGain == 'low':
            self.setDrainLowGain()
        elif DrainGain == 'high':
            self.setDrainHighGain()
        if GateGain == 'low':
            self.setGateLowGain()
        elif GateGain == 'high':
            self.setGateHighGain()
        if DrainCirc == 'TIA':
            self.setDrainToTIA()
        elif DrainCirc == 'CSA':
            self.setDrainToCSA()
        if GateCirc == 'TIA':
            self.setGateToTIA()
        elif GateCirc == 'CSA':
            self.setGateToCSA()
        if ScanDir == 'Horizontal':
            self.setWordsAsSource()
        elif ScanDir == 'Vertical':
            self.setBitsAsSource()
        self.resetAllToHold()

    def SysReset(self):  # Runs a sequence to reset all the relays for next run -- APM 09SEP25
        self.resetAllToHold()

    def SysSoftShutdown(self):  # Runs a sequence to setup for shutdown but leave MUXes powered -- APM 09SEP25
        self.resetAllToHold()

    def SysHardShutdown(self):  # Runs a sequence to setup for shutdown including depowering the MUXes -- APM 09SEP25
        self.resetAllToHold()
        self.setRelaysToOff()

    def WordRelayTest(self,bias,HoldTime):
        if bias == 'S':
            self.setWordsAsSource()
        elif bias == 'D':
            self.setBitsAsSource()
        print('Prepare to test Word:',self.ChipWordList[1],' in 1 seconds.')
        time.sleep(1)
        for i in chain(range(1, 15), range(27, 14, -1)):
            print('Wordline: ', self.ChipWordList[i], ' to Hold for ', HoldTime, ' seconds.')
            self.nodeToHold(i,1)
            time.sleep(HoldTime)
            print('Wordline: ',self.ChipWordList[i],' to ',bias,' for ',HoldTime,' seconds.')
            self.nodeToMeasure(i,1)
            time.sleep(HoldTime)
            print('Wordline: ', self.ChipWordList[i], ' to Hold for ', HoldTime, ' seconds.')
            self.nodeToHold(i,1)
            time.sleep(HoldTime)
            if i < 27:
                print('Prepare to test Word:',self.WordList[i+1],' in 1 second.')
                time.sleep(1)
            else:
                print('Finished Test.')
                print()
                time.sleep(3)

    def BitRelayTest(self,bias,HoldTime):
        if bias == 'S':
            self.setBitsAsSource()
        elif bias == 'D':
            self.setWordsAsSource()
        print('Prepare to test Bit:',self.ChipBitList[1],' in 1 seconds')
        time.sleep(1)
        for i in range(1,28):
            print ('Bitline: ',self.ChipBitList[i],' to Hold for ',HoldTime,' seconds.')
            self.nodeToHold(1,i)
            time.sleep(HoldTime)
            print('Bitline: ',self.ChipBitList[i],' to ',bias,' for ',HoldTime,' seconds.')
            self.nodeToMeasure(1,i)
            time.sleep(HoldTime)
            print('Bitline: ',self.ChipBitList[i],' to Hold for ',HoldTime,' seconds.')
            self.nodeToHold(1,i)
            time.sleep(HoldTime)
            if i < 27:
                print('Prepare to test Bit:',self.ChipBitList[i+1],' in 1 second.')
                time.sleep(1)
            else:
                print('Finished Test.')
                print()
                time.sleep(3)

    def SysTestSingle(self,word,bit,wait): # Switches a given device over to connection for a specified time -- APM 10SEP25
        self.nodeToMeasure(word,bit)
        print('Testing: ', self.ChipWordList[word], self.ChipBitList[bit])
        time.sleep(wait)
        self.nodeToMeasure(word,bit)

    def SysTestFull(self,wait): # Switches each node on for a specified time in sequence -- APM 10SEP25
        for i in chain(range(1, 15), range(27, 14, -1)):
            for j in range(1, 28):
                self.nodeToMeasure(i,j)
                print('Testing: ',self.ChipWordList[i],self.ChipBitList[j])
                time.sleep(wait)
                self.nodeToMeasure(i,j)

    def SysTest4x4(self,wait): # Switches each node on for a specified time in sequence -- APM 10SEP25
        for i in range(1,5):
            for j in range(1,5):
                self.nodeToMeasure(i,j)
                print('Testing: ',self.ChipWordList[i],self.ChipBitList[j])
                time.sleep(wait)
                self.nodeToHold(i,j)

if __name__ == "__main__": # execute only if this script is run, not when it's being imported
    my_teensy = TeensyMUX()
    my_teensy.SysInit() # Running as main will initialise system -- APM 09SEP25
#    my_teensy.WordRelayTest('S',1.5)
#    my_teensy.BitRelayTest('D',1.5)
#    my_teensy.SysTestSingle(3,3,10) # Will connect to device A1 for 10 sec -- APM 10SEP25
#    my_teensy.SysTest4x4(20) # Runs a test using the 4x4 board -- APM 30SEP25
#    my_teensy.SysTestFull(0.1) # Will connect to each device for 0.1 sec -- APM 10SEP25
    my_teensy.SysReset() # Runs a reset -- APM 10SEP25