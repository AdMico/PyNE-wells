#!/usr/bin/env python
#
# MCC 128 example program
# Read and display analog input values
#
import sys
from daqhats import hat_list, HatIDs, mcc128

print("Started")

# get hat list of MCC daqhat boards
board_list = hat_list(filter_by_id = HatIDs.ANY)
if not board_list:
    print("No boards found")
    sys.exit()

# Read and display every channel
for entry in board_list:
    if entry.id == HatIDs.MCC_128:
        print("Board {}: MCC 128".format(entry.address))
        board = mcc128(entry.address)

        for channel in range(8):
#        for channel in range(board.info().NUM_AI_CHANNELS): # Fails on compile, not sure why
            value = board.a_in_read(channel)
            print("Ch {0}: {1:.3f}".format(channel, value))