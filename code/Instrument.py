"""
Brought to PyNE-wells v1.2.0 on Thu Aug 07 2025 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima
@author: Jakob Seidl

Utility code for the instrument setting/getting capabilities in the various instruments.
Used currently in all of the USB6216 components
"""

import collections.abc
collections.Iterable = collections.abc.Iterable # Quick and dirty fix for V4.0, implement properly later.
# Checks if val is iterable, but not a string

def isIterable(val):
     return hasattr(val,'__iter__') and not isinstance(val, str)

def flatten(iterable):
    flattenedList = []
    for e1 in iterable:
        if isIterable(e1):
            for e2 in e1:
                flattenedList.append(e2)
        else:
            flattenedList.append(e1)
    return flattenedList

# Converts one element lists to just the element itself (e.g., ["a"] -> "a"),
# while leaving everything else untouched. This way we can have an "intuitive"
# format for options that only take a single argument, but still preserve
# support for multiple argument options
def unwrap(args):
    if isIterable(args) and len(args) == 1:
        return args[0]
    return args

class Instrument(object):
    # This contains all the available options an instrument has. This is
    # populated automatically for each individual instrument class with the
    # @addOptionSetter/Getter and @enableOptions decorators defined later in the file.
    # The key is the option name, while the values are: {
    #     "order": The relative order the option should be set in, when setting
    #              multiple options at once (only for _optionSetters)
    #     "fn": The actual class member function that sets the option
    # }
    _optionSetters = {}
    _optionGetters = {}

    def __init__(self):
        self._options = {}

    def get(self, option, forceCached = False):
        if not forceCached and option in type(self)._optionGetters:
            return unwrap(self._optionGetters[option]["fn"](self))
        elif option in type(self)._optionSetters:
            return unwrap(self._options[option])
        else:
            raise ValueError(
                "{} is not a valid option to get. {} are available".format(
                    option,
                    set(list(type(self)._optionSetters.keys()) + list(type(self)._optionGetters.keys()))
                )
            )

    def set(self, option, *args):
        if not option in type(self)._optionSetters:
            raise ValueError("{} is not a valid option. {} are available".format(option, list(type(self)._optionSetters.keys())))

        type(self)._optionSetters[option]["fn"](self, *args)
        self._options[option] = args

    def getOptions(self):
        options = self._options.copy()
        for option, args in list(options.items()):
            options[option] = unwrap(args)
        for option in type(self)._optionGetters:
            options[option] = self.get(option)
        return options

    def setOptions(self, options):
        # First check all options exist
        options = list(options.items())
        for option, _ in options:
            if not option in type(self)._optionSetters:
                raise ValueError("{} is not a valid option. {} are available".format(option, list(type(self)._optionSetters.keys())))

        # Sort the options so they're set in the correct order
        options = sorted(options, key = lambda option: type(self)._optionSetters[option[0]]["order"])

        # Actually set the options
        for option, args in options:
            if not isIterable(args):
                args = (args,)
            self.set(option, *args)

# Having a "totalOptions" variable lets us assign a total order to the options,
# by giving each option a unique number. This way we can ensure an order to
# setting the options when setting multiple options at once, since some options
# might require being set before others
            
totalOptions = 0
def addOptionSetter(name):
    def decorator(optionSetter):
        global totalOptions
        totalOptions += 1
        optionSetter.optionInfo = {"name": name, "order": totalOptions}
        return optionSetter
    return decorator

def addOptionGetter(name):
    def decorator(optionGetter):
        optionGetter.optionInfo = {"name": name, "isGetter": True}
        return optionGetter
    return decorator

# Since we can't access the class until it's finished being created, we have to
# have a separate decorator over the entire class, so we can then set the
# _optionsSetters property with the available options
    
def enableOptions(instrument):
    instrument._optionSetters = {}
    instrument._optionGetters = {}

    for option in list(instrument.__dict__.values()):
        if not hasattr(option, "optionInfo"):
            continue
        info = option.optionInfo
        if "isGetter" in info:
            instrument._optionGetters[info["name"]] = {"fn": option}
        else:
            instrument._optionSetters[info["name"]] = {"order": info["order"], "fn": option}

    return instrument

def closeInstruments(instrumentList1,instrumentList2=None):
    if instrumentList2 != None:
        List = flatten([instrumentList1,instrumentList2])
    else: List = instrumentList1

    for instrument in List:
        try:
            instrument.close()
        except:
            continue