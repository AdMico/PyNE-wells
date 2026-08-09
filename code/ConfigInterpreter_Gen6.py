"""
Brought to PyNE-wells v2.0.0 on Sun Aug 09 2026 by APM

@developers: Adam Micolich

This acts as an interpreter of the Config_Gen6.py file to supply additional parameters to AssayRun_Gen6.py
"""

from Config_Gen6 import Instruments,DrainGain,GateGain,VSource,VHold,GateModeExt

class ConfigInterp:

    def __init__(self):
        # Nothing to go in here yet.

    def Polarities():
        # Use source and hold voltages to set the DAC polarities
        if VSource >= 0.0:
            SourcePol = 'Positive'
        else:
            SourcePol = 'Negative'
        if VHold > 0.0:
            HoldPol = 'Positive'
        elif VHold < 0.0:
            HoldPol = 'Negative'
        else:
            HoldPol = SourcePol
        return SourcePol,HoldPol

    def Source():
        if Instruments == 'External':  # External Instrument Settings
            Source = 'Dev1/ao0'
        elif Instruments == 'Internal':  # Internal Instrument Settings
            Source = 'MCC152/ao0'
        return Source

    def Hold():
        if Instruments == 'External':  # External Instrument Settings
            Hold = 'Dev1/ao1'
        elif Instruments == 'Internal':  # Internal Instrument Settings
            Hold = 'MCC152/ao1'
        return Hold

    def Drain():
        if Instruments == 'External':  # External Instrument Settings
            Drain = 'Dev1/ai0'
        elif Instruments == 'Internal':  # Internal Instrument Settings
            Drain = 'MCC128/ai0'
        return Drain

    def Gate():
        if Instruments == 'External':  # External Instrument Settings
            if GateModeExt == 'USB6216':
                Gate = 'Dev1/ai1'
        elif Instruments == 'Internal':  # Internal Instrument Settings
            Gate = 'MCC128/ai1'
        return Gate

    def SR():
        if Instruments == 'External':  # External Instrument Settings
            SR = float(4e5)  # Sample Rate in samples/second. 4e5 is maximum for single channel, 2e5 is maximum for pairburst
        elif Instruments == 'Internal':  # Internal Instrument Settings
            SR = float(1e5)  # Sample Rate in samples/second. 1e5 is maximum for single channel, 5e4 is maximum for pairburst.
        return SR

    def SpC():
        if Instruments == 'External':  # External Instrument Settings
            SpC = int(1e3)  # Samples per Channel per measurement -- strongly influences speed
        elif Instruments == 'Internal':  # Internal Instrument Settings
            SpC = int(1e5)  # Samples per Channel per measurement -- strongly influences speed
        return SpC

    def P1Gain():
        # Settings for Current Preamplifiers - P1Gain will be on the drain.
        if Instruments == 'External':  # External Instrument Settings
            P1Gain = float(1e4)
        elif Instruments == 'Internal':  # Internal Instrument Settings
            if DrainGain == 'Low':
                P1Gain = float(1e3)
            elif DrainGain == 'High':
                P1Gain = float(1e4)
        return P1Gain

    def P2Gain():
        # Settings for Current Preamplifiers - P2Gain will be the gate (if used).
        if Instruments == 'External':  # External Instrument Settings
            P2Gain = float(1e4)
        elif Instruments == 'Internal':  # Internal Instrument Settings
            if GateGain == 'Low':
                P2Gain = float(1e3)
            elif GateGain == 'High':
                P2Gain = float(1e4)
        return P2Gain