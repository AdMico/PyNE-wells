"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima
"""

import pandas as pd
import measurement
import easygui
from datetime import datetime
from pathlib import Path
import simulation_utils
import analysis
import utils
from Imports import *

def simulate_measure(device_list=[i for i in range(1, 10)],
                     fileName='simulation',
                     repeats=10,
                     event_repeat=5,
                     Pi_IP_address='129.94.163.203',
                     currentVoltagePreAmp_gain=1E3,
                     start_end_step=[0, -0.5, 0.1],
                     comment='no comment',
                     testSample='no',
                     plot_speed=1
                     ):

    G_data = simulation_utils.generate_data(device_list=device_list,
                                            repeats=repeats,
                                            event_repeat=event_repeat)

    stop_text = """If you want to shut down the program early, 
    go to G:\\Shared drives\\Nanoelectronics Team Drive\\Data\\2023\\Adam\\Stop button 
    open the \'stop\' file and replace this text with \'stop\'. Then save and close the file. 
    The program will shut down when it finishes the current repeat."""

    with open('G:/Shared drives/Nanoelectronics Team Drive/Data/2023/Adam/Stop button/stop.txt', 'w') as f:
        f.write(stop_text)

    start_sd = start_end_step[0]  # USER INPUT start value for IV sweep
    end_sd = start_end_step[1]  # USER INPUT end value for IV sweep
    step_sd = start_end_step[2]  # USER INPUT step size for IV sweep
    V_SD = utils.targetArray([start_sd, end_sd, start_sd],stepsize=step_sd)  # creates array of V_sd value for voltage sweep0000
    print(V_SD)

    delay = 0  # USER INPUT delay between sets of IV measurements - measure all devices -> delay -> measure all devices
    basePath = easygui.diropenbox().replace('\\', '/')  # opens window to select folder for data to be saved

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

    myTime = TimeMeas(0)  # gets time

    MasterDF = pd.DataFrame(
        columns=['ID', 'repeat', 'time', 'datetime', 'device', 'V_SD', 'I_SD', 'G', 'std_err'])  # Sets up results table
    t0 = time.time()  # gets time

    centimetre = 1 / 2.54
    fig, ax1 = plt.subplots(figsize=(30 * centimetre, 20 * centimetre))
    plt.subplots_adjust(left=None, bottom=None, right=0.8, top=None, wspace=None, hspace=None)
    ID = 0

    for j in range(repeats):
        for i, device in enumerate(device_list):
            time_1 = time.time() - t0  # Gets time relative to start time of the measurement
            ID += 1

            G_target = G_data[i,j]

            I_SD = simulation_utils.generate_IV(G_target, V_SD)
            df = pd.DataFrame({'V_SD': V_SD, 'I_SD': I_SD})

            Params = {'ID': [ID], 'repeat': j, 'time': [time_1], 'datetime': [datetime.now()],
                      'device': [device], 'V_SD': [list(df['V_SD'])],
                      'I_SD': [list(df['I_SD'])]}  # inserts data for results table
            print('Measurement ID: ' + str(Params['ID']) + ' + repeat: ' + str(j))  # prints status to console
            MasterDF = measurement.merge_df(Params, measurement.fit_for_Master(df, 'V_SD', 'I_SD'),
                                 MasterDF)  # Performs linear fit of IV sweep to get G and adds G to result table
            # live plotting. Adding legend on first repeat zero
            if i%plot_speed == 0:
                if len(MasterDF.device.unique()) < len(device_list):
                    analysis.plot_all_live(MasterDF, ax1=ax1, label=False)
                else:
                    analysis.plot_all_live(MasterDF, ax1=ax1, label=True)

                    if add_legend == True:
                        analysis.plot_all_live_add_legend(ax1)
                        add_legend = False

            plt.pause(0.01)  # needed for live plotting to work
        time.sleep(delay)  # delay set by user input

        with open('G:/Shared drives/Nanoelectronics Team Drive/Data/2023/Adam/Stop button/stop.txt', 'r') as f:
            r = f.read()
        if r == 'stop':
            print('stop')
            with open(basePath + '/comments.txt', 'a') as c:
                c.write('\n\n---------measurement was ended using stop.txt---------\n\n')
            break


    MasterDF.to_csv(basePath + '/' + fileName + '.csv')  # save results table after each repeat

    MasterDF.to_csv(
        basePath + '/' + fileName + str(Params['ID']) + '.csv')  # save final results table with ID of the last sweep.

    dfa = analysis.get_G_average(MasterDF)

    Path(basePath + "/devices").mkdir(parents=True, exist_ok=True)

    for device in device_list:  # saves result tables for individual devices
        df_ind = MasterDF[MasterDF['device'] == device]
        df_ind.to_csv(basePath + '/devices/' + fileName + '_device_' + str(device) + '.csv')

    analysis.save_for_manual_plot(MasterDF, basePath, save=True)

    with open(basePath + '/comments.txt', 'a') as f:
        f.write('average values: \n' + dfa.to_string() + '\n \n' + 'measurement finished at ' + str(datetime.now()))

    analysis.plot_all(MasterDF, title=fileName, save=True, basepath=basePath, cutoff=0.01)
    plt.show()

    return MasterDF, basePath

if __name__ == '__main__':
    comment = 'comment here'
    t0 = time.time()
    df, basePath = simulate_measure(repeats=10, event_repeat=5, currentVoltagePreAmp_gain=1E3,
                                    device_list=[i for i in range(1, 20)],
                                    comment=comment,
                                    plot_speed=1)
    t1 = time.time()
    print(t1-t0)
