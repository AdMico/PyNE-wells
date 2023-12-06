"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima
@author: Jakob Seidl
"""

from collections.abc import Iterable
import json
import GlobalMeasID as ID
import numpy as np
import scipy.io as sio
import time
import os
import pandas as pd
from itertools import product
import matplotlib.pyplot as plt
import warnings

# Specify plotting options:
#Plot style presets: e.g, 'fivethirtyeight' or 'ggplot' or 'seaborn. More examples -> https://matplotlib.org/3.3.3/gallery/style_sheets/style_sheets_reference.html
plt.style.use('ggplot')
# mpl.rcParams['axes.linewidth'] = 1.0    #  boxplot linewidth
# mpl.rcParams.update({'font.size': 11})  #  fontsize
########################################

# mpl.use('TkAgg') #This should be the default on windows I think, but on my mac it isnt

# For each input point:
# 1. Sets the instruments to the input point by calling the inputSetters with the point
# 2. Calls each outputReaders to get the output point
# 3. Calls outputReceiver with the point
# After all input points have been processed, outputFinisher is called
# 

def sweepAndSave(
                 inputDict,
                 extraInstruments = [],
                 saveEnable = True,
                 delay = 0.0,
                 plotVars = None,
                 comments = "No comments provided by user",
                 plotParams = [('go--','linear-linear'),('ro-','linear-linear')]*10,
                 saveCounter = 10,
                 breakCondition = None,
                 plotCounter = 1,
                 plotSize = (10,10),
                 plotAlpha = 0.8,
                    ):
    """Executes a measurement sweep using pre-defined instruments and parameter values.
       See usage under https://pypi.org/project/pyneMeas/

    Parameters
    ----------
        inputDict : dict various value types.
                    inputDict requires the following keys: 'basePath', 'fileName','setters','sweepArray', 'readers'.

        extraInstruments : list of intrument objects, optional.
                           Used to keep track of instruments that are not directly used as setter or reader. Default= []

        saveEnable : Boolean, optional.
                     whether you want to save data to disk. Currently saveEnable = True is required for plotting. Default = True

        delay : float, optional.
                         Float, wait time in seconds after a value has been set and before instruments are read out. Default = 0.0.

        plotVars : list of (string1,string2) tuples, optional.
                         list of `('xVar','yVar')` tuples to be plotted. Example: `[ ('V_SD', 'I_SD'),('V_SD', 'I_Leak')]`. Default = None.

        plotParams : list of `('plotString','XAxisScale-YAxisScale')` tuples, optional. Needs to contain one tuple
                     for each x-y variable pair to be plotted, see above.
                     `'plotString'` contains color, line and marker info. XAxisScale/YAxisScale can be 'linear' or 'log'.
                       Example:  [('go-', 'linear-linear')]

        comments : str, optional.
                Comments written to the .log file. Include information such as sample ID, setup, etc. Default = "No comments provided by user".

        saveCounter : int, optional.
                After how many datapoints do you want to save data to disc. Can help speed up the measurement slightly. Default = 10.

        breakCondition : tuple, optional.
                Tuple: ('testVariable',operator,limit). operator can be '>' (greater than) or '<' (lower than).
                 Example: ('Isd','>',50E-9) breaks the measurement when/if 'Isd' surpasses 50 nA. Default = None.

        plotCounter : int, optional.
                After how many datapoints do you want to plot the acquired data. plotCounter > 1 can help speed up the measurement significantly
                since plotting is resource intensive. Default = 1.

        plotSize : tuple of flots/ints, optional.
                   (sizeX,sizeY) Size of the plot window in cm. Default = (10,10).

        plotAlpha : float, optional.
                   float ranging from 0 -> 1. Transparency of markers in plot. Default = 0.8.
    Returns
    -------
        df : pandas.DataFrame
            dataframe object with columns labelled as variable names and one row for each point in the sweepArray.

    """
    # sweepAndSave is the main function of this module and THE sweepfunction. It is the only function that the user actually calls himlself
    # - all other functions provided here all called 'under the hood by sweepAndsave'. It can be subdivided into three parts:
    # (1): Initialize: Check if user input is valid, create data and log files on disk and set up the plot object. All this is done ONCE ONLY.
    # (2): sweep() function which calls receiver() within: LOOP Section: This is the actual sweep,
    # i.e., iterative process carried out over every single datapoint in the inputArray. This is: (I) set setter Instr to inputArray point, then Query all meas instruments,
    # (II) append data to files and plots and (III) every N-th iteration (default =10), force the file to be written on disk.
    # (3): Wrap-up: Write the final instrument parameters and data to file, save the plot as .png, close all file connections (good practice!)
    # def unpackInputDict(inputDict):
    #     keyList = ['basePath','fileName','inputHeaders','sweepArray',
    #                'inputSetters','outputHeaders','outputReaders']
    #     return [inputDict[key] for key in keyList]
    def unpackInputDict(inputDict):
        keyList = ['basePath','fileName','setters','sweepArray',
                   'readers']
        return [inputDict[key] for key in keyList]

    def instrumentsHeadersfromDict(inputDict):
        instruments, headers = [], []
        for key, item in inputDict.items():
            instruments.append(key)
            if isinstance(item, list) or isinstance(item, tuple):
                for i in item:
                    headers.append(i)
            else:
                headers.append(item)
        return (instruments, headers)

    inputDict = checkInputDict(inputDict,saveEnable)
    basePath, fileName, setters, inputPoints, readers = unpackInputDict(inputDict)
    inputSetters,inputHeaders = instrumentsHeadersfromDict(setters)
    outputReaders,outputHeaders = instrumentsHeadersfromDict(readers)

    lenInputList = len(inputPoints)

    ######################################################################## Part(1)
    #########################################################################################################################################################
    #Turn input array into itertools.product if it isnt already. Since our sweepArray is usually a 1D array anyway, this is usually not necessary and is more of a relic than a feature:
    if (type(inputPoints) == product):
        pass
    elif (type(inputPoints) == list or type(inputPoints) == np.ndarray):
        inputPoints = product(inputPoints)
    else:
        pass

    inputHeaders = flatten(inputHeaders);\
    outputHeaders = flatten(outputHeaders); #Make sure we have simple lists, not lists within lists etc..
    # allHeaders = inputHeaders + outputHeaders

    ### New breakCond Stuff ####
    if breakCondition != None and len(breakCondition) == 3:
        breakIndex =  outputHeaders.index(breakCondition[0])
    else: breakIndex = None

    # Prepare a dict for the data too. This dict will be used to write data to a .mat file which can be conveniently read by Matlab or Python
    pointsDict = {}
    for header in flatten((flatten(inputHeaders), flatten(outputHeaders))):
        pointsDict[header] = []

    ID.increaseID()
    measurementName = str(ID.readCurrentSetup()) + str(ID.readCurrentID())
    startTime = time.time()  # Start time

    # Main loop if user wants to save data to file:
    if(saveEnable):
        fileName = str(ID.readCurrentSetup()) + str(ID.readCurrentID()) + "_" + fileName
        instruments  = set(inputSetters + outputReaders + extraInstruments)
        config = {}
        for instrument in instruments: #This goes through the list of all instruments and queries all options that have a associated 'get()' method. E.g., 'sourceMode' for the Keithely2401
            config["{}-{}-{}".format(instrument.get('name'),type(instrument).__name__,len(config)+1)] = instrument.getOptions()#The ['key'] for each instrument is its 'name' and its type.

        #  write the initial config to the LOG file:
        log = open(basePath+fileName +"_LOG"+ ".tsv", "w")
        log.write("Measurement Log file for measurement >>> "+ str(ID.readCurrentSetup()) + str(ID.readCurrentID())+" <<< \n")
        log.write("Starting time and date: "+time.asctime(time.localtime(time.time()))+"\n")
        log.write("\n")
        log.write("Set/sweeped variables/instruments:\n")
        log.write("Variable\tInst name\tInst type\n")
        log.write("-----------------------------------\n")
        for header,name, Insttype in zip(inputHeaders, [setter.name for setter in inputSetters], [setter.type for setter in inputSetters]):
            log.write(f"{header}\t{name}\t{Insttype}\n")

        log.write("\n")
        log.write("Measuring variables/instruments:\n")
        log.write("Variable\tInst name\tInst type\n")
        log.write("-----------------------------------\n")
        for header,name, Insttype in zip(outputHeaders, [getter.name for getter in outputReaders], [getter.type for getter in outputReaders]):
            log.write(f"{header}\t{name}\t{Insttype}\n")

        log.write("\n")
        log.write("User comments: "+str(comments) +"\n")
        log.write("-----------------------------------\n")
        log.write("Delay = "+str(delay)+"s \n")
        log.write("Initial instrument configuration\n")
        log.write("-----------------------------------\n")
        log.write(json.dumps(config, indent = 4, sort_keys = True)) #Writes all initial instrument paramters in intented Json format
        log.write("\n-----------------------------------\n")
        log.close()

        #Write data headers to plain text file :
        tsv = open(basePath + fileName + ".tsv", "w")
        tsv.write("\t".join(flatten(inputHeaders))+ "\t")
        tsv.write("\t".join(flatten(outputHeaders)) + "\n")

        ##############          Prepare Plotting: ###############
        # measurementName = str(ID.readCurrentSetup()) + str(ID.readCurrentID()) # returns e.g. At104

        Xvalues1 = [];Yvalues1 = [];Xvalues2 = [];Yvalues2 = [] #Generate empty lists of X and Y Data. This is used later in the plotting routine.
        if plotVars is not None:
            ############## Initialize the plot. Actual plotting happens within receiver() within save() ###############
            plt.ion()  # this is the call to matplotlib that allows dynamic plotting
            fig = plt.figure(figsize = plotSize)
            lineObjs = []
            axObjs = []
            nSubplot = len(plotVars)
            nRows = int(np.ceil(np.sqrt(nSubplot)))
            nCols = int(np.floor(np.sqrt(nSubplot)))
            if nRows*nCols < nSubplot:
                nRows += 1

            for index,(xyAxisName,plotParamTuple) in enumerate(zip(plotVars,plotParams)):
                xAxisName,yAxisName = xyAxisName
                plotString, axisString = plotParamTuple
                subplotIndex = nRows*100+nCols*10+index+1
                axObj = fig.add_subplot(subplotIndex)

                # create a variable for the line so we can later update it (in the receiver)
                line, = axObj.plot(0.01, 0.02, plotString, alpha = plotAlpha)

                xScale = axisString.split('-')[0]
                yScale = axisString.split('-')[1]
                axObj.set_xscale(xScale)
                axObj.set_yscale(yScale)

                # update plot label/title
                if plotVars !=None and len(plotVars) == nSubplot:
                    plt.ylabel(yAxisName)
                    plt.xlabel(xAxisName)
                if index == 0:
                    plt.title(f'{measurementName}')

                lineObjs.append(line)
                axObjs.append(axObj)
            plt.subplots_adjust(left=0.125, right=0.94, bottom=0.1, top=0.93, wspace=0.5, hspace=0.5)
            plt.show()
        ############### END initialize plot ###############################

        ######################################################################## Part(2) --The loop-- ########################################################################
        #########################################################################################################################################################

        ########  The receiver() function is a sub-section of the save() function and is called for EACH point in the sweepArray.
        #It does two things: 1) Append the set of measured values (e.g. results from you SRS830 and K2401) to your measurement text file (.tsv)
            #and append it to your python dictionary of results (used for export as .mat file in the end). 2) It updates the current plot with the new data.

        ##############  Definition of receiver() ###############################
        def receiver(inputPoint, outputPoint,counter,lenInputList,forceSave = False, forcePlot = False,):

            for value, header in zip(flatten(inputPoint), flatten(inputHeaders)):
                pointsDict[header].append(value)
            for value, header in zip(flatten(outputPoint), flatten(outputHeaders)):
                pointsDict[header].append(value)

            tsv.write("\t".join(map(str, flatten(inputPoint))) + "\t") #takes the input points, 'flattens' the list (aka gets rid of unecessary lists in lists) turns them into strings and writes them separated by a tab \t in the tsv file.
            tsv.write("\t".join(map(str, flatten(outputPoint))) + "\n")

            progressBar(counter, lenInputList, barLength=20)
            #these force saving commands should probably only be executed every tenth iteration or so to speed things up.
            if (counter%saveCounter == 0 or forceSave):
                tsv.flush()   #These two commands force the tsv file and .mat file to be saved to disk. Otherwise the file will be lost when killing the program
                os.fsync(tsv.fileno())
                sio.savemat(basePath +fileName + '.mat', pointsDict)

            if plotVars is not None:
                xyDatSet = [(pointsDict[p1],pointsDict[p2]) for p1,p2 in plotVars]
                #Do the actual Plotting:
                if (counter % plotCounter == 0 or forcePlot):
                    for lineOb, axObj, xyTuple in zip(lineObjs, axObjs, xyDatSet):
                        x, y = xyTuple
                        lineOb.set_ydata(y)
                        lineOb.set_xdata(x)

                        stdY = np.std(y)
                        stdX = np.std(x) / 4
                        try: #Introduced this since sometimes 'NaNs' or other chunk data may impede setting the axis limits properly
                            with warnings.catch_warnings():  #used to suppress the annoying matplotlib warning about singular axe
                                warnings.simplefilter("ignore")
                                axObj.set_ylim([np.min(y) - stdY, np.max(y) + stdY])
                                axObj.set_xlim([np.min(x) - stdX, np.max(x) + stdX])
                        except:
                            pass

                    plt.pause(0.00001)
                ############## END Definition of receiver() ###############################

        #sweep() does the actual sweep and calls receiver() defined just above! sweep() is defined just below, outside of the sweepAndSave() definition
        sweep(inputPoints, inputSetters, outputReaders, receiver,delay,breakCondition,breakIndex,lenInputList)

        ######################################################################## Part(3) ########################################################################
        #########################################################################################################################################################
        ###### Wrapping up the measurement: close the data.tsv file, write the final settings of all instruments in .log file,
        #save a final version of the data to .mat format and save the figure created as .png

        tsv.flush()  # These three commands force the tsv file and .mat file to be saved to disk. Otherwise the file will be lost when killing the program
        os.fsync(tsv.fileno())
        tsv.close()
        sio.savemat(basePath +fileName + '.mat', pointsDict)

        elapsedTime = time.time()-startTime
        log = open(basePath +fileName +"_LOG"+ ".tsv", "a")
        log.write("Ending time and date: "+time.asctime(time.localtime(time.time()))+"\n")
        log.write("Time elapsed: "+str(elapsedTime)+" seconds." +"\n")
        log.write("Final instrument configuration: \n")
        log.write("-----------------------------------\n")
        log.write(json.dumps(config, indent = 4, sort_keys = True)) #Writes all the instrument parameters in indeted json format
        log.write("\n-----------------------------------\n")
        log.close()

        if plotVars is not None:
            plt.savefig(basePath +fileName+'.png') #Save Plot as .png as additional feature (only if plotting parameters were specified
            plt.close('all')

    # Main loop if user doesnt want to save data to file:
    elif(not saveEnable): #

        def receiverNoSave(inputPoint, outputPoint):
            for value, header in zip(flatten(inputPoint), flatten(inputHeaders)):
                pointsDict[header].append(value)
            for value, header in zip(flatten(outputPoint), flatten(outputHeaders)):
                pointsDict[header].append(value)

        sweepNoSave(inputPoints, inputSetters, outputReaders,receiverNoSave , delay,breakCondition,breakIndex,lenInputList)  # This does the actual sweep (without saving)!

    # Wrap Up:
    elapsedTime = time.time()-startTime
    print(f'/>>>>>> Finished measurement {measurementName:} | Duration: {elapsedTime:.1f} seconds = {elapsedTime/60:.1f} min  <<<<<<<')
    return pd.DataFrame.from_dict(pointsDict)

######################################################################## END of sweepAndSave() ########################################################################
#######################################################################################################################################################################

def sweep(inputPoints, inputSetters, outputReaders, receiver,delay,breakCondition,breakIndex,lenInputList):
    """sweep() defines the 'actual sweep',i.e.,, we define what is done for each 'inputPoint' of the array we want to sweep over. """
    prevPoint = None
    counter = 0

    def checkPointBreaks():
        if breakCondition[1] == '>':
            return (flatten(outputPoint)[breakIndex] < breakCondition[2])
        elif breakCondition[1] == '<':
            return (flatten(outputPoint)[breakIndex] > breakCondition[2])

    # Actual loop over all points in inputArray:
    for inputPoint in inputPoints:
#            while(running): #If we wanted something like a break condition, this would be the place to put them. Not yet implemented, though.
                if len(inputPoint) != len(inputSetters):#Usually len(inputPoint) is 1 since it's a single point in a 1D array. One instrument, one value.
                    raise ValueError("Length of input point does not match length of input setters")

                #We define the 'previous' state of the sweep so we are able to
                if prevPoint == None: #For the first point of each sweep, this is the case. The setter.goTo(target) then slowly goes to the first value. This is mainly to catch user errors.
                    prevPoint = [None] * len(inputPoint) #Usually len(inputPoint) is 1 since it's a single point in a 1D array.
                    for value,setter in zip(inputPoint,inputSetters):
                        setter.goTo(value)
                #A Set source instrument
                for value, prevValue, setter in zip(inputPoint, prevPoint, inputSetters):
                    # Avoid setting a value if it is already set to it
                    if value != prevValue: #only change outputs if they are in fact different to the previous once. Saves time.
                        if callable(setter):# In principle one could directly pass a (lambda) function instead of a real instrument. Then this block is carried out.
                            setter(value)
                        else: # This is carried out when a real Instrument is passed to the SweepAndSave function, so nearly always.
                            setter.set(type(setter).defaultOutput, value)

                prevPoint = inputPoint
                #### B Reading out all instruments defined as 'outputReaders'
                time.sleep(delay) #This is the delay specified by the user, typicall 0.2s
                outputPoint = []
                for reader in outputReaders:
                    if callable(reader): # In principle one could directly pass a (lambda) function instead of a real instrument. Then this block is carried out.
                        tempRes = reader()

                        outputPoint.append(tempRes)

                    else: #However, usually we provide a 'real' instrument object and the appropriate instrument.get('readVariable') is called.
                        tempRes = reader.get(type(reader).defaultInput)
                        outputPoint.append(tempRes)

                #  !!!! BREAK !!!!!!!! BREAK !!!!!!!! BREAK !!!!
                if (breakIndex == None or checkPointBreaks()):
                    receiver(inputPoint, outputPoint,counter,lenInputList)
                    counter = counter+1
                else:
                    print(f"Terminated measurement: Reached breakCondition: \nMeasured variable: {breakCondition[0]} reached {flatten(outputPoint)[breakIndex]} which is {breakCondition[1]} {breakCondition[2]}")
                    break
    receiver(inputPoint, outputPoint, counter,lenInputList, forceSave=True, forcePlot=True,)

#               inputPoints, inputSetters, outputReaders, receiver,delay,breakCondition,breakIndex,lenInputList
def sweepNoSave(inputPoints, inputSetters, outputReaders,receiverNoSave,delay,breakCondition,breakIndex,lenInputList): #Since by default the 'saveEnable' option is True, this funciton is barely ever called.

    def checkPointBreaks():
        if breakCondition[1] == '>':
            return (flatten(outputPoint)[breakIndex] < breakCondition[2])
        elif breakCondition[1] == '<':
            return (flatten(outputPoint)[breakIndex] > breakCondition[2])

    prevPoint = None
    for inputPoint in inputPoints:
        if len(inputPoint) != len(inputSetters):
            raise ValueError("Length of input point does not match length of input setters")

        #We define the 'previous' state of the sweep so we are able to only change outputs if they are in fact different to the previous once. Saves time.
        if prevPoint == None: #For the first point of each sweep, this is the case.
            prevPoint = [None] * len(inputPoint) #Usually len(inputPoint) is 1 since it's a single point in a 1D array.

        for value, prevValue, setter in zip(inputPoint, prevPoint, inputSetters):
            # Avoid setting a value if it is already set to it
            if value != prevValue:
                if callable(setter):
                    setter(value)
                else:
                    setter.set(type(setter).defaultOutput, value)
        prevPoint = inputPoint

        time.sleep(delay)
        outputPoint = []
        for reader in outputReaders:
            if callable(reader):
                outputPoint.append(reader())
            else:
                outputPoint.append(reader.get(type(reader).defaultInput))

        if (breakIndex == None or checkPointBreaks()):
            receiverNoSave(inputPoint, outputPoint)
        else:
            print(
                f"Terminated measurement: Reached breakCondition: \nMeasured variable: {breakCondition[0]} reached {flatten(outputPoint)[breakIndex]} which is {breakCondition[1]} {breakCondition[2]}")
            break
    receiverNoSave(inputPoint, outputPoint)

#################################### From here on unimportant and helper functions ################
###################################################################################################

def checkInputDict(inputDict,saveEnable):
    requiredKeys = {'basePath','fileName','setters',
                    'sweepArray','readers'}
    inputArgs = set(inputDict.keys())

    missingInputs = requiredKeys.difference(inputArgs)
    unusedInputs = inputArgs.difference(requiredKeys)

    # 1. Assert we have all essential input keys
    assert len(missingInputs) == 0, f"\n Please define the following MISSING ARGUMENTS in your input dictionary: \n {[key for key in missingInputs]}"

    # 2. Letting user know some of his inputs will be ignored. Happens when extra dict keys are used.
    if len(unusedInputs) !=0:
        warnings.warn(f"Warning: The following arguments in your input dictionary will be ignored: \n {[arg for arg in unusedInputs]} ")

    #  3. basePath
    assert isinstance(inputDict['basePath'],str), f"The 'basePath' attribute of the input dictionary needs to be a string! You entered {inputDict['basePath']}."
    if os.path.exists(inputDict['basePath']):
        if saveEnable: print(f'Saving data to existing directory: {inputDict["basePath"]}')
        else: print('Data not saved to disk. Use pandas.dataFrame return value of sweep() to use data.')
    else:
        os.mkdir(inputDict['basePath'])
        print(f'Created data storage directory: {inputDict["basePath"]}')
    if inputDict['basePath'][-1] != '/': # When the user specifies a path not ending on /, we still want to save on the lowest subfolder. -> Add /
        inputDict['basePath'] = inputDict['basePath'] + '/'

    #  4. fileName
    assert isinstance(inputDict['fileName'],str), f"The 'fileName' attribute of the input dictionary needs to be a string! You entered {inputDict['fileName']}."

    # 5. setters
    if not isinstance(inputDict['setters'],dict):
        raise  ValueError(f'Your input dictionary with key "setters" mus be a dictionary itself. You assigned: {inputDict["setters"]} of type: {type(inputDict["setters"]).__name__}\n Please assign the instrument as "key" and the corresponding variable name(s) as values')

    # 6. sweepArray
    assert type(inputDict['sweepArray']) in [range,list,np.ndarray],f"sweepArray needs to be Python list, numpy.array or a range object. You supplied data of type: {type(inputDict['sweepArray']).__name__}"
    if type(inputDict['sweepArray']) == range:
        inputDict['sweepArray'] = [*inputDict['sweepArray']] # Unpack range into a list

    # 8. readers
    if not isinstance(inputDict['readers'],dict):
        raise ValueError(
            f'Your input dictionary with key "readers" mus be a dictionary itself. You assigned: {inputDict["readers"]} of type: {type(inputDict["readers"]).__name__}\n Please assign the instrument as "key" and the corresponding variable name(s) as values')

    # 10. Make sure

    return inputDict

# Checks if val is iterable, but not a string
def isIterable(val):
    return isinstance(val, Iterable) and not isinstance(val, str)

# Flattens a list: [[1, 2, 3], 4, [5], [6, 7]] => [1, 2, 3, 4, 5, 6, 7]
def flatten(iterable):
    flattenedList = []
    for e1 in iterable:
        if isIterable(e1):
            for e2 in e1:
                flattenedList.append(e2)
        else:
            flattenedList.append(e1)
    return flattenedList

def checkPointMatchesHeaders(point, headers): # I added heaps of flatten() in here in order to prevent weird errors where there shouldnt be any.
    if len(flatten(point)) != len(flatten(headers)):
        raise ValueError("Point {} does not have same length as header {}".format(flatten(point), flatten(headers)))

    for value, header in zip(flatten(point), flatten(headers)):
        if isIterable(header) and isIterable(value):
            if len(flatten(header)) != len(flatten(value)):
                raise ValueError("Point {} does not have same length as header {}".format(flatten(point), flatten(headers)))
        elif not isIterable(header) and not isIterable(value):
            pass
        else:
            raise ValueError("Point {} does not have same length as header {}".format(flatten(point), flatten(headers)))

def checkPlotHeaders(inputHeaders,outputHeaders,plotVars):
    if plotVars == None:
        return
    if (len(plotVars) ==2 and plotVars[0] in (flatten(inputHeaders)+flatten(outputHeaders)) and plotVars[1] in (flatten(inputHeaders)+flatten(outputHeaders))):
        return 1
    elif (len(plotVars) ==4 and plotVars[0] in (flatten(inputHeaders)+flatten(outputHeaders)) and plotVars[1] in (flatten(inputHeaders)+flatten(outputHeaders)) and plotVars[2] in (flatten(inputHeaders)+flatten(outputHeaders)) and plotVars[3] in (flatten(inputHeaders)+flatten(outputHeaders))):
        return 2
    else:
        raise ValueError("{} does either not have the right format (either two or 4 parameters) or one of the given values is not found in input or output Headers".format(plotVars))

def progressBar(current, total, barLength = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))

    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')