::USE::
Takes a readfile.txt file created by Carlos for use by Triangle MicroWorks Protocol Test Harness, and a commfile which contains the Source IP, Source Port, Source DNP, Destination IP, Destination Port and Destination DNP.
The readfile.txt contains DAQ settings, and then will utilize Igor's DNP3Master which will query the device for Analog Inputs.
The Analog Inputs are cleaned into a timestamped outfile in the folder .\OutFiles
All files and .exe must be in the same directory


::INPUT::
readfile.txt  [example for 2 switch system]
Profile: Fulle device name, eg. 68023PM
DAQSetting1: Voltage Switch 1 Phase A, Voltage Switch 1 Phase B, Voltage Switch 1 Phase C, Voltage Switch 2 Phase A, Voltage Switch 2 Phase B, Voltage Switch 2 Phase C, Current Switch 1 Phase A, Current Switch 1 Phase B, Current Switch 1 Phase C, Current Switch 2 Phase A, Current Switch 2 Phase B, Current Switch 2 Phase C
DAQSetting2: Voltage Switch 1 Phase A, Voltage Switch 1 Phase B, Voltage Switch 1 Phase C, Voltage Switch 2 Phase A, Voltage Switch 2 Phase B, Voltage Switch 2 Phase C, Current Switch 1 Phase A, Current Switch 1 Phase B, Current Switch 1 Phase C, Current Switch 2 Phase A, Current Switch 2 Phase B, Current Switch 2 Phase C
DAQPhaseOffets1: N/A, N/A, N/A, N/A, N/A, N/A, Switch 1 Phase Angle A, Switch 1 Phase Angle B, Switch 1 Phase Angle C, Switch 2 Phase Angle A, Switch 2 Phase Angle B, Switch 2 Phase Angle C 
DAQPhaseOffets2: N/A, N/A, N/A, N/A, N/A, N/A, Switch 1 Phase Angle A, Switch 1 Phase Angle B, Switch 1 Phase Angle C, Switch 2 Phase Angle A, Switch 2 Phase Angle B, Switch 2 Phase Angle C 

commfile.txt
Source IP Address: 
Source Port: 
Source DNP Address: 
Destination IP Address: 
Destination Port: 
Destination DNP Address: 
Setpoint Path: 


::OUTPUT::
*TimeStamp* output.txt
index,label,value
