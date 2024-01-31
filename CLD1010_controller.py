
"""
Created on Fri Jan 19 16:55:59 2024

@author: Lab User
"""

import pyvisa as visa
import time
import numpy as np
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox

#Opens a resource manager and shows the available VISA devices.
rm = visa.ResourceManager()
rm.list_resources()
rname = 'USB0::0x1313::0x804F::M00940866::INSTR'

'''
instr = rm.open_resource(rname)

#Returns the identification of the device.
#The command instr.query can be used when you want to get data from the device.

print("Used device:", instr.query("*IDN?"))
instr.write("output2:state on")

set_temp = 25
temp=0
set_current = 0.20
instr.write("source2:temperature:spoint:def 25")

print()

while np.abs(set_temp-float(instr.query("sense2:temperature:data?"))) >0.1:
    time.sleep(1)
    
instr.write(f"source1:current:level:amplitude {set_current}")


print("Set LD current [A]:", instr.query("source1:current:level:amplitude?"))
#duration of laser on in the following line in sec
time.sleep(30)
instr.write("output1:state off")
instr.write("output2:state off")

#These lines will close the resource manager and the handle to the device.
instr.close()
rm.close()
'''
def update_status_labels(ldc_device, status_label, current_label,tec_status_label):
    if ldc_device is not None:
        try:
            # Read the LD current from the device
            ld_current = float(ldc_device.query("source1:current:level:amplitude?"))
            # Update the current label
            current_label.config(text=f"LD Current setpoint: {ld_current} A")

            # Check if LD laser output is on
            laser_output_state = ldc_device.query("output1:state?")
            print(laser_output_state)
            if float(laser_output_state):
                print('on!')
                status_label.config(text="LD Laser Output: ON", foreground="green")
            else:
                print('off!')
                status_label.config(text="LD Laser Output: OFF", foreground="red")

            # Check if TEC is on
            tec_state = ldc_device.query("output2:state?")
            if float(tec_state):
                print('on!')
                tec_status_label.config(text="TEC: ON", foreground="green")
            else:
                print('off!')
                tec_status_label.config(text="TEC: OFF", foreground="red")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def initialise_LDC(resource_name="USB0::0x1313::0x804F::M00940866::INSTR"):
    rm=visa.ResourceManager()
    device=rm.open_resource(resource_name)
    device.write("*RST")
    device_name = device.query("*IDN?")
    return device, device_name

def laser_on(device=None):
    if device is None:
        device, device_name = initialise_LDC()

    device.write("output1:state on")

def laser_off(device=None):
    if device is None:
        device, device_name = initialise_LDC()

    device.write("output1:state off")

def TEC_on(device=None):
    if device is None:
        device, device_name = initialise_LDC()

    device.write("output2:state on")
    
def TEC_off(device=None):
    if device is None:
        device, device_name = initialise_LDC()

    device.write("output2:state off")
    
def toggle_ld(device=None, ld_status_var=None,ld_status_label=None):
    if device is None:
        device, device_name = initialise_LDC()

    ld_status = ld_status_var.get()

    if ld_status == "OFF":
        device.write("output1:state on")
        ld_status_var.set("ON")
        ld_status_label.config(text="LD Laser Output: ON", foreground="green")
    else:
        device.write("output1:state off")
        ld_status_var.set("OFF")
        ld_status_label.config(text="LD Laser Output: OFF", foreground="red")
    
        

def toggle_tec(device=None, tec_status_var=None,tec_status_label=None):
    if device is None:
        device, device_name = initialise_LDC()

    tec_status = tec_status_var.get()

    if tec_status == "OFF":
        print('tec on')
        device.write("output2:state on")
        tec_status_var.set("ON")
        tec_status_label.config(text="TEC: ON", foreground="green")
        
    else:
        print('tec off')
        device.write("output2:state off")
        tec_status_var.set("OFF")
        tec_status_label.config(text="TEC: OFF", foreground="red")
    
def get_ld_current(device=None):
    if device is None:
        device, device_name = initialise_LDC()
    return float(device.query("source1:current:level:amplitude?"))

# Function to set LD current
def set_ld_current(device=None, current=0.20):
    if device is None:
        device, device_name = initialise_LDC()
    device.write(f"source1:current:level:amplitude {current}")
    
def set_ld_current_limit(device=None, current=0.20):
    if device is None:
        device, device_name = initialise_LDC()
    device.write(f"source1:current:limit:amplitude {current}")
def get_ld_current_limit(device=None):
    if device is None:
        device, device_name = initialise_LDC()
    return float(device.query("source1:current:limit:amplitude?"))

# Function to get TEC temperature
def get_tec_temperature(device=None):
    if device is None:
        device, device_name = initialise_LDC()
    return float(device.query("sense2:temperature:data?"))

def get_tec_setpoint(device=None):
    if device is None:
        device, device_name = initialise_LDC()
    return float(device.query("source2:temperature:spoint?"))


# Function to set TEC temperature
def set_tec_temperature(device=None, temperature=25):
    if device is None:
        device, device_name = initialise_LDC()
    device.write(f"source2:temperature:spoint:def {temperature}")
    print(f'setting to {temperature}')


def update_ld_tec_labels(ldc_device, ld_current_label, tec_temp_label,tec_setpoint_label,ld_limit_label):
    ld_current = get_ld_current(ldc_device)
    tec_temp = get_tec_temperature(ldc_device)
    tec_setpoint = get_tec_setpoint(ldc_device)
    ld_limit = get_ld_current_limit(ldc_device)
    ld_current_label.config(text=f"LD Current Setpoint: {ld_current} A")
    tec_temp_label.config(text=f"TEC Temperature: {tec_temp} °C")
    tec_setpoint_label.config(text=f"TEC Setpoint: {tec_setpoint} °C")
    ld_limit_label.config(text=f"LD Current Limit: {ld_limit} A")
    return ld_current, tec_temp
def continuous_update(ld_current_label, tec_temp_label,tec_setpoint_label,ld_limit_label):
    ld_current, tec_temp = update_ld_tec_labels(ldc_device, ld_current_label, tec_temp_label,tec_setpoint_label,ld_limit_label)
    root.after(100, continuous_update, ld_current_label, tec_temp_label, tec_setpoint_label,ld_limit_label)
def on_initialise(instr_name):
    global ldc_device
    ldc_device, device_name = initialise_LDC(instr_name)

    ld_current_label = ttk.Label(frm, text="")
    ld_current_label.grid(column=0, row=5, columnspan=2)
    
    ld_limit_label = ttk.Label(frm, text="")
    ld_limit_label.grid(column=2, row=5, columnspan=2)


    tec_temp_label = ttk.Label(frm, text="")
    tec_temp_label.grid(column=0, row=6, columnspan=2)
    
    tec_setpoint_label = ttk.Label(frm, text="")
    tec_setpoint_label.grid(column=2, row=6, columnspan=2)

    update_ld_tec_labels(ldc_device, ld_current_label, tec_temp_label,tec_setpoint_label,ld_limit_label)
    ld_status_var = tk.StringVar()
    tec_status_var = tk.StringVar()
    # update_status_labels(ldc_device, laser_status_label, current_ld_label)
    ld_status_var.set("OFF")
    tec_status_var.set("OFF")
    # messagebox.showinfo("Initialization", f"LD Controller initialized. Device: {device_name}")

    
    instr_name_label = ttk.Label(frm, text="Instrument resource name")
    instr_name_label.grid(column=0, row=1)
    
    instr_name_var = tk.StringVar()
    instr_name_entry = ttk.Entry(frm, textvariable=instr_name_var)
    instr_name_entry.grid(column=1, row=1)
    instr_name_var.set("USB0::0x1313::0x804F::M00940866::INSTR")

    
    # Labels to display LD and TEC status
    ld_status_label = ttk.Label(frm, text="LD Laser Output: OFF", foreground="red")
    ld_status_label.grid(column=0, row=3, columnspan=2)
    
    tec_status_label = ttk.Label(frm, text="TEC: OFF", foreground="red")
    tec_status_label.grid(column=0, row=4, columnspan=2)
    

    # Button to toggle LD laser output
    toggle_ld_button = ttk.Button(frm, text="Toggle LD", command=lambda: toggle_ld(ld_status_var=ld_status_var,
                                                                                   ld_status_label=ld_status_label))
    toggle_ld_button.grid(column=0, row=2, pady=10)
    
    # Button to toggle TEC
    toggle_tec_button = ttk.Button(frm, text="Toggle TEC", command=lambda: toggle_tec(tec_status_var=tec_status_var,
                                                                                      tec_status_label=tec_status_label))
    toggle_tec_button.grid(column=1, row=2, pady=10)
    
    continuous_update(ld_current_label, tec_temp_label,tec_setpoint_label,ld_limit_label)  # Start continuous updates

# ld_current_label = None
# tec_temp_label = None
# ldc_device = None
root = Tk()
root.title("CLD1010 LD driver controller")
frm = ttk.Frame(root)
frm.grid()
instr_name = ttk.Label(frm, text="Instrument resource name")
instr_name.grid(column=0, row=1)
instr_name_var = tk.StringVar()
instr_name_entry = ttk.Entry(frm, textvariable=instr_name_var)
instr_name_entry.grid(column=1, row=1)
instr_name_var.set(rname)  # Set your default argument here
 
# Button to initialise SMU with the entry value
initialise_button = ttk.Button(frm, text="Initialise LD controller", command=lambda: on_initialise(instr_name_var.get()))
initialise_button.grid(column=2, row=1)

ttk.Button(frm, text="Quit", command=root.destroy).grid(column=3, row=0)

set_ld_current_button = ttk.Button(frm, text="Set LD Current", command=lambda: set_ld_current(ldc_device, float(ld_current_entry.get())))
set_ld_current_button.grid(column=0, row=7)

# Entry for LD current value
ld_current_var = tk.StringVar()
ld_current_entry = ttk.Entry(frm, textvariable=ld_current_var)
ld_current_entry.grid(column=1, row=7)

# Button to set TEC temperature
set_tec_temp_button = ttk.Button(frm, text="Set TEC Temperature", command=lambda: set_tec_temperature(ldc_device, float(tec_temp_entry.get())))
set_tec_temp_button.grid(column=0, row=8)

# Entry for TEC temperature value
tec_temp_var = tk.StringVar()
tec_temp_entry = ttk.Entry(frm, textvariable=tec_temp_var)
tec_temp_entry.grid(column=1, row=8)

set_ld_limit_button = ttk.Button(frm, text="Set LD Current Limit", command=lambda: set_ld_current_limit(ldc_device, float(ld_limit_entry.get())))
set_ld_limit_button.grid(column=0, row=9)

# Entry for LD current value
ld_limit_var = tk.StringVar()
ld_limit_entry = ttk.Entry(frm, textvariable=ld_limit_var)
ld_limit_entry.grid(column=1, row=9)


root.mainloop()
