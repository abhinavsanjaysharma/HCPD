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

def create_function_button(frame, text, command):
    button = ttk.Button(frame, text=text, command=command)
    return button

def display_device_name(frame, device_name):
    label = ttk.Label(frame, text=f"Device Name: {device_name}")
    label.grid(column=0, row=1)

#pick one of the ways of setting voltage points below

Vs = np.arange(-0.5,0.5,0.01) # (start, end, step)
Vs = np.linspace(-0.6,0.6,10) # (start, end, number_of_points)

#pick one of the ways of setting voltage points above

def IV_measure(source_values,device,file_name='IV_curve',comments='',save=False,plot=True,ax=None,fig=None,gui=False,fourwire=False,sourcevolt=True,source_limit=0.1):
        
    measure_values = [None for value in source_values]
    device.write("reset()")
    # print('setting according to voltage or current source')
    if sourcevolt:
        print('Voltage source mode')
        # Configuration for measuring current
        source_func = "smu.FUNC_DC_VOLTAGE"
        measure_func = "smu.FUNC_DC_CURRENT"
        measure_label = 'Current (A)'
        source_label = 'Voltage (V)'
        device.write(f"smu.source.func = {source_func}")
        device.write(f"smu.measure.func = {measure_func}")  # set measurement function
        device.write(f"smu.source.ilimit.level = {source_limit}")  # set current limit (in Amps)
        # device.write("smu.source.ilimit.level = 0.1")  # set current limit (in Amps)
        
    else:
        print('Current source mode')
        # Configuration for measuring voltage
        source_func = "smu.FUNC_DC_CURRENT"
        measure_func = "smu.FUNC_DC_VOLTAGE"
        measure_label = 'Voltage (V)'
        source_label = 'Current (A)'
        device.write(f"smu.source.func = {source_func}")
        device.write(f"smu.measure.func = {measure_func}")  # set measurement function
        device.write(f"smu.source.vlimit.level = {source_limit}")  
        
    # print('rest of the commands')
      # set source function
    
    device.write("smu.source.autorange = smu.ON")  # set voltage/current range to auto
    device.write("smu.source.autodelay = smu.ON")  # set delay to auto
    
    device.write("smu.measure.autorange = smu.ON")  # set current/voltage range to auto
    device.write("smu.measure.nplc = 0.01")   
    if fourwire: # set to 2WIRE or 4WIRE
        device.write("smu.measure.sense=smu.SENSE_4WIRE") 
    else:
        
        device.write("smu.measure.sense=smu.SENSE_2WIRE") 
    # print('moving to plot')
    if plot:
        if not ax:
            fig, ax = plt.subplots(figsize=(1.5, 1))
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
            # print('measure values frame')
            # print(measure_values[frame])
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
        
        
        

    # print('Measured values')    
    # print(measure_values)
    df = pd.DataFrame({source_label: source_values, measure_label: measure_values}) # turn data into a pandas dataframe with voltage and current columns
    print('Final measured data')
    print(df)
    
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
    
    
        
        

    return df,animation

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

def IT_loop(device, set_V,duration,nplc=1,gui=False,ilimit=0.1):
    device.write("reset()")
    device.write("smu.source.func = smu.FUNC_DC_VOLTAGE") # set source to voltage
    device.write(f"smu.source.ilimit.level = {ilimit}") # set current limit (in Amps)
    device.write("smu.source.autorange = smu.ON") # set voltage range to auto
    device.write("smu.source.autodelay = smu.ON") # set delay                                                                                                                                                                                                                to auto
    device.write("smu.measure.func = smu.FUNC_DC_CURRENT") # set measurement to current
    device.write("smu.measure.autorange = smu.ON") # set current range to auto
    # device.write("smu.measure.nplc = 1") 
    device.write("smu.measure.sense=smu.SENSE_2WIRE") # set to 2WIRE or 4WIRE
    device.write("smu.source.level = "+str(set_V)) # Set voltage 
    device.write("smu.source.output = smu.ON") # SMU output on
    device.write("smu.source.delay = 0")
    device.write("smu.measure.nplc = "+str(nplc))
    # start = datetime.datetime.now()
    Is, times = [], []
    time = 0
    fig,ax = plt.subplots()

    while time <= duration:
        device.write("smu.measure.read()") # measure current
        # time = (datetime.datetime.now()-start).total_seconds()
        # print(f'time:{time}')
        # times.append(time)
        try:
            Vs.append(float(device.query("print(defbuffer1.sourcevalues[defbuffer1.endindex]")))
            Is.append(float(device.query("print(defbuffer1.readings[defbuffer1.endindex])"))) # store current reading
            times.append(float(device.query("print(defbuffer1.relativetimestamps[defbuffer1.endindex])")))
        except:
            continue
        time = times[-1]
        # print(f'Is:{Is}')
        ax.clear()
        ax.set_ylabel('Current (A)')
        ax.set_xlabel('Time (s)')
        ax.plot(times,Is)
        # plt.legend()
        plt.pause(0.05)
        # if gui:
        #     # fig, ax = plt.subplots()
        #     # ax.plot(V, I, label='I-t plot')
        #     # ax.set_ylabel('Current (A)')
        #     # ax.set_xlabel('Time(s)')
        #     # ax.legend()

        #     # Embed the plot in the Tkinter window
        #     canvas = FigureCanvasTkAgg(fig, master=frm)
        #     canvas_widget = canvas.get_tk_widget()
        #     canvas_widget.grid(column=0, row=6, columnspan=4)
            
    
    device.write("smu.source.output = smu.OFF") # SMU output off
    df = pd.DataFrame({'Time(s)': times, 'Voltage (V)': Vs, 'Current (A)': Is})
    save = save_var.get()

    if save:
        # print('in the save')
        save_data(df,comments='It')
    return times, Is       
def pulse_train(device,biaslevel=0,pulselevel=0.5,biaswidth=0.5,pulsewidth=0.5,points=10,limit=2.1,points_per_pulse = 5):
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
    save = save_var.get()

    if save:
        # print('in the save')
        save_data(df,comments='pulse_train')
         
def clear_measurement_widgets(measurement_frame):
    # Destroy existing widgets to clear the layout
    for widget in measurement_frame.winfo_children():
        widget.destroy()
def show_iv_widgets(measurement_frame,device):
    # Create and display labels and entry widgets for I-V measurement
    vs_type_label = ttk.Label(measurement_frame, text="Source range:")
    vs_type_label.grid(column=0, row=0)
    vs_type_var = StringVar()  # Define vs_type_var here
    vs_type_var.set("linspace")  # Default value
    vs_type_options = ["linspace", "logspace", "arange"]
    vs_type_menu = OptionMenu(measurement_frame, vs_type_var, *vs_type_options)
    vs_type_menu.grid(column=1, row=0)
    # Start
    start_label = ttk.Label(measurement_frame, text="Start:")
    start_label.grid(column=2, row=0)
    start_var = StringVar()
    start_var.set('-1') # Default value
    start_entry = ttk.Entry(measurement_frame, textvariable=start_var)
    start_entry.grid(column=3, row=0)
    
    # Stop
    stop_label = ttk.Label(measurement_frame, text="Stop:")
    stop_label.grid(column=0, row=1)
    stop_var = StringVar()
    stop_var.set('1') # Default value
    stop_entry = ttk.Entry(measurement_frame, textvariable=stop_var)
    stop_entry.grid(column=1, row=1)
    
    # Num/Step
    num_label = ttk.Label(measurement_frame, text="Num/Step:")
    num_label.grid(column=2, row=1)
    num_var = StringVar()
    num_var.set('10') # Default value
    num_entry = ttk.Entry(measurement_frame, textvariable=num_var)
    num_entry.grid(column=3, row=1)
    
    lim_label = ttk.Label(measurement_frame, text="Measure var limit")
    lim_label.grid(column=4, row=1)
    lim_var = StringVar()
    lim_var.set('0.1') # Default value
    lim_entry = ttk.Entry(measurement_frame, textvariable=lim_var)
    lim_entry.grid(column=5, row=1)
    
    # Sensing type (2 or 4 wire)
    # fourwire_label = ttk.Label(measurement_frame, text="Four Wire:")
    fourwire_var = BooleanVar()
    fourwire_menu = ttk.Checkbutton(measurement_frame, text="4-Wire", variable=fourwire_var)
    fourwire_menu.grid(column=0, row=2)
    fourwire_var.set(False)  # Default value is False (2-wire sensing)
    # fourwire_options = ["2-Wire", "4-Wire"]
    # fourwire_menu = OptionMenu(measurement_frame, fourwire_var, *fourwire_options)
    # fourwire_menu.grid(column=1, row=2)
    # Source type (Voltage or Current)
    # source_label = ttk.Label(measurement_frame, text="Source Type:")
    # source_label.grid(column=2, row=2)
    sourcevolt_var = BooleanVar()
    sourcevolt_var.set(True)  # Default value is True (sourcing voltage)
    sourcevolt_menu = ttk.Checkbutton(measurement_frame, text="Voltage sourcing \n Current source if unchecked", variable=sourcevolt_var)
    sourcevolt_menu.grid(column=3, row=2)
    
    #Loop count (number of IV curves)
    loop_count_label = ttk.Label(measurement_frame, text="Loop Count:")
    loop_count_label.grid(column=1, row=3)
    loop_count_var = StringVar(value="1")  # Default value is 1
    loop_count_entry = ttk.Entry(measurement_frame, textvariable=loop_count_var)
    loop_count_entry.grid(column=2, row=3)
    # Measure IV Button
    measure_button = ttk.Button(measurement_frame, text="Measure IV", command=lambda: iv_function(device, vs_type_var, start_var, stop_var, num_var,loop_count_var,fourwire_var,sourcevolt_var,lim_var))
    measure_button.grid(column=0, row=4, columnspan=4, pady=5)
    

    # Add more labels and entry widgets as needed for I-V

def show_it_widgets(measurement_frame,device):
    # Create and display labels and entry widgets for I-t measurement
    # label = ttk.Label(measurement_frame, text="Time Duration:")
    # label.grid(column=0, row=0)
    # entry = ttk.Entry(measurement_frame)
    # entry.grid(column=1, row=0)
    # it_frame = ttk.Frame(frm)
    # it_frame.grid(column=3, row=5, columnspan=4, pady=10)
    # Duration
    duration_label = ttk.Label(measurement_frame, text="Duration (s):")
    duration_label.grid(column=4, row=0)
    duration_var = StringVar()
    duration_var.set('30')
    duration_entry = ttk.Entry(measurement_frame, textvariable=duration_var)
    duration_entry.grid(column=5, row=0)
    
    # Bias
    bias_label = ttk.Label(measurement_frame, text="Bias (V):")
    bias_label.grid(column=4, row=1)
    bias_var = StringVar()
    bias_var.set('1')
    bias_entry = ttk.Entry(measurement_frame, textvariable=bias_var)
    bias_entry.grid(column=5, row=1)
    
    lim_label = ttk.Label(measurement_frame, text="Current limit (A)")
    lim_label.grid(column=4, row=2)
    lim_var = StringVar()
    lim_var.set('0.1') # Default value
    lim_entry = ttk.Entry(measurement_frame, textvariable=lim_var)
    lim_entry.grid(column=5, row=2)
    
    nplc_label = ttk.Label(measurement_frame, text="NPLC")
    nplc_label.grid(column=4, row=3)
    nplc_var = StringVar()
    nplc_var.set('1') # Default value
    nplc_entry = ttk.Entry(measurement_frame, textvariable=nplc_var)
    nplc_entry.grid(column=5, row=3)
    
    measure_button_IT = ttk.Button(measurement_frame, text="Measure I-t", command=lambda: IT_loop(device, float(bias_var.get()), float(duration_var.get()),gui=True,
                                                                                                  ilimit=float(lim_var.get()),nplc=float(nplc_var.get()) ))
    measure_button_IT.grid(column=4, row=4, columnspan=4, pady=5)


def show_pulse_train_widgets(measurement_frame,device):
    
    # Create and display labels and entry widgets for Pulse Train
    
    # Button select bottom level of pulse
    biaslevel_label = ttk.Label(measurement_frame, text="Bottom Level (V):")
    biaslevel_label.grid(column=0, row=0)
    biaslevel_var = StringVar()
    biaslevel_var.set('0')
    biaslevel_entry = ttk.Entry(measurement_frame, textvariable=biaslevel_var)
    biaslevel_entry.grid(column=1, row=0)

    # Section for 'pulselevel'
    pulselevel_label = ttk.Label(measurement_frame, text="Top Level (V):")
    pulselevel_label.grid(column=0, row=1)
    pulselevel_var = StringVar()
    pulselevel_var.set('1')
    pulselevel_entry = ttk.Entry(measurement_frame, textvariable=pulselevel_var)
    pulselevel_entry.grid(column=1, row=1)

    # Section for 'biaswidth'
    biaswidth_label = ttk.Label(measurement_frame, text="Bottom time (s):")
    biaswidth_label.grid(column=2, row=0)
    biaswidth_var = StringVar()
    biaswidth_var.set('0.5')
    biaswidth_entry = ttk.Entry(measurement_frame, textvariable=biaswidth_var)
    biaswidth_entry.grid(column=3, row=0)

    # Section for 'pulsewidth'
    pulsewidth_label = ttk.Label(measurement_frame, text="Top time (s):")
    pulsewidth_label.grid(column=2, row=1)
    pulsewidth_var = StringVar()
    pulsewidth_var.set('0.5')
    pulsewidth_entry = ttk.Entry(measurement_frame, textvariable=pulsewidth_var)
    pulsewidth_entry.grid(column=3, row=1)

    # Section for 'points'
    points_label = ttk.Label(measurement_frame, text="Number of pulses:")
    points_label.grid(column=0, row=2)
    points_var = StringVar()
    points_var.set('10')
    points_entry = ttk.Entry(measurement_frame, textvariable=points_var)
    points_entry.grid(column=1, row=2)
    

    pulse_train_button = create_function_button(measurement_frame, "Apply Pulse Train", 
                                                command=lambda: pulse_train(device,float(biaslevel_var.get()),float(pulselevel_var.get()),float(biaswidth_var.get()),float(pulsewidth_var.get()),float(points_var.get())))
    pulse_train_button.grid(column=3, row=2)
def on_measurement_option_change(measurement_option,measurement_frame,device):
    selected_option = measurement_option.get()

    # Clear existing widgets
    clear_measurement_widgets(measurement_frame)

    # Display relevant widgets based on the selected option
    if selected_option == "I-V":
        show_iv_widgets(measurement_frame,device)
    elif selected_option == "I-t":
        show_it_widgets(measurement_frame,device)
    elif selected_option == "Pulse Train":
        show_pulse_train_widgets(measurement_frame,device)        
def on_initialise(resource_name):
    device, device_name = initialise_SMU(resource_name)
    display_device_name(frm, device_name)
    # vs_frame = ttk.Frame(frm)
    # vs_frame.grid(column=0, row=5, columnspan=4, pady=10)
    
    measurement_option = tk.StringVar()
    measurement_option.set("I-V")  # Default option
    measurement_label = ttk.Label(root, text="Select Measurement:")
    measurement_label.grid(column=0, row=0)
    
    measurement_options = ttk.Combobox(root, textvariable=measurement_option, values=["I-V", "I-t", "Pulse Train"])
    measurement_options.grid(column=1, row=0)
    measurement_frame = ttk.Frame(root)
    measurement_frame.grid(column=0, row=1, columnspan=2)
    measurement_options.bind("<<ComboboxSelected>>", lambda event: on_measurement_option_change(measurement_option, measurement_frame,device))
   
   
def save_data(df,comments=None):
    # print('saving!')
    folder = directory_var.get()
    file_name=file_var.get()
    save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S') #get current date and time
    
    # folder  = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/'
    total_filename = folder+'/'+file_name+'_'+str(comments)+save_datetime+'.csv'
    df.to_csv(total_filename)
          
def iv_function(device, vs_type_var, start_var, stop_var, num_var, loop_count_var,fourwire_var,sourcevolt_var,lim_var):
    Vs_type = vs_type_var.get()
    start = float(start_var.get())
    stop = float(stop_var.get())
    num = float(num_var.get())
    loop_count = float(loop_count_var.get())
    four_wire = fourwire_var.get()
    source_volt=sourcevolt_var.get()
    lim = lim_var.get()
    
    
    # Generate Vs based on the selected type
    if Vs_type == "linspace":
        Vs = np.linspace(start, stop, int(num))
    elif Vs_type == "logspace":
        Vs = np.logspace(start, stop, int(num))
    elif Vs_type == "arange":
        Vs = np.arange(start, stop, num)
    fig, ax = plt.subplots()
    save = save_var.get()
    # folder = directory_var.get()
    # file_name=file_var.get()
    for i in np.arange(loop_count):
        df,animation = IV_measure(Vs,device,plot=True,gui=True,comments=i,fig=fig,ax=ax,fourwire=four_wire,sourcevolt=source_volt,source_limit=lim)
        plt.pause(0.01)
        # V, I = df['Voltage (V)'],df['Current (A)']
        if save:
            # print('in the save')
            save_data(df,comments=f'IV_{i}')
            # file_name = 'IV_curve' #set filename as desired              
            # save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S') #get current date and time
            
            # folder  = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/'
            # total_filename = folder+'/'+file_name+'_'+str(i)+save_datetime+'.csv'
            # df.to_csv(total_filename)
        
        # ax.plot(V, I, label=str(i))
        # ax.set_xlabel('Voltage (V)')
        # ax.set_ylabel('Current (A)')
        # ax.legend(title='IV curve')

    # Embed the plot in the Tkinter window
    # canvas = FigureCanvasTkAgg(fig, master=frm)
    # canvas_widget = canvas.get_tk_widget()
    # canvas_widget.grid(column=0, row=6, columnspan=4)
    
def select_directory():
    directory_path = filedialog.askdirectory()
    directory_var.set(directory_path)
def toggle_save():
    save_var.set(not save_var.get())
    
if __name__ == "__main__":
    
    rname = "USB0::0x05E6::0x2470::04473418::INSTR"
    # sys.exit()
    print('Welcome to the Keithley 2470 control software')
    
    root = Tk()
    root.title("Keithley 2470 SMU controller")
    directory_var = tk.StringVar()
    c_dir = os.getcwd()
    directory_label = tk.Label(root, text="Selected Directory:")
    directory_label.grid(row=3, column=1, padx=5, pady=5)
    
    directory_entry = tk.Entry(root, textvariable=directory_var, state="readonly", width=30)
    directory_entry.grid(row=3, column=2, padx=5, pady=5)
    # directory_var.set(c_dir)
    directory_var.set('C:/Data/')
    
    file_var = StringVar()
    file_label = Label(root, text="File Name:")
    file_label.grid(column=2, row=4, padx=10, pady=10)
    
    file_entry = Entry(root, textvariable=file_var)
    file_entry.grid(column=2, row=5, padx=10, pady=10)
    
    select_button = tk.Button(root, text="Select Directory", command=select_directory)
    select_button.grid(row=2, column=1, columnspan=2, pady=10)
    save_var = tk.BooleanVar()

    save_checkbutton = tk.Checkbutton(root, text="Save Data", variable=save_var)
    save_checkbutton.grid(row=4, column=1, padx=10, pady=10)
    
    frm = ttk.Frame(root, padding=10)
    frm.grid()

    ttk.Label(frm, text="Keithley 2470 SMU controller").grid(column=0, row=0)
    
    # Entry widget for the default argument
    default_arg_label = ttk.Label(frm, text="Instrument resource name")
    default_arg_label.grid(column=0, row=1)
    default_arg_var = tk.StringVar()
    default_arg_entry = ttk.Entry(frm, textvariable=default_arg_var)
    default_arg_entry.grid(column=1, row=1)
    default_arg_var.set(rname)  # Set your default argument here
    
    # Button to initialise SMU with the entry value
    initialise_button = ttk.Button(frm, text="Initialise SMU", command=lambda: on_initialise(default_arg_var.get()))
    initialise_button.grid(column=2, row=1)
 
    # Quit button
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=3, row=0)
    
    root.mainloop()
    '''
    device,device_name= initialise_SMU(rname)        
    device.timeout = 100000
    # IV_loop(Vs,device,1,file_name='IV_JD_ICL10b',plot=True,save=False)
    # IT_loop(device, 1,20,nplc=1)
    source_values_1 = np.arange(0,0.002,0.0001)
    source_values_2 = np.arange(0.002,0,-0.0001)
    source_values = np.append(source_values_1,source_values_2)
    # source_values = np.arange(0,6,0.1)
    IV_measure(source_values,device,file_name='IV_curve',comments='',save=False,plot=True,ax=None,fig=None,gui=False,fourwire=False,sourcevolt=True)
    
    
    pulse_train(device,biaslevel=0,pulselevel=3,biaswidth=0.1,pulsewidth=0.1,points=50,limit=2.1)
    
    time.sleep(1)
    device.write("*OPC?")
    try:
        print('try')
        status = float(device.read())
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
    # print('df')
    # print(df)
    

    # file_name = 'IV_curve' #set filename as desired              
    save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S') #get current date and time
    file_name = 'Test_pulse'    
    folder  = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/'
    folder = 'C:/Data/'
    comments=None
    total_filename = folder+file_name+'_'+str(comments)+save_datetime+'.csv'
    df.to_csv(total_filename)
''' 
    
    
    
    



          