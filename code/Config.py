"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

This informs various parts of the software about aspects of your bench setup
"""

# Information about which Raspberry Pi you are using (MeasureOne, MeasureTwo, etc)
# Details for the various Pis are in Pi_control.py
PiBox = 'MeasureThree'

# Information about which Truth Table to use (Devices, Rows, etc)
# Details are in Pi-control.py but Test is for hardware test (devices), Run is for measurements with two pre-amps (rows) on Gen 3a/4 MuxBoards
MuxMode = 'Run'

# Information about which NIDAQ ports you are using
Source = 'Dev1/ao0'
Gate = 'Dev1/ao1'
DrainLeft = 'Dev1/ai0'
DrainRight = 'Dev1/ai1'

# Settings for NIDAQ PairBurst Mode operation
SR = float(2e5) # Sample Rate in samples/second. 2e5 appears to be maximum for pairburst (400kS/s per channel single channel)
SpC = int(1e5) # Samples per Channel per measurement -- strongly influences speed (200000 at 200kS/s takes about 1 second)

# Settings for Femto Preamplifiers
P1Gain = float(1e4)
P2Gain = float(1e4)

# Settings for Measurement Biases
VSource = float(0.5)
VGate = float(0.0)

# AssayRun settings
ItersAR = int(3) # Number of iterations of device sampling to run before program ends
WaitAR = float(60) # Wait time in seconds between end of one iteration and start of the next -- APM to update to be pace independent
zeroThres = float(1e-2) # If current is smaller, we consider current to be zero and resistance to be zero (i.e., open circuit) to help data handling
basePath = '../data' # This should not need changing, the software will autoallocate data to sensible folders