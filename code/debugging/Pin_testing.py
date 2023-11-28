"""
Brought to v4.0.0 on Fri Sep 1 2023 by APM

@author: Jan Gluschke
"""

from pi_control import PiMUX

Pi_IP_address='129.94.163.203'

my_Pi = PiMUX(IP=Pi_IP_address)

# Enter device number here, 0=off
my_Pi.setMuxToOutput(26)