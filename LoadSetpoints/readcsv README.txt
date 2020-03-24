readcsv.ps1 README

::USE::
Takes a .csv file and loads setpoints into all controllers listed based on the corresponding
setpoint file.
Loads all but Communications DNP Routing and Communications Other setpoints

::INPUT::
Input file is a .csv file.
All parameters must be quoted.
Requires the following header:
ConnectType,Connect,Port,LocalAddr,PeerAddr,SetpointPath
    
ConnectType: Either "Serial" or "TCP" depending on the way a connection is obtained to the device
Connect: Either the com port (ex. "COM1") or ip to device (ex. "10.64.240.155")
Port: null if connecting through serial, either given for TCP (ex. "20000")
LocalAddr: The UDP local address used to connect to the device (ex. "65432")
PeerAddr: The UDP peer address used to connect to the device (ex. "65532")
SetpointPath: Complete path to setpoint file (ex. "C:\Users\patrick.talley\Documents\Setpoints\SG68023pm all setpoint fixed deadbands.xspt")

::OUTPUT::
Creates an 'out.csv' file into the folder containing the script.
This file contains the input parameters and whether the setpoints were successfully loaded.