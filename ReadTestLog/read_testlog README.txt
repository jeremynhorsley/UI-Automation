read_testlog.py README

::USE::
Tranform a log file created in triangle microworks protocol test harness to a readable format which determines 
whether multiple analog input points have successfully passed.
Points are determined as "pass" whether or not 2 events were recorded for the point index.
Most useful with a test file which triggers all point indeces.

::INPUT::
Uses log file from triangle microwork's protocol test harness test

::OUTPUT::
The log file is moved into a DataFrame.csv file where all points are recorded and given all
pass or fail given if they recorded 2 events.
