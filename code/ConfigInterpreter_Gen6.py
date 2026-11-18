"""
Brought to PyNE-wells v2.1.0 on Wed Nov 18 2026 by APM

@developers: Adam Micolich

This acts as an interpreter of the Config_Gen6.py file to supply additional parameters to AssayRun_Gen6.py
"""

from Config_Gen6 import SourceInst,DrainInst,HoldInst,GateInst,DrainGain,HGGain,DrainCirc,HGCirc,VSource,VHold,VGate,SR_Int,SR_Ext,SpC_Int,SpC_Ext
from Config_Gen6 import FemtoOneGain,FemtoTwoGain,SourceCurrMode,HGCurrMode,DrainExt,GateExt,HGMode

class ConfigInterp:

    def Polarities():
        # Use source and hold/gate voltages to set the DAC polarities
        if VSource >= 0.0:
            SourcePol = "Positive"
        else:
            SourcePol = "Negative"
        if HGMode == "HoldTIA":
            if VGate > 0.0:
                HGPol = "Positive"
            elif VGate < 0.0:
                HGPol = "Negative"
            else:
                HGPol = SourcePol
        elif HGMode == "GateTIA":
            if VHold > 0.0:
                HGPol = "Positive"
            elif VHold < 0.0:
                HGPol = "Negative"
            else:
                HGPol = SourcePol
        return SourcePol,HGPol

    def SourceVoltage():
        if SourceInst == "External":  # External Instrument Settings
            SourceOutput = "K2401"
        elif SourceInst == "Internal":  # Internal Instrument Settings
            SourceOutput = "MCC152/ao0"
        return SourceOutput

    def DrainVoltage():
        if DrainInst == "External":  # External Instrument Settings
            DrainOutput = DrainExt
        elif DrainInst == "Internal":  # Internal Instrument Settings
            DrainOutput = "MCC128/Ch0"
        return DrainOutput

    def HoldVoltage():
        if HoldInst == "External":  # External Instrument Settings
            HoldOutput = HoldExt
        elif HoldInst == "Internal":  # Internal Instrument Settings
            if HGMode == "HoldTIA":
                HoldOutput = "MCC128/Ch1"
            elif HGMode == "GateTIA":
                HoldOutput = "MCC152/ao1"
        return HoldOutput

    def GateVoltage():
        if GateInst == "External":  # External Instrument Settings
            GateOutput = GateExt
        elif GateInst == "Internal":  # Internal Instrument Settings
            if HGMode == "HoldTIA":
                GateOutput = "MCC152/ao1"
            elif HGMode == "GateTIA":
                GateOutput = "MCC128/Ch1"
        return GateOutput

    def SourceCurrent():
        if SourceCurrMode == "Inactive":
            SourceCurrent = "Off"
        elif SourceCurrMode == "Active":
            if SourceInst == "External":  # External Instrument Settings
                SourceCurrent = "K2401"
            if SourceInst == "Internal":  # Internal Instrument Settings
                SourceCurrent = "MCC128/Ch4"
        return SourceCurrent

    def DrainCurrent():
        if DrainInst == "External":  # External Instrument Settings
            if DrainExt == "K2401":
                DrainCurrent = "K2401"
            elif DrainExt == "Femto":
                DrainCurrent = "MCC128/Ch2"
        elif DrainInst == "Internal":  # Internal Instrument Settings
            DrainCurrent = "MCC128/Ch0"
        return DrainCurrent

    def HoldCurrent():
        if (HGMode == "GateTIA" and HGCurrMode == "Inactive"):
            HoldCurrent = "Off"
        else:
            if HoldInst == "External":  # External Instrument Settings
                if HoldExt == "K2401":
                    HoldCurrent = "K2401"
                elif HoldExt == "Femto":
                    HoldCurrent = "MCC128/Ch3"
            elif HoldInst == "Internal":  # Internal Instrument Settings
                if HGMode == "HoldTIA":
                    HoldCurrent = "MCC128/Ch1"
                elif HGMode == "GateTIA":
                    HoldCurrent = "MCC128/Ch5"
        return HoldCurrent

    def GateCurrent():
        if (HGMode == "HoldTIA" and HGCurrMode == "Inactive"):
            GateCurrent = "Off"
        else:
            if GateInst == "External":  # External Instrument Settings
                if GateExt == "K2401":
                    GateCurrent = "K2401"
                elif GateExt == "Femto":
                    GateCurrent = "MCC128/Ch3"
            elif GateInst == "Internal":  # Internal Instrument Settings
                if HGMode == "HoldTIA":
                    GateCurrent = "MCC128/Ch5"
                elif HGMode == "GateTIA":
                    GateCurrent = "MCC128/Ch1"
        return GateCurrent

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

    def PSGain():
        # Gain Setting for Source Current Preamplifier.
        if SourceInst == "External":  # External Instrument Setting
            PSGain = float(1e0) # K2401 has no gain -- APM 09Sep26
        elif SourceInst == "Internal":  # Internal Instrument Setting
            PSGain = float(5e2) # Default gain as it is an upstream CSA circuit using INA190A5
        return PSGain

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
                PDGain = float(5e2) # Gain from INA190A5
        return PDGain

    def PHGain():
        # Gain Setting for Hold Current Preamplifier.
        if HoldInst == "External":  # External Instrument Setting
            if HoldExt == "K2401":
                PHGain = float(1e0)
            elif HoldExt == "Femto":
                PHGain = FemtoTwoGain # Gain for the Femto connected to the hold line
        elif HoldInst == "Internal":  # Internal Instrument Setting
            if HGMode == "GateTIA":
                if HGCirc == "TIA":
                    if HGGain == "Low":
                        PHGain = float(1e3)
                    elif HGGain == "High":
                        PHGain = float(1e4)
                elif HGCirc == "CSA":
                    PHGain = float(5e2) # Gain from INA190A5
            elif HGMode == "HoldTIA":
                PHGain = float(5e2)  # Default gain as it is an upstream CSA circuit using INA190A5
        return PHGain

    def PGGain():
        # Gain Setting for Gate Current Preamplifier.
        if GateInst == "External":  # External Instrument Setting
            if GateExt == "K2401":
                PGGain = float(1e0)
            elif GateExt == "Femto":
                PGGain = FemtoTwoGain # Gain for the Femto connected to the gate line
        elif GateInst == "Internal":  # Internal Instrument Setting
            if HoldGateMode == "GateTIA":
                if GateCirc == "TIA":
                    if GateGain == "Low":
                        PGGain = float(1e3)
                    elif GateGain == "High":
                        PGGain = float(1e4)
                elif GateCirc == "CSA":
                    PGGain = float(5e2) # Gain from INA190A5
            elif HoldGateMode == "HoldTIA":
                PGGain = float(5e2)  # Default gain as it is an upstream CSA circuit using INA190A5
        return PGGain

    def PSRange():
        # Range Setting for Source Current Preamplifier.
        if SourceInst == "External":  # External Instrument Setting
            PSRange = "Auto"
        elif SourceInst == "Internal":  # Internal Instrument Only
            PSRange = "BIP_1V" # 1V range for CSA
        return PSRange

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

    def PHRange():
        # Range Setting for Hold Current Preamplifier.
        if HGMode == "HoldTIA":
            if HoldInst == "External":  # External Instrument Setting
                if HoldExt == "K2401":
                    PHRange = "Auto"
                elif HoldExt == "Femto":
                    PHRange = "BIP_10V"
            elif HoldInst == "Internal":  # Internal Instrument Only
                if HoldCirc == "TIA":
                    PHRange = "BIP_5V"  # 5V range for TIA
                elif HoldCirc == "CSA":
                    PHRange = "BIP_1V"  # 1V range for CSA
        elif HGMode == "GateTIA":
            if HoldInst == "External":  # External Instrument Setting
                PHRange = "Auto"
            elif HoldInst == "Internal":  # Internal Instrument Only
                PHRange = "BIP_1V"  # 1V range for CSA
        return PHRange

    def PGRange():
        # Range Setting for Gate Current Preamplifier.
        if HGMode == "GateTIA":
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
        elif HGMode == "HoldTIA":
            if GateInst == "External":  # External Instrument Setting
                PGRange = "Auto"
            elif GateInst == "Internal":  # Internal Instrument Only
                PGRange = "BIP_1V" # 1V range for CSA
        return PGRange