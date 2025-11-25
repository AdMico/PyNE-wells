"""
Brought to PyNE-wells v1.2.0 on Thur Aug 07 2025 by APM

@developers: Adam Micolich & Jan Gluschke

This informs various parts of the software about aspects of your bench setup. Edit as needed for your setup.
"""

## IMPORTANT -- YOU NEED TO SET PiBox CORRECTLY BEFORE YOU FIRST USE THE SOFTWARE to avoid controlling someone else's hardware by mistake -- see main README.md file
## IMPORTANT -- If you are using a K2401 for the gate, you need to change the GateMode parameter under AssayRun settings below.

# Information about which Raspberry Pi you are using (MeasureOne, MeasureTwo, etc)
# Details for the various Pis are in Pi_control.py
PiBox = 'MeasureThree'

# Mode settings for the various generations of multiplexer box
# Details are in PiControlGen4.py but Test is for hardware test (devices), Run is for measurements with two pre-amps (rows) on Gen 3a/4 MuxBoards
MuxMode_Gen4 = 'Run'
# Details are in PiControlGen5.py but 'Pi-power' is for powering the MUXes off the RPi, 'Battery' is for powering the MUXes off the batteries on Gen 5 MuxBoards
MuxMode_Gen5 = 'Pi-power'
# Details are in PiControlGen5.py but 'Horizontal' scan along bitlines, which are connected to preamp; 'Vertical' will scan along wordlines, which are connected to preamp on Gen 5 MuxBoards
ScanDir_Gen5 = 'Horizontal'

# Information about which NIDAQ ports you are using for your NI USB6216BNC instance -- For AssayRunGen4.py
Source_Gen4 = 'Dev1/ao0'
Gate_Gen4 = 'Dev1/ao1'
DrainLeft_Gen4 = 'Dev1/ai0'
DrainRight_Gen4 = 'Dev1/ai1'

# Information about which NIDAQ ports you are using for your NI USB6216BNC instance -- For AssayRunGen5.py
Source_Gen5 = 'Dev1/ao0'
Hold_Gen5 = 'Dev1/ao1'
Drain_Gen5 = 'Dev1/ai0'

# Settings for NIDAQ PairBurst Mode operation
SR = float(4e5) # Sample Rate in samples/second. 2e5 appears to be maximum for pairburst (400kS/s per channel single channel)
SpC = int(1e3) # Samples per Channel per measurement -- strongly influences speed (200000 at 200kS/s takes about 1 second)

# Settings for Femto Preamplifiers -- Only P1Gain matters for Gen 5/6, both matter for Gen4.
P1Gain = float(1e4)
P2Gain = float(1e4)

# Settings for Measurement Biases
VSource = float(1.0)
VGate = float(0.0)
VHold = float(0.0) #Sets the Hold voltage line for Gen5/6 only (not used in Gen4)

# AssayRun settings
ItersAR = int(5) # Number of iterations of device sampling to run before program ends
WaitAR = float(120) # Wait time in seconds between end of one iteration and start of the next -- APM to update to be pace independent
zeroThres = float(0.1) # If conductance is lower, the GUI will display zero for GUI management reasons (but correct conductance will go to data file) -- 30Oct25 APM
basePath = '../data'
GuiUpdateMode = 'grab' # Two options 'point' to update each device pair in a grab, or 'grab' to only update at the end of the whole grab (faster) -- New 11Sep25 APM
GateMode = 'USB6216' # Two options 'USB6216' for default setup (Ag/AgCl electrode on AO1 of USB6216) and 'K2401' for using the Keithley 2401 instead -- New 30Oct25 APM
PlotTwoMode = 'First' # Two options 'First' makes second Seaborn panel in Gen 5 difference to start, 'Last'makes difference to last grab.