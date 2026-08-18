"""
Brought to PyNE-wells v2.0.0 on Sun Aug 09 2026 by APM

@developers: Adam Micolich

This acts as an interpreter of the Config_Gen6.py file to supply additional parameters to AssayRun_Gen6.py
"""

from Config_Gen6 import Instruments,DrainGain,GateGain,DrainCirc,GateCirc,VSource,VHold,GateModeExt,SR_Int,SR_Ext,SpC_Int,SpC_Ext,FemtoGateGain,FemtoDrainGain

class ConfigInterp:

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

    def SourceVoltage():
        if Instruments == 'External':  # External Instrument Settings
            SourceOutput = 'USB6216/ao0'
        elif Instruments == 'Internal':  # Internal Instrument Settings
            SourceOutput = 'MCC152/ao0'
        return SourceOutput

    def HoldVoltage():
        if Instruments == 'External':  # External Instrument Settings
            HoldOutput = 'USB6216/ao1'
        elif Instruments == 'Internal':  # Internal Instrument Settings
            HoldOutput = 'MCC152/ao1'
        return HoldOutput

    def DrainCurrent():
        if Instruments == 'External':  # External Instrument Settings
            DrainCurrent = 'USB6216/ai0'
        elif Instruments == 'Internal':  # Internal Instrument Settings
            DrainCurrent = 'MCC128/Ch0'
        return DrainCurrent

    def GateCurrent():
        if Instruments == 'External':  # External Instrument Settings
            if GateModeExt == 'USB6216':
                GateCurrent = 'USB6216/ai1'
            elif GateModeExt == 'K2401':
                GateCurrent = 'K2401'
        elif Instruments == 'Internal':  # Internal Instrument Settings
            GateCurrent = 'MCC128/Ch1'
        return GateCurrent

    def SourceCurrent():
        if Instruments == 'Internal':  # Internal Instrument Settings
            SourceCurrent = 'MCC128/Ch4'
        return SourceCurrent

    def HoldCurrent():
        if Instruments == 'Internal':  # Internal Instrument Settings
            HoldCurrent = 'MCC128/Ch5'
        return HoldCurrent

    def SR():
        if Instruments == 'External':  # External Instrument Settings
            SR = SR_Ext
        elif Instruments == 'Internal':  # Internal Instrument Settings
            SR = SR_Int
        return SR

    def SpC():
        if Instruments == 'External':  # External Instrument Settings
            SpC = SpC_Ext
        elif Instruments == 'Internal':  # Internal Instrument Settings
            SpC = SpC_Int
        return SpC

    def PDGain():
        # Settings for Drain Current Preamplifier.
        if Instruments == 'External':  # External Instrument Settings
            PDGain = FemtoDrainGain
        elif Instruments == 'Internal':  # Internal Instrument Settings
            if DrainCirc == "TIA":
                if DrainGain == 'Low':
                    PDGain = -float(1e3) # Negative to correct for TIA op-amp behaviour
                elif DrainGain == 'High':
                    PDGain = -float(1e4) # Negative to correct for TIA op-amp behaviour
            elif DrainCirc == "CSA":
                PDGain = float(1e2) # Gain from INA240A3
        return PDGain

    def PGGain():
        # Settings for Gate Current Preamplifier.
        if Instruments == 'External':  # External Instrument Settings
            PGGain = FemtoGateGain
        elif Instruments == 'Internal':  # Internal Instrument Settings
            if GateCirc == "TIA":
                if GateGain == 'Low':
                    PGGain = -float(1e3) # Negative to correct for TIA op-amp behaviour
                elif GateGain == 'High':
                    PGGain = -float(1e4) # Negative to correct for TIA op-amp behaviour
            elif GateCirc == "CSA":
                PGGain = float(1e2) # Gain from INA240A3
        return PGGain

    def PSGain():
        # Settings for Source Current Preamplifier.
        if Instruments == 'External':  # External Instrument Settings
            PSGain = float(1e4) # Serves no real function as not part of standard external hardware set -- APM 13Aug26
        elif Instruments == 'Internal':  # Internal Instrument Settings
            PSGain = float(1e2) # Default gain as it is an upstream CSA circuit using INA240A3
        return PSGain

    def PHGain():
        # Settings for Hold Current Preamplifier.
        if Instruments == 'External':  # External Instrument Settings
            PHGain = float(1e4) # Serves no real function as not part of standard external hardware set -- APM 13Aug26
        elif Instruments == 'Internal':  # Internal Instrument Settings
            PHGain = float(1e2) # Default gain as it is an upstream CSA circuit using INA240A3
        return PHGain