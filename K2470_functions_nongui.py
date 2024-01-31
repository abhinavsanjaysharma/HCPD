import pyvisa as visa
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import sys

from tkinter import *

from tkinter import ttk
import tkinter as tk

from tkinter import simpledialog
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import threading
import time        
import os

def initialise_SMU(resource_name="USB0::0x05E6::0x2470::04473418::INSTR"):
    rm=visa.ResourceManager()
    device=rm.open_resource(resource_name)
    device.write("*RST")
    device_name = device.query("*IDN?")
    device.timeout = 100000
    return device, device_name

def pulse_train(device,biaslevel=0,pulselevel=0.5,biaswidth=0.5,pulsewidth=0.5,points=10,limit=2.1,points_per_pulse = 5,gui=False,folder='C:/Data/',file_name='Test_Pulsetrain'):
    """
    --[[Set Up Pulse parameters
                *biaslevel: the offset current for the pulse train
                *pulselevel: the amplitude current of each pulse (from zero, not bias level)
                *biaswidth: the time at the bias level
                *pulsewidth: the time at amplitude level for each pulse
                *points: total number of pulses
                *limit: the source limit level
    ]]
    """
    device.write("reset()")
    device.write("smu.source.output = smu.OFF") # SMU output off  
    
    # #--User specified test parameters:
    # biaslevel = 0
    # pulselevel = 0.5
    # biaswidth = 0.5
    # pulsewidth = 0.5
    
    # points = 5
    # limit = 2.1
    period = pulsewidth + biaswidth 
    
    #--Set to current source and set up source config list
    device.write("smu.source.configlist.create('OutputList')")
    device.write("smu.source.func = smu.FUNC_DC_VOLTAGE")
    device.write("smu.source.readback = smu.OFF")
    
    #--Set up measure commands
    device.write("smu.measure.func = smu.FUNC_DC_CURRENT")
    device.write("smu.measure.nplc = 0.01")       
    device.write("smu.measure.autozero.once()")
    
    device.write("smu.measure.terminals = smu.TERMINALS_FRONT")
    device.write("smu.measure.range ="+str(limit))
    device.write("smu.measure.sense = smu.SENSE_4WIRE")
        
    # measuredelay = pulsewidth -((1/localnode.linefreq)*smu.measure.nplc + 450e-6)
    # if measuredelay < 50e-6:
    # measuredelay = 50e-6
          
    #-- Set the source range large enough to fit both the bias and level.
    device.write("smu.source.range ="+str( np.max([np.abs(biaslevel), np.abs(pulselevel)]) ))
    device.write("smu.source.delay = 0")
    # device.write("smu.source.vlimit.level ="+str(limit))
    
    #--Set to pulselevel (amplitude) and save to list
    device.write("smu.source.level = "+str(pulselevel))
    device.write("smu.source.configlist.store('OutputList')")
    
    #--Set to biaslevel and save to list
    device.write("smu.source.level ="+ str(biaslevel))
    device.write("smu.source.configlist.store('OutputList')")
    
    #--Setup Timers
    #-- Use timer[1] to control the Period of the pulse train
    device.write("trigger.timer[1].reset()")
    device.write("trigger.timer[1].start.generate = trigger.ON")
    device.write("trigger.timer[1].delay =" +str(period))
    device.write("trigger.timer[1].count =" +str(points - 1))   #-- Effective count will be points because trigger.timer[1].start.generate = trigger.ON
    
    #-- Use timer[2] to control the Pulse Width of the pulses
    device.write("trigger.timer[2].reset()")
    device.write("trigger.timer[2].start.stimulus = trigger.EVENT_TIMER1")
    device.write("trigger.timer[2].start.generate = trigger.OFF")
    device.write("trigger.timer[2].delay =" +str(pulsewidth))
    device.write("trigger.timer[2].count = 1")
    device.write("trigger.timer[2].enable = trigger.ON")
    
    #--Trigger model setup
    points_per_pulse = 5

    # Adjust measuredelay for the desired frequency of measurements within each pulse
    measuredelay = pulsewidth / points_per_pulse
    
    # Modify the trigger model to include multiple measurement points within each pulse
    device.write("trigger.model.setblock(1, trigger.BLOCK_BUFFER_CLEAR)")
    device.write("trigger.model.setblock(2, trigger.BLOCK_SOURCE_OUTPUT, smu.ON)")
    device.write("trigger.model.setblock(3, trigger.BLOCK_WAIT, trigger.EVENT_TIMER1)")
    device.write("trigger.model.setblock(4, trigger.BLOCK_CONFIG_RECALL, 'OutputList')")
    current_block = 5

    for i in range(points_per_pulse):
        # Calculate block numbers for the current iteration
        delay_block = current_block 
        measure_block = current_block + 1
        print('delay block, in 1st measurement')
        print(delay_block)

        # Set up the trigger model blocks for the current iteration

        device.write(f"trigger.model.setblock({delay_block}, trigger.BLOCK_DELAY_CONSTANT, {measuredelay})")
        device.write(f"trigger.model.setblock({measure_block}, trigger.BLOCK_MEASURE)")

        # Increment the block number for the next iteration
        current_block += 2
    device.write(f"trigger.model.setblock({current_block}, trigger.BLOCK_WAIT, trigger.EVENT_TIMER2)")
    device.write(f"trigger.model.setblock({current_block+1}, trigger.BLOCK_CONFIG_NEXT, 'OutputList')")
    
    current_block +=2

    for i in range(points_per_pulse):
        # Calculate block numbers for the current iteration
        delay_block = current_block 
        measure_block = current_block + 1
        print('delay block, in 2nd measurement')

        print(delay_block)

        # Set up the trigger model blocks for the current iteration

        device.write(f"trigger.model.setblock({delay_block}, trigger.BLOCK_DELAY_CONSTANT, {measuredelay})")
        device.write(f"trigger.model.setblock({measure_block}, trigger.BLOCK_MEASURE)")

        # Increment the block number for the next iteration
        current_block += 2

    # Set up the final block to branch back to the beginning
    final_block = current_block
    print(final_block)
    device.write(f"trigger.model.setblock({final_block}, trigger.BLOCK_BRANCH_COUNTER, {points}, 3)")
    device.write(f"trigger.model.setblock({final_block+1}, trigger.BLOCK_SOURCE_OUTPUT, smu.OFF)")

    
    #--Start the trigger model
    device.write("defbuffer1.clear()")
    device.write("trigger.model.initiate()")
    device.write("delay(0.001)")
    device.write("trigger.timer[1].enable = trigger.ON")
    device.write("waitcomplete()")
    time.sleep(1)
    device.write("*OPC?")
    try:
        print('try')
        status = float(device.read())
        print(status)
    except:
        print('except')
        status=0
    while status != 1:
        time.sleep(1)
        device.write("*OPC?")
        status = float(device.read())
        print('Measurement ongoing, please wait...')
    Vs, Is, times = [], [],[]

    
    for i in np.arange(float(device.query("print(defbuffer1.n)"))):
        Vs.append(float(device.query("print(defbuffer1.sourcevalues["+str(i+1)+"])")))
        times.append(float(device.query("print(defbuffer1.relativetimestamps["+str(i+1)+"])")))
        Is.append(float(device.query("print(defbuffer1.readings["+str(i+1)+"])")))
        
    
    

    plt.figure()
    plt.xlabel('Time (s)')
    plt.plot(times,Vs,'o-')
    plt.ylabel('Voltage (V)')
    plt.figure()
    plt.xlabel('Time (s)')
    plt.plot(times, Is,'o-')
    plt.ylabel('Current (A)')
    plt.figure()
    plt.plot(Vs,Is,'o-')
    plt.ylabel('Current (A)')
    plt.xlabel('Voltage (V)')
    
    df = pd.DataFrame({'Time(s)': times, 'Voltage (V)': Vs, 'Current (A)': Is}) # turn data into a pandas dataframe with voltage and current columns
    if gui:
        
        save = save_var.get()
    else:
        save=True

    if save:
        

        save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S') #get current date and time
        total_filename = folder+'/'+file_name+'_'+save_datetime+'.csv'
        df.to_csv(total_filename)
        
         
if __name__ == "__main__":
    rname = "USB0::0x05E6::0x2470::04473418::INSTR"
    device,device_name= initialise_SMU(rname)        
    device.timeout = 100000
    # IV_loop(Vs,device,1,file_name='IV_JD_ICL10b',plot=True,save=False)
    # IT_loop(device, 1,20,nplc=1)
    source_values_1 = np.arange(0,0.002,0.0001)
    source_values_2 = np.arange(0.002,0,-0.0001)
    source_values = np.append(source_values_1,source_values_2)
    # source_values = np.arange(0,6,0.1)
    # IV_measure(source_values,device,file_name='IV_curve',comments='',save=False,plot=True,ax=None,fig=None,gui=False,fourwire=False,sourcevolt=True)
    
    
    pulse_train(device,biaslevel=0,pulselevel=3,biaswidth=0.1,pulsewidth=0.1,points=10,limit=2.1,points_per_pulse=5,
                folder='C:/Data/',file_name='Test_pulse')
     
    
    
    
    



          