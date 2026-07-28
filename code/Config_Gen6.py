"""
Brought to PyNE-wells v2.0.0 on Fri Aug 15 2025 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

This informs various parts of the software about aspects of your bench setup. Edit as needed for your setup.
"""

## IMPORTANT -- YOU NEED TO SET TeensyPort CORRECTLY BEFORE YOU FIRST USE THE SOFTWARE to avoid having the relay switching fail -- see main README.md file
## IMPORTANT -- I've designed the software for two different instrument configurations: External and Internal
## 'External' runs with the Gen 5 instrument pack (K2401 in source, hold and gate, preamp to NIDAQ on drain)
## 'Internal' runs with the Gen 6 instrument pack (everything via the MCC128/152 DAQHAT system)
Instruments = 'External'

# Information about which Raspberry Pi USB port you are using for the Teensy Serial Connection for switching relays
TeensyPort = '/dev/ttyACM0' #Insert the Raspberry Pi port where your Teensy 4.1 is connected here

# Scan Direction for the array: 'Horizontal' scans along bitlines, which are connected to drain; 'Vertical' scans along wordlines, which are connected to drain
ScanDir = 'Horizontal'

# Settings for Measurement Biases -- VHold must be same sign as VSource (or zero) -- APM 28JUL27
VSource = float(1.0) # Cannot exceed +/- 5V if using internal DAC
VGate = float(0.0) # Must be zero if set to internal
VHold = float(0.0) # Cannot exceed +/- 5V if using internal DAC

# AssayRun settings
ItersAR = int(5) # Number of iterations of device sampling to run before program ends
WaitAR = float(120) # Wait time in seconds between end of one iteration and start of the next -- APM to update to be pace independent
zeroThres = float(0.1) # If conductance is lower, the GUI will display zero for GUI management reasons (but correct conductance will go to data file) -- 30Oct25 APM
basePath = '../data'
GuiUpdateMode = 'grab' # Two options 'point' to update each device pair in a grab, or 'grab' to only update at the end of the whole grab (faster) -- New 11Sep25 APM
PlotTwoMode = 'First' # Two options 'First' makes second Seaborn panel in Gen 5 difference to start, 'Last'makes difference to last grab.

if Instruments == 'External': # External Instrument Settings

    # Settables for this mode go here.
    GateMode = 'USB6216'  # Two options 'USB6216' for default setup (Ag/AgCl electrode on AO1 of USB6216) and 'K2401' for using the Keithley 2401 instead -- New 30Oct25 APM

    # Information about which NIDAQ ports you are using for your NI USB6216BNC instance -- For AssayRunGen6.py
    Source = 'Dev1/ao0'
    Hold = 'Dev1/ao1'
    Drain = 'Dev1/ai0'
    if GateMode == 'USB6216':
        Gate = 'Dev1/ai1'

    # Settings for NIDAQ PairBurst Mode operation
    SR = float(4e5) # Sample Rate in samples/second. 2e5 appears to be maximum for pairburst (400kS/s per channel single channel)
    SpC = int(1e3) # Samples per Channel per measurement -- strongly influences speed (200000 at 200kS/s takes about 1 second)

    # Settings for Femto Preamplifiers - P1Gain will be on the drain, P2Gain will be the gate (if used).
    P1Gain = float(1e4)
    P2Gain = float(1e4)

elif Instruments == 'Internal': # Internal Instrument Settings

    # Settables for this mode go here.
    DrainGain = 'Low' # 'Low' is 10^3 V/A and 'High' is 10^4 V/A
    GateGain = 'Low' # 'Low is 10^3 V/A and 'High' is 10^4 V/A
    DrainCirc = 'TIA' # 'TIA' uses the transimpedance amplifier circuit; 'CSA' uses the current sense amplifier circuit
    GateCirc = 'TIA' # 'TIA' uses the transimpedance amplifier circuit; 'CSA' uses the current sense amplifier circuit

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

    # Information about which MCC ports you are using
    Source = 'MCC152/ao0'
    Hold = 'MCC152/ao1'
    Drain = 'MCC128/ai0'
    Gate = 'MCC128/ai1'

    # Settings for MCC128 Burst Mode operation
    SR = float(1e5) # Sample Rate in samples/second. 1e5 is maximum for single channel, 5e4 is maximum for dual channel (pairburst).
    SpC = int(1e5) # Samples per Channel per measurement -- strongly influences speed (100000 at 100kS/s takes about 1 second)

    # Settings for Internal Preamplifiers
    if DrainGain == 'Low':
        P1Gain = float(1e3)
    elif DrainGain == 'High':
        P1Gain = float(1e4)
    if GateGain == 'Low':
        P2Gain = float(1e3)
    elif GateGain == 'High':
        P2Gain = float(1e4)