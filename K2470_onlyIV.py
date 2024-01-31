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

#pick one of the ways of setting voltage points below

#pick one of the ways of setting voltage points above

def IV_measure(source_values,device,folder='C:/Data/',file_name='IV_curve',comments='',
               save=False,plot=True,ax=None,fig=None,gui=False,fourwire=False,sourcevolt=True,
               ilimit=0.1):
        
    measure_values = [None for value in source_values]
    device.write("reset()")
    print('setting according to voltage or current source')
    if sourcevolt:
        print('voltage source!')
        # Configuration for measuring current
        source_func = "smu.FUNC_DC_VOLTAGE"
        measure_func = "smu.FUNC_DC_CURRENT"
        measure_label = 'Current (A)'
        source_label = 'Voltage (V)'
        device.write(f"smu.source.ilimit.level = {ilimit}")  # set current limit (in Amps)
        # device.write("smu.source.ilimit.level = 0.1")  # set current limit (in Amps)
        
    else:
        print('current source!')
        # Configuration for measuring voltage
        source_func = "smu.FUNC_DC_CURRENT"
        measure_func = "smu.FUNC_DC_VOLTAGE"
        measure_label = 'Voltage (V)'
        source_label = 'Current (A)'
        device.write("smu.source.vlimit.level = 1")  # set current limit (in Amps)
        device.write(f"smu.source.ilimit.level = {ilimit}")  # set current limit (in Amps)
    print('rest of the commands')
    device.write(f"smu.source.func = {source_func}")  # set source function
    
    device.write("smu.source.autorange = smu.ON")  # set voltage/current range to auto
    device.write("smu.source.autodelay = smu.ON")  # set delay to auto
    device.write(f"smu.measure.func = {measure_func}")  # set measurement function
    device.write("smu.measure.autorange = smu.ON")  # set current/voltage range to auto
    device.write("smu.measure.nplc = 0.01")   
    if fourwire: # set to 2WIRE or 4WIRE
        device.write("smu.measure.sense=smu.SENSE_4WIRE") 
    else:
        
        device.write("smu.measure.sense=smu.SENSE_2WIRE") 
    print('moving to plot')
    if plot:
        if not ax:
            fig, ax = plt.subplots()
            # print('newax')
        line, = ax.plot([], [],'o-', label=comments)
        ax.set_xlabel(source_label)
        ax.set_ylabel(measure_label)
        if gui and False:
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.grid(column=1, row=6)  # Adjust the row and column as needed
    
            def on_close():
                # Stop the animation and close the Tkinter window
                animation.event_source.stop()
                root.destroy()
        
            root.protocol("WM_DELETE_WINDOW", on_close)  # Handle window close event
        def update_plot(frame):
            source_value = source_values[frame]
        
            device.write("smu.source.level = "+str(source_value)) # Set voltage 
            device.write("smu.source.output = smu.ON") # SMU output on
            device.write("smu.measure.read()") # measure current
            # device.write("smu.source.output = smu.OFF") # SMU output off
            measure_values[frame] = device.query("print(defbuffer1.readings[defbuffer1.endindex])") # store current reading
        
            measure_values[frame] = float(measure_values[frame]) # .query returns a string, so it must be casted to float number
            print('measure values frame')
            print(measure_values[frame])
            if frame%1 == 0:
                # ax.clear()
                # ax.plot(Vs[:frame+1],Is[:frame+1],label=comments)
                line.set_xdata(source_values[:frame+1])
                line.set_ydata(measure_values[:frame+1])
                ax.relim()
                ax.autoscale_view(True, True, True)
                # ax.set_xlim(np.nanmin(np.array(Vs,dtype=float)), np.nanmax(np.array(Vs,dtype=float)))
                # ax.set_ylim(np.nanmin(np.array(Is,dtype=float)), np.nanmax(np.array(Is,dtype=float)))
                ax.legend()
                # plt.pause(0.05)
            if gui and False:
                canvas.draw()
                root.update()
        animation = FuncAnimation(fig, update_plot, frames=len(source_values), repeat=False, interval=5)
        # plt.show()
        # time.sleep(1)
        # device.write("*OPC?")
        # try:
        #     print('try')
        #     status = float(device.read())
        # except:
        #     print('except')
        #     status=0
    while None in measure_values:
        # print('sleeping')
        plt.pause(0.01)
            # device.write("*OPC?")
            # status = float(device.read())
        
        
        

    print('final mvalues')    
    print(measure_values)
    df = pd.DataFrame({source_label: source_values, measure_label: measure_values}) # turn data into a pandas dataframe with voltage and current columns
    print('df')
    print(df)
    
    if save:
        # file_name = 'IV_curve' #set filename as desired              
        save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S') #get current date and time
        
        # folder  = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/'
        total_filename = folder+file_name+'_'+str(comments)+save_datetime+'.csv'
        df.to_csv(total_filename)
    
    # if plot:
    #     fig, ax = plt.subplots()
    #     ax.plot(Vs,Is)
    #     ax.set_ylabel('Current (A)')
    #     ax.set_xlabel('Voltage (V)')
    #     # plt.draw()
    #     plt.show()
    
    
        
        

    return df,animation
def IV_loop(source_values,device, runs, depvars=None,file_name='IV_curve',
            save=False,plot=False,click=False,folder=None,ilimit=0.1,sourcevolt=True,fourwire=False):
    # if plot:
    #     fig, ax = plt.subplots()
    #     # print('newax_loop')
    # else:
    #     fig, ax = None, None
    for run in np.arange(runs):
        if not depvars:
            comments = run+1
        
        if click:
            if run == 0:
                input("Press Enter to start first measurement")
            else:
                input("Press Enter to start next measurement")
        

        df,anim = IV_measure(source_values,device,file_name,comments=comments,save=save,plot=plot,fourwire=fourwire, sourcevolt=sourcevolt,
                             ilimit=ilimit)
        
        
        print(f'Measurement {run+1} complete')
        if save:
            # comments2 = input('If required, enter additional comments to the filename\n')
            # comments2=None
            save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S') #get current date and time
            if folder is None:
            # folder  = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/'
                folder = 'C:/Data/'
            total_filename = folder+file_name+'_'+str(comments)+'_'+save_datetime+'.csv'
            df.to_csv(total_filename)
if __name__ == "__main__":
    rname = "USB0::0x05E6::0x2470::04473418::INSTR"
    device,device_name= initialise_SMU(rname)    
    
    #FOR VOLTAGE-CONTROLLED TESTING ENABLE THE FOLLOWING
    # source_values = np.arange(-0.5,0.5,0.01) # (start, end, step)
    # source_values_1 = np.arange(0,3.2,0.05) # (start, end, number_of_points)
    # source_values_2 = np.arange(3.2,0,-0.05)
    # source_values = np.append(source_values_1,source_values_2)
    
    # FOR CURRENT-CONTROLLED TESTING ENABLE THE FOLLOWING
    source_values_1 = np.arange(0,0.005,0.0001)
    source_values_2 = np.arange(0.005,0,-0.0001)
    source_values = np.append(source_values_1,source_values_2)
    
    
    #sourcevolt = True means VOLTAGE SOURCING
    #sourevolt = False means CURRENT SOURCING
    
    IV_loop(source_values,device,runs=1,file_name='Nb20nm_20um_d9_2_NDR_50 Ohm',plot=True,save=True,
            click=False,folder='C:/Data/NbOx/Nb 20 nm/',ilimit=0.005,sourcevolt=False,
            fourwire=False)
        
 
 

