# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 10:35:52 2023

@author: z5239428
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from solcore.structure import Structure
from solcore.absorption_calculator import calculate_rat
from scipy.interpolate import interp1d


Ag_nkdf = pd.read_csv('C:/Users/z5239428/OneDrive - UNSW/Ag_nk.csv')
Cr_nkdf = pd.read_csv('C:/Users/z5239428/OneDrive - UNSW/Cr_nk.csv')
SiO2_nkdf = pd.read_csv('C:/Users/z5239428/OneDrive - UNSW/SiO2_nk.csv')

Ag_nfunc, Ag_kfunc = interp1d(np.array(Ag_nkdf['wl'])*1000, np.array(Ag_nkdf['n']), kind='cubic'),\
                     interp1d(np.array(Ag_nkdf['wl'])*1000, np.array(Ag_nkdf['k']), kind='cubic')
Cr_nfunc, Cr_kfunc = interp1d(np.array(Cr_nkdf['wl'])*1000, np.array(Cr_nkdf['n']), kind='cubic'),\
                     interp1d(np.array(Cr_nkdf['wl'])*1000, np.array(Cr_nkdf['k']), kind='cubic')
SiO2_nfunc, SiO2_kfunc = interp1d(np.array(SiO2_nkdf['wl'])*1000, np.array(SiO2_nkdf['n']), kind='cubic'),\
                     interp1d(np.array(SiO2_nkdf['wl'])*1000, np.array(SiO2_nkdf['k']), kind='cubic')

thicknesses = np.arange(0.1,100,0.1)
theta=0
wls=np.array([500,501])
# def thickloop(stack, thicknesses, wls):
    

Rs, As, Ts = np.zeros(thicknesses.size),np.zeros(thicknesses.size),np.zeros(thicknesses.size)
Rs2, As2, Ts2 = np.zeros(thicknesses.size),np.zeros(thicknesses.size),np.zeros(thicknesses.size)
Rs3, As3, Ts3 = np.zeros(thicknesses.size),np.zeros(thicknesses.size),np.zeros(thicknesses.size)
Rs4, As4, Ts4 = np.zeros(thicknesses.size),np.zeros(thicknesses.size),np.zeros(thicknesses.size)




for i, t in enumerate(thicknesses):
    stack = Structure([
        [t, wls, Cr_nfunc(wls), Cr_kfunc(wls)],
        [4000, wls, SiO2_nfunc(wls), SiO2_kfunc(wls)]
    ])

    stack2 = Structure([
        [1000, wls, SiO2_nfunc(wls), SiO2_kfunc(wls)],
        [t, wls, Cr_nfunc(wls), Cr_kfunc(wls)],
        [1000, wls, SiO2_nfunc(wls), SiO2_kfunc(wls)]
    ])

    stack3 = Structure([

        [t, wls, Cr_nfunc(wls), Cr_kfunc(wls)],
        [84, wls, SiO2_nfunc(wls), SiO2_kfunc(wls)],
        [200, wls, Ag_nfunc(wls), Ag_kfunc(wls)]
    ])

    stack4 = Structure([
        [84, wls, SiO2_nfunc(wls), SiO2_kfunc(wls)],
        [t, wls, Cr_nfunc(wls), Cr_kfunc(wls)],
        [84, wls, SiO2_nfunc(wls), SiO2_kfunc(wls)],
        [200, wls, Ag_nfunc(wls), Ag_kfunc(wls)]
    ])
    # wavelengths = np.arange(400,1000,1)
    rat_data = calculate_rat(stack, angle=theta, wavelength=wls,no_back_reflection=False)
    rat_data2 = calculate_rat(stack2, angle=theta, wavelength=wls,no_back_reflection=False)
    rat_data3 = calculate_rat(stack3, angle=theta, wavelength=wls,no_back_reflection=False)
    rat_data4 = calculate_rat(stack4, angle=theta, wavelength=wls,no_back_reflection=False)
    Rs[i], As[i], Ts[i] = rat_data["R"][0]*100,rat_data["A"][0]*100,rat_data["T"][0]*100
    Rs2[i], As2[i], Ts2[i] = rat_data2["R"][0]*100,rat_data2["A"][0]*100,rat_data2["T"][0]*100
    Rs3[i], As3[i], Ts3[i] = rat_data3["R"][0]*100,rat_data3["A"][0]*100,rat_data3["T"][0]*100
    Rs4[i], As4[i], Ts4[i] = rat_data4["R"][0]*100,rat_data4["A"][0]*100,rat_data4["T"][0]*100
    
plt.figure()
plt.title('4.3a Cr-SiO2')

plt.plot(thicknesses,Rs,label='R')
plt.plot(thicknesses,As,label='A')
plt.plot(thicknesses,Ts,label='T')
plt.legend() 

plt.figure()
plt.title('4.3b SiO2-Cr-SiO2')

plt.plot(thicknesses,Rs2,label='R')
plt.plot(thicknesses,As2,label='A')
plt.plot(thicknesses,Ts2,label='T')
plt.legend() 

plt.figure()
plt.title('4.3c Cr-SiO2-Ag')

plt.plot(thicknesses,Rs3,label='R')
plt.plot(thicknesses,As3,label='A')
plt.plot(thicknesses,Ts3,label='T')
plt.legend() 

plt.figure()
plt.title('4.3d SiO2-Cr-SiO2-Ag')

plt.plot(thicknesses,Rs4,label='R')
plt.plot(thicknesses,As4,label='A')
plt.plot(thicknesses,Ts4,label='T')
plt.legend() 


        


    
    
    
    


  
