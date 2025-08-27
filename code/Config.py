"""
Brought to PyNE-wells v2.0.0 on Fri Aug 15 2025 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

This informs various parts of the software about aspects of your bench setup. Edit as needed for your setup.
"""

## IMPORTANT -- YOU NEED TO SET PiBox CORRECTLY BEFORE YOU FIRST USE THE SOFTWARE to avoid controlling someone else's hardware by mistake -- see main README.md file
# Information about which Raspberry Pi you are using (MeasureOne, MeasureTwo, etc)
# Details for the various Pis are in Pi_control.py
PiBox = 'MeasureFour'

# Information about which Truth Table to use (Devices, Rows, etc)
# Details are in Pi-control.py but Test is for hardware test (devices), Run is for measurements with two pre-amps (rows) on Gen 3a/4 MuxBoards
MuxMode = 'Run'

#
# Settings for Gen 4/5 setup
#

# Information about which NIDAQ ports you are using for your NI USB6216BNC instance.
Source_Gen5 = 'Dev1/ao0'
Gate_Gen5 = 'Dev1/ao1'
DrainLeft_Gen5 = 'Dev1/ai0'
DrainRight_Gen5 = 'Dev1/ai1'

# Settings for NIDAQ PairBurst Mode operation
SR_Gen5 = float(2e5) # Sample Rate in samples/second. 2e5 appears to be maximum for pairburst (400kS/s per channel single channel)
SpC_Gen5 = int(1e5) # Samples per Channel per measurement -- strongly influences speed (200000 at 200kS/s takes about 1 second)

#
# Settings for Generation 6 Setup
#

# Information about which MCC ports you are using
Source_Gen6 = 'MCC152/ao0'
Hold_Gen6 = 'MCC152/ao1'
Drain_Gen6 = 'MCC128/ai0'

# Settings for MCC128 Burst Mode operation
SR_Gen6 = float(1e5) # Sample Rate in samples/second. 1e5 is maximum for single channel, 5e4 is maximum for dual channel (pairburst).
SpC_Gen6 = int(1e5) # Samples per Channel per measurement -- strongly influences speed (100000 at 100kS/s takes about 1 second)

#
# Settings for measurements
#

# Settings for Femto Preamplifiers
P1Gain = float(1e4)
P2Gain = float(1e4)

# Settings for Measurement Biases
VSource = float(0.5)
VGate = float(0.0)

# AssayRun settings
ItersAR = int(1) # Number of iterations of device sampling to run before program ends
WaitAR = float(60) # Wait time in seconds between end of one iteration and start of the next -- APM to update to be pace independent
zeroThres = float(1e-2) # If current is smaller, we consider current to be zero and resistance to be zero (i.e., open circuit) to help data handling
basePath = '../data'