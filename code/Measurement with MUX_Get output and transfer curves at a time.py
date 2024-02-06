"""
Brought to PyNE-wells v1.0.0 on Tue Feb 6 2024 by SK

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

Contents: getting output and transfer curves at a time with MUX
Note:
---Config.py: MuxMode = 'test'
---Scatter log plot: This doesn't work at Python 3.11)
"""

import pandas as pd
import os
from Pi_control import PiMUX
import collections.abc
collections.Iterable = collections.abc.Iterable # Quick and dirty fix for V4.0, implement properly later.
from Imports2 import *
import glob
import shutil
import time
from scipy.interpolate import make_interp_spline

"""
Create folders
"""

print('Select directory to create two folders:1. Id_Ig vs Vsd, and 2. Id_Ig vs Vg')

[basePath,fileName] = fileDialog()
list = ['Id_Ig vs Vsd', 'Id_Ig vs Vg']

for items in list:
    os.mkdir(basePath + items)

print('Two folders have been created.')

# Define device/instruments

currentVoltagePreAmp_gain = 1E4
my_Pi = PiMUX()  # sets up raspberry pi


daqout_S = USB6216Out(0)  # sets up NIDAQ
daqout_S.setOptions({
        "feedBack": "Int",
        "extPort": 0,  # Can be any number 0-7 if in 'Int'
        "scaleFactor": 1
    })
daqin_D = USB6216In(0)  # sets up NIDAQ
daqin_D.set('scaleFactor', currentVoltagePreAmp_gain)  # sets up NIDAQ to work with the current preamp

my_Pi.setMuxToOutput(0)  # sets multiplexer to state with all outputs off

# ---Keithley Vg -----------
KVg = Keithley2401(27)
KVg.setOptions({
        "beepEnable": False,
        "sourceMode": "voltage",
        "sourceRange": 10,
        # "senseRange": 1.05e-6,
        # "compliance": 1.0E-2,
        "scaleFactor": 1
    })


"""
Get transfer and output curves
"""

print('Get transfer and output curves')
start_time = time.time()

"""
Number of devices to be measured
"""
c1 = 1

C = 27 # Beginning of device#

for j in range(c1):
    print('Start device {}/{}'.format((1 + j), c1))

    my_Pi.setMuxToOutput(j+1+(C-1))

    # sets multiplexer to the desired device
    print('Measuring device#{}'.format(j + 1 + (C - 1)))
    # time.sleep(0.5)  # short wait to settle. May not be necessary. Can investigate later

    """
    Vsd sweep
    """
    # Vsd sweep range

    print('Start Id_Ig vs Vsd measurement')

    os.mkdir(basePath + "device#{}".format(j + 1 + (C - 1)))

    start = 0;
    end = -0.525;
    step = -0.025;
    Vsd = np.arange(start, end, step)

    #
    # Vg sweep range
    start = 0;
    end = 1.1;
    step = 0.2;
    Vg = np.arange(start, end, step)

    STEP = 0.2
    NVg = 6  # end/step

    for n in Vg:
        KVg.goTo(n, delay=0.001)
        # --------------Headers and setters for Vg curves
        inputHeaders = ["Vsd [V]"]
        inputSetters = [daqout_S]
        outputHeaders = ["Id@Vg={}V [A]".format(n), "Ig@Vg={}V [A]".format(n)]
        # outputHeaders = ["Id@Vg={}V [A]".format(n)]
        outputReaders = [daqin_D, KVg]
        # outputReaders = [daqin_D]

        inputPoints = product(Vsd)

        sweepAndSave(
            basePath + "device#{}".format(j + 1+(C-1)),
            inputHeaders, inputPoints, inputSetters,
            outputHeaders, outputReaders, saveEnable=True,
        )

    target_dir = basePath + "device#{}".format(j + 1+(C-1))

    file_names = os.listdir(basePath)

    for file_name in file_names:
        if (file_name.startswith("device#{}".format(j + 1+(C-1)))):
            shutil.move(os.path.join(basePath, file_name), target_dir)

    # list all csv files only
    os.chdir(basePath + "device#{}".format(j + 1+(C-1)))
    file_list = os.listdir(basePath + "device#{}".format(j + 1+(C-1)))

    # print(file_list)
    tsv_files = glob.glob('*.{}'.format('tsv'))
    filteredResults = [i for i in tsv_files if "LOG" not in i]
    # print(filteredResults)
    Output_Id_Vsd = pd.concat([pd.read_csv(f, sep='\t') for f in filteredResults])
    Output_Id_Vsd.to_csv('Output_Id_Vsd_device#{}.csv'.format(j + 1+(C-1)), sep='\t')

    df = pd.read_csv('Output_Id_Vsd_device#{}.csv'.format(j + 1+(C-1)), sep='\t')

    dfs = {}
    for m in range(NVg):
        R = len(Vsd)
        dff = pd.read_csv('Output_Id_Vsd_device#{}.csv'.format(j + 1+(C-1)), sep='\t', skiprows=1 + (R + 1) * m, nrows=R)
        headers = ["Vsd [V]", "Id [A]", "Ig [A]"]
        # headers = ["Vsd [V]", "Id [A]"]
        dff.columns = headers
        dff.to_csv('dff{}.csv'.format(1 + m), header=True, index=False)

        dfs['Vg={}[V]'.format(m * STEP)] = pd.read_csv('dff{}.csv'.format(1 + m))
        # print(dfs)

    DF_list = []

    for p in range(0, len(dfs)):
        DF = dfs['Vg={}[V]'.format(p * STEP)]
        DF_list.append(DF)

        if p == 0:

            DF_list[p]['Id [A]'] = DF_list[p]['Id [A]']*(1E6)


            ax = DF_list[p].plot.scatter(x='Vsd [V]', y = 'Id [A]', c="k")
            # ax = DF_list[p].plot(x='Vsd [V]', y='Isd [A]',label='Id@Vg={}[V]'.format(p * 0.1), kind='line')
            ax.invert_xaxis()
            ax.invert_yaxis()
        else:
            DF_list[p]['Id [A]'] = DF_list[p]['Id [A]']*(1E6)  ## A->uA
            DF_list[p].plot.scatter(x='Vsd [V]', y = 'Id [A]', c="k", ax=ax)
            # DF_list[p].plot(x='Vsd [V]', y='Isd [A]', label='Id@Vg={}[V]'.format(p * 0.1), kind='line', ax=ax)


        x = DF_list[p]['Vsd [V]']
        x = np.array(x)
        x = x.tolist()
        x = sorted(x)

        y = DF_list[p]['Id [A]'] ## Unit is A->uA
        y = np.array(y)
        y = y.tolist()
        y = np.flipud(y)

        X_Y_Spline = make_interp_spline(x, y)

        X_ = np.linspace(min(x), max(x), 300)
        Y_ = X_Y_Spline(X_)

        rounded_number = round(p * STEP, 3)

        plt.plot(X_, Y_, label="Id@Vg={}[V]".format(rounded_number))
        plt.xlabel("Vsd [V]")
        plt.ylabel("Id [uA]")

        plt.legend(loc='best', fancybox=True, shadow=True)
        # plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper right')

    plt.title('Id vs Vsd_device#{}'.format(j + 1+(C-1)))

    plt.legend(bbox_to_anchor=(1.04, 1),borderaxespad=0)
    fig = plt.gcf()
    fig.set_size_inches(8, 5)
    fig.tight_layout()

    plt.show()
    plt.draw()
    fig.savefig('Id_vs_Vsd_device#{}.png'.format(j + 1+(C-1)), dpi=100)


    os.chdir(basePath)
    source_dir = "device#{}".format(j + 1+(C-1))
    target_dir = "Id_Ig vs Vsd"
    shutil.move(source_dir, target_dir)

    os.chdir(r"C:\Users\z5345591\PycharmProjects\Nanowells_4p0b\Code")

    """"
    Vg sweep
    """
    print('Start Id_Ig vs Vg measurement')
    os.mkdir(basePath + "device#{}".format(j + 1 + (C - 1)))

    # Vsd sweep range

    # start = -0.5;end = -0.6;step = -0.5
    # STEP=-0.5

    start = -0.125; end = -0.625; step = -0.125
    STEP = -0.125

    # start = 0;end = -0.625;step = -0.125
    # STEP=-0.125

    Vsd = np.arange(start, end, step)

    # Vg sweep range
    start = 1.0;
    end = -0.1;
    step = -0.1
    Vg = np.arange(start, end, step)

    NVsd = 4  # end/step

    for n in Vsd:
        daqout_S.goTo(n, delay=0.001)
        # --------------Headers and setters for Vg curves
        inputHeaders = ["Vg"]
        inputSetters = [KVg]
        # outputHeaders = ["Id@Vsd={}V".format(n)]
        outputHeaders = ["Id@Vsd={}V".format(n), "Ig@Vsd={}V".format(n)]
        outputReaders = [daqin_D, KVg]

        inputPoints = product(Vg)

        sweepAndSave(
            basePath + "device#{}".format(j + 1 + (C - 1)),
            inputHeaders, inputPoints, inputSetters,
            outputHeaders, outputReaders, saveEnable=True,
        )

    target_dir = basePath + "device#{}".format(j + 1 + (C - 1))

    file_names = os.listdir(basePath)

    for file_name in file_names:
        if (file_name.startswith("device#{}".format(j + 1 + (C - 1)))):
            shutil.move(os.path.join(basePath, file_name), target_dir)

    # list all csv files only
    os.chdir(basePath + "device#{}".format(j + 1 + (C - 1)))
    file_list = os.listdir(basePath + "device#{}".format(j + 1 + (C - 1)))

    # print(file_list)
    tsv_files = glob.glob('*.{}'.format('tsv'))
    filteredResults = [i for i in tsv_files if "LOG" not in i]
    # print(filteredResults)
    Output_Id_Vsd = pd.concat([pd.read_csv(f, sep='\t') for f in filteredResults])
    Output_Id_Vsd.to_csv('Output_Id_Vg_device#{}.csv'.format(j + 1 + (C - 1)), sep='\t')

    df = pd.read_csv('Output_Id_Vg_device#{}.csv'.format(j + 1 + (C - 1)), sep='\t')

    dfs = {}
    for m in range(NVsd):
        R = len(Vg)
        dff = pd.read_csv('Output_Id_Vg_device#{}.csv'.format(j + 1 + (C - 1)), sep='\t', skiprows=1 + (R + 1) * m,
                          nrows=R)
        headers = ["Vg [V]", "Id [A]", "Ig [A]"]
        # headers = ["Vg [V]", "Id [A]"]
        dff.columns = headers

        dff.to_csv('dff{}.csv'.format(1 + m), header=True, index=False)

        # dfs['Vsd={}[V]'.format(m * STEP)] = pd.read_csv('dff{}.csv'.format(1 + m))
        dfs['Vsd={}[V]'.format((m + 1) * STEP)] = pd.read_csv('dff{}.csv'.format(1 + m))
        # print(dfs)

    DF_list = []
    Gm_X_list = []
    x_list = []
    gm_list = []
    Gm_X = {}

    for p in range(0, len(dfs)):
        # DF = dfs['Vsd={}[V]'.format(p * STEP)]
        DF = dfs['Vsd={}[V]'.format((p + 1) * STEP)]
        DF_list.append(DF)

        for q in range(0, len(Vg) - 1):
            X = DF_list[p]['Vg [V]'][q] - (DF_list[p]['Vg [V]'][q] - DF_list[p]['Vg [V]'][q + 1]) / 2
            # DF2 = dfs['Vsd={}[V]'.format((p + 1) * STEP)]
            x_list.append(X)

            dId = (DF_list[p]['Id [A]'][q] - DF_list[p]['Id [A]'][q + 1])
            dVg = (DF_list[p]['Vg [V]'][q] - DF_list[p]['Vg [V]'][q + 1])
            gm = abs(dId / dVg)*(1.0E+6)
            gm_list.append(gm)

        # gm_X_list = pd.DataFrame(np.column_stack([X_list, gm_list]), columns=['Vg', 'gm'])
        gm_X_list = [(x_list[i], gm_list[i]) for i in range(len(x_list))]
        gm_X = pd.DataFrame(gm_X_list)
        headers = ["Vg", "gm"]
        # headers = ["Vg [V]", "Id [A]"]
        gm_X.columns = headers

        gm_X.to_csv('gm_X_Vsd={}[V].csv'.format((p + 1) * STEP), header=True, index=False)

        Gm_X['Vsd={}[V]'.format((p + 1) * STEP)] = pd.read_csv('gm_X_Vsd={}[V].csv'.format((p + 1) * STEP))
        x_list *= 0
        gm_list *= 0

    for g in range(0, len(Gm_X)):
        # DF = dfs['Vsd={}[V]'.format(p * STEP)]
        Gm_XX = Gm_X['Vsd={}[V]'.format((g + 1) * STEP)]
        Gm_X_list.append(Gm_XX)

    ###(Plot Id&gm_vs_Vg)

    ### (plot Id vs Vg)

    for p in range(0, len(dfs)):
        if p == 0:
            DF_list[p]['Id [A]'] = DF_list[p]['Id [A]'] * (1E6)  ## A->uA
            ax = DF_list[p].plot.scatter(x='Vg [V]', y = 'Id [A]', c="k")
            ax.invert_yaxis()
        else:
            DF_list[p]['Id [A]'] = DF_list[p]['Id [A]'] * (1E6)  ## A->uA
            DF_list[p].plot.scatter(x='Vg [V]', y = 'Id [A]', c="k", ax=ax)

        x1 = DF_list[p]['Vg [V]']
        x1 = np.array(x1)
        x1 = x1.tolist()
        x1 = sorted(x1)

        y1 = DF_list[p]['Id [A]']
        # y1 = abs(y1)
        y1 = np.array(y1)
        y1 = y1.tolist()
        y1 = np.flipud(y1)

        X1_Y1_Spline = make_interp_spline(x1, y1)

        X1_ = np.linspace(min(x1), max(x1), 50)
        Y1_ = X1_Y1_Spline(X1_)

        #     # rounded_number = round(p * STEP, 3)
        rounded_number = round((p + 1) * STEP, 3)
        plt.plot(X1_, Y1_, label="Id@Vsd={}[V]".format(rounded_number))

    plt.xlabel("Vg [V]")
    plt.ylabel("Id [uA]")
    plt.legend(loc='best', fancybox=True, shadow=True)
    plt.title('Id vs Vg_device#{}'.format(j + 1 + (C - 1)))
    plt.legend(bbox_to_anchor=(1.04, 1), borderaxespad=0)
    fig = plt.gcf()
    fig.set_size_inches(8, 5)
    fig.tight_layout()
    plt.show()
    plt.draw()
    fig.savefig('Id_vs_Vg_device#{}.png'.format(j + 1 + (C - 1)), dpi=100)

    ### (plot gm vs Vg)
    for p in range(0, len(dfs)):
        if p == 0:
            ax = Gm_X_list[p].plot.scatter(x='Vg', y = 'gm', c="k")
        else:
            Gm_X_list[p].plot.scatter(x='Vg', y = 'gm', c="k", ax=ax)

        x2 = Gm_X_list[p]['Vg']
        x2 = np.array(x2)
        x2 = x2.tolist()
        x2 = sorted(x2)

        y2 = Gm_X_list[p]["gm"]
        # y2 = abs(y2) * (1.0E+6)
        y2 = y2.tolist()
        y2 = np.flipud(y2)

        X2_Y2_Spline = make_interp_spline(x2, y2)

        X2_ = np.linspace(min(x2), max(x2), 50)
        X2_ = np.array(X2_, dtype=float)

        Y2_ = X2_Y2_Spline(X2_)
        Y2_ = np.array(Y2_, dtype=float)

        #     # rounded_number = round(p * STEP, 3)
        rounded_number = round((p + 1) * STEP, 3)

        plt.plot(X2_, Y2_, label="|gm|@Vsd={}[V]".format(rounded_number))

    plt.xlabel("Vg [V]")
    plt.ylabel("|gm| [uS]")
    plt.legend(loc='best', fancybox=True, shadow=True)
    plt.title('gm vs Vg_device#{}'.format(j + 1 + (C - 1)))
    plt.legend(bbox_to_anchor=(1.04, 1), borderaxespad=0)
    fig = plt.gcf()
    fig.set_size_inches(8, 5)
    fig.tight_layout()
    plt.show()
    plt.draw()
    fig.savefig('gm_vs_Vg_device#{}.png'.format(j + 1 + (C - 1)), dpi=100)

    ### (plot Id&gm(at a time) vs Vg)

    fig, ax1 = plt.subplots()
    ax1.invert_yaxis()
    ax2 = ax1.twinx()
    ls = {}
    labs = {}
    LS = []
    LABS = []

    for p in range(0, len(dfs)):

        x1 = DF_list[p]['Vg [V]']
        x1 = np.array(x1)
        x1 = x1.tolist()
        x1 = sorted(x1)

        y1 = DF_list[p]['Id [A]']
        # y1 = abs(y1)
        y1 = np.array(y1)
        y1 = y1.tolist()
        y1 = np.flipud(y1)

        X1_Y1_Spline = make_interp_spline(x1, y1)

        X1_ = np.linspace(min(x1), max(x1), 50)
        Y1_ = X1_Y1_Spline(X1_)

        ### gm vs Vg

        x2 = Gm_X_list[p]['Vg']
        x2 = np.array(x2)
        x2 = x2.tolist()
        x2 = sorted(x2)

        y2 = Gm_X_list[p]["gm"]
        # y2 = abs(y2) * (1.0E+6)
        y2 = y2.tolist()
        y2 = np.flipud(y2)

        X2_Y2_Spline = make_interp_spline(x2, y2)

        X2_ = np.linspace(min(x2), max(x2), 50)
        X2_ = np.array(X2_, dtype=float)

        Y2_ = X2_Y2_Spline(X2_)
        Y2_ = np.array(Y2_, dtype=float)

        #     # rounded_number = round(p * STEP, 3)
        rounded_number = round((p + 1) * STEP, 3)

        ax1.scatter(x1, y1, c="r")
        l1 = ax1.plot(X1_, Y1_, label='Id@Vsd={}[V]'.format(rounded_number))
        #
        ax2.scatter(x2, y2, c="b")
        l2 = ax2.plot(X2_, Y2_, label='|gm|@Vsd={}[V]'.format(rounded_number))

        ax1.set_xlabel('Vg [V]')
        ax1.set_ylabel('Id [uA]')
        ax2.set_ylabel('|gm| [uS]')

        ls[p] = l1 + l2

        labs[p] = [l.get_label() for l in ls[p]]

        if p == len(dfs)-1:
            for i in range(0, len(dfs)):
                LS = LS + ls[i]
                LABS = LABS + labs[i]
        ax1.legend(LS, LABS, loc='best', fancybox=True, shadow=True, bbox_to_anchor=(1.04, 1))

    plt.title('Id&gm vs Vg_device#{}'.format(j + 1 + (C - 1)))
    fig = plt.gcf()
    fig.set_size_inches(11, 7)
    fig.tight_layout()

    plt.show()
    plt.draw()
    fig.savefig('Id&gm_vs_Vg_device#{}.png'.format(j + 1 + (C - 1)), dpi=100)

    ####(Log plot_|Id| and |Ig| vs Vg)
    for p in range(0, len(dfs)):
        # DF = dfs['Vsd={}[V]'.format(p * STEP)]
        DF = dfs['Vsd={}[V]'.format((p + 1) * STEP)]
        DF_list.append(DF)

        if p == 0:
            DF_list[p]['Id [A]'] = abs(DF_list[p]['Id [A]'])*(1E6)
            ax = DF_list[p].plot.scatter(x='Vg [V]', y='Id [A]', c="r")

            DF_list[p]['Ig [A]'] = abs(DF_list[p]['Ig [A]'])* (1E6)  ## A->uA
            DF_list[p].plot.scatter(x='Vg [V]', y='Ig [A]', c="b", ax=ax)
            # ax = DF_list[p].plot(x='Vg [V]', y='Isd [A]',label='Id@Vsd={}[V]'.format(p * 0.1), kind='line')
            # ax.invert_xaxis()
            # ax.invert_yaxis()
        else:
            DF_list[p]['Id [A]'] = abs(DF_list[p]['Id [A]'])* (1E6)
            DF_list[p].plot.scatter(x='Vg [V]', y='Id [A]', c="r", ax=ax)


            DF_list[p]['Ig [A]'] = abs(DF_list[p]['Ig [A]']) *(1E6)  ## A->uA
            DF_list[p].plot.scatter(x='Vg [V]', y='Ig [A]', c="b", ax=ax)

            # DF_list[p].plot(x='Vg [V]', y='Id [A]', label='Id@Vsd={}[V]'.format(p * 0.1), kind='line', ax=ax)

        x = DF_list[p]['Vg [V]']
        x = np.array(x)
        x = x.tolist()
        x = sorted(x)

        y = DF_list[p]['Id [A]']
        y = abs(y)
        y = np.array(y)
        y = y.tolist()
        y = np.flipud(y)

        X_Y_Spline = make_interp_spline(x, y)

        X_ = np.linspace(min(x), max(x), 11)
        Y1_ = X_Y_Spline(X_)
        ###

        y = DF_list[p]['Ig [A]']
        y = abs(y)
        y = np.array(y)
        y = y.tolist()
        y = np.flipud(y)

        X_Y_Spline = make_interp_spline(x, y)

        X_ = np.linspace(min(x), max(x), 11)
        Y2_ = X_Y_Spline(X_)

        rounded_number = round(p * STEP, 3)
        rounded_number = round((p + 1) * STEP, 3)

        plt.plot(X_, Y1_, label="Id@Vsd={}[V]".format(rounded_number))
        plt.plot(X_, Y2_, label="Ig@Vsd={}[V]".format(rounded_number))

        plt.yscale("log")
        plt.xlabel("Vg [V]")
        plt.ylabel("|current| [uA]")
        plt.legend(loc='best', fancybox=True, shadow=True)
        # plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper right')

    plt.title('Id&Ig(Log scale) vs Vg_device#{}'.format(j + 1 + (C - 1)))

    plt.legend(bbox_to_anchor=(1.04, 1), borderaxespad=0)
    fig = plt.gcf()
    fig.set_size_inches(8, 5)
    fig.tight_layout()

    plt.show()
    plt.draw()
    fig.savefig('Id&Ig(Log)_vs_Vg_device#{}.png'.format(j + 1 + (C - 1)), dpi=100)

    os.chdir(basePath)
    source_dir = "device#{}".format(j + 1 + (C - 1))
    target_dir = "Id_Ig vs Vg"
    shutil.move(source_dir, target_dir)

    os.chdir(r"C:\Users\z5345591\PycharmProjects\Nanowells_4p0b\Code")
    print('Finished device{}/{}'.format((j + 1), c1))


daqout_S.goTo(0, delay=0.001)
KVg.goTo(0, delay=0.001)
my_Pi.setMuxToOutput(0)  # sets multiplexer to 0

end_time = time.time()
print('Elapsed time: {} [sec]'.format(end_time - start_time))# time in seconds

print("End of all processes =)")
