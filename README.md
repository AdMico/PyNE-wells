# PyNE-wells v1.1.1 (Updated 19APR24 APM)

**Written by:** Adam Micolich, Jan Gluschke & Shuji Kojima

**Purpose:** Software for the electronic measurements for the lipid-sealed wells project (Australian Research Council DP20210XXXX).

## Structure

Top level has two folders -- *code* and *data*. The *code* folder has all the active software at the top level. There are two sub-folders -- *debugging* and *purgatory*. The *debugging* folder has pieces of code that are used for debugging and connection checking for the various bits of hardware used in the measurements. The *purgatory* folder has pieces of old code that will be deleted in future releases but are kept for now just in case they are useful. The *data* folder is where the software will place experimental data, it will put these in automatically created folders with naming based on the global measurement ID (GMID) and the date/time. Files inside these subfolders will be automatically named accordingly, based also on the corresponding device measured.

## Program Components


## Installation