import pyvisa as visa
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt




def initialise_SMU(resource_name):
    rm=visa.ResourceManager()
    device=rm.open_resource(resource_name)
    # device.write("*RST")
    print(device.query("*IDN?"))
    return device 

#pick one of the ways of setting voltage points below

Vs = np.arange(-0.5,0.5,0.01) # (start, end, step)
Vs_1 = np.arange(-5,5,0.1) # (start, end, number_of_points)
Vs_2 = np.arange(5,-5,-0.1)
Vs = np.append(Vs_1,Vs_2)
# Vs = np.repeat(-2,100)
#pick one of the ways of setting voltage points above

def IV_measure(Vs,device,file_name='IV_curve',comments='',save=False,plot=False,ax=None,ilimit=0.1):
        
    Is = [None for volt in Vs]
    device.write("reset()")
    device.write("smu.source.func = smu.FUNC_DC_VOLTAGE") # set source to voltage
    device.write(f"smu.source.ilimit.level = {ilimit}") # set current limit (in Amps)
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
        ax.clear()
        ax.plot(Vs,Is,label=comments)
        plt.legend()
        plt.pause(0.05)
        
    
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

def IV_loop(Vs,device, runs, depvars=None,file_name='IV_curve',save=False,plot=False,click=False,folder=None,ilimit=0.1):
    if plot:
        fig, ax = plt.subplots()
        # print('newax_loop')
    else:
        fig, ax = None, None
    for run in np.arange(runs):
        if not depvars:
            comments = run+1
        
        if click:
            if run == 0:
                input("Press Enter to start first measurement")
            else:
                input("Press Enter to start next measurement")
        

        df = IV_measure(Vs,device,comments=comments,save=False,plot=plot,ax=ax,ilimit=ilimit)
        
        
        print(f'Measurement {run+1} complete')
        if save:
            comments2 = input('If required, enter additional comments to the filename\n')
            
            save_datetime = datetime.datetime.now().strftime('_%Y-%m-%d %H-%M-%S') #get current date and time
            if folder is None:
            # folder  = 'C:/Users/z5239428/OneDrive - UNSW/Data/I-V/HC_photodetection_IV/'
                folder = 'C:/Data/'
            total_filename = folder+file_name+'_'+str(comments)+'_'+comments2+save_datetime+'.csv'
            df.to_csv(total_filename)
        
        
        
        
if __name__ == "__main__":     
    rname = "USB0::0x05E6::0x2470::04473418::INSTR"
    device= initialise_SMU(rname)     
    Vs = np.arange(-0.5,0.5,0.01) # (start, end, step)
    Vs_1 = np.arange(0,3,0.05) # (start, end, number_of_points)
    Vs_2 = np.arange(3,0,-0.05)
    Vs = np.append(Vs_1,Vs_2)
    IV_loop(Vs,device,runs=1,file_name='1550nm_200mAV3O5_5um_L1_D2_TS_50 Ohm',plot=True,save=True,click=False,folder='C:/Data/V3O5 deviices/5um width_5um gap_L1_D1/',ilimit=0.005)
        
    
    
    
    



          