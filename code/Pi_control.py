"""
Brought to v4.0.0 on Fri Sep 1 2023 by APM

@author: Jan Gluschke

This class sets up the pi to be controlled remotely. The truth table is that of the multiplexer.
"""
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory

class PiMUX:

    def __init__(self, IP = '129.94.163.203'):
        self.IP = IP
        self.PiFactory = PiGPIOFactory(host= self.IP)
        #TruthTable format: Device: [A3,A2,A1,A0,EN1,EN2,EN3,EN4], #MUX<number> Switch <number> (Pin <number>)
        self.TruthTable = {0: [0, 0, 0, 0, 0, 0, 0, 0],  #OFF state
                           1: [1, 0, 1, 0, 0, 1, 0, 0],  # MUX2 Switch 11 (9)
                           2: [1, 0, 0, 1, 0, 1, 0, 0],  # MUX2 contact 10 (10)
                           3: [1, 0, 0, 0, 0, 1, 0, 0],  # MUX2 contact 9 (11)
                           4: [0, 1, 1, 1, 0, 1, 0, 0],  # MUX2 contact 8 (26)
                           5: [0, 1, 1, 0, 0, 1, 0, 0],  # MUX2 contact 7 (25)
                           6: [0, 1, 0, 1, 0, 1, 0, 0],  # MUX2 contact 6 (24)
                           7: [0, 1, 0, 0, 0, 1, 0, 0],  # MUX2 contact 5 (23)
                           8: [0, 0, 1, 1, 0, 1, 0, 0],  # MUX2 contact 4 (22)
                           9: [0, 0, 1, 0, 0, 1, 0, 0],  # MUX2 contact 3 (21)
                           10: [0, 0, 0, 1, 0, 1, 0, 0],  # MUX2 contact 2 (20)
                           11: [0, 0, 0, 0, 0, 1, 0, 0],  # MUX2 contact 1 (19)
                           12: [1, 1, 1, 1, 1, 0, 0, 0],  # MUX1 contact 16 (4)
                           13: [1, 1, 1, 0, 1, 0, 0, 0],  # MUX1 contact 15 (5)
                           14: [1, 1, 0, 0, 1, 0, 0, 0],  # MUX1 contact 13 (7)
                           15: [1, 0, 1, 1, 1, 0, 0, 0],  # MUX1 contact 12 (8)
                           16: [1, 0, 1, 0, 1, 0, 0, 0],  # MUX1 contact 11 (9)
                           17: [1, 0, 0, 1, 1, 0, 0, 0],  # MUX1 contact 10 (10)
                           18: [1, 0, 0, 0, 1, 0, 0, 0],  # MUX1 contact 9 (11)
                           19: [0, 1, 1, 1, 1, 0, 0, 0],  # MUX1 contact 8 (26)
                           20: [0, 1, 1, 0, 1, 0, 0, 0],  # MUX1 contact 7 (25)
                           21: [0, 1, 0, 1, 1, 0, 0, 0],  # MUX1 contact 6 (24)
                           22: [0, 1, 0, 0, 1, 0, 0, 0],  # MUX1 contact 5 (23)
                           23: [0, 0, 1, 1, 1, 0, 0, 0],  # MUX1 contact 4 (22)
                           24: [0, 0, 1, 0, 1, 0, 0, 0],  # MUX1 contact 3 (21)
                           25: [0, 0, 0, 1, 1, 0, 0, 0],  # MUX1 contact 2 (20)
                           26: [0, 0, 0, 0, 1, 0, 0, 0],  # MUX1 contact 1 (19)
                           27: [0, 0, 0, 0, 0, 0, 1, 0],  # MUX3 contact 1 (19)
                           28: [0, 0, 0, 1, 0, 0, 1, 0],  # MUX3 contact 2 (20)
                           29: [0, 0, 1, 0, 0, 0, 1, 0],  # MUX3 contact 3 (21)
                           30: [0, 0, 1, 1, 0, 0, 1, 0],  # MUX3 contact 4 (22)
                           31: [0, 1, 0, 0, 0, 0, 1, 0],  # MUX3 contact 5 (23)
                           32: [0, 1, 0, 1, 0, 0, 1, 0],  # MUX3 contact 6 (24)
                           33: [0, 1, 1, 0, 0, 0, 1, 0],  # MUX3 contact 7 (25)
                           34: [0, 1, 1, 1, 0, 0, 1, 0],  # MUX3 contact 8 (26)
                           35: [1, 0, 0, 0, 0, 0, 1, 0],  # MUX3 contact 9 (11)
                           36: [1, 0, 0, 1, 0, 0, 1, 0],  # MUX3 contact 10 (10)
                           37: [1, 0, 1, 0, 0, 0, 1, 0],  # MUX3 contact 11 (9)
                           38: [1, 0, 1, 1, 0, 0, 1, 0],  # MUX3 contact 12 (8)
                           39: [1, 1, 0, 0, 0, 0, 1, 0],  # MUX3 contact 13 (7)
                           40: [1, 1, 1, 0, 0, 0, 1, 0],  # MUX3 contact 15 (5)
                           41: [1, 1, 1, 1, 0, 0, 1, 0],  # MUX3 contact 16 (4)
                           42: [0, 0, 0, 0, 0, 0, 0, 1],  # MUX4 contact 1 (19)
                           43: [0, 0, 0, 1, 0, 0, 0, 1],  # MUX4 contact 2 (20)
                           44: [0, 0, 1, 0, 0, 0, 0, 1],  # MUX4 contact 3 (21)
                           45: [0, 0, 1, 1, 0, 0, 0, 1],  # MUX4 contact 4 (22)
                           46: [0, 1, 0, 0, 0, 0, 0, 1],  # MUX4 contact 5 (23)
                           47: [0, 1, 0, 1, 0, 0, 0, 1],  # MUX4 contact 6 (24)
                           48: [0, 1, 1, 0, 0, 0, 0, 1],  # MUX4 contact 7 (25)
                           49: [0, 1, 1, 1, 0, 0, 0, 1],  # MUX4 contact 8 (26)
                           50: [1, 0, 0, 0, 0, 0, 0, 1],  # MUX4 contact 9 (11)
                           51: [1, 0, 0, 1, 0, 0, 0, 1],  # MUX4 contact 10 (10)
                           52: [1, 0, 1, 0, 0, 0, 0, 1]}  # MUX4 contact 11 (9)

        #Define what GPIO pins are connected to the selector pins on the MUX

        self.E1_pin = LED(6,pin_factory = self.PiFactory)
        self.E2_pin = LED(13,pin_factory = self.PiFactory)
        self.E3_pin = LED(19,pin_factory = self.PiFactory)
        self.E4_pin = LED(26,pin_factory = self.PiFactory)

        self.A0_pin = LED(12,pin_factory = self.PiFactory)
        self.A1_pin = LED(16,pin_factory = self.PiFactory)
        self.A2_pin = LED(20,pin_factory = self.PiFactory)
        self.A3_pin = LED(21,pin_factory = self.PiFactory)

        self.listPins = [self.A3_pin,self.A2_pin,self.A1_pin,self.A0_pin,self.E1_pin,self.E2_pin,self.E3_pin,self.E4_pin]

        #Uses truth table to set GPIO pin voltages to activate desired output.

    def setMuxToOutput(self, desiredOutput):
        for index,item in enumerate(self.listPins):
            if self.TruthTable[desiredOutput][index]:
                item.on()
            else:
                item.off()

if __name__ == "__main__": # execute only if this script is run, not when it's being imported
    my_pi = PiMUX()
    my_pi.setMuxToOutput(0)