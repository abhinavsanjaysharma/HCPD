# HCPD

Code associated with the Hot Carrier Photodetection (HCPD) project.

The main purpose is to achive remote device control and measurement automation.

The various pieces of code interface with

a) A source measurement unit (Keithley 2470 model)

b) A temperature controller (T96, part of a Linkam cryostage kit)

c) A laser diode controller (Thorlabs CLD1010)

Additionally, Cr_TMM.py replicates some results from James Dimmock's thesis using the TMM features of solcore: https://www.solcore.solar/

## --- SMU control ---
SMU control is achieved using pyvisa: https://pyvisa.readthedocs.io/en/latest/

The commands specific to the Keithely 2470 model are found below

https://download.tek.com/manual/2470-901-01B_Sept_2019_Ref.pdf

K2470_controller is the most up-to-date commented file, and is written to be run as a GUI.

The GUI is written using tkinter: https://docs.python.org/3/library/tkinter.html

However, the functions written in it can be used on their own. 

## --- Linkam temperature control ---

Cryostage control is achieved using pylinkam: https://github.com/swinburne-sensing/pylinkam

This requires license and .dll files that come with the Linkam software development kit (SDK)

Linkam.py is the most up-to-date commented file, and is designed to do temperature dependent IV measurements, interfacing both with the temperature controller and the SMU.

## --- Laser diode controller --- 

Laser diode control is achieved using pyvisa: https://pyvisa.readthedocs.io/en/latest/

The commands specific to the CLD101x controllers are found below 

https://www.thorlabs.com/drawings/a779b8d497e4cf66-ABDDEC42-9985-6CBF-A36BEDF50784839D/CLD1010LP-ProgrammersReferenceManual.pdf

CLD1010_controller is the most up-to-date commented file, and is written to be run as a GUI.

The GUI is written using tkinter: https://docs.python.org/3/library/tkinter.html

However, the functions written in it can be used on their own. 

