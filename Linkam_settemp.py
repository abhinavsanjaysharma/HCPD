# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 16:12:08 2024

@author: Lab User
"""

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
def temperature_monitor(connection, start, stop_event, data_queue):
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
if __name__ == "__main__":
    times = []
    temps = []
    fig, ax = plt.subplots()
    stop_event = threading.Event()
    data_queue = Queue()
    ani = FuncAnimation(fig, update_plot, fargs=(data_queue, ax), interval=10)
    
    
    temp_range=[30]
    
    # temp_range = np.arange(30,35,2)
    stabilization_duration = 30
    tolerance=0.05
    stay_duration = 10
    
    logging.basicConfig(level=logging.DEBUG)

    
    with sdk.SDKWrapper() as handle:
        with handle.connect() as connection:
            print(f"Name: {connection.get_controller_name()}")
            print(f"Heater measurement: {connection.get_value(interface.StageValueType.HEATER1_TEMP)}")
            print(f"Heater set-point before: {connection.get_value(interface.StageValueType.HEATER_SETPOINT)}")
    

                
                # main_loop(Vs, temp_range, device, connection)
            start = datetime.datetime.now()  
            
            temperature_thread = threading.Thread(target=temperature_monitor, args=(connection,start, stop_event, data_queue))
            temperature_thread.start()
            for i, set_temp in enumerate(temp_range):
                if not connection.set_value(interface.StageValueType.HEATER_SETPOINT, set_temp):
                    raise Exception('Something broke')
                connection.enable_heater(True)

        
                plt.pause(0.01)
                # print('moving on!')
                print(f"Heater set-point after: {connection.get_value(interface.StageValueType.HEATER_SETPOINT)}")       
                start_time = time.time()
                stable_duration = 0
            
                # print('about to while')
                while stable_duration < stabilization_duration:
                    plt.pause(0.01)
                    # print(stable_duration)
                    current_temperature = connection.get_value(interface.StageValueType.HEATER1_TEMP)
                    
                    # Check if the current temperature is within the tolerance range around the target temperature
                    if abs(current_temperature - set_temp) <= tolerance:
                        stable_duration += time.time() - start_time
                    else:
                        # Reset the start time if the temperature goes outside the tolerance range
                        start_time = time.time()
                        stable_duration = 0
        
                # Adjust the sleep interval based on your system's characteristics
                plt.pause(stay_duration)
            stop_event.set()
            temperature_thread.join()
            connection.enable_heater(False)