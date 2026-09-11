"""
Brought to PyNE-wells v2.0.0 on Sun Aug 09 2026 by APM

@developers: Adam Micolich

This acts as an interpreter of the Config_Gen6.py file to supply additional parameters to AssayRun_Gen6.py
"""

from Config_Gen6 import SourceInst, DrainInst,HoldInst,GateInst,DrainGain,GateGain,DrainCirc,GateCirc,VSource,VHold,SR_Int,SR_Ext,SpC_Int,SpC_Ext
from Config_Gen6 import FemtoOneGain,FemtoTwoGain,SourceCurrMode,HoldCurrMode,DrainExt,GateExt

class ConfigInterp:

    def Polarities():
        # Use source and hold voltages to set the DAC polarities
        if VSource >= 0.0:
            SourcePol = "Positive"
        else:
            SourcePol = "Negative"
        if VHold > 0.0:
            HoldPol = "Positive"
        elif VHold < 0.0:
            HoldPol = "Negative"
        else:
            HoldPol = SourcePol
        return SourcePol,HoldPol

    def SourceVoltage():
        if SourceInst == "External":  # External Instrument Settings
            SourceOutput = "K2401"
        elif SourceInst == "Internal":  # Internal Instrument Settings
            SourceOutput = "MCC152/ao0"
        return SourceOutput

    def HoldVoltage():
        if HoldInst == "External":  # External Instrument Settings
            HoldOutput = "K2401"
        elif HoldInst == "Internal":  # Internal Instrument Settings
            HoldOutput = "MCC152/ao1"
        return HoldOutput

    def DrainCurrent():
        if DrainInst == "External":  # External Instrument Settings
            if DrainExt == "K2401":
                DrainCurrent = "K2401"
            elif DrainExt == "Femto":
                DrainCurrent = "MCC128/Ch2"
        elif DrainInst == "Internal":  # Internal Instrument Settings
            DrainCurrent = "MCC128/Ch0"
        return DrainCurrent

    def GateCurrent():
        if GateInst == "External":  # External Instrument Settings
            if GateExt == "K2401":
                GateCurrent = "K2401"
            elif GateExt == "Femto":
                GateCurrent = "MCC128/Ch3"
        elif GateInst == "Internal":  # Internal Instrument Settings
            GateCurrent = "MCC128/Ch1"
        return GateCurrent

    def SourceCurrent():
        if SourceInst == "External":  # External Instrument Settings
            if SourceCurrMode == "Active":
                SourceCurrent = "K2401"
            elif SourceCurrMode == "Inactive":
                SourceCurrent = "Off"
        if SourceInst == "Internal":  # Internal Instrument Settings
            if SourceCurrMode == "Active":
                SourceCurrent = "MCC128/Ch4"
            elif SourceCurrMode == "Inactive":
                SourceCurrent = "Off"
        return SourceCurrent

    def HoldCurrent():
        if HoldInst == "External":  # External Instrument Settings
            if HoldCurrMode == "Active":
                HoldCurrent = "K2401"
            elif HoldCurrMode == "Inactive":
                HoldCurrent = "Off"
        if HoldInst == "Internal":  # Internal Instrument Settings
            if HoldCurrMode == "Active":
                HoldCurrent = "MCC128/Ch5"
            elif HoldCurrMode == "Inactive":
                HoldCurrent = "Off"
        return HoldCurrent

    def SR():
        if DrainInst == "External":  # External Instrument Settings
            SR = SR_Ext
        elif DrainInst == "Internal":  # Internal Instrument Settings
            SR = SR_Int
        return SR

    def SpC():
        if DrainInst == "External":  # External Instrument Settings
            SpC = SpC_Ext
        elif DrainInst == "Internal":  # Internal Instrument Settings
            SpC = SpC_Int
        return SpC

    def PDGain():
        # Gain Setting for Drain Current Preamplifier.
        if DrainInst == "External":  # External Instrument Setting
            if DrainExt == "K2401":
                PDGain = float(1e0)
            elif DrainExt == "Femto":
                PDGain = FemtoOneGain # Gain for the Femto connected to the drain line
        elif DrainInst == "Internal":  # Internal Instrument Setting
            if DrainCirc == "TIA":
                if DrainGain == "Low":
                    PDGain = float(1e3)
                elif DrainGain == "High":
                    PDGain = float(1e4)
            elif DrainCirc == "CSA":
                PDGain = float(1e2) # Gain from INA240A3
        return PDGain

    def PGGain():
        # Gain Setting for Gate Current Preamplifier.
        if GateInst == "External":  # External Instrument Setting
            if GateExt == "K2401":
                PGGain = float(1e0)
            elif GateExt == "Femto":
                PGGain = FemtoTwoGain # Gain for the Femto connected to the gate line
        elif GateInst == "Internal":  # Internal Instrument Setting
            if GateCirc == "TIA":
                if GateGain == "Low":
                    PGGain = float(1e3)
                elif GateGain == "High":
                    PGGain = float(1e4)
            elif GateCirc == "CSA":
                PGGain = float(1e2) # Gain from INA240A3
        return PGGain

    def PSGain():
        # Gain Setting for Source Current Preamplifier.
        if SourceInst == "External":  # External Instrument Setting
            PSGain = float(1e0) # K2401 has no gain -- APM 09Sep26
        elif SourceInst == "Internal":  # Internal Instrument Setting
            PSGain = float(1e2) # Default gain as it is an upstream CSA circuit using INA240A3
        return PSGain

    def PHGain():
        # Gain Setting for Hold Current Preamplifier.
        if HoldInst == "External":  # External Instrument Setting
            PHGain = float(1e0) # K2401 has no gain -- APM 09Sep26
        elif HoldInst == "Internal":  # Internal Instrument Setting
            PHGain = float(1e2) # Default gain as it is an upstream CSA circuit using INA240A3
        return PHGain

    def PDRange():
        # Range Setting for Drain Current Preamplifier.
        if DrainInst == "External":  # External Instrument Setting
            if DrainExt == "K2401":
                PDRange = "Auto"
            elif DrainExt == "Femto":
                PDRange = "BIP_10V"
        elif DrainInst == "Internal":  # Internal Instrument Only
            if DrainCirc == "TIA":
                PDRange = "BIP_5V" # 5V range for TIA
            elif DrainCirc == "CSA":
                PDRange = "BIP_1V" # 1V range for CSA
        return PDRange

    def PGRange():
        # Range Setting for Gate Current Preamplifier.
        if GateInst == "External":  # External Instrument Setting
            if GateExt == "K2401":
                PGRange = "Auto"
            elif GateExt == "Femto":
                PGRange = "BIP_10V"
        elif GateInst == "Internal":  # Internal Instrument Only
            if GateCirc == "TIA":
                PGRange = "BIP_5V" # 5V range for TIA
            elif GateCirc == "CSA":
                PGRange = "BIP_1V" # 1V range for CSA
        return PGRange

    def PSRange():
        # Range Setting for Source Current Preamplifier.
        if SourceInst == "External":  # External Instrument Setting
            PSRange = "Auto"
        elif SourceInst == "Internal":  # Internal Instrument Only
            PSRange = "BIP_1V" # 1V range for CSA
        return PSRange

    def PHRange():
        # Range Setting for Hold Current Preamplifier.
        if HoldInst == "External":  # External Instrument Setting
            PHRange = "Auto"
        elif HoldInst == "Internal":  # Internal Instrument Only
            PHRange = "BIP_1V" # 1V range for CSA
        return PHRange