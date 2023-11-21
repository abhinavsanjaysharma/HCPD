# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 12:42:37 2023

@author: z5239428
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pyvisa as visa
    
import logging
import time

from pylinkam import interface, sdk
import datetime
import threading 
from queue import Queue, Empty
from matplotlib.animation import FuncAnimation

def initialise_SMU(resource_name):
    rm=visa.ResourceManager()
    device=rm.open_resource(resource_name)
    # device.write("*RST")
    print(device.query("*IDN?"))
    return device 

#pick one of the ways of setting voltage points below

Vs = np.arange(-0.5,0.5,0.01) # (start, end, step)
Vs = np.linspace(-0.6,0.6,10) # (start, end, number_of_points)

#pick one of the ways of setting temperature points below

temp_range = np.arange(25,30,1)
temp_range = np.linspace(30,32,2)

def update_IV_plot(frame, ax, Vs,Is,comments):
    ax.clear()
    ax.plot(Vs,Is,label=comments)
    plt.legend()
    plt.pause(0.05)
        

def IV_measure(Vs,device,file_name='IV_curve',comments='',save=False,plot=True,ax=None):
        
    Is = [None for volt in Vs]
    device.write("reset()")
    device.write("smu.source.func = smu.FUNC_DC_VOLTAGE") # set source to voltage
    device.write("smu.source.ilimit.level = 0.1") # set current limit (in Amps)
    device.write("smu.source.autorange = smu.ON") # set voltage range to auto
    device.write("smu.source.autodelay = smu.ON") # set delay                                                                                                                                                                                                                to auto
    device.write("smu.measure.func = smu.FUNC_DC_CURRENT") # set measurement to current
    device.write("smu.measure.autorange = smu.ON") # set current range to auto
    device.write("smu.measure.nplc = 1") 
    device.write("smu.measure.sense=smu.SENSE_2WIRE") # set to 2WIRE or 4WIRE
    if plot:
        if not ax:
            fig, ax = plt.subplots()
            # print('newax')
            
    for i, volt in enumerate(Vs):
        device.write("smu.source.level = "+str(volt)) # Set voltage 
        device.write("smu.source.output = smu.ON") # SMU output on
        device.write("smu.measure.read()") # measure current
        device.write("smu.source.output = smu.OFF") # SMU output off
        Is[i] = device.query("print(defbuffer1.readings[defbuffer1.endindex])") # store current reading
    
        Is[i] = float(Is[i]) # .query returns a string, so it must be casted to float number
        # ax.clear()
        # ax.plot(Vs,Is,label=comments)
        # plt.legend()
        # plt.pause(0.05)
        
        aniV = FuncAnimation(fig, update_IV_plot, fargs=(ax, Vs,Is,comments), interval=1000)
        
    
    df = pd.DataFrame({'Voltage (V)':Vs, 'Current (A)': Is}) # turn data into a pandas dataframe with voltage and current columns
    
    
    if save:
        # file_name = 'IV_curve' #set filename as desired              
        save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S') #get current date and time
        
        folder  = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/'
        total_filename = folder+file_name+'_'+str(comments)+save_datetime+'.csv'
        df.to_csv(total_filename)
    
    # if plot:
    #     fig, ax = plt.subplots()
    #     ax.plot(Vs,Is)
    #     ax.set_ylabel('Current (A)')
    #     ax.set_xlabel('Voltage (V)')
    #     # plt.draw()
    #     plt.show()
    
    
        
        

    return df


def IV_loop(Vs,device, runs, depvars=None,file_name='IV_curve',save=False,plot=False):
    if plot:
        fig, ax = plt.subplots()
        # print('newax_loop')
    else:
        fig, ax = None, None
    for run in np.arange(runs):
        if not depvars:
            comments = run+1
        if run == 0:
            input("Press Enter to start first measurement")
        else:
            input("Press Enter to start next measurement")
        

        df = IV_measure(Vs,device,comments=comments,save=False,plot=plot,ax=ax)
        
        
        print(f'Measurement {run+1} complete')
        if save:
            comments2 = input('If required, enter additional comments to the filename\n')
            
            save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S') #get current date and time
            
            folder  = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/'
            total_filename = folder+file_name+'_'+str(comments)+'_'+comments2+save_datetime+'.csv'
            df.to_csv(total_filename)
        
        
def temperature_monitor(connection, stop_event, data_queue):
    while not stop_event.is_set():
        dt_now = (datetime.datetime.now() - start).total_seconds()
        temp = connection.get_value(interface.StageValueType.HEATER1_TEMP)
        data_queue.put((dt_now, temp))

        time.sleep(1)
def update_plot(frame, data_queue, ax):
    try:
        timestamp, temperature = data_queue.get_nowait()
        times.append(timestamp)
        temps.append(temperature)
        ax.clear()
        ax.plot(times, temps, 'o-', label='Temperature')
        ax.set_xlabel('Time since start (s)')
        ax.set_ylabel('Temperature (C)')
        ax.legend()
        
        # plt.draw()
        # plt.pause(0.001)
    except Empty:
        pass

def wait_for_temperature_stabilization(connection, target_temperature, tolerance=0.1, stabilization_duration=60):
    """
    Wait for the temperature to stabilize around the target temperature.

    Parameters:
    - connection: The connection to the temperature control instrument.
    - target_temperature: The target temperature to stabilize.
    - tolerance: The acceptable temperature deviation from the target temperature.
    - stabilization_duration: The duration for which the temperature must remain stable.

    Note: Adjust the tolerance and stabilization_duration according to your system's behavior.
    """
    start_time = time.time()
    stable_duration = 0

    while stable_duration < stabilization_duration:
        current_temperature = connection.get_value(interface.StageValueType.HEATER1_TEMP)

        # Check if the current temperature is within the tolerance range around the target temperature
        if abs(current_temperature - target_temperature) <= tolerance:
            stable_duration += time.time() - start_time
        else:
            # Reset the start time if the temperature goes outside the tolerance range
            start_time = time.time()
            stable_duration = 0

        # Adjust the sleep interval based on your system's characteristics
        time.sleep(1)






logging.basicConfig(level=logging.DEBUG)
stop_event = threading.Event()
data_queue = Queue()







rname = "USB0::0x05E6::0x2470::04473418::INSTR"
device= initialise_SMU(rname)   

times = []
temps = []

# stop_event.is_set()
fig, ax = plt.subplots()
times = []
temps = []

with sdk.SDKWrapper() as handle:
    with handle.connect() as connection:
        print(f"Name: {connection.get_controller_name()}")
        print(f"Heater measurement: {connection.get_value(interface.StageValueType.HEATER1_TEMP)}")
        print(f"Heater set-point before: {connection.get_value(interface.StageValueType.HEATER_SETPOINT)}")

        start = datetime.datetime.now()
        for i, set_temp in enumerate(temp_range):
            
            # main_loop(Vs, temp_range, device, connection)
            
            if not connection.set_value(interface.StageValueType.HEATER_SETPOINT, set_temp):
                raise Exception('Something broke')
            connection.enable_heater(True)

            

            
            
            temperature_thread = threading.Thread(target=temperature_monitor, args=(connection, stop_event, data_queue))
            temperature_thread.start()

            # Create a thread for plotting temperature
            # plot_thread = threading.Thread(target=plot_temperature, args=(data_queue, stop_event))
            # plot_thread.start()
            
            

            ani = FuncAnimation(fig, update_plot, fargs=(data_queue, ax), interval=1000)
            
            print(f"Heater set-point after: {connection.get_value(interface.StageValueType.HEATER_SETPOINT)}")
    
            # for _ in range(10):
            #     print(f"Heater measurement: {connection.get_value(interface.StageValueType.HEATER1_TEMP)}")
            #     time.sleep(1)
            
            # while np.abs(set_temp-connection.get_value(interface.StageValueType.HEATER1_TEMP))>0.1:
            #     time.sleep(1)
            wait_for_temperature_stabilization(connection, set_temp)

                # print(f"Heater measurement: {connection.get_value(interface.StageValueType.HEATER1_TEMP)}")
                
            
            IV_measure(Vs,device,comments = set_temp,plot=True)
            
            
    stop_event.set()
    temperature_thread.join()
    connection.enable_heater(False)
    

plt.show()

'''
"""
# Created on Thu Nov  2 12:42:37 2023

# @author: z5239428
"""

import numpy as np
import matplotlib
matplotlib.use('TkAgg') 

import matplotlib.pyplot as plt
import pandas as pd
import pyvisa as visa
    
import logging
import time

from pylinkam import interface, sdk
import datetime
import threading 
from queue import Queue, Empty
from matplotlib.animation import FuncAnimation

def initialise_SMU(resource_name):
    rm=visa.ResourceManager()
    device=rm.open_resource(resource_name)
    # device.write("*RST")
    print(device.query("*IDN?"))
    return device 

#pick one of the ways of setting voltage points below

Vs = np.arange(-0.5, 0.5, 0.01)  # (start, end, step)
Vs = np.linspace(-0.6, 0.6, 10)  # (start, end, number_of_points)
temp_range = np.arange(25, 30, 1)
temp_range = np.linspace(30, 32, 1)

#pick one of the ways of setting voltage points above

def IV_measure(vs, device, file_name='IV_curve', comments='', save=False, plot=True, ax=None):
    is_values = [None for volt in vs]
    device.write("reset()")
    device.write("smu.source.func = smu.FUNC_DC_VOLTAGE")  # set source to voltage
    device.write("smu.source.ilimit.level = 0.1")  # set current limit (in Amps)
    device.write("smu.source.autorange = smu.ON")  # set voltage range to auto
    device.write("smu.source.autodelay = smu.ON")  # set delay to auto
    device.write("smu.measure.func = smu.FUNC_DC_CURRENT")  # set measurement to current
    device.write("smu.measure.autorange = smu.ON")  # set current range to auto
    device.write("smu.measure.nplc = 1") 
    device.write("smu.measure.sense=smu.SENSE_2WIRE")  # set to 2WIRE or 4WIRE
    if plot:
        if not ax:
            fig, ax = plt.subplots()
            
    for i, volt in enumerate(vs):
        device.write(f"smu.source.level = {volt}")  # Set voltage 
        device.write("smu.source.output = smu.ON")  # SMU output on
        device.write("smu.measure.read()")  # measure current
        device.write("smu.source.output = smu.OFF")  # SMU output off
        is_values[i] = device.query("print(defbuffer1.readings[defbuffer1.endindex])")  # store current reading
        is_values[i] = float(is_values[i])  # .query returns a string, so it must be casted to float number
        if plot:
            ax.clear()
            ax.plot(vs, is_values, label=comments)
            plt.legend()
            plt.pause(0.05)
    
    df = pd.DataFrame({'Voltage (V)': vs, 'Current (A)': is_values})
    
    if save:
        save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S')
        folder = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/'
        total_filename = folder + file_name + '_' + str(comments) + save_datetime + '.csv'
        df.to_csv(total_filename)

    return df

def IV_loop(vs, device, runs, depvars=None, file_name='IV_curve', save=False, plot=False):
    if plot:
        fig, ax = plt.subplots()
    else:
        fig, ax = None, None
    for run in np.arange(runs):
        if not depvars:
            comments = run + 1
        if run == 0:
            input("Press Enter to start first measurement")
        else:
            input("Press Enter to start next measurement")
        
        df = IV_measure(vs, device, comments=comments, save=False, plot=plot, ax=ax)
        print(f'Measurement {run+1} complete')
        if save:
            comments2 = input('If required, enter additional comments to the filename\n')
            save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S')
            folder = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/'
            total_filename = folder + file_name + '_' + str(comments) + '_' + comments2 + save_datetime + '.csv'
            df.to_csv(total_filename)

def temperature_monitor(connection, stop_event, data_queue):
    while not stop_event.is_set():
        dt_now = (datetime.datetime.now() - start).total_seconds()
        temp = connection.get_value(interface.StageValueType.HEATER1_TEMP)
        data_queue.put((dt_now, temp))
        time.sleep(1)

def update_plot(frame, data_queue, ax, ax2):
    try:
        timestamp, temperature, iv_data = data_queue.get_nowait()
        times.append(timestamp)
        temps.append(temperature)
        ax.clear()
        ax.plot(times, temps, 'o-', label='Temperature')
        ax.set_xlabel('Time since start (s)')
        ax.set_ylabel('Temperature (C)')
        ax.legend()

        # Plot IV curve on a different axis
        ax2.clear()
        ax2.plot(iv_data['Voltage (V)'], iv_data['Current (A)'], label='IV Curve')
        ax2.set_xlabel('Voltage (V)')
        ax2.set_ylabel('Current (A)')
        ax2.legend()
        
        plt.pause(0.01)
    except Empty:
        pass

def wait_for_temperature_stabilization(connection, target_temperature, tolerance=0.1, stabilization_duration=60):
    start_time = time.time()
    stable_duration = 0

    while stable_duration < stabilization_duration:
        current_temperature = connection.get_value(interface.StageValueType.HEATER1_TEMP)
        if abs(current_temperature - target_temperature) <= tolerance:
            stable_duration += time.time() - start_time
        else:
            start_time = time.time()
            stable_duration = 0
        time.sleep(1)

def iv_measure_threaded(vs, device, temperature, data_queue):
    is_values = []
    iv_data = IV_measure(vs, device,plot=False)
    data_queue.put((temperature, iv_data))
    is_values.append(iv_data)
    return is_values

def main_loop(vs, set_temperatures, device, connection):
    temperature_thread = None

    try:
        for temperature in set_temperatures:
            if not connection.set_value(interface.StageValueType.HEATER_SETPOINT, temperature):
                raise Exception('Something broke')
            connection.enable_heater(True)
            wait_for_temperature_stabilization(connection, temperature)

            iv_data_queue = Queue()
            iv_thread = threading.Thread(target=iv_measure_threaded, args=(vs, device, temperature, iv_data_queue))
            iv_thread.start()

            # Create a thread for continuous temperature monitoring
            temperature_thread = threading.Thread(target=temperature_monitor, args=(connection, stop_event, data_queue))
            temperature_thread.start()

            # Create a FuncAnimation for updating the plot
            ani = FuncAnimation(fig, update_plot, fargs=(data_queue, ax, ax2), interval=1000)
            plt.show()

            iv_thread.join()

            iv_data = []
            try:
                while True:
                    iv_data.append(iv_data_queue.get_nowait())
            except Empty:
                pass

    finally:
        if temperature_thread:
            stop_event.set()
            temperature_thread.join()
            connection.enable_heater(False)

logging.basicConfig(level=logging.DEBUG)
stop_event = threading.Event()
data_queue = Queue()

rname = "USB0::0x05E6::0x2470::04473418::INSTR"
device = initialise_SMU(rname)

times = []
temps = []

fig, (ax, ax2) = plt.subplots(1, 2)

with sdk.SDKWrapper() as handle:
    with handle.connect() as connection:
        print(f"Name: {connection.get_controller_name()}")
        print(f"Heater measurement: {connection.get_value(interface.StageValueType.HEATER1_TEMP)}")
        print(f"Heater set-point before: {connection.get_value(interface.StageValueType.HEATER_SETPOINT)}")

        start = datetime.datetime.now()

        main_loop(Vs, temp_range, device, connection)


'''














