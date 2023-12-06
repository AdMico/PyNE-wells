"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima
"""

from pi_control import PiMUX

Pi_IP_address='129.94.163.203'

my_Pi = PiMUX(IP=Pi_IP_address)

# Enter device number here, 0=off
my_Pi.setMuxToOutput(26)