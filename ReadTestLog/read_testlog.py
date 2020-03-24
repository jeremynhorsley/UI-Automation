import pandas as pd
import numpy as np
import math
import re
import sys

testFile = "testFile.txt"
file = open(testFile, 'r')

is_event = False
is_input = False
eos_version = np.nan
serial_num = np.nan
app_version = np.nan

test_choice = ["fixed", "percent"]

columns = ["test_type", "device", "app_version", "eos_version", "serial_num", "ind",  "meaning", "static_1", "static_2", "delta_fix", "delta_pct","event_1","event_2","event_3","event_pass_fail"]

df = pd.DataFrame(data=np.zeros((0,len(columns))), columns=columns)
for line in file:
    if re.match("TestID: ", line):
        device = re.split('_',re.split(': ', line)[1])[0] 
    if re.match("Description: ", line):
        lineSplit = re.split(" ", line)
        a = set(lineSplit)
        b = set(test_choice)
        s= a.intersection(b)
        test_type = " ".join(str(x) for x in s)   
    elif re.search("Application", line):
        app = re.split("\n", re.split(": ",line)[1])[0]
    elif re.search("serial", line):
        serial = re.split("\n", re.split(": ",line)[1])[0]
    elif re.search("EOS", line):
        eos = re.split("\n", re.split(": ",line)[1])[0]
    elif (re.match("^[|]", line) and is_event):
        myLine = re.split("\s[|]\s", line)
        group = re.split("\s",myLine[0])[1]
        indexDesc = re.split(" ", myLine[3])
        id = indexDesc[0]
        desc = indexDesc[1]
        value = float(myLine[4])

        if group == "30":
            if any(df.ind.isin(list(id))):
                if np.isnan(df[df.ind.isin(list(id))].static_1.values[0]):
                    indexval = df[df.ind.isin(list(id))].index.tolist()
                    df.set_value(indexval[0], 'static_1', float(value))
                    #df[df.ind.isin(list(id))].static_1 = value
                elif np.isnan(df[df.ind.isin(list(id))].static_2.values[0]):
                    indexval = df[df.ind.isin(list(id))].index.tolist()
                    df.set_value(indexval[0], 'static_2', float(value))
            else:
                d = pd.DataFrame({"test_type":test_type, "device":device, "app_version":app, "eos_version":eos, "serial_num":serial, "ind":id,  
                    "meaning":desc, "static_1":value, "static_2":np.nan,"delta_fix":np.nan, "delta_pct":np.nan, 
                    "event_1":np.nan,"event_2":np.nan,"event_3":np.nan,"event_pass_fail":np.nan},index=[1,15])
                df = pd.concat([df,d],ignore_index=True).drop_duplicates().reset_index(drop=True)
                
        if group == "32":
            if any(df.ind.isin(list(id))):
                if np.isnan(df[df.ind.isin(list(id))].event_1.values[0]):
                    indexval = df[df.ind.isin(list(id))].index.tolist()
                    df.set_value(indexval[0], 'event_1', float(value))
                    #df[df.ind.isin(list(id))].event_1 = value
                elif np.isnan(df[df.ind.isin(list(id))].event_2.values[0]):
                    indexval = df[df.ind.isin(list(id))].index.tolist()
                    df.set_value(indexval[0], 'event_2', float(value))
                    #df[df.ind.isin(list(id))].event_2 = value
                elif np.isnan(df[df.ind.isin(list(id))].event_3.values[0]):
                    indexval = df[df.ind.isin(list(id))].index.tolist()
                    df.set_value(indexval[0], 'event_3',float(value))
            else:
                d = pd.DataFrame({"test_type":test_type, "device":device, "app_version":app, "eos_version":eos, "serial_num":serial, "ind":id,  
                    "meaning":desc, "static_1":np.nan, "static_2":np.nan, "delta_fix":np.nan, "delta_pct":np.nan, 
                    "event_1":value,"event_2":np.nan,"event_3":np.nan,"event_pass_fail":np.nan},index=[1,15])
                df = pd.concat([df,d],ignore_index=True).drop_duplicates().reset_index(drop=True)
            
    elif (re.match("^[|]", line) and is_input):    
        myLine = re.split("\s[|]\s", line)
        group = myLine[10]
        indexDesc = re.split(" ", myLine[0])
        id = indexDesc[1]
        desc = indexDesc[2]
        value = float(re.split("\s",myLine[1])[6])
        if re.search("Master", group):
            if any(df.ind.isin(list(id))):
                if np.isnan(float(df[df.ind.isin(list(id))].static_1.values[0])):
                    indexval = df[df.ind.isin(list(id))].index.tolist()
                    df.set_value(indexval[0], 'static_1', float(value))
                elif np.isnan(float(df[df.ind.isin(list(id))].static_2.values[0])):
                    indexval = df[df.ind.isin(list(id))].index.tolist()
                    df.set_value(indexval[0], 'static_2', float(value))
            else:
                d = pd.DataFrame({"test_type":test_type, "device":device, "app_version":app, "eos_version":eos, "serial_num":serial, "ind":id,  
                    "meaning":desc, "static_1":value, "static_2":np.nan, "delta_fix":np.nan, "delta_pct":np.nan, 
                    "event_1":np.nan,"event_2":np.nan,"event_3":np.nan,"event_pass_fail":np.nan},index=[1,15])
                df = pd.concat([df,d],ignore_index=True).drop_duplicates().reset_index(drop=True)
                
        if re.search("Unsoli", group):
            if any(df.ind.isin(list(id))):
                if np.isnan(df[df.ind.isin(list(id))].event_1.values[0]):
                    indexval = df[df.ind.isin(list(id))].index.tolist()
                    df.set_value(indexval[0], 'event_1', float(value))
                    #df[df.ind.isin(list(id))].event_1 = value
                elif np.isnan(df[df.ind.isin(list(id))].event_2.values[0]):
                    indexval = df[df.ind.isin(list(id))].index.tolist()
                    df.set_value(indexval[0], 'event_2', float(value))
                    #df[df.ind.isin(list(id))].event_2 = value
                elif np.isnan(df[df.ind.isin(list(id))].event_3.values[0]):
                    indexval = df[df.ind.isin(list(id))].index.tolist()
                    df.set_value(indexval[0], 'event_3', float(value))
            else:
                d = pd.DataFrame({"test_type":test_type, "device":device, "app_version":app, "eos_version":eos, "serial_num":serial, "ind":id,  
                    "meaning":desc, "static_1":np.nan, "static_2":np.nan,"delta_fix":np.nan, "delta_pct":np.nan,
                    "event_1":value,"event_2":np.nan,"event_3":np.nan,"event_pass_fail":np.nan},index=[1,15])
                df = pd.concat([df,d],ignore_index=True).drop_duplicates().reset_index(drop=True)
                    
    if re.search("Analog Outputs:", line):
        is_input = False           
    if re.search("Test Statistics:", line):
        is_event=False
    if re.search("Group", line):
        is_event = True
    if re.search("AnlgInput", line):
        is_input = True

df['delta_fix'] = df['static_1'] - df['static_2']
df['delta_pct'] = (df['static_1'] - df['static_2']) / df['static_1'] * 100
df['event_pass_fail'] = np.where(np.isnan(df['event_2']), 'fail','pass')
df.to_csv("DataFrame.csv")