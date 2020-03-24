@echo off

DNP3Master.exe --localIP 192.168.0.1 --localPort 20000 --remoteIP 192.168.0.2 --remotePort 20000 --localDNP 2 --remoteDNP 1 --numRetry 1 --numAppRetry 1 --timeSync --enableUnsolOnStartup --enableUnsolOnRestart --xspt "C:\Users\patrick.talley\Documents\SetPoints\SG68023pm all setpoint fixed deadbands.xspt"