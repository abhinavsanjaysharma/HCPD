# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 11:48:10 2023

@author: z5239428
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


path = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/GaAs-Cr_JamesDimmock_LN_lightIV_test.xlsx'

df = pd.read_excel(path)
runs = np.array(df.columns)[::2]
header=df.iloc[0]
df = df.rename(columns=header)
df=df[1:]

plt.figure()
plt.xlabel('Voltage (V)')
plt.ylabel('Current (A)')
for i, run in enumerate(runs):
    voltage = df.iloc[:,2*i]
    current = df.iloc[:,2*i + 1]
    plt.plot(voltage, -current,label=run)
    plt.axhline(y=0, color='k')
    plt.axvline(x=0, color='k')

plt.legend()
    
    