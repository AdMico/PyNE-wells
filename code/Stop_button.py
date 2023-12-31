"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima
@author: Sam Shelton
"""

from easygui import *

switch = True

window_title = 'Stop Button'
text = 'Push the Button to stop an active Measure.py program'
button_text = ['STOP', 'QUIT Stop Button']
stop_text = 'stop'

while switch == True:

    output = buttonbox(text, window_title, button_text)

    if output == 'STOP':
        with open('stop.txt', 'w') as f:
            f.write(stop_text)
            switch = False #added APM 04SEP23 to auto-kill window

    if output == 'QUIT Stop Button':
        switch = False