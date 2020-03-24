'''
Created on Mar 28, 2015

@author: bustamac
'''


from PyDAQmx import *
from PyDAQmx.DAQmxTypes import *
from PyDAQmx.DAQmxConstants import *


from math import *
from ctypes import *
from numpy import *

from time import sleep 

class DAQmx(object):
    def __init__(self):
        
        #DAQlib, DAQlib_variadic = DAQmxConfig.get_lib()
        #self.nidaq = DAQlib
        #self.DAQlib, DAQlib_variadic = DAQmxConfig.get_lib()
        self.nidaq = ctypes.windll.nicaiu
        self.task_running = False
        self.NI_Devices()
               
    def NI_Devices (self):
        self.NI_devices = []
        buff = ctypes.create_string_buffer(2048)
        self.nidaq.DAQmxGetSysDevNames(byref(buff), 2048)
        temp = [n.strip() for n in buff.value.split(',') if n.strip()]
        print 'NI-devices:', temp #self.NI_devices
        print 'buff', buff
        
        for x in temp:
            device = ctypes.c_char_p(x)
            buff = ctypes.create_string_buffer(2048)
            self.nidaq.DAQmxGetDevProductType(device, byref(buff), 2048)
            print 'Device:%s ProductType:%s'  %(x,buff.value)
            self.NI_devices.append ([x,buff.value ])
        
        print 'class DAQmx NI_Devices self.NI_devices list:', self.NI_devices
    
    def get_NI_Device(self):
        #return self.NI_devices
        return self.NI_devices                
          
    def generateSineWave(self, sys_frequency):
                
        amplitude = float64()       #c_double
        frequency = float64()       #c_double
        sampleClockRate = float64()
        cyc_buf = float64()
        temp1 = float64() #c_double
        temp2 = float64() #c_double
        deltaT = float64() #c_double
        rate_hz = float64()
        
        numElements = float64() #int32
                
        #data_type = float64*32  
        #offsetIndex  = data_type() 
        offsetIndex = numpy.zeros((32), dtype=numpy.int32)
         
        amplitude = 2.0             #cell (8,2)
        cyc_buf = 1.0  
        numElements = self.numSampsPerChannel   
        
        print type(sampleClockRate), type(self.rate_hz) , type(self.numSampsPerChannel), type(cyc_buf)           
        
        self.calculate_desired_frequency(sys_frequency)           #adjust self.rate_hz when desired system frequency is less than 60
        rate_hz = self.desired_freq
        print 'in generateSineWave methond-- rate_hz:', rate_hz
        print 'self.rate_hz:', self.rate_hz
        #sampleClockRate = self.rate_hz * self.numSampsPerChannel * cyc_buf
        sampleClockRate = (rate_hz * self.numSampsPerChannel) / cyc_buf
        sampsPerCycle = self.numSampsPerChannel / cyc_buf
        frequency = sampleClockRate / sampsPerCycle
        deltaT = 1.0 / sampleClockRate
        print 'frequency', frequency
                
        for i in range (self.nChannels):                      #nChannels -1
            #print 'in generateSineWave i ',i
            #print ' myPhaseOffsets [i]',  self.phaseOffsets [i] 
            offsetIndex[i] = self.phaseOffsets [i] * self.numSampsPerChannel /360
            #print 'offsetIndex[i], i', offsetIndex[i], i
            
        for i in range (numElements):               #numElements -1
            for j in range (self.nChannels):                       #nChannels - 1
                temp1= self.dcOffsets [j] + self.amplitudes[j] *sin((i + offsetIndex[j])*2.0*pi*frequency * deltaT)
                temp2 = self.harmonicsAmplitudes[j] * sin(((i + offsetIndex[j]) *2.0 * pi)* self.harmonicComponents[j] * frequency * deltaT)
                    #print 'sin', sin(i + offsetIndex[j]), offsetIndex[j],i, sin((i + offsetIndex[j])*2.0*frequency * deltaT)
                    #print 'deltaT', deltaT, sampleClockRate
                                                                            
                self.data[j * numElements + i] = temp1 + temp2
                #print 'i, j, temp1>>', i,j, temp1
                #print ' myData[j *numElements + i]', self.data[j *numElements + i]
        
        print 'sine wave generation complete'
    
    def listNI_DAQ_devices(self): 
        
        for x in self.NI_devices:
            
            #print 'x', x, type (x)
            device, ProductType = x 
            
            print 'Device:%s ProductType:%s' %(device, ProductType)
            
    def setPhysChanName(self,name):
        #self.physChan.value  = name 
        self.physChan  =ctypes.c_char_p(name)        
        print 'updated phys channel>', self.physChan
        
    def getPhysChans(self):
        '''
        Returns a list of physical channels based on NI hardware detected
        '''
        new_list = []
        phys_chans =[]
        NI_dev = self.NI_devices
            
        #using list comprehension
        unique_matches = list (set(m for index in NI_dev for m in re.findall('cDAQ[\d]+', index[0] ))) 
        #print 'unique_matches', unique_matches, type (unique_matches)
        unique_matches.sort()
               
        for j in unique_matches:
            sub_list = []
            for k in range (len(NI_dev)):
                if j in NI_dev[k][0]:
                    sub_list.append(NI_dev[k][0])   
            new_list.append(sub_list)                    
   
        
        for module in new_list:
            #print 'module:', module
            try:
                phys_chans.append ('%s/ao0:2,%s/ao0:2,%s/ao0:5' %(module[1], module[2], module[3]))
            except IndexError:
                pass
                                 
        print 'returning phys_chans', phys_chans 
        return phys_chans
        
    def configure(self):
                
        print '\nin configure task'
        self.taskHandle = TaskHandle() 
        self.nidaq.DAQmxCreateTask("", byref(self.taskHandle))
        print  'self.nidaq', self.nidaq
                        
        print 'configuring voltage channel'
        print 'self.physChan', self.physChan
        print 'DAQmx_Val_Volts', DAQmx_Val_Volts
               
        self.errorCheck(self.nidaq.DAQmxCreateAOVoltageChan(self.taskHandle, self.physChan,'-',c_double(-10.0),c_double(10.0), DAQmx_Val_Volts, None), 'DAQmxCreateAOVoltageChan')
               
        self.DAQ_configure_timing()
                             
        self.write_updated_buffer()        
        #self.DAQlib.DAQmxStartTask(self.taskHandle)
        self.task_running = True
        #print 'writing analog values to DAQ' 
        print 'self.task_running>', self.task_running
        #writeFile(self.data, 'configure')
        print 'end configure task'
       
    def DAQ_configure_timing(self):
        #configure timing for parameters for the task
        self.errorCheck(self.nidaq.DAQmxCfgSampClkTiming(self.taskHandle, "",c_double(self.desired_freq), DAQmx_Val_Rising, DAQmx_Val_ContSamps, self.numSampsPerChannel), 'DAQmxCfgSampClkTiming')#1650
        
    
    def write_updated_buffer(self):
        print '\n<<< write_updated_buffer: self.numSampsPerChannel', self.numSampsPerChannel
        print 'printing self.data', self.data 
        print 'number of channels:', self.nChannels
        
        sampsPerChanWritten = c_long()
                
        self.errorCheck (self.nidaq.DAQmxWriteAnalogF64(self.taskHandle, self.numSampsPerChannel,False, c_double(10.0), DAQmx_Val_GroupByChannel, self.data, 
                                    byref (sampsPerChanWritten), None), 'DAQmxWriteAnalogF64')
        
        if not self.task_running:
            self.errorCheck (self.nidaq.DAQmxStartTask(self.taskHandle), 'DAQmxStartTask')
            
        print 'writing DAQ buffer:', sampsPerChanWritten.value
                
    def stop_daq(self):
        
        print '\n<<< in stop_daq >>>'
        #clear DAQmx task and clear task if it running
        
        try:
            #self.analog_output.ClearTask()
            self.errorCheck (self.nidaq.DAQmxStopTask(self.taskHandle), 'DAQmxStopTask')
        except AttributeError:
            print '\n<<< DAQC...stop_daq No task running'
        else:
            self.errorCheck (self.nidaq.DAQmxClearTask(self.taskHandle), 'DAQmxClearTask')
            self.taskHandle = 0
            
            self.task_running = False
            print '\n<<< DAQC stop_daq stopping DAQ'
            print 'self.task_running>', self.task_running
                            
    def reset_daq(self, module_name):
        '''
        Reset DAQ module specified in module_name
        '''
              
        print '*** DAQC reset_daq ***'
                
        for j in self.NI_devices:
            temp_device, device_type = j 
            device = ctypes.create_string_buffer(32)
            device.value = temp_device
                       
            if module_name in temp_device:          #if device has 'Mod' in the name it passes if statement i.e cDAQ2Mod
                
                result = self.errorCheck(self.nidaq.DAQmxResetDevice(device), 'DAQmxResetDevice')
                 
                if result == 0:
                    print '*** <%s (%s)> DAQ has been reset ***' %(temp_device, device_type)
                else:
                    print '<%s> not reset, DAQ result code:%d' %(temp_device, result)
         
        if self.task_running:
            self.task_running = False
            print 'self.task_running>', self.task_running 
        
        print '*** End DAQC reset_daq ***'  
                      
    def zero_daq(self):
        
        print '*** zero_daq ***'
        
        for i in range (self.nChannels * self.numSampsPerChannel):
            self.data[i] = 0         

        if self.task_running:   #stop if task is running
            self.write_updated_buffer()
        else:
            self.configure()                                
            
        #writeFile(self.data)
        #self.configure()
        sleep(1)
        self.stop_daq()        
        
        print '*** DAQ zero complete ***' 
        
    def update_daq(self, volts, phaseOffsets, sys_frequency = 60.0):
        # arguments are passed as a list i.e. [1.9,1.9,0.2,1.9,1.9,0.2,1.9,1.9,0.2]
        #      
        print '\n<<< in DAQC update_daq X>>>'  
        for index in range(len(volts)):
            self.amplitudes [index] = volts[index]
        
        for index in range(len(phaseOffsets)):
            self.phaseOffsets [index]= phaseOffsets[index]
                            
       
        self.generateSineWave(sys_frequency)
        sleep(1)
        
        if self.task_running:
            print 'task is already running...writing new analog values'            
            self.DAQ_configure_timing()      #added 11/21/15
                        
            self.write_updated_buffer()
                    
        else:
            print 'task isn not running...creating task'
            self.configure()
    
    def errorCheck(self, error_code, func):
        print 'in errorCheck method, error code %d <<%s>>' %(error_code, func)
        errBuff = create_string_buffer(2048)
        
        if error_code < 0:
            self.nidaq.DAQmxGetExtendedErrorInfo(errBuff,2048)            
        elif error_code > 0:
            self.nidaq.DAQmxGetErrorString(error_code, errBuff, 2048)
        
        print errBuff.value.decode("utf-8")
        return error_code
       
    def update_daq_settings(self, nchannels, rate, numSampsPerChannel ):
            
        print '\n<< DAQC update_daq_settings method'
        self.nChannels = nchannels
        self.numSampsPerChannel = c_double (numSampsPerChannel)
        print 'self.numSampsPerChannel', self.numSampsPerChannel, type (self.numSampsPerChannel)
        self.rate_hz = rate 
                       
        #resize self.data array
        self.data = (c_double * (self.nChannels * self.numSampsPerChannel))()
        self.amplitudes = (c_double * self.nChannels)()
        self.phaseOffsets = (c_double * self.nChannels)()
          
        
        for j in range (len (self.phaseOffsets2)):
            self.phaseOffsets[j] = self.phaseOffsets2[j]
            self.amplitudes[j] = self.amplitudes2[j]
            
            print 'j, self.phaseOffsets[j]', j , self.phaseOffsets[j], type (self.phaseOffsets[j])
            print 'j, self.amplitudes[j]', j , self.amplitudes[j], type (self.amplitudes[j])
            
        print 'resized self.amplitudes', self.amplitudes, type (self.amplitudes)
        print 'resized self.phaseOffsets', self.phaseOffsets, type (self.phaseOffsets)
    
    def setup_daq_parameters(self, physChan, nchannels, rate, numSampsPerChannel, amplitudes, phaseOffsets, dcOffsets, 
                             harmonicAmplitudes, harmonicComponents, system_freq):
        
        print '\n<<< in DAQC setup_daq_parameters >>>'
        self.numSampsPerChannel = uInt64()
        self.numSampsPerChannel = numSampsPerChannel #c_double(numSampsPerChannel) #int32()
        print 'self.numSampsPerChannel', self.numSampsPerChannel
        self.rate_hz = float64 () # (c_double(rate))              #float64()
        self.rate_hz = rate
        print 'self.rate_hz', self.rate_hz, type(self.rate_hz)
        #self.nChannels = int 
        self.nChannels = nchannels #c_double (nchannels)
        print 'self.nChannels', self.nChannels, type (self.nChannels)
                       
        #self.physChan = ctypes.c_char_p(physChan) #data_type(physChan)
        self.physChan = c_char_p(physChan)
       
        #resize c_type arrays   (c_int * NEW_SIZE)()
        self.data = (c_double * (self.nChannels * self.numSampsPerChannel))()
        self.amplitudes = (c_double * self.nChannels)()
        self.phaseOffsets = (c_double * self.nChannels)()
        self.dcOffsets = (c_double * self.nChannels)
        self.harmonicsAmplitudes = (c_double * 32)()
        self.harmonicComponents =  (c_double * 32)() 
               
        #initialize arrays
        self.amplitudes = [j for j in amplitudes]
        print 'self.amplitudes', self.amplitudes
        self.phaseOffsets = [j for j in phaseOffsets]
        print 'self.phaseOffsets', self.phaseOffsets
        self.dcOffsets = [j for j in dcOffsets ]
        print 'self.dcOffsets', self.dcOffsets
        self.harmonicsAmplitudes = [j for j in harmonicAmplitudes]
        print 'self.harmonicsAmplitudes', self.harmonicsAmplitudes
        self.harmonicComponents = [j for j in harmonicComponents]
        print 'self.harmonicComponents', self.harmonicComponents
        
        self.calculate_desired_frequency(system_freq)       #initialize self.desired_freq
                      
    def calculate_desired_frequency(self, system_freq):
        #adjust self.rate_hz when desired system frequency is less than 60        
        print 'calculating new self.desired_freq'
        self.desired_freq = self.rate_hz*(system_freq/60.0)
    
                
    def test(self):
                  
        #physChan = 'cDAQ4mod1/ao0:2,cDAQ4mod2/ao0:2,cDAQ4mod3/ao0:5'
        physChan = 'cDAQ2Mod1/ao0:2,cDAQ2Mod2/ao0:2,cDAQ2Mod4/ao0:5'
        nchannels = 12
        rate = 64800.0
        numSampsPerChannel = 1080
        sys_frequency = 60
        amplitudes = [7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 3, 3, 3, 3, 3, 3]
        phaseOffsets = [0,-120,120,0,-120,120,-5.5,-125.5,114.5,-5.5,-125.2,114.5]
        dcOffsets = [0,0,0,0,0,0, 0,0,0,0,0,0]
        harmonicAmplitudes = [0,0,0,0,0,0, 0,0,0,0,0,0]
        harmonicComponents = [0,0,0,0,0,0, 0,0,0,0,0,0]
        
        self.setup_daq_parameters(physChan, nchannels, rate, numSampsPerChannel, amplitudes, phaseOffsets, dcOffsets, 
                                  harmonicAmplitudes, harmonicComponents, sys_frequency)
        
        self.generateSineWave(sys_frequency)
        #execute d.getPhysChans() to get list of available channels
        #execute d.setPhysChanName(physical_channel) physical channel is one of the channels listed in d.getPhysChan
        self.configure()
        #d.reset_daq(physical_channel)
        #self.update_daq_settings(64800,12,1080)
                     
def main(amplitudes, phaseOffsets, endreset = False): 
        
    physChan = 'cDAQ2Mod1/ao0:2,cDAQ2Mod2/ao0:2,cDAQ2Mod4/ao0:5'
    nchannels = 12
    rate = 64800.0
    numSampsPerChannel = 1080
    sys_frequency = 60
    #amplitudes = [7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 3, 3, 3, 3, 3, 3]
    #phaseOffsets = [0,-120,120,0,-120,120,-5.5,-125.5,114.5,-5.5,-125.2,114.5]
    dcOffsets = [0,0,0,0,0,0, 0,0,0,0,0,0]
    harmonicAmplitudes = [0,0,0,0,0,0, 0,0,0,0,0,0]
    harmonicComponents = [0,0,0,0,0,0, 0,0,0,0,0,0]
    
    d = DAQmx ()
    sleep(5)
    #d.listNI_DAQ_devices()
    NI_module = get_NI_Module_name(physChan)
    print 'NI_module', NI_module
    d.reset_daq(NI_module) 
    sleep(5)        
    d.setup_daq_parameters(physChan, nchannels, rate, numSampsPerChannel, amplitudes, phaseOffsets, dcOffsets, 
                              harmonicAmplitudes, harmonicComponents, sys_frequency)
    
    d.generateSineWave(sys_frequency)
    sleep(5)
    d.configure()
    
    if endreset:
        sleep(5)
        d.reset_daq(NI_module)

def get_NI_Module_name(module_name):
        '''
        Get NI module prefix from NI_devices drop down list
        '''
        
        NI_module_name = re.search('cDAQ[\d]+Mod', module_name) 
        
        if NI_module_name:
            print NI_module_name.group(), type (NI_module_name.group())
        
        return NI_module_name.group()

def start_daq():
    
    d.generateSineWave()
    d.configure()
    
def stop_daq():
    physChan = 'cDAQ2Mod1/ao0:2,cDAQ2Mod2/ao0:2,cDAQ2Mod4/ao0:5'
    nchannels = 12
    rate = 64800.0
    numSampsPerChannel = 1080
    sys_frequency = 60
    NI_module = get_NI_Module_name(physChan)
    d = DAQmx ()
    amplitudes = [7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 3, 3, 3, 3, 3, 3]
    phaseOffsets = [0,-120,120,0,-120,120,-5.5,-125.5,114.5,-5.5,-125.2,114.5]
    dcOffsets = [0,0,0,0,0,0, 0,0,0,0,0,0]
    harmonicAmplitudes = [0,0,0,0,0,0, 0,0,0,0,0,0]
    harmonicComponents = [0,0,0,0,0,0, 0,0,0,0,0,0]
    d.setup_daq_parameters(physChan, nchannels, rate, numSampsPerChannel, amplitudes, phaseOffsets, dcOffsets, 
                          harmonicAmplitudes, harmonicComponents, sys_frequency)
    d.reset_daq(NI_module) 
    d.zero_daq()
       
def writeFile(data, func_name):
    print 'in writeFile function'
    d = DAQmx ('cDAQ1mod1/ao0:2,cDAQ1mod2/ao0:2,cDAQ1mod3/ao0:2')
    handle = open(r'c:\logfiles\dataArray.txt', 'a') 
    
    for index in range (len (data)):
        text = "%i, %f\n" %(index, data[index])
        handle.write(text)
    
    text = '*** End ****' + func_name
    handle.write(text+ '\n')
        
    handle.close()
        
if __name__ == '__main__':
    main()