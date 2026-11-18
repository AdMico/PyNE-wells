"""
Brought to PyNE-wells v2.1.0 on Wed Nov 18 2026 by APM

@developer: Adam Micolich

This class sets up the Teensy to be controlled remotely. The truth table is now in the Teensy .ino file.
This code mostly just handles the serial interface from the Raspberry Pi to the Teensy in the Gen 6 boxes.
"""

from Config_Gen6 import DrainInst,SourceInst,HoldInst,GateInst,ScanDir,DrainGain,HGGain,DrainCirc,HGCirc,TeensyPort
from ConfigInterpreter_Gen6 import ConfigInterp
import serial
import time
from itertools import chain

class TeensyMUX:

    def __init__(self):
        self.port = TeensyPort
        self.teensy = serial.Serial(self.port,9600)
        self.ChipWordList = ["OFF","A","B","C","D","E","F","G","H","I","J","K","L","M","N",
                           "&","Z","Y","X","W","V","U","T","S","R","Q","P","O"]
        self.ChipBitList = ["OFF","1","2","3","4","5","6","7","8","9","10","11","12","13","14",
                           "15","16","17","18","19","20","21","22","23","24","25","26","27"]
        self.TeensyWordList = ["OFF","A","B","C","D","E","F","G","H","I","J","K","L","M","N",
                           "O","P","Q","R","S","T","U","V","W","X","Y","Z","&"]
        self.TeensyBitList = ["OFF","A","B","C","D","E","F","G","H","I","J","K","L","M","N",
                           "O","P","Q","R","S","T","U","V","W","X","Y","Z","&"]

        ## Useful mapping information follows below.
        # GPIO Mapping for Gen6 V2+: W-EN1 = 1; W-EN2 = 2; W-A0 = 3; W-A1 = 4; W-A2 = 5; W-A3 = 6;
        # B-EN1 = 7; B-EN2 = 8; B-A0 = 9; B-A1 = 10; B-A2 = 11; B-A3 = 12;
        # Bias Bits = 13; Bias Words (def) = 14; Word On = 15; Word Off (def) = 16; Bit On = 17;
        # Bit Off (def) = 18; Gate TIA = 19; Hold TIA (def) = 20; Source Ext = 21; Source Int (def) = 22;
        # Drain Ext = 23; Drain Int (def) = 24; Hold Ext = 25; Hold Int (def) = 26; Gate Ext = 27;
        # Gate Int (def) = 28; V1-Pos = 29; V1-Neg (def) = 30; V2-Pos = 31; V2-Neg (def) = 32;
        # I1-Hi = 33; I1-Lo (def) = 34; I2-Hi = 35; I2-Lo (def) = 36; I1-CSA = 37;
        # I1-TIA (def) = 38, I2-CSA = 39; I2-TIA (def) = 40.
        #
        # Control Relay Commands: 01 = K-O; 02 = K-P; 03 = K-S; 04 = K-D; 05 = K-H; 06 = K-G;
        # 07 = K-V1, K-X1, K-I5; 08 = K-V2, K-X2, K-I6; 09 = K-I1; 10 = K-I2, 11 = K-I3, 12 = K-I4
        # D command sets to relay default, N command sets to relay non-default.

    def send(self,msg):
        msg = msg + "\n" #add newline to string
        command = msg.encode("ascii")  #encode to ascii
        self.teensy.write(command)

    def receive(self):
        msg = self.teensy.read_until()  #read until newline
        response = msg.decode("ascii")  #decode from ascii
        return response

    def setWordsAsSource(self): # Sets words as source and bits as drain -- APM 23JUL26
        self.send("D01")
        Err = self.receive()
        return Err

    def setBitsAsSource(self): # Sets bits as source and words as drain -- APM 23JUL26
        self.send("N01")
        Err = self.receive()
        return Err

    def setHoldToTIA(self): # Sets Hold to the second TIA circuit, Gate on MCC152/AO1 -- APM 18NOV26
        self.send("D02")
        Err = self.receive()
        return Err

    def setGateToTIA(self): # Sets Gate to the second TIA circuit, Hold on MCC152/AO1 -- APM 18NOV26
        self.send("N02")
        Err = self.receive()
        return Err

    def setSourceInt(self): # Connects source to MCC152 AO0 -- APM 23JUL26
        self.send("D03")
        Err = self.receive()
        return Err

    def setSourceExt(self): # Connects source to BNC -- APM 23JUL26
        self.send("N03")
        Err = self.receive()
        return Err

    def setDrainInt(self): # Connects drain to MCC128 CH0H -- APM 23JUL26
        self.send("D04")
        Err = self.receive()
        return Err

    def setDrainExt(self): # Connects drain to BNC -- APM 23JUL26
        self.send("N04")
        Err = self.receive()
        return Err

    def setHoldInt(self): # Connects hold to MCC152 AO1 -- APM 23JUL26
        self.send("D05")
        Err = self.receive()
        return Err

    def setHoldExt(self): # Connects hold to BNC -- APM 23JUL26
        self.send("N05")
        Err = self.receive()
        return Err

    def setGateInt(self): # Connects gate to MCC128 CH1H -- APM 23JUL26
        self.send("D06")
        Err = self.receive()
        return Err

    def setGateExt(self): # Connects gate to BNC -- APM 23JUL26
        self.send("N06")
        Err = self.receive()
        return Err

    def setNegSource(self): # Sets Source to negative voltage range -- APM 28JUL26
        self.send("D07")
        Err = self.receive()
        return Err

    def setPosSource(self): # Sets Source to positive voltage range -- APM 28JUL26
        self.send("N07")
        Err = self.receive()
        return Err

    def setNegHG(self): # Sets Hold/Gate to negative voltage range -- APM 18NOV26
        self.send("D08")
        Err = self.receive()
        return Err

    def setPosHG(self): # Sets Hold/Gate to positive voltage range -- APM 18NOV26
        self.send("N08")
        Err = self.receive()
        return Err

    def setDrainLowGain(self): # Sets drain to 10^3 V/A gain -- APM 23JUL26
        self.send("D09")
        Err = self.receive()
        return Err

    def setDrainHighGain(self): # Sets drain to 10^4 V/A gain -- APM 23JUL26
        self.send("N09")
        Err = self.receive()
        return Err

    def setGateLowGain(self): # Sets gate to 10^3 V/A gain -- APM 23JUL26
        self.send("D10")
        Err = self.receive()
        return Err

    def setGateHighGain(self): # Sets gate to 10^4 V/A gain -- APM 23JUL26
        self.send("N10")
        Err = self.receive()
        return Err

    def setDrainToTIA(self): # Routes the drain through the TIA circuit -- APM 23JUL26
        self.send("D11")
        Err = self.receive()
        return Err

    def setDrainToCSA(self): # Routes the drain through the CSA circuit -- APM 23JUL26
        self.send("N11")
        Err = self.receive()
        return Err

    def setGateToTIA(self): # Routes the gate through the TIA circuit -- APM 23JUL26
        self.send("D12")
        Err = self.receive()
        return Err

    def setGateToCSA(self): # Routes the gate through the CSA circuit -- APM 23JUL26
        self.send("N12")
        Err = self.receive()
        return Err

    def testRelaysFast(self): # Runs fast hardware test of all 54 device relays -- APM 23JUL26
        self.send("TFX")
        Err = self.receive()
        return Err

    def testRelaysSlow(self): # Runs slow hardware test of all 54 device relays -- APM 23JUL26
        self.send("TSX")
        Err = self.receive()
        return Err

    def resetAllNodesToHold(self): # Resets all 54 device relays to hold state -- APM 26AUG26
        self.send("RDX")
        Err = self.receive()
        return Err

    def resetAllControlsToDefault(self): # Resets all control relays to their default state -- APM 26AUG26
        self.send("RCX")
        Err = self.receive()
        return Err

    def askForActiveNode(self): # Asks Teensy for the active node -- APM 27AUG26
        self.send("ACT")
        Err = self.receive()
        return Err

    def nodeToMeasure(self,word,bit): # Sets a given node to the Measure state -- APM 27JUL26
        cmd = "M" + self.TeensyWordList[word] + self.TeensyBitList[bit]
        self.send(cmd)
        Err = self.receive()
        return Err

    def nodeToHold(self,word,bit): # Sets a given node to the Hold state -- APM 27JUL26
        cmd = "H" + self.TeensyWordList[word] + self.TeensyBitList[bit]
        self.send(cmd)
        Err = self.receive()
        return Err

    def wordShift(self,hold,meas): # Shifts measure from one word line to another -- APM 26AUG26
        cmd = "W" + self.TeensyWordList[hold] + self.TeensyWordList[meas]
        self.send(cmd)
        Err = self.receive()
        return Err

    def bitShift(self,hold,meas): # Shifts measure from one bit line to another -- APM 26AUG26
        cmd = "B" + self.TeensyBitList[hold] + self.TeensyBitList[meas]
        self.send(cmd)
        Err = self.receive()
        return Err

    def SysInit(self):  # Runs a sequence to initialise all the relays at start -- APM 23JUL26
        self.setRelaysToOn()
        if SourceInst == "Internal":
            self.setSourceInt()
        elif SourceInst == "External":
            self.setSourceExt()
        if DrainInst == "Internal":
            self.setDrainInt()
        elif DrainInst == "External":
            self.setDrainExt()
        if HoldInst == "Internal":
            self.setHoldInt()
        elif HoldInst == "External":
            self.setHoldExt()
        if GateInst == "Internal":
            self.setGateInt()
        elif GateInst == "External":
            self.setGateExt()
        SourcePol, HGPol = ConfigInterp.Polarities()
        if SourcePol == "Positive":
            self.setPosSource()
        elif SourcePol == "Negative":
            self.setNegSource()
        if HGPol == "Positive":
            self.setPosHG()
        elif HGPol == "Negative":
            self.setNegHG()
        if DrainGain == "Low":
            self.setDrainLowGain()
        elif DrainGain == "High":
            self.setDrainHighGain()
        if HGGain == "Low":
            self.setGateLowGain()
        elif HGGain == "High":
            self.setGateHighGain()
        if DrainCirc == "TIA":
            self.setDrainToTIA()
        elif DrainCirc == "CSA":
            self.setDrainToCSA()
        if HGCirc == "TIA":
            self.setGateToTIA()
        elif HGCirc == "CSA":
            self.setGateToCSA()
        if ScanDir == "Horizontal":
            self.setWordsAsSource()
        elif ScanDir == "Vertical":
            self.setBitsAsSource()
        self.resetAllNodesToHold()

    def SysReset(self):  # Runs a sequence to reset all the relays for next run -- APM 09SEP25
        self.resetAllNodesToHold()

    def SysSoftShutdown(self):  # Runs a sequence to setup for shutdown but leave MUXes powered -- APM 09SEP25
        self.resetAllNodesToHold()

    def SysHardShutdown(self):  # Runs a sequence to setup for shutdown including depowering the MUXes -- APM 09SEP25
        self.resetAllNodesToHold()
        self.setRelaysToOff()

    def WordRelayTest(self,bias,HoldTime):
        if bias == "S":
            self.setWordsAsSource()
        elif bias == "D":
            self.setBitsAsSource()
        print("Prepare to test Word:",self.ChipWordList[1]," in 1 seconds.")
        time.sleep(1)
        for i in chain(range(1, 15), range(27, 14, -1)):
            print("Wordline: ", self.ChipWordList[i], " to Hold for ", HoldTime, " seconds.")
            self.nodeToHold(i,1)
            time.sleep(HoldTime)
            print("Wordline: ",self.ChipWordList[i]," to ",bias," for ",HoldTime," seconds.")
            self.nodeToMeasure(i,1)
            time.sleep(HoldTime)
            print("Wordline: ", self.ChipWordList[i], " to Hold for ", HoldTime, " seconds.")
            self.nodeToHold(i,1)
            time.sleep(HoldTime)
            if i < 27:
                print("Prepare to test Word:",self.WordList[i+1]," in 1 second.")
                time.sleep(1)
            else:
                print("Finished Test.")
                print()
                time.sleep(3)

    def BitRelayTest(self,bias,HoldTime):
        if bias == "S":
            self.setBitsAsSource()
        elif bias == "D":
            self.setWordsAsSource()
        print("Prepare to test Bit:",self.ChipBitList[1]," in 1 seconds")
        time.sleep(1)
        for i in range(1,28):
            print ("Bitline: ",self.ChipBitList[i]," to Hold for ",HoldTime," seconds.")
            self.nodeToHold(1,i)
            time.sleep(HoldTime)
            print("Bitline: ",self.ChipBitList[i]," to ",bias," for ",HoldTime," seconds.")
            self.nodeToMeasure(1,i)
            time.sleep(HoldTime)
            print("Bitline: ",self.ChipBitList[i]," to Hold for ",HoldTime," seconds.")
            self.nodeToHold(1,i)
            time.sleep(HoldTime)
            if i < 27:
                print("Prepare to test Bit:",self.ChipBitList[i+1]," in 1 second.")
                time.sleep(1)
            else:
                print("Finished Test.")
                print()
                time.sleep(3)

    def SysTestSingle(self,word,bit,wait): # Switches a given device over to connection for a specified time -- APM 10SEP25
        self.nodeToMeasure(word,bit)
        print("Testing: ", self.ChipWordList[word], self.ChipBitList[bit])
        time.sleep(wait)
        self.nodeToMeasure(word,bit)

    def SysTestFull(self,wait): # Switches each node on for a specified time in sequence -- APM 10SEP25
        for i in chain(range(1, 15), range(27, 14, -1)):
            for j in range(1, 28):
                self.nodeToMeasure(i,j)
                print("Testing: ",self.ChipWordList[i],self.ChipBitList[j])
                time.sleep(wait)
                self.nodeToMeasure(i,j)

    def SysTest4x4(self,wait): # Switches each node on for a specified time in sequence -- APM 10SEP25
        for i in range(1,5):
            for j in range(1,5):
                self.nodeToMeasure(i,j)
                print("Testing: ",self.ChipWordList[i],self.ChipBitList[j])
                time.sleep(wait)
                self.nodeToHold(i,j)

if __name__ == "__main__": # execute only if this script is run, not when it"s being imported
    my_teensy = TeensyMUX()
    my_teensy.SysInit() # Running as main will initialise system -- APM 09SEP25
    Err = my_teensy.askForActiveNode()
    print(Err)
    Err = my_teensy.nodeToMeasure(1,1)
    print(Err)
    Err = my_teensy.askForActiveNode()
    print(Err)
    Err = my_teensy.wordShift(1,2)
    print(Err)
    Err = my_teensy.askForActiveNode()
    print(Err)
    Err = my_teensy.bitShift(1,2)
    print(Err)
    Err = my_teensy.askForActiveNode()
    print(Err)
    Err = my_teensy.nodeToHold(2,2)
    print(Err)
    Err = my_teensy.askForActiveNode()
    print(Err)
#    my_teensy.testRelaysFast()
#    my_teensy.WordRelayTest("S",1.5)
#    my_teensy.BitRelayTest("D",1.5)
#    my_teensy.SysTestSingle(3,3,10) # Will connect to device A1 for 10 sec -- APM 10SEP25
#    my_teensy.SysTestFull(0.1) # Will connect to each device for 0.1 sec -- APM 10SEP25
    my_teensy.SysReset() # Runs a reset -- APM 10SEP25