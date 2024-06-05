# PyNE-wells v1.1.1 (Updated 05JUN24 APM)

**Written by:** Adam Micolich, Jan Gluschke, Shuji Kojima & Sidd Rawat

**Purpose:** Software for the electronic measurements for the lipid-sealed wells project (Australian Research Council DP210102085).

*Developed and tested using Python 3.12.*

## Structure

Top level has two folders -- *code* and *data*. The *code* folder has all the active software at the top level. There are two sub-folders -- *debugging* and *purgatory*. The *debugging* folder has pieces of code that are used for debugging and connection checking for the various bits of hardware used in the measurements. The *purgatory* folder has pieces of old code that will be deleted in future releases but are kept for now just in case they are useful. The *data* folder is where the software will place experimental data, it will put these in automatically created folders with naming based on the global measurement ID (GMID) and the date/time. Files inside these subfolders will be automatically named accordingly, based also on the corresponding device measured.

## Program Components

The main functional component is `AssayRun4.py`, which runs the electrical measurement GUI, everything else is a subroutine.

`AssayRun4.py`: Main GUI for the electrical setup. There are only three buttons in the GUI. The first button is *start run* which will start a measurement. The specifications for the measurements (e.g., number of 'grabs', delay between 'grabs', etc. are set in `Config.py`). A 'grab' is a single readout of all 52 devices on the chip. The second button is *last grab*, which enables you to stop a sequence of immediately after the next grab. When used, *last grab* will leave the GUI running just as would be the case if you had let the specified number of grabs in `Config.py` complete. This enables a new sequence of grabs to be started without needing to restart the software. When you commence a new grab, the datafile structure (folder and names) will update automatically, no intervention is required. The third button is *End Program*, which shuts down the GUI and terminates `AssayRun4.py`.

`Config.py`: This contains all the key configuration details for your instance of the software. The individual parameters are explained in the comments. The most crucial one to note is the `PiBox` parameter. You need to ensure this matches the Raspberry Pi you are using in your hardware set-up, otherwise when you run the GUI, all the multiplexer commands will be going to another set-up, which may be running at the time.

`GlobalMeasID.py`: This contains all the code for setting, reading and incrementing the Global Measurement ID (GMID) used to trace data files to hardware-setup and owner. A user will only need to interact with this program to initialise the GMID for their setup. This is done at the `initID` function by setting the desired prefix (ideally 2 letter string, but can be more) and ID number. If this file is run (and the Reset switch at the top = 1) then the GMID will reinitialise to the value you set in `initID`. Can be useful to leave Reset = 0 once you've initialised the first time, just to prevent accidental loss of GMID value, but it ships with Reset = 1 as that's the most common usage case.

`GlobalMeasIDBinary`: Binary file containing the GMID. Automatically incremented by the software via routines in `GlobalMeasID.py`.

`Imports.py`: Master import file to simplify code. Doesn't need edits unless you add new library calls to the software (if you do, please update `requirements.txt` accordingly).

`Instrument.py`: This appears to be legacy from PyNE-probe, likely to be deprecated in a future version of PyNE-wells.

`Pi_control_Gen4.py`: This controls all the hardware interactions with the Raspberry Pi, including setting the respective IP address, switching the power control relay for the MUXes, and specifying the truth-tables to correctly connect the measure circuit to a given device. The MUXes are MAX306 16-channel CMOS analog multiplexer ICs, and there are currently four in each MUXBox. Further details can be found in a future GitHub repository for the hardware design. Instance can be run as main to enable direct debugging control of the multiplexers, see bottom of code for details.

`Res_Pull.py`: This is useful legacy from development and enables the resistance to be pulled outside of the GUI in `AssayRun4.py` for testing purposes. Left in the code folder for this instance, but will be moved to the `debugging` folder later.

`SampleRateTest.py`: This is a special instance of `AssayRun4.py` that assists with setting the samples per channel (`SpC`) variable in `Config.py`. This will be moved to `debugging` folder in a future update.

`stop.txt`: Software stop button, not sure it's used currently, may deprecate in future version.

`SweepFunction.py`: Old PyNE sweep code, likely to be deprecated in future update as I don't think it gets used here currently.

`TimeMeas.py`: Old PyNE sweep code, likely to be deprecated in future update as I don't think it gets used here currently. 

`USB6216InSS.py`: Basic code for reading in single-shot, single-channel measurements from the National Instruments USB6216-BNC instrument. Used by other programs.

`USB6216InSB.py`: Code for reading in burst-averaged, single-channel measurements from the National Instruments USB6216-BNC instrument. Used by other programs.

`USB6216InPB.py`: Code for reading in burst-averaged, dual-channel measurements from the National Instruments USB6216-BNC instrument. Used by other programs.

`USB6216InPB_SRT.py`: Special version of `USB6216InPB.py` that enables the samples per channel to be specified in the function call rather than by `Config.py`. Used by `SampleRateTest.py` only.

`USB6216Out.py`: Basic code for setting the voltage on the analog outputs in the National Instruments USB6216-BNC instrument. Used by other programs.

## Updates to be made in next version (submit requests here)

- Deprecate `Instrument.py` if none of its functions are used (i.e., is true legacy).
- Update filename for Pi_control_Gen4 to remove underscores.
- Update filename for Res_Pull to remove underscore.
- Move `Res_Pull.py` across to `debugging` folder.
- Move `SampleRateTest.py` across to `debugging` folder.
- Do we still need `stop.txt` or can we deprecate?
- Can we deprecate `SweepFunction.py` and `TimeMeas.py` in next version?
- How do I deal with `USB6216InPB_SRT.py` long-term? Can I put a software switch into `USB6216InPB.py` to make it redundant and remove?
- Clean up the `PiBox` issue where a user who hasn't read the documentation can accidentally run someone else's MUXBox by mistake.
- APM to create github repo for the hardware and link to it here for context.

## Installation

APM currently runs this software in PyCharm, you may need to change accordingly for use in another IDE.

1. In PyCharm set up a new Python project called `PyNE-wells` and ensure it is configured as Project venv and using your Python 3.12 interpreter.
2. Navigate using GitBash to the folder where the project is (typically `C:/Users/.../PyCharmProjects/PyNE-wells/`).
3. Initialise the folder using `git init`.
4. Switch the default branch from `master` to `main` using `git branch -m master main`, as an option, you might also set this as a default using `git config --global init.defaultBranch main`.
5. Connect to the PyNE-wells repo using `git remote add origin https://github.com/AdMico/PyNE-wells/`.
6. Pull the repo using `git pull origin main`.
7. Install the requirements for the package as specified in `requirements.txt`.
8. Go to `Config.py` file and set the hardware configurations, making particular note to correctly set the `PiBox` parameter so you don't send commands to someone else's MUXBox.
9. Go to `GlobalMeasID.py` and initialise the GMID for your particular instance.
10. You are ready to run, and `AssayRun4.py` is the best place to start. Further information in the repo for our electrical set-up, which is coming in the near future.