import DAQC 
import re
import subprocess
import os
import time

def createBat(filename, localIP, localDNP, localPort, remoteIP, remoteDNP, remotePort, setpointPath, batPath):
    # Creates the .bat file for DNP3Master
    bat = open(filename, 'w')
    bat.write("@echo off\n\n")
    line = 'DNP3Master.exe --localIP %s --localPort %s --remoteIP %s --remotePort %s --localDNP %s --remoteDNP %s --numRetry 1 --numAppRetry 1 --timeSync --enableUnsolOnStartup --enableUnsolOnRestart --xspt "%s"' %(
        localIP, localPort, remoteIP, remotePort, localDNP, remoteDNP, setpointPath)
    bat.write(line)
    bat.close()
    
def cleanOutput(directory):
    # Takes the output from the DNP3Master.exe and places it into an out file with less clutter
    dirs = os.listdir(directory)
    for file in dirs:
    # Finds the final file matching, because timestamp places most recent at bottom of the string.
    # Useful in case os.remove(f) does not work
        if re.match("DNP3Master_*", file):
            f = file
    pointFile = open(f, 'r')
    fileName = ".\\OutFiles\\" + time.strftime("%x").replace('/', '.') + " " + time.strftime("%X").replace(':', '_') + " output.txt"
    if not os.path.exists(".\\OutFiles"):
        os.makedirs(".\\OutFiles")
    outFile = open(fileName, 'w')
    outFile.write("index,label,value\n")
    for line in pointFile:
        if re.search("Analog*", line):
            found = re.match(r"[^[]*\[([^]]*)\]", line).groups()[0]
            pointAndMeaning = found.split(":")
            index = pointAndMeaning[0]
            try:
                meaning = pointAndMeaning[1]
            except:
                meaning = "Unmapped"
            splitVal = line.split("value: ")
            value = splitVal[1]
            outString = "%s,%s,%s" %(index, meaning, value)
            outFile.write(outString)
    outFile.close()
    pointFile.close()
    os.remove(f)

def runDAQAndBat(amplitude, offset, command, directory, res=False):
    # Runs DAQ, then calls .bat then stops DAQ
    runFail = True
    while runFail:
        DAQC.main(amplitude, offset, res)
        p = subprocess.call(command)
        DAQC.stop_daq()
        dirs = os.listdir(directory)
        for file in dirs:
            if re.match("DNP3Master_*", file):
                f = file
        statinfo = os.stat(f)
        if statinfo.st_size > 1500:
            runFail = False
    


def main():
    testFile = "readfile.txt"
    commFile = "commfile.txt"
    batpath = os.path.dirname(os.path.realpath("DNP3Master.exe"))  # Assumes the current directory contains DNP3Master.exe

    test = open(testFile, 'r')
    comm = open(commFile, 'r')
        
    for line in test:
        # Reads the test file created by Carlos for use by TMW
        if re.match("Profile:", line):
            splitLine = re.split("\s", line)
            device = splitLine[1]
        elif re.match("DAQSetting1:", line):
            splitLine = re.split("\s", line)
            amp1 = [s for s in splitLine if re.search (",", s)]
            amp1 = re.split(",", amp1[0])
            amp1 = map(float, amp1)
        elif re.match ("DAQSetting2:", line):
            splitLine = re.split("\s", line)
            amp2 = [s for s in splitLine if re.search (",", s)]
            amp2 = re.split(",", amp2[0])
            amp2 = map(float, amp2)
        elif re.match("DAQPhaseOffets:", line): # File uses the phrase 'Offets' 
            splitLine = re.split("\s", line)
            off1 = [s for s in splitLine if re.search (",", s)]
            off1 = re.split(",", off1[0])
            off1 = map(float, off1)
        elif re.match("DAQPhaseOffets1:", line):
            splitLine = re.split("\s", line)
            off2 = [s for s in splitLine if re.search (",", s)]
            off2 = re.split(",", off2[0])
            off2 = map(float, off2)

    for line in comm:
        # Reads the device's communication file created by a user
        if re.match("Source IP", line):
            splitLine = re.split("\s", line)
            sourceIP = splitLine[(len(splitLine)-2)]
        elif re.match("Source Port", line):
            splitLine = re.split("\s", line)
            sourcePort = splitLine[(len(splitLine)-2)]
        elif re.match("Source DNP", line):
            splitLine = re.split("\s", line)
            sourceDNP = splitLine[(len(splitLine)-2)]
        elif re.match("Destination IP", line):
            splitLine = re.split("\s", line)
            destIP = splitLine[(len(splitLine)-2)]
        elif re.match("Destination Port", line):
            splitLine = re.split("\s", line)
            destPort = splitLine[(len(splitLine)-2)]
        elif re.match("Destination DNP", line):
            splitLine = re.split("\s", line)
            destDNP = splitLine[(len(splitLine)-2)]
        elif re.match("Connection Type:", line):
            splitLine = re.split("\s", line)
            connType = splitLine[(len(splitLine)-2)]
        elif re.match("Comm Port", line):
            splitLine = re.split("\s", line)
            commPort = splitLine[(len(splitLine)-2)]
        elif re.match("Setpoint Path", line):
            splitLine = re.split(": ", line)
            setpointPath = splitLine[(len(splitLine)-1)].rstrip()

    test.close()
    comm.close()

    batName = batpath + "\\" + device + "start.bat"
    createBat(batName, sourceIP, sourceDNP, sourcePort, destIP, destDNP, destPort, setpointPath, batpath)
    commandPath = batpath + "\\" + "commandfile.txt"
    runName = batName + " < " + commandPath

    runDAQAndBat(amp1, off1, runName, batpath)
    cleanOutput(batpath)
    
main()

