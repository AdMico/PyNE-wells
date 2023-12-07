"""
Brought to v4.0.0 on Fri Sep 1 2023 by APM

@author: Jan Gluschke
"""
import threading
import pandas as pd
from matplotlib.pyplot import cm
from scipy import stats
import Analysis
from datetime import datetime
from pathlib import Path
from Pi_control import PiMUX
from tkinter import * #maybe refactor code to avoid importing as *
from tkinter import filedialog
from pandastable import Table, TableModel
from Imports import *
import collections.abc
collections.Iterable = collections.abc.Iterable # Quick and dirty fix for V4.0, implement properly later.
import Utils
import SweepFunction as SF
import GlobalMeasID as GMID

DevNum=52

GUI_dataframe = pd.DataFrame(np.zeros((DevNum, 6)), columns=['Time', 'V_SD', 'I_SD', 'G', 'std_err', 'Repeat'])

def fit_for_Master(df, xVar='V_SD', yVar='I_SD'):
    slope, intercept, r_value, p_value, std_err = stats.linregress(df[xVar], df[yVar])
    return {'G': [slope], 'std_err': [std_err]}

def stop():
    with open('stop.txt', 'w') as f:
        f.write('stop')

def update_df():
    table.updateModel(TableModel(GUI_dataframe))
    table.redraw()

def merge_df(Params, Fit, Master):
    Params.update(Fit)
    DF = pd.DataFrame(Params)
    Master = pd.concat([Master,DF],ignore_index=True)
    return Master

def micr_measure(deviceList=[i for i in range(1,DevNum+1)],
                 fileName='test',
                 repeats=3,
                 Pi_IP_address='129.94.163.203',
                 currentVoltagePreAmp_gain=1E3,
                 start_end_step=[0, 0.5, 0.1],
                 comment='no comment',
                 testSample='no',
                 plot_speed=1
                 ):
    stop_text = """If you want to stop the program, simply replace this text with 'stop' and save it."""

    with open('stop.txt', 'w') as f:
        f.write(stop_text)

    start_sd = start_end_step[0]
    end_sd = start_end_step[1]
    step_sd = start_end_step[2]
    V_SD = Utils.targetArray([start_sd, end_sd, start_sd],
                         stepsize=step_sd)  # creates array of V_sd value for voltage sweep

    delay = 0  # USER INPUT delay between sets of IV measurements - measure all devices -> delay -> measure all devices
    basePath = filedialog.askdirectory()  # opens window to select folder for data to be saved

    add_legend = True

    with open(basePath + '/comments.txt', 'w') as f:
        f.write('start: ' + str(datetime.now()) + '\n' +
                'Filename: ' + fileName + '\n' +
                'Pi IP: ' + Pi_IP_address + '\n' +
                'repeats = ' + str(repeats) + '\n' +
                'Pi_IP_address = ' + Pi_IP_address + '\n' +
                'Preamp gain = ' + str(currentVoltagePreAmp_gain) + '\n' +
                'IV start, stop, step = ' + str(start_end_step) + '\n' +
                'data at: ' + basePath + '\n \n' +
                'comment = ' + comment + '\n \n'
                )

    # 2.Define device/instruments
    my_Pi = PiMUX(IP=Pi_IP_address)  # sets up raspberry pi

    daqout_S = USB6216Out(0)  # sets up NIDAQ
    daqout_S.setOptions({
        "feedBack": "Int",
        "extPort": 0,  # Can be any number 0-7 if in 'Int'
        "scaleFactor": 1
    })
    daqin_D = USB6216In(0)  # sets up NIDAQ
    daqin_D.set('scaleFactor', currentVoltagePreAmp_gain)  # sets up NIDAQ to work with the current preamp

    my_Pi.setMuxToOutput(0)  # sets multiplexer to state with all outputs off

    myTime = TimeMeas(0)  # gets time
    Dct = {}  # sets up IV sweep including where to save the files
    Dct['basePath'] = basePath + '/IV'
    Dct['fileName'] = fileName
    Dct['setters'] = {daqout_S: 'V_SD'}
    Dct['readers'] = {myTime: 'time',
                      daqin_D: 'I_SD'}
    Dct['sweepArray'] = V_SD

    MasterDF = pd.DataFrame(
        columns=['ID', 'repeat', 'time', 'datetime', 'device', 'V_SD', 'I_SD', 'G', 'std_err'])  # Sets up results table
    t0 = time.time()  # gets time

    # Starting the measurement
    addlegend = True  # variable used to make sure the legend only gets added once to realtime plot
    linestyles = ['-', '--', '-.', ':']  # list used to altenate between line styles for different devices
    centimetre = 1 / 2.54
    color = iter(cm.tab20(np.linspace(0, 1, len(deviceList))))
    colors = [i for i in color]

    fig, ax1 = plt.subplots(figsize=(30 * centimetre, 20 * centimetre))
    plt.subplots_adjust(left=None, bottom=None, right=0.8, top=None, wspace=None, hspace=None)

    for j in range(repeats):
        for i, device in enumerate(deviceList):
            my_Pi.setMuxToOutput(device)  # sets multiplexer to the desired device
            time.sleep(0.5)  # short wait to settle. May not be necessary. Can investigate later
            time_1 = time.time() - t0  # Gets time relative to start time of the measurement
            df = SF.sweepAndSave(Dct)  # Perform IV sweep using the NIDAQ pyne module
            Params = {'ID': [GMID.readCurrentID()], 'repeat': j, 'time': [time_1], 'datetime': [datetime.now()],
                      'device': [device], 'V_SD': [list(df['V_SD'])],
                      'I_SD': [list(df['I_SD'])]}  # inserts data for results table
            print(str(Params['ID']) + ' + ' + str(j))  # prints status to console
            MasterDF = merge_df(Params, fit_for_Master(df, 'V_SD', 'I_SD'),
                                 MasterDF)  # Performs linear fit of IV sweep to get G and adds G to result table
            df1 = MasterDF[MasterDF['device'] == device]  # creates dataframe with just one device to plot as a distinct line in live plot

            # Data that you want on live GUI, must match length of column names exe in df definition
            if __name__ == '__main__':
                row_vector = [1, 2, 3, 4, 5, i] #'Time', 'V_SD', 'I_SD', 'G', 'std_err', 'Repeat'
                GUI_dataframe.iloc[i-1] = row_vector
                if (i-1)%26 == 0:
                    update_df()

            # live plotting. Adding legend on first repeat zero
            if i % plot_speed == 0:
                if len(MasterDF.device.unique()) < len(deviceList):
                    Analysis.plot_all_live(MasterDF, ax1=ax1, label=False)
                else:
                    Analysis.plot_all_live(MasterDF, ax1=ax1, label=True)

                    if add_legend:
                        Analysis.plot_all_live_add_legend(ax1)
                        add_legend = False

            plt.pause(0.01)  # needed for live plotting to work

        with open('stop.txt', 'r') as f:
            r = f.read()
        if r == 'stop':
            print('stopped on repeat', j)
            with open(basePath + '/comments.txt', 'a') as c:
                c.write('\n\n---------measurement was ended using stop.txt---------\n\n')
            break
        #addlegend = False
        time.sleep(delay)  # delay set by user input

    my_Pi.setMuxToOutput(0)  # sets multiplexer to 0
    print ('MUXes off')

    MasterDF.to_csv(basePath + '/' + fileName + '.csv')  # save results table after each repeat

    MasterDF.to_csv(
        basePath + '/' + fileName + str(Params['ID']) + '.csv')  # save final results table with ID of the last sweep.

    dfa = Analysis.get_G_average(MasterDF)

    Path(basePath + "/devices").mkdir(parents=True, exist_ok=True)

    for device in deviceList:  # saves result tables for individual devices
        df_ind = MasterDF[MasterDF['device'] == device]
        df_ind.to_csv(basePath + '/devices/' + fileName + '_device_' + str(device) + '.csv')

    Analysis.save_for_manual_plot(MasterDF, basePath, save=True)

    with open(basePath + '/comments.txt', 'a') as f:
        f.write('average values: \n' + dfa.to_string() + '\n \n' + 'measurement finished at ' + str(datetime.now()))

    Analysis.plot_all(MasterDF, title=fileName, save=True, basepath=basePath)

    #if __name__!="__main__":
    #    return MasterDF, basePath # only returns when not main

if __name__ == '__main__':
    comment = 'working out preamp issues'

    t0 = time.time()

    t1 = time.time()
    print(t1-t0)

    root = Tk()
    root.title("Measurement Live GUI")
    frame = Frame(root)
    frame.pack(fill='both', expand=True)
    table = Table(frame, showtoolbar=False, showstatusbar=False)
    table.show()
    table.autoResizeColumns()
    update_df()

    Button(root, text='STOP Button', command=lambda *args: stop()).pack()

    update_thread = threading.Thread(target=micr_measure(
                repeats=3,
                currentVoltagePreAmp_gain=1E3,
                deviceList=[i for i in range(1, DevNum+1)],
                comment=comment,
                plot_speed=10))

    update_thread.daemon = True
    update_thread.start()
    root.mainloop()