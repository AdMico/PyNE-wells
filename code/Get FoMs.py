"""
Brought to PyNE-wells v1.0.0 on Tue Feb 6 2024 by SK

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

Contents:
---Get FoMs and draw histrogram accompanied with normal distribution curves of multiple devices
---Screening 52 devices to see if they can meet each criterion or not (This can be set at Line 511.)

Note:
---Prior to running this code, Dataset of 52 devices taken by 'measurement with MUX_Get output and transfer curves at a time.py' is needed.
"""

import scipy.stats as st
import math
from scipy.interpolate import make_interp_spline
from Imports2 import *
import os
import numpy as np
import pandas as pd

#Select a folder where set of data for 52 devices is stored.
[basePath,fileName] = fileDialog()

c1 = 52 # Number of devices
FOMS = []

for i in range(c1):
 os.chdir(basePath + "Id_Ig vs Vg/device#{}".format(i+ 1))

 ####Id vs Vg
 df2 = pd.read_csv('dff4.csv')
 # print(df2)

 x = df2['Vg [V]']

 x = np.array(x)
 x = x.tolist()
 X = sorted(x)

 y = df2['Id [A]']
 y = y * (1E6)
 y = np.array(y)
 y = y.tolist()
 Y = np.flipud(y)

 ##Interpolation
 X_Y_Spline = make_interp_spline(X, Y)

 X_ = np.linspace(min(X), max(X), 50)
 Y_ = X_Y_Spline(X_)

 ####gm
 gm_X = pd.read_csv('gm_X_Vsd=-0.5[V].csv')

 x = gm_X['Vg']

 x = np.array(x)
 x = x.tolist()
 X = sorted(x)

 y = gm_X['gm']
 # y = y * (1E6)
 y = np.array(y)
 Y = y.tolist()
 Y = np.flipud(y)

 ##Interpolation
 X_Y_Spline = make_interp_spline(X, Y)

 X_ = np.linspace(min(X), max(X), 50)
 Y_ = X_Y_Spline(X_)


 ##### Ig-Vg
 df1 = pd.read_csv('dff4.csv')
 x = df1['Vg [V]']
 x = np.array(x)
 x = x.tolist()
 X = sorted(x)

 y = df1['Ig [A]']

 y = y * (1E6)
 y = np.array(y)
 y = y.tolist()
 Y = np.flipud(y)

 ##Interpolation
 X_Y_Spline = make_interp_spline(X, Y)

 X_ = np.linspace(min(X), max(X), 50)
 Y1_ = X_Y_Spline(X_)

 ##### Id-Vg
 df2 = pd.read_csv('dff4.csv')
 x = df1['Vg [V]']
 x = np.array(x)
 x = x.tolist()
 X = sorted(x)

 I = -0.5
 y = df2['Id [A]']

 y = y * (1E6)
 y = np.array(y)
 y = y.tolist()
 Y = np.flipud(y)

 ##Interpolation
 X_Y_Spline = make_interp_spline(X, Y)

 X_ = np.linspace(min(X), max(X), 50)
 Y2_ = X_Y_Spline(X_)

 #### Get FoMs:
 # 1. gm [uS]
 # 2. Id(Vg=0V) [A]
 # 3. Id(Vg=1.0V) [A]
 # 4. Ratio Id_on:Id_off
 # 5. Ig (Max) [uA]

 FOMs = ['gm_X', 'Id1', 'Id2', 'R', 'Ig_max']

 gm_X = max(gm_X["gm"])
 gm_X = round(gm_X, 3)
 # print('1. gm [uS]:{}'.format(gm_X))
 FOMs[0] = gm_X

 Id1 = df2['Id [A]'][10]
 Id1 = Id1 * (1E6)
 # print('2. Id(Vg=0V) [uA]:{}'.format(Id1))
 FOMs[1] = Id1

 Id2 = df2['Id [A]'][0]
 Id2 = Id2 * (1E6)
 Id2 = round(Id2, 2)
 # print('3. Id(Vg=1.0V) [uA]:{}'.format(Id2))
 FOMs[2] = Id2

 R = Id1 / Id2
 R = round(R, 0)
 # print('4. Ratio Id_on:Id_off:{}'.format(R))
 FOMs[3] = R

 Ig_max = max(df1['Ig [A]'])
 Ig_max = Ig_max * (1E6)
 Ig_max = round(Ig_max, 5)
 # print('5. Ig (Max) [uA]:{}'.format(Ig_max))
 FOMs[4] = Ig_max


 if i == 0:
  FOMS = pd.DataFrame([FOMs])

  FOMS.columns = ['gm_X[uS]', 'Id1[uA]', 'Id2[uA]', 'On-Off ratio', 'Ig_max[uA]']
  # print(FOMS)

 else:
  new_rows = pd.DataFrame([FOMs])
  new_rows.columns = ['gm_X[uS]', 'Id1[uA]', 'Id2[uA]', 'On-Off ratio', 'Ig_max[uA]']
  FOMS = pd.concat([FOMS, new_rows], axis=0, ignore_index=True)


print("Number of devices: {}".format(c1))
FOMS.index = np.arange(1, len(FOMS) + 1)

print('***** List of FOMs ({} device) ****'.format(c1))
print(FOMS)
print(' ')

os.chdir(basePath)
FOMS.to_csv('FOMS.csv', header=True, index=True)

### Draw Gaussian curve over histogram

os.chdir(r"C:\Users\z5345591\PycharmProjects\Nanowells_4p0b\Output\20240105\2")

df = pd.read_csv('FOMS.csv')

### 1. gm [uS]
p1 = df["gm_X[uS]"]

p1 = np.array(p1)

# Parameters for drawing graphs

x_min, x_max = 0, 10000  # Plot range: min and max
j = 0.5                   # Y_axis (Frequency) Step width
k = 1000                   # Width of Interval
bins = 10               # Number of interval: (x_max-x_min)/k  (10000-0)/1000->10

# Process for drawing graph form here
plt.figure(dpi=96)
# plt.xlim(x_min,x_max)
d = 0.001

# (1) Statistical processing
n   = len(p1)         # Sample size
mu  = p1.mean()       # Average
sig = p1.std(ddof=0)  # Standard deviation：ddof(Degree of freedom)=0
print(f'■ Average：{mu:.1f}uS Standard deviation：{sig:.1f}uS')
ci1, ci2 = (None, None)

# # Test of normality (5% significance level) and 95% confidence interval of population mean
_, p = st.shapiro(p1)
if p >= 0.05 :
  print(f'  - p={p:.2f} ( p>=0.05 ) It can be said that the population has normality.')
  U2 = p1.var(ddof=1)  # Population variance estimate (unbiased variance)
  DF = n-1                     # Degree of freedom
  SE = math.sqrt(U2/n)         # Standard error
  ci1,ci2 = st.t.interval(loc=mu, scale=SE, df=DF ,alpha=0.95)
  print(f'  - 95% confidence interval CI for the population mean = [{ci1:.2f} , {ci2:.2f}]')
else:
  print(f'  ※ p={p:.2f} ( p<0.05 ) It cannot be said that the population has normality.')


# # (2) Drawing histogram

hist_data = plt.hist(p1, bins=bins, color='tab:green', range=(x_min, x_max), rwidth=0.9, alpha=0.3)
plt.gca().set_xticks(np.arange(x_min,x_max-k+d, k))

# (3) Approximate curve assuming normal distribution

sig = p1.std(ddof=1)  # Unbiased standard deviation：ddof(Degree of freedom)=1
nx = np.linspace(x_min, x_max+d, 150) # 150 divided
ny = st.norm.pdf(nx,mu,sig) * k * len(p1)

plt.plot( nx , ny, color='tab:green', linewidth=1.5, linestyle='--')

# # # (4) X_axis scale・label setting
plt.xlabel('gm (uS)',fontsize=12)
plt.gca().set_xticks(np.arange(x_min,x_max+d, k))
# # #

# # # # (5) Y_axis scale・label setting
plt.ylabel('# of chip',fontsize=12)

fig = plt.gcf()
fig.set_size_inches(6, 5)
fig.tight_layout()

plt.show()
plt.draw()
fig.savefig('gm (uS)', dpi=100)



# 2. Id(Vg=0V) [A]
p2 = df["Id1[uA]"]
p2 = np.array(p2)

# Parameters for drawing graphs

x_min, x_max = -800, 200  # Plot range: min and max
j = 0.5                   # Y_axis (Frequency) Step width
k = 100                   # Width of Interval
bins = 10               # Number of interval:(x_max-x_min)/k  (-800-200)/100->10

# Process for drawing graph form here
plt.figure(dpi=96)
# plt.xlim(x_min,x_max)
d = 0.001

# (1) Statistical processing
n   = len(p2)         # Sample size
mu  = p2.mean()       # Average
sig = p2.std(ddof=0) # Standard deviation：ddof(Degree of freedom)=0
print(f'■ Average：{mu:.1f}uA Standard deviation：{sig:.1f}uA')
ci1, ci2 = (None, None)

# # Test of normality (5% significance level) and 95% confidence interval of population mean
_, p = st.shapiro(p2)
if p >= 0.05 :
  print(f'  - p={p:.2f} ( p>=0.05 )It can be said that the population has normality.')
  U2 = p1.var(ddof=1)  # Population variance estimate (unbiased variance)
  DF = n-1                     # Degree of freedom
  SE = math.sqrt(U2/n)         # Standard error
  ci1,ci2 = st.t.interval(loc=mu, scale=SE, df=DF ,alpha=0.95)
  print(f'  - 95% confidence interval CI for the population mean = [{ci1:.2f} , {ci2:.2f}]')
else:
  print(f'  ※ p={p:.2f} ( p<0.05 ) It cannot be said that the population has normality.')


# # (2) Drawing histogram

hist_data = plt.hist(p2, bins=bins, color='tab:green', range=(x_min, x_max), rwidth=0.9, alpha=0.3)
plt.gca().set_xticks(np.arange(x_min,x_max-k+d, k))

# (3) Approximate curve assuming normal distribution

sig = p2.std(ddof=1)  # Unbiased standard deviation：ddof(Degree of freedom)=1
nx = np.linspace(x_min, x_max+d, 150) # 150 divided
ny = st.norm.pdf(nx,mu,sig) * k * len(p1)

plt.plot( nx , ny, color='tab:green', linewidth=1.5, linestyle='--')

# # # (4) X_axis scale・label setting
plt.xlabel('Id(Vg=0V) (uS)',fontsize=12)
plt.gca().set_xticks(np.arange(x_min,x_max+d, k))
# # #

# # # # (5) Y_axis scale・label setting
plt.ylabel('# of chip',fontsize=12)

fig = plt.gcf()
fig.set_size_inches(6, 5)
fig.tight_layout()

plt.show()
plt.draw()
fig.savefig('Id(Vg=0V) (uS)', dpi=100)

# 3. Id(Vg=1.0V) [A]
p3 = df["Id2[uA]"]

p3 = np.array(p3)

# Parameters for drawing graphs

x_min, x_max = -1100, 100  # Plot range: min and max
j = 0.5                   # Y_axis (Frequency) Step width
k = 100                   # Width of Interval
bins = 12               # Number of interval(x_max-x_min)/k  (-1100-100)/100->10

# Process for drawing graph form here
plt.figure(dpi=96)
# plt.xlim(x_min,x_max)
d = 0.001

# (1) Statistical processing
n   = len(p3)         # Sample size
mu  = p3.mean()       # Average
sig = p3.std(ddof=0)  # Standard deviation：ddof(Degree of freedom)=0
print(f'■ Average：{mu:.1f}uA Standard deviation：{sig:.1f}uA')
ci1, ci2 = (None, None)

# Test of normality (5% significance level) and 95% confidence interval of population mean
_, p = st.shapiro(p3)
if p >= 0.05 :
  print(f'  - p={p:.2f} ( p>=0.05 ) It can be said that the population has normality.')
  U2 = p1.var(ddof=1)  # Population variance estimate (unbiased variance)
  DF = n-1                     # Degree of freedom
  SE = math.sqrt(U2/n)         # Standard error
  ci1,ci2 = st.t.interval(loc=mu, scale=SE, df=DF ,alpha=0.95)
  print(f'  - 95% confidence interval CI for the population mean = [{ci1:.2f} , {ci2:.2f}]')
else:
  print(f'  ※ p={p:.2f} ( p<0.05 ) 95% confidence interval CI for the population mean')

# # (2) Drawing histogram

hist_data = plt.hist(p3, bins=bins, color='tab:green', range=(x_min, x_max), rwidth=0.9, alpha=0.3)
plt.gca().set_xticks(np.arange(x_min,x_max-k+d, k))

# (3) Approximate curve assuming normal distribution

sig = p3.std(ddof=1)  # Unbiased standard deviation：ddof(Degree of freedom)=1
nx = np.linspace(x_min, x_max+d, 150) # 150 divied
ny = st.norm.pdf(nx,mu,sig) * k * len(p1)

plt.plot( nx , ny, color='tab:green', linewidth=1.5, linestyle='--')

# # # (4) X_axis scale・label setting
plt.xlabel('Id(Vg=1.0V) (uS)',fontsize=12)
plt.gca().set_xticks(np.arange(x_min,x_max+d, k))
# # #

# # # # (5) ) Y_axis scale・label setting
plt.ylabel('# of chip',fontsize=12)

fig = plt.gcf()
fig.set_size_inches(6, 5)
fig.tight_layout()

plt.show()
plt.draw()
fig.savefig('Id(Vg=1.0V) (uS).png', dpi=100)


## 4. Ratio Id_on:Id_off
p4 = df["On-Off ratio"]
p4 = np.array(p4)

# Parameters for drawing graphs

x_min, x_max = -250, 250  # Plot range: min and max
j = 0.5                   # Y_axis (Frequency) Step width
k = 50                   # Width of Interval
bins = 12              # Number of interval　(x_max-x_min)/k  (-250-250)/50->10

# Process for drawing graph form here
plt.figure(dpi=96)
# plt.xlim(x_min,x_max)
d = 0.001

# (1) Statistical processing
n   = len(p4)        # Sample size
mu  = p4.mean()       # Average
sig = p4.std(ddof=0)  # Standard deviation：ddof(Degree of freedom)=0
print(f'■ Average：{mu:.1f}、Standard deviation：{sig:.1f}')
ci1, ci2 = (None, None)

# # Test of normality (5% significance level) and 95% confidence interval of population mean
_, p = st.shapiro(p4)
if p >= 0.05 :
  print(f'  - p={p:.2f} ( p>=0.05 ) It can be said that the population has normality')
  U2 = p1.var(ddof=1)  # Population variance estimate (unbiased variance)
  DF = n-1                     # Degree of freedom
  SE = math.sqrt(U2/n)         # Standard error
  ci1,ci2 = st.t.interval(loc=mu, scale=SE, df=DF ,alpha=0.95)
  print(f'  - 95% confidence interval CI for the population mean  = [{ci1:.2f} , {ci2:.2f}]')
else:
  print(f'  ※ p={p:.2f} ( p<0.05 ) It cannot be said that the population has normality')


# # (2) Drawing histogram
hist_data = plt.hist(p4, bins=bins, color='tab:green', range=(x_min, x_max), rwidth=0.9, alpha=0.3)
plt.gca().set_xticks(np.arange(x_min,x_max-k+d, k))

# (3) Approximate curve assuming normal distribution

sig = p4.std(ddof=1)  # Unbiased standard deviation：ddof(Degree of freedom)=1
nx = np.linspace(x_min, x_max+d, 150) # 150 divied
ny = st.norm.pdf(nx,mu,sig) * k * len(p1)

plt.plot( nx , ny, color='tab:green', linewidth=1.5, linestyle='--')

# # # (4) X_axis scale・label setting
plt.xlabel('Ratio Id_on:Id_off',fontsize=12)
plt.gca().set_xticks(np.arange(x_min,x_max+d, k))
# # #

# # # # (5) Y_axis scale・label setting
plt.ylabel('# of chip',fontsize=12)

fig = plt.gcf()
fig.set_size_inches(6, 5)
fig.tight_layout()

plt.show()
plt.draw()
fig.savefig('Ratio_Id_on_Id_off.png', dpi=100)

# 5. Ig_max
p5 = df["Ig_max[uA]"]

p5 = np.array(p5)

# print(max(p5))
# print(min(p5))

# Parameters for drawing graphs

x_min, x_max = 0, 0.00001  # Plot range: min and max
j = 0.5                   # Y_axis (Frequency) Step width
k = 0.000001                   # Width of Interval
bins = 10               # Number of interval　(x_max-x_min)/k  (0-0.00001)/0.0001->10

# Process for drawing graph form here
plt.figure(dpi=96)
# plt.xlim(x_min,x_max)
d = 0.001

# (1) Statistical processing
n   = len(p5)         # Sample size
mu  = p5.mean()       # Average
sig = p5.std(ddof=0)  # Standard deviation：ddof(Degree of freedom)=0
print(f'■ Average：{mu:.1f}uA Standard deviation：{sig:.1f}uA')
ci1, ci2 = (None, None)
# # Test of normality (5% significance level) and 95% confidence interval of population mean

_, p = st.shapiro(p5)
if p >= 0.05 :
  print(f'  - p={p:.2f} ( p>=0.05 ) It can be said that the population has normality.')
  U2 = p1.var(ddof=1)  # Population variance estimate (unbiased variance)
  DF = n-1                     # Degree of freedom
  SE = math.sqrt(U2/n)         # Standard error
  ci1,ci2 = st.t.interval(loc=mu, scale=SE, df=DF ,alpha=0.95)
  print(f'  - 95% confidence interval CI for the population mean = [{ci1:.2f} , {ci2:.2f}]')
else:
  print(f'  ※ p={p:.2f} ( p<0.05 ) It cannot be said that the population has normality.')


# # (2) Drawing histogram

hist_data = plt.hist(p5, bins=bins, color='tab:green', range=(x_min, x_max), rwidth=0.9, alpha=0.3)
plt.gca().set_xticks(np.arange(x_min,x_max-k+d, k))

# (3) Approximate curve assuming normal distribution
sig = p5.std(ddof=1)  # Unbiased standard deviation：ddof(Degree of freedom)=1
nx = np.linspace(x_min, x_max+d, 150) # 150 divided
ny = st.norm.pdf(nx,mu,sig) * k * len(p1)

plt.plot( nx , ny, color='tab:green', linewidth=1.5, linestyle='--')

# # # (4) X_axis scale・label setting
plt.xlabel('Ig_max (uA)',fontsize=12)
plt.gca().set_xticks(np.arange(x_min,x_max+d, k))
# # #

# # # # (5) Y_axis scale・label setting
plt.ylabel('# of chip',fontsize=12)

fig = plt.gcf()
fig.set_size_inches(6, 5)
fig.tight_layout()

plt.show()
plt.draw()
fig.savefig('Ig_max (uA).png', dpi=100)


""""
Screening 52 devices to see if they can meet each criterion or not
"""

os.chdir(r"C:\Users\z5345591\PycharmProjects\Nanowells_4p0b\Output\20240105\2")

df = pd.read_csv('FOMS.csv')

FOMs_DY = ['Device#', 'gm_X', 'Id1', 'Id2', 'R', 'Ig_max']


# print(df['gm_X[uS]'][0],df['Id1[uA]'][0],df['Id2[uA]'][0],df['On-Off ratio'][0],df['Ig_max[uA]'][0])

# aa = 300
# bb = 145
# cc = 1
# dd = 170
# ee =1

aa = 0
bb = -1000
cc = -1000
dd = -300
ee = -1

print('')
print('Criteria: gm_X[uS]:{}>, Id1[uA]:{}>, Id2[uA]:{}<, On-Off ratio:{}>, Ig_max[uA]:{}<'.format(aa,bb,cc,dd,ee))
print('')

FOMS_DY = [] #DY: Device Yield
#
FOMS_DY = pd.DataFrame([FOMs_DY])
FOMS_DY.columns = ['Device#', 'gm_X[uS]', 'Id1[uA]', 'Id2[uA]', 'On-Off ratio', 'Ig_max[uA]']
FOMS_DY=FOMS_DY.iloc[1:]


for i in range(c1):
    # if df['gm_X[uS]'][i]>aa  and df['Id1[uA]'][i]>bb and df['Id2[uA]'][i]<cc:
    if df['gm_X[uS]'][i]>aa and df['Id1[uA]'][i]>bb and df['Id2[uA]'][i]>cc and df['On-Off ratio'][i]>dd and df['Ig_max[uA]'][i]>ee:
        a = df.iloc[i]

        # a1 = int(a[0])
        a1 = int(a.iloc[0])
        FOMs_DY[0] = a1

        # a2 = round(a[1], 2)
        a2 = round(a.iloc[1], 2)
        FOMs_DY[1] = a2

        a3 = round(a.iloc[2], 2)
        FOMs_DY[2] = a3

        a4 = round(a.iloc[3], 2)
        FOMs_DY[3] = a4

        a5 = round(a.iloc[4], 2)
        FOMs_DY[4] = a5

        a6 = round(a.iloc[5], 2)
        FOMs_DY[5] = a6

        new_rows = pd.DataFrame([FOMs_DY])
        new_rows.columns = ['Device#', 'gm_X[uS]', 'Id1[uA]', 'Id2[uA]', 'On-Off ratio', 'Ig_max[uA]']


        # FOMS_DY = pd.concat([FOMS_DY,new_rows], axis=0, ignore_index=True)
        FOMS_DY = pd.concat([FOMS_DY.astype(new_rows.dtypes),new_rows.astype(FOMS_DY.dtypes)],axis=0, ignore_index=True)
        # out = pd.concat([df1.astype(df2.dtypes), df2.astype(df1.dtypes)])

        # if i == 0:
        #      FOMS_DY = pd.DataFrame([FOMs_DY])
        #      FOMS_DY.columns = ['Device#', 'gm_X[uS]', 'Id1[uA]', 'Id2[uA]', 'On-Off ratio', 'Ig_max[uA]']

        # else:
        #     new_rows_DY = pd.DataFrame([FOMs_DY])
        #     new_rows_DY.columns = ['Device#', 'gm_X[uS]', 'Id1[uA]', 'Id2[uA]', 'On-Off ratio', 'Ig_max[uA]']
        #     # FOMS_DY = pd.concat([FOMS_DY, new_rows_DY], axis=0, ignore_index=True)


print("*** List of devices that meet the criteria ***")
print(FOMS_DY)

print("Number of devices that meet criteria:{}/{}".format (len(FOMS_DY),c1))
dy = (len(FOMS_DY)/c1)*100
dy = int(dy)
print("Device Yield:{} %".format(dy))

# DY = ['Device Yield [%]']
DY = []
DY = pd.DataFrame([DY])
DY[1] =dy
DY.columns = ['Device Yield [%]']

os.chdir(basePath)

DY.to_csv('Device Yield.csv', header=True, index=False)
FOMS_DY.to_csv('FOMS_DY.csv', header=True, index=False)

