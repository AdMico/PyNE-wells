import threading
import pandas as pd
import numpy as np
import time # Im still wrapping my head around time/datetime in Py, this can probably be improved
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from pandastable import Table, TableModel  #for whatever reason this only works on Windows - no mac/linux

#Maybe need to rewrite everthing in measure.py to use same GUI package (i.e., drop easyGUI)?

num_devices=52; loops=6
devices = np.arange(num_devices + 1)[1:] # list of ints 1 to 52
# The dataframe that gets constantly overwritten and displayed to user
temp_dataframe = pd.DataFrame(np.zeros((num_devices, 4)), columns=["Mean", "Min", "Max", "Time"])

# This loop function is to mimic measurement.py, replace junk_data generation with the actual measurements
def dummy_measurement_loop(): #Number of Devices and Number of Loops, both ints

    print("User Selecting Directory to save data...")
    directory = tk.filedialog.askdirectory()
    print("Saving data to ", directory)

    stop_text = """If you want to stop the program, simply replace this text with 'stop' and save it."""

    with open('stop.txt', 'w') as f:
        f.write(stop_text)

    for i in range(loops): # Dummy logic that mimics structure of measure.py

        for j in devices:

            junk_data = np.random.normal(loc=j, scale=0.2, size=30)

            row_vector = [ np.mean(junk_data),  np.min(junk_data), np.max(junk_data), datetime.now().strftime("%H:%M:%S") ]
            temp_dataframe.iloc[j-1] = row_vector

            time.sleep(0.2)

            print("measured device {} as part of the {} th loop".format(j, i+1))

        if __name__=="__main__": # will this allow measure to be calld externally?
            update_df()

        with open('stop.txt', 'r') as f:
            r = f.read()
        if r == 'stop':
            print('stopped safely after repeat', i+1)
            break

    print("Measurement Daemon Completed Successfully")

def stop(): # This function runs when stop button pressed, havn't figured this out yet!
    with open('stop.txt', 'w') as f:
        f.write('stop')

def update_df():
    table.updateModel(TableModel(temp_dataframe))
    table.redraw()

if  __name__ == "__main__":

    #  Making GUI
    root = tk.Tk()
    root.title("Measurement Live GUI")

    #Frame
    frame = tk.Frame(root)
    frame.pack(fill='both', expand=True)

    # Putting PandasTable into the frame
    table = Table(frame, showtoolbar=False, showstatusbar=False)
    table.show()
    table.autoResizeColumns()
    update_df()  # So it doesn't look wierd

    # Threading: While running the GUI in the main thread, run the measurement loop in the "background"
    update_thread = threading.Thread(target=dummy_measurement_loop)
    update_thread.daemon = True

    tk.Button(root, text='STOP Button',command=lambda *args: stop()).pack()

    # Start running the loops and stuff
    update_thread.start()
    root.mainloop()

