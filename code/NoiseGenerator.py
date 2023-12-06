"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima
@author: Jakob Seidl
"""

from numpy import random
import numpy as np
import Instrument

@Instrument.enableOptions
class LinearNoiseGenerator(Instrument.Instrument):
    """Creates a LinearNoiseGenerator virtual instrument that creates simulated linearly increasing noise signal.

    :param
    :return: NoiseGenerator instance

    >>> LinearNoiseGenerator()

    """

    defaultOutput = "sourceLevel"
    defaultInput = "noise"
    def __init__(self,slope = 1,std=5):
        super(LinearNoiseGenerator,self).__init__()
        self.counter  = 0
        self.type = 'NoiseGenerator'
        self.name = 'myNoiseGenerator'
        self.slope = slope
        self.std = std
    @Instrument.addOptionSetter("sourceLevel")
    def _dummySourceFunction(self,dummyVariable):
        pass

    @Instrument.addOptionGetter("noise")
    def _getNoise(self):
        self.counter += 1

        return (self.slope*self.counter + random.normal(0 , self.std))

    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName

    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name

    def reset(self):
        self.counter = 0

    def goTo(target = 0.1,delay = 0.2,stepsize = 0.2): #Dummy function. Is required for every class to be passed to the sweep functin.
        return

@Instrument.enableOptions
class SineNoiseGenerator(Instrument.Instrument):
    """Creates a SineNoiseGenerator virtual instrument that creates simulated sinusoidal noise signal.

    :param
    :return: NoiseGenerator instance

    >>> SineNoiseGenerator()

    """

    defaultOutput = "sourceLevel"
    defaultInput = "noise"

    def __init__(self, amplitude=2, std=0.3,linearSlope = 0):
        super(SineNoiseGenerator, self).__init__()
        self.counter = 0
        self.type = 'NoiseGenerator'
        self.name = 'myNoiseGenerator'
        self.amplitude = amplitude
        self.std = std
        self.linearSlope = linearSlope
    @Instrument.addOptionSetter("sourceLevel")
    def _dummySourceFunction(self, dummyVariable):
        pass

    @Instrument.addOptionGetter("noise")
    def _getNoise(self):
        self.counter += 1

        return (self.amplitude * np.sin((self.counter)/30*2*np.pi) + self.linearSlope*self.counter + random.normal(0, self.std))

    @Instrument.addOptionSetter("name")
    def _setName(self, instrumentName):
        self.name = instrumentName

    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name

    def goTo(target=0.1, delay=0.2,
             stepsize=0.2):  # Dummy function. Is required for every class to be passed to the sweep function.
        return
    def reset(self):
        self.counter = 0

@Instrument.enableOptions
class DoubleNoiseGenerator(Instrument.Instrument):
    """Creates a TimeMeas virtual instrument that can set time (setter) or measure the elapsed time during a measurement.

    :param
    :return: NoiseGenerator instance

    >>> DoubleNoiseGenerator()

    """

    defaultOutput = "sourceLevel"
    defaultInput = "noise"

    def __init__(self, amplitude=1, std=1,linearSlope = 0):
        super(DoubleNoiseGenerator, self).__init__()
        self.counter = 0
        self.name = 'myDoubleNoiseGenerator'
        self.amplitude = amplitude
        self.std = std
        self.type = 'DoubleNoiseGenerator'
        self.linearSlope = linearSlope
    @Instrument.addOptionSetter("sourceLevel")
    def _dummySourceFunction(self, dummyVariable):
        pass

    @Instrument.addOptionGetter("noise")
    def _getNoise(self):
        self.counter += 1
        res = self.amplitude * np.sin((self.counter)/30*2*np.pi) + self.linearSlope*self.counter + random.normal(0, self.std)
        return (res,-res)

    @Instrument.addOptionSetter("name")
    def _setName(self, instrumentName):
        self.name = instrumentName

    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name

    def reset(self):
        self.counter = 0

    def goTo(target=0.1, delay=0.2,
             stepsize=0.2):  # Dummy function. Is required for every class to be passed to the sweep function.
        return