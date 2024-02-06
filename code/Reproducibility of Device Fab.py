"""
Brought to PyNE-wells v1.0.0 on Tue Feb 6 2024 by SK

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

Contents:
---Investigate reproducibility of device fabrication
Note:
---Prior to running this code, Dataset of device yield/ chip (At least n=30?) taken by 'Get FoMs.py' is needed.
"""


import scipy.stats as st
import math
from Imports2 import *
import os
import numpy as np
import pandas as pd

#Select a folder where dataset of device yield/ chip is stored.
[basePath,fileName] = fileDialog()


c1 = 30 # Number of chips
print("Number of chips:{}".format(c1))
# FOMS = []
#
X= []
for i in range(c1):
 os.chdir(basePath + "ID2024XXXX/{}".format(i+ 1))

 ####Get device yield per chip
 df2 = pd.read_csv('Device Yield.csv')
 x = df2['Device Yield [%]']
 x = np.array(x)
 x = x.tolist()
 x = sorted(x)

 X = np.append(X,x)

### Draw Gaussian curve over histogram


df = pd.DataFrame(X)
df.columns = ['Device Yield[%]']
df.index = np.arange(1, len(df) + 1)
print(df)

## 1. gm [uS]
p1 = df['Device Yield[%]']

# Parameters for drawing graphs

x_min, x_max = 90, 100  # Plot range: min and max
j = 5                   # Y_axis (Frequency) Step width
k =  1                  # Width of Interval
bins = 10               # Number of interval: (x_max-x_min)/k  10/->1

# Process for drawing graph form here
plt.figure(dpi=96)
# plt.xlim(x_min,x_max)
d = 0.001

# (1) Statistical processing
n   = len(p1)         # Sample size
mu  = p1.mean()       # Average
sig = p1.std(ddof=0)  # Standard deviation：ddof(Degree of freedom)=0
print(f'■ Average：{mu:.1f}% Standard deviation：{sig:.1f}%')
ci1, ci2 = (None, None)

# # Test of normality (5% significance level) and 95% confidence interval of population mean
_, p = st.shapiro(p1)
if p >= 0.05 :
   print(f'  - p={p:.2f} ( p>=0.05 ) It can be said that the population has normality.')
   U2 = p1.var(ddof=1)  # Population variance estimate (unbiased variance)
   DF = n-1                     # Degree of freedom
   SE = math.sqrt(U2/n)         # Standard error
   ci1,ci2 = st.t.interval(loc=mu, scale=SE, df=DF ,confidence=0.95)
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
plt.xlabel('Device Yield (%)',fontsize=12)
plt.gca().set_xticks(np.arange(x_min,x_max+d, k))
# # #

# # # # (5) Y_axis scale・label setting
plt.ylabel('# of chip',fontsize=12)

fig = plt.gcf()
fig.set_size_inches(6, 5)
fig.tight_layout()

plt.show()
plt.draw()
os.chdir(basePath)
fig.savefig('Reproducibility of device fabrication.png', dpi=100)
