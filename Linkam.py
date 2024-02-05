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
import matplotlib as mat
# mat.use("TkAgg")

def initialise_SMU(resource_name):
    rm=visa.ResourceManager()
    device=rm.open_resource(resource_name)
    # device.write("*RST")
    print(device.query("*IDN?"))
    return device 



def update_IV_plot(frame, ax, Vs,Is,comments):
    ax.clear()
    ax.plot(Vs,Is,label=comments)
    plt.legend()
    plt.pause(0.05)
        

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
    if not ax:
        fig, ax = plt.subplots()
    ax.set_xlabel(source_label)
    ax.set_ylabel(measure_label)
    for i, source_value in enumerate(source_values):
        device.write("smu.source.level = "+str(source_value)) # Set voltage 
        device.write("smu.source.output = smu.ON") # SMU output on
        device.write("smu.measure.read()") # measure current
        # device.write("smu.source.output = smu.OFF") # SMU output off
        measure_values[i] = device.query("print(defbuffer1.readings[defbuffer1.endindex])") # store current reading
    
        measure_values[i] = float(measure_values[i]) # .query returns a string, so it must be casted to float number
        ax.clear()
        ax.plot(source_values,measure_values,label=comments)
        plt.legend()
        plt.pause(0.01)
        
        
        # aniV = FuncAnimation(fig, update_IV_plot, fargs=(ax, Vs,Is,comments), interval=1000)
        
    df = pd.DataFrame({source_label: source_values, measure_label: measure_values})
    if save:
        # file_name = 'IV_curve' #set filename as desired              
        save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S') #get current date and time
        
        # folder  = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/'
        total_filename = folder+file_name+'_'+str(comments)+save_datetime+'.csv'
        df.to_csv(total_filename)

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
        # print('monitoring temp function activATED!')
        dt_now = (datetime.datetime.now() - start).total_seconds()
        temp = connection.get_value(interface.StageValueType.HEATER1_TEMP)
        data_queue.put((dt_now, temp))
        # plt.pause(0.01)
        time.sleep(1)
def update_plot(frame, data_queue, ax):
    try:
        # print('UPDATEING PLOT!')
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
        # print('THE EMPYTINES OF LIFE')
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
ani = FuncAnimation(fig, update_plot, fargs=(data_queue, ax), interval=10)
if __name__ == "__main__":
    #pick one of the ways of setting voltage points below
# FOR Voltage controlled use the following
    # Vs = np.arange(-0.5,0.5,0.01) # (start, end, step)
    # Vs = np.linspace(-0.6,0.6,10) # (start, end, number_of_points)
    # source_values = np.arange(-0.5,0.5,0.01) # (start, end, step)
    # source_values_1 = np.arange(0,3.2,0.05) # (start, end, number_of_points)
    # source_values_2 = np.arange(3.2,0,-0.05)
    # source_values = np.append(source_values_1,source_values_2)
    
# FOR Current controlled use the following
    source_values_1 = np.arange(0,0.005,0.0001)
    source_values_2 = np.arange(0.005,0,-0.0001)
    source_values = np.append(source_values_1,source_values_2)
    # Vs=source_values
    #pick one of the ways of setting temperature points below

    temp_range = np.arange(25,27,1)
    # temp_range = np.linspace(30,45,5)
    folder='C:/Data/NbOx/Nb 20 nm/' 
    file_name='20nm Nb_20um_d9_2_test_50 Ohm' 
    save=True
    
    ilimit=0.005 
    sourcevolt=False
    fourwire=False
    stabilization_duration = 120
    tolerance=0.05
    with sdk.SDKWrapper() as handle:
        with handle.connect() as connection:
            print(f"Name: {connection.get_controller_name()}") # get and print name of temperature controller
            print(f"Heater measurement: {connection.get_value(interface.StageValueType.HEATER1_TEMP)}") # get heater measurement
            print(f"Heater set-point before: {connection.get_value(interface.StageValueType.HEATER_SETPOINT)}") # get temperature set point
    
            start = datetime.datetime.now() # get starting time
            for i, set_temp in enumerate(temp_range):
                
                # main_loop(Vs, temp_range, device, connection)
                
                if not connection.set_value(interface.StageValueType.HEATER_SETPOINT, set_temp): # try setting temperature
                    raise Exception('Something broke') # raise error if setting temperature doesn't work
                connection.enable_heater(True) # enable heater
    
                
    
                
                # start a thread of contrinuous temperature monitoring
                temperature_thread = threading.Thread(target=temperature_monitor, args=(connection, stop_event, data_queue))
                temperature_thread.start()
    
                # Create a thread for plotting temperature
                # plot_thread = threading.Thread(target=plot_temperature, args=(data_queue, stop_event))
                # plot_thread.start()
                
                

                
                plt.pause(0.01)
                # print heater setpoint after having enabled heater
                print(f"Heater set-point after: {connection.get_value(interface.StageValueType.HEATER_SETPOINT)}")
        
                start_time = time.time()
                stable_duration = 0 # initialise the variable 

                # wait for temperature stabilisation
                while stable_duration < stabilization_duration:
                    plt.pause(0.01) # pause is important as it allows animations to update

                    current_temperature = connection.get_value(interface.StageValueType.HEATER1_TEMP)
                    
                    # Check if the current temperature is within the tolerance range around the target temperature
                    if abs(current_temperature - set_temp) <= tolerance:
                        stable_duration += time.time() - start_time
                    else:
                        # Reset the start time if the temperature goes outside the tolerance range
                        start_time = time.time()
                        stable_duration = 0
    
                    # Adjust the sleep interval based on your system's characteristics
                    time.sleep(1) # not sure this sleep time is needed. 
    
                    # print(f"Heater measurement: {connection.get_value(interface.StageValueType.HEATER1_TEMP)}")
                    
                plt.pause(0.01)
                # temperature is stable, so trigger IV measurement
                IV_measure(source_values,device,file_name=file_name,plot=True,save=save,
                        folder=folder,ilimit=ilimit,sourcevolt=sourcevolt,
                        fourwire=fourwire,comments=set_temp+'C')
                time.sleep(1)
                
                # keep inquiring device status and wait until IV measurement is done
                device.write("*OPC?")
                try:

                    status = float(device.read())

                except:
                    print('except')
                    status=0
                while status != 1:
                    print('Still measuring IV - hold your horses!')
                    time.sleep(1)
                    device.write("*OPC?")
                    status = float(device.read())
                plt.pause(0.01)
                
                
        # join threads and disable heater once measurements are done     
        stop_event.set()
        temperature_thread.join()
        connection.enable_heater(False)
        
    
    plt.show()
    if ani is not None:
        ani.event_source.stop()
    #     plt.close()




