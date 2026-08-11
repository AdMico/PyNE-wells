"""
Brought to PyNE-wells v2.0.0 on Fri Aug 15 2025 by APM

@developers: Adam Micolich & Jan Gluschke

This informs various parts of the software about aspects of your bench setup. Edit as needed for your setup.
"""

## IMPORTANT -- YOU NEED TO SET TeensyPort CORRECTLY BEFORE YOU FIRST USE THE SOFTWARE to avoid having the relay switching fail -- see main README.md file
## IMPORTANT -- I've designed the software for two different instrument configurations: External and Internal
## 'External' runs with the Gen 5 instrument pack (K2401 in source, hold and gate, preamp to NIDAQ on drain)
## 'Internal' runs with the Gen 6 instrument pack (everything via the MCC128/152 DAQHAT system)
Instruments = 'Internal'

# Information about which Raspberry Pi USB port you are using for the Teensy Serial Connection for switching relays
TeensyPort = '/dev/ttyACM0' #Insert the Raspberry Pi port where your Teensy 4.1 is connected here

# Scan Direction for the array: 'Horizontal' scans along bitlines, which are connected to drain; 'Vertical' scans along wordlines, which are connected to drain
ScanDir = 'Horizontal'

# Settings for Measurement Biases -- VHold must be same sign as VSource (or zero) -- APM 28JUL26
VSource = float(0.1) # Cannot exceed +/- 5V if using internal DAC
VGate = float(0.0) # Must be zero if set to internal
VHold = float(0.0) # Cannot exceed +/- 5V if using internal DAC

# AssayRun Settings
ItersAR = int(5) # Number of iterations of device sampling to run before program ends
WaitAR = float(30) # Wait time in seconds between end of one iteration and start of the next -- APM to update to be pace independent
zeroThres = float(0.1) # If conductance is lower, the GUI will display zero for GUI management reasons (but correct conductance will go to data file) -- Added 30Oct25 APM
basePath = '../data'
GuiUpdateMode = 'grab' # Two options 'point' to update each device pair in a grab, or 'grab' to only update at the end of the whole grab (faster) -- Added 11Sep25 APM
PlotTwoMode = 'First' # Two options 'First' makes second Seaborn panel in Gen 5 difference to start, 'Last'makes difference to last grab.

# External Instrument Settings
SR_Ext = float(4e5)  # Sample Rate in samples/second. 4e5 is maximum for single channel, 2e5 is maximum for pairburst.
SpC_Ext = int(1e3)  # Samples per Channel per measurement -- strongly influences speed
GateModeExt = 'USB6216' # Two options 'USB6216' for default setup (Ag/AgCl electrode on AO1 of USB6216) and 'K2401' for using the Keithley 2401 instead -- 09Aug26 APM

# Internal Instrument Settings
SR_Int = float(1e5)  # Sample Rate in samples/second. 1e5 is maximum for single channel, 5e4 is maximum for pairburst.
SpC_Int = int(1e2)  # Samples per Channel per measurement -- strongly influences speed
DrainGain = 'High' # 'Low' is 10^3 V/A and 'High' is 10^4 V/A
GateGain = 'High' # 'Low is 10^3 V/A and 'High' is 10^4 V/A
DrainCirc = 'CSA' # 'TIA' uses the transimpedance amplifier circuit; 'CSA' uses the current sense amplifier circuit
GateCirc = 'CSA' # 'TIA' uses the transimpedance amplifier circuit; 'CSA' uses the current sense amplifier circuit