from System import *   
import clr 

"""
Example code to demonstrate the Triangle MicroWorks .NET Source Code Library API in IronPython
"""


# load TMW assemblies
clr.AddReference("TMW.SCL") 
from TMW.SCL.DNP import * 
from TMW.SCL.DNP.Master import * 
from TMW.SCL.DNP.Slave import * 
from TMW.SCL import * 

from TimeFunctions import (getdatetime)
    
class DNPClass(object):
    #list of all DNPClass
    all_dnpClasses = []
    dnpClass_index = 0 
              
    def __init__(self):
       
        self.__class__.all_dnpClasses.append(self)
        self.__class__.dnpClass_index +=1
                
        self.masterChan = DNPChannel()
        self.masterSesn = MDNPSession()
                
        self.slaveChan = DNPChannel()
        self.slaveSesn = MDNPSession()
                                      
    def openMasterUDP(self,sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress, UDPBroadcastAddr, *args, **kwargs):
                  
        """open a UDP DNP master device"""
        
        print 'openMasterUDP kwargs', kwargs
        print '\nopenMasterUDP args', args
                              
        if args:                
            self.logEnable = args[0]
            self.logFile = args[1]
            self.Filename = args[2]
            
         #enum NETWORK_TYPE, values: NO_IP (0), TCP_ONLY (1), TCP_UDP (2), UDP_ONLY (3) 
        
        print 'opening UDP master channel'          
        self.masterChan = DNPChannel(TMW_CHANNEL_OR_SESSION_TYPE.MASTER) 
        self.masterChan.ChannelConnectStateEvent += self.ChannelConnectState
         
        # masterChan.Type = WINIO_TYPE.TCP'
        self.masterChan.Type = WINIO_TYPE.UDP_TCP
        self.masterChan.Name = "PyUDP_M" +  repr(sourceAddress)
        self.masterChan.WinTCPipAddress = destIPAddress  # "127.0.0.1"
        self.masterChan.WinTCPipPort = sourcePort
        'masterChan.WinTCPipPort = 20010'
        self.masterChan.LocalUDPPort = sourcePort
        self.masterChan.DestUDPPort = destPort
        self.masterChan.UDP_PORT_SRC = sourcePort
        'masterChan.WinTCPmode = TCP_MODE.CLIENT'
        self.masterChan.WinTCPmode = TCP_MODE.UDP
        self.masterChan.WinUDPBroadcastAddress = UDPBroadcastAddr
        self.masterChan.NetworkType = self.masterChan.NetworkType.UDP_ONLY
        self.masterChan.OpenChannel()        
        self.masterSesn = MDNPSession(self.masterChan)
        self.masterSesn.Destination = destAddress
        self.masterSesn.Source = sourceAddress
        self.masterSesn.AutoClassPollIIN = False
        self.masterSesn.AutoIntegrityLocal = False
        self.masterSesn.AutoUnsolStartup = True
        self.masterSesn.AutoClearRestart = False
        self.masterSesn.AutoIntegrityRestart = False
        self.masterSesn.AutoIntegrityOverflow = False
        
                
        print 'self.masterChanc connect state', self.masterChan.ConnectState
        self.masterSesn.Name = "PyUDP_Sessn" + repr (sourceAddress)
     
        self.openSession('UDP', *args, **kwargs)
                        
    def openMasterTCP(self,sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress, UDPBroadcastAddr, UDPLocalPort, *args, **kwargs):
        
        print 'openMasterTCP kwargs', kwargs
        print '\nopenMasterTCP args', args
        """open a DNP master device"""
                        
        if args:                
            self.logEnable = args[0]
            self.logFile = args[1]
            self.Filename = args[2]
                
        self.masterChan = DNPChannel(TMW_CHANNEL_OR_SESSION_TYPE.MASTER)
        self.masterChan.ChannelConnectStateEvent += self.ChannelConnectState
          
        self.masterChan.Type = WINIO_TYPE.TCP
        #self.masterChan.Type = WINIO_TYPE.UDP_TCP
        
        self.masterChan.Name = "PyTCP_M" + repr(sourceAddress)
        self.masterChan.WinTCPipAddress = destIPAddress  # "127.0.0.1"
        self.masterChan.WinTCPipPort = sourcePort       #destPort changed 10-15-13
        self.masterChan.DualEndPointIpPort = destPort
        self.masterChan.WinTCPmode = TCP_MODE.DUAL_ENDPOINT  # TCP_MODE.CLIENT
        self.masterChan.WinUDPBroadcastAddress = UDPBroadcastAddr
        self.masterChan.LocalUDPPort = UDPLocalPort
        self.masterChan.OpenChannel() 
        self.masterSesn = MDNPSession(self.masterChan) 
        self.masterSesn.Destination = destAddress
        self.masterSesn.Source = sourceAddress
        self.masterSesn.AutoEnableUnsol = False
        self.masterSesn.AutoIntegrityOnline = False
        self.masterSesn.AutoClassPollIIN = False
        self.masterSesn.AutoIntegrityLocal = False
        self.masterSesn.AutoClearRestart = False
        self.masterSesn.AutoIntegrityRestart = False
        self.masterSesn.AutoIntegrityOverflow = False
        self.masterSesn.Name = "PyTCP_Sessn" + repr(sourceAddress)
          
        self.openSession('TCP', *args, **kwargs)
      
    def openSlaveUDP(self,sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress):
        """open a UDP DNP slave device"""
        
        self.slaveChan = DNPChannel(TMW_CHANNEL_OR_SESSION_TYPE.SLAVE)  
  # slaveChan.Type = WINIO_TYPE.TCP'
        self.slaveChan.Type = WINIO_TYPE.UDP_TCP
        self.slaveChan.Name = "Python UDP DNP Slave"
  # slaveChan.WinTCPipAddress = "*.*.*.*"'
        self.slaveChan.WinTCPipAddress = destIPAddress  # "127.0.0.1"
  # slaveChan.WinTCPipPort = 20010'
        self.slaveChan.LocalUDPPort = destPort
        self.slaveChan.DestUDPPort = sourcePort
        self.slaveChan.InitUnsolUDPPort = sourcePort
  # slaveChan.UDP_PORT_SRC=20000' 
  # slaveChan.WinTCPmode = TCP_MODE.SERVER'
        self.slaveChan.WinTCPmode = TCP_MODE.UDP
        self.slaveChan.NetworkType = self.slaveChan.NetworkType.UDP_ONLY
        self.slaveChan.OpenChannel()
        self.slaveSesn = SDNPSession(self.slaveChan)
        self.slaveSesn.Destination = sourceAddress
        self.slaveSesn.Source = destAddress  
        self.slaveSesn.Name = "Slave"
        self.slaveSesn.OpenSession() 
        self.slaveSesn.SimDatabase.Reset()
        
    def openSlaveTCP(self,sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress):
        """open a DNP slave device"""
        
        self.slaveChan = DNPChannel(TMW_CHANNEL_OR_SESSION_TYPE.SLAVE)  
        self.slaveChan.Type = WINIO_TYPE.TCP
        self.slaveChan.Name = "Python TCP DNP Slave"
        self.slaveChan.WinTCPipAddress = sourceIPAddress  # "*.*.*.*"
        self.slaveChan.WinTCPipPort = destPort
        self.slaveChan.WinTCPmode = TCP_MODE.SERVER
        self.slaveChan.OpenChannel() 
        self.slaveSesn = SDNPSession(self.slaveChan)
        self.slaveSesn.Destination = sourceAddress
        self.slaveSesn.Source = destAddress
        self.slaveSesn.Name = "Slave"
        self.slaveSesn.OpenSession() 
 
        self.slaveSesn.SimDatabase.Reset()
        
    def openRS_232Master(self,sourceAddress,destAddress, baudRate= "9600", commPort= "COM1",
                         numDataBits =8, numStopBits = 1, parity ="NONE",dtrMode= "DISABLE",
                         portMode= "NONE", rtsMode= "ENABLE", *args, **kwargs):
        
        """open a serial  master device"""
        
        print 'openRS_232Master kwargs', kwargs
        print '\nopenRS_232Master args', args
        """open a DNP master device"""
                        
        if args:                
            self.logEnable = args[0]
            self.logFile = args[1]
            self.Filename = args[2]
        #enum RS232_DATA_BITS, values: BITS_7 (7), BITS_8 (8) 
        #enum RS232_STOP_BITS, values: BITS_1 (1), BITS_2 (2) 
        #enum RS232_PARITY, values: EVEN (1), NONE (0), ODD (2) 
        #enum RS232_DTR_MODE, values: DISABLE (0), ENABLE (1), HANDSHAKE (2) 
        #enum RS232_PORT_MODE, values: HARDWARE (1), NONE (0), WINDOWS (2) 
        #enum RS232_RTS_MODE, values: DISABLE (0), ENABLE (1), HANDSHAKE (2), TOGGLE (3) 
        
        
        ParitySetting  = {"EVEN": 1, "NONE":0, "ODD":2}
        DTR_Mode = {"DISABLE" : 0, "ENABLE": 1, "HANDSHAKE": 2}
        Port_Mode = {"HARDWARE": 1, "NONE": 0, "WINDOWS": 2}
        RTS_Mode = {"DISABLE": 0, "ENABLE": 1, "HANDSHAKE": 2, "TOGGLE":3}
  
        self.masterChan = DNPChannel(TMW_CHANNEL_OR_SESSION_TYPE.MASTER)
        self.masterChan.ChannelConnectStateEvent += self.ChannelConnectState
                
        self.masterChan.Type = WINIO_TYPE.RS232
        self.masterChan.NetworkType = self.masterChan.NetworkType.NO_IP
        self.masterChan.Name = "PySerial_M" +  repr(sourceAddress)
        self.masterChan.Win232baudRate = baudRate       #"9600"
        self.masterChan.Win232comPortName = commPort    #"COM1"
                
        self.masterChan.Win232numDataBits  = Enum.ToObject(RS232_DATA_BITS, numDataBits)
        self.masterChan.Win232numStopBits = Enum.ToObject(RS232_STOP_BITS, numStopBits)
        self.masterChan.Win232parity = Enum.ToObject (RS232_PARITY, ParitySetting.get(parity))
        self.masterChan.Win232portDtrMode  = Enum.ToObject(RS232_DTR_MODE, DTR_Mode.get(dtrMode))
        self.masterChan.Win232portMode  = Enum.ToObject (RS232_PORT_MODE, Port_Mode.get(portMode))
        self.masterChan.Win232portRtsMode  = Enum.ToObject (RS232_RTS_MODE, RTS_Mode.get(rtsMode))
                       
        self.masterChan.OpenChannel() 
        self.masterSesn = MDNPSession(self.masterChan)
        self.masterSesn.Destination = destAddress
        self.masterSesn.Source = sourceAddress
        self.masterSesn.AutoClassPollIIN = False
        self.masterSesn.AutoIntegrityLocal = False
        self.masterSesn.AutoUnsolStartup = True
        self.masterSesn.AutoClearRestart = False
        self.masterSesn.AutoIntegrityRestart = False        
        self.masterSesn.AutoIntegrityOverflow = False
        
        self.masterSesn.Name = "PySerial" + repr(sourceAddress)
     
        print 'self.masterChanc connect state', self.masterChan.ConnectState
        self.openSession('Serial', *args, **kwargs)
                      
    def openLoopBackUDP(self,sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress):
        "open a UDP dnp master and slave device"
        self.openMasterUDP(sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress)
        self.openSlaveUDP(sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress)
        
    def openLoopBackTCP(self,sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress):
        "open a dnp master and slave device"
        self.openMasterTCP(sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress)
        self.openSlaveTCP(sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress)
        
    def openUDP(self,sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress, UDPBroadcastAddr, *args, **kwargs):
        "open a UDP dnp master and slave device"
        self.openMasterUDP(sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress, UDPBroadcastAddr, *args, **kwargs)
        
    def openTCP(self,sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress, UDPBroadcastAddr, UDPLocalPort, *args, **kwargs):
        "open a dnp master and slave device"
        self.openMasterTCP(sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress, UDPBroadcastAddr, UDPLocalPort, *args, **kwargs)
        
    def closeMaster(self):
        """close a DNP master device"""
        #global masterChan
        #global masterSesn
        self.masterSesn.CloseSession()
        self.masterChan.CloseChannel()
        print 'closing self.masterChan', self.masterChan.ConnectState
        self.masterChan.ChannelConnectStateEvent -= self.ChannelConnectState
        
        
    def closeSlave(self):
        """close a dnp slave device"""
        #global slaveChan
        #global slaveSesn
        self.slaveSesn.CloseSession()
        self.slaveChan.CloseChannel()
        
    def close(self):
        """close a DNP master and slave device"""
        self.closeMaster()
        self.closeSlave()
    
    def openSession(self, connectionType, *args,  **kwargs):
        print 'entering openSession session'
        
        self.masterSesn.OpenSession() 
        
        time_as_string, currentResponseTime = getdatetime('local', True)
        
        self.MDNPReq = MDNPRequest(self.masterSesn)
        print 'openSession master channel', self.masterChan
              
        if kwargs.get('event_handler'):
            self.MDNPReq.RequestEvent += kwargs.get('event_handler')
        
        if self.masterChan.OpenChannel:
            textLine = '%s channel <%s> opened [%s]\n' %(connectionType, self.masterChan.Name, time_as_string )
            self.writeToLogFile(textLine)  
                       
            self.MyStartUpSequence()
            #self.__class__.dnpClass_index +=1        
    
    def MyStartUpSequence(self):
        """ My manual Master Startup Sequence"""
        #self.DisableUnsolicited (True, True, True)
        self.IntegrityPoll (False)
    
    def ChannelConnectState (self, s, e):
        time_as_string, currentResponseTime = getdatetime('local', True)
        print '\n$$$$ self.masterChan.ChannelConnectStateEvent has fired $$$'        
        print '$$$ channel connected', e
        print '$$$ channel connected', s 
        print '$$$ $$$ $$$'   
        
        textLine = '\nChannel <%s> state change: %r [%s]\n' %(self.masterChan.Name, e, time_as_string )
        
        self.writeToLogFile(textLine)                    
    
    def writeToLogFile(self, textlines):
        
        if hasattr(self, 'logEnable') and hasattr(self, 'logFile') and hasattr(self, 'Filename'):
            writeDataToLogFile(textlines, self.logEnable, self.logFile, self.Filename)
            
    def reqEventSubscribe (self):
        print 'Registering for MDNPRequest Events', self.MDNPReq.ToString
        self.MDNPReq.RequestEvent += self.handleResponseEvent 
        
    def reqEventUnSubscribe (self):
        print 'Unregestering for MDNPRequest Events', self.MDNPReq.ToString
        self.MDNPReq.RequestEvent -= self.handleResponseEvent 
        
    def binIn(self,groupID, variation, qualifier, start, stop):
        """print value of Binary Inputs from <start> to <stop>"""
        # req = MDNPRequest(masterSesn)
        # req.ReadGroup( groupID, variation, Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier),  start, stop )  
        r = range(start, stop + 1)
        print 'groupID', groupID
        for i in r:
            point = self.masterSesn.SimDatabase.GetPoint(groupID, i)
            # print 'printing point', point
            # print 'point type', type (point)
            # print 'add event' , point.MDNPSimBinIn.add_PointEvent()
            # pointEvent = point.enableEvent(point)
            # print 'point.AddEvent', point.AddEvent()
            # pointEvent = point.enableEvent(MDNPSimBinIn)
            # print ' point event', pointEvent
            # print 'adding point event add_PointEvent', point.add_PointEvent()
            # point.PointEvent += handlePointEvent
            # point.PointEventDelegate += handlePointEvent
  
            print 'point enable event', point.enableEvent (point) 
  
  
        string = "Group: " + str (groupID) + " Point Number: " + point.PointNumber.ToString() + " Value: " + point.Value.ToString() + \
        " Time: " + point.PointTime.ToString() 
    
  
        print string
        # string2 = point.PointEvent.ToString()
        # print 'printing point event??', string2


    def binInOnePoint(self,groupID, variation, qualifier, pointIndex):
        """print value of Single point specified by Group ID"""
  
        point = self.masterSesn.SimDatabase.GetPoint(groupID, pointIndex)
    
        string = "Group: " + str (groupID) + " Point Number: " + point.PointNumber.ToString() + " Value: " + point.Value.ToString() + \
        " Time: " + point.PointTime.ToString() 
    
  
        #print 'printing from binInOnePoint function', string
        return string
    
    def binInOnePointDict(self,groupID, variation, qualifier, pointIndex):
        """print value of Single point specified by Group ID"""
  
        point = self.masterSesn.SimDatabase.GetPoint(groupID, pointIndex)
        dict = {}
        print 'types point.PointNumber, point.Value', type (point.PointNumber), type (point.Value)
        
        dict.update ({'group': str(groupID), 'Pt.Number': point.PointNumber, 'Pt.Value': point.Value, "Time": point.PointTime.ToString()})
    
        #string = "Group: " + str (groupID) + " Point Number: " + point.PointNumber.ToString() + " Value: " + point.Value.ToString() + \
        #" Time: " + point.PointTime.ToString() 
    
  
        #print 'printing from binInOnePoint function', string
        return dict
  
 
    def readGroup(self,groupID, variation, qualifier, start, stop, broadcast_flag = False):
        """
        readGroup(  groupId, variation,  start, stop )
  
          read an object group from <start> to <stop>
          """
  
        #req = MDNPRequest(masterSesn)
        if not broadcast_flag:
            self.MDNPReq.ReadGroup(groupID, variation, Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier), start, stop)
        else:
            print 'Sending broadcast message'
            self.MDNPBroacastReq.ReadGroup(groupID, variation, Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier), start, stop)
    
    
    def AnalogCommand(self,fc, autoOperate, feedback, feedbackDelay, qualifier, variation, point, value, broadcast_flag = False, **kwargs):
        """
        AnalogCommand( fc, autoOperate, feedback, feedbackDelay, qualifier, variation, point, value )
    
      send analog command
        where
        fc - DNP Function Code
        autoOperate - send select then operate codes
        feedback - follow command with feedback poll
        feedbackDelay - mS delay before feedback poll
        variation - DNP objeect variation
        point - DNP point number
        value - value to set 
        
        ** note: this function does allow invalid inputs. ie: variation 2 will cause the slave to respond with IIN2.1 Object Unknown.
      """
  
  
        a = AnalogInfo(point, value)
        analogArray = Array.CreateInstance(AnalogInfo, 1)
  
        analogArray[0] = a;
  
        #req = MDNPRequest(masterSesn)
        if not broadcast_flag:            
            self.MDNPReq.AnalogCommand(Enum.ToObject(MDNPRequest.DNP_FUNCTION_CODE, fc), autoOperate, feedback, feedbackDelay, Enum.ToObject(MDNPRequest.DNP_QUALIFIER,
                         qualifier), variation, analogArray)         
        else:
            self.MDNPBroacastReq.AnalogCommand(Enum.ToObject(MDNPRequest.DNP_FUNCTION_CODE, fc), autoOperate, feedback, feedbackDelay, 
                        Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier), variation, analogArray)
  
    def BinaryCommand(self,fc, autoOperate, feedback, feedbackDelay, qualifier, point, control, broadcast_flag = False):
        """
      'bool BinaryCommand(self, DNP_FUNCTION_CODE fc, bool autoOperate, bool feedback, UInt32 feedbackDelay, DNP_QUALIFIER qualifier, Array[CROBInfo] crobArray)' 
  
      CROBInfo(UInt16 pointNumber, CROB_CTRL control, Byte count, UInt32 onTime, UInt32 offTime) 
  
      CROBInfo(UInt16 pointNumber, CROB_CTRL control, UInt32 onTime, UInt32 offTime) 
  
      enum CROB_CTRL, values: CLEAR (32), LOFF (4), LON (3), NUL (0), PAIRED_CLOSE (64), PAIRED_TRIP (128), POFF (2), PON (1), QUEUE (16) 
 
      CROB_CTRL CreateInstance[CROB_CTRL]() 
    
      enum DNP_CROB_CTRL, values: CLEAR (32), LATCH_OFF (4), LATCH_ON (3), NUL (0), PAIRED_CLOSE (64), PAIRED_TRIP (128), PULSE_OFF (2), PULSE_ON (1), QUEUE (16) 
  
      enum DNP_FUNCTION_CODE, values: ABORT (30), ACTIVATE_CONFIG (31), ASSIGN_CLASS (22), AUTHENTICATE (29), CLOSE_FILE (26), COLD_RESTART (13), CONFIRM (0), DELAY_MEASURE (23), DELETE_FILE (27), DIRECT_OP (5), DIRECT_OP_NOACK (6), DISABLE_UNSOL (21), ENABLE_UNSOL (20), FRZ (7), FRZ_CLEAR (9), FRZ_CLEAR_NOACK (10), FRZ_NOACK (8), GET_FILE_INFO (28), OPEN_FILE (25), OPERATE (4), READ (1), RECORD_TIME (24), SELECT (3), WARM_RESTART (14), WRITE (2) 

      CreateInstance(elementType: Type, *lengths: Array[int]) -> Array 
      CreateInstance(elementType: Type, *lengths: Array[Int64]) -> Array 
      CreateInstance(elementType: Type, lengths: Array[int], lowerBounds: Array[int]) -> Array 
      CreateInstance(elementType: Type, length: int) -> Array 
      CreateInstance(elementType: Type, length1: int, length2: int) -> Array 
      CreateInstance(elementType: Type, length1: int, length2: int, length3: int) -> Array 

      
      """
 
        ctrl = Enum.ToObject(CROBInfo.CROB_CTRL, control) 
        a = CROBInfo(point, ctrl, 0, 0)
                
        binaryArray = Array.CreateInstance(CROBInfo, 1)
        binaryArray[0] = a
          
        #req = MDNPRequest(masterSesn)
        if not broadcast_flag:
            self.MDNPReq.BinaryCommand(Enum.ToObject(MDNPRequest.DNP_FUNCTION_CODE, fc), autoOperate, feedback, feedbackDelay, Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier), 
                                   binaryArray)
        else:
            self.MDNPBroacastReq.BinaryCommand(Enum.ToObject(MDNPRequest.DNP_FUNCTION_CODE, fc), autoOperate, feedback, feedbackDelay, Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier), 
                                   binaryArray)           
        
    def BinaryCommandMultiple(self,fc, autoOperate, feedback, feedbackDelay, qualifier, point, control):
       """
     'bool BinaryCommand(self, DNP_FUNCTION_CODE fc, bool autoOperate, bool feedback, UInt32 feedbackDelay, DNP_QUALIFIER qualifier, Array[CROBInfo] crobArray)' 
 
     CROBInfo(UInt16 pointNumber, CROB_CTRL control, Byte count, UInt32 onTime, UInt32 offTime) 
 
     CROBInfo(UInt16 pointNumber, CROB_CTRL control, UInt32 onTime, UInt32 offTime) 
 
     enum CROB_CTRL, values: CLEAR (32), LOFF (4), LON (3), NUL (0), PAIRED_CLOSE (64), PAIRED_TRIP (128), POFF (2), PON (1), QUEUE (16) 

     CROB_CTRL CreateInstance[CROB_CTRL]() 
   
     enum DNP_CROB_CTRL, values: CLEAR (32), LATCH_OFF (4), LATCH_ON (3), NUL (0), PAIRED_CLOSE (64), PAIRED_TRIP (128), PULSE_OFF (2), PULSE_ON (1), QUEUE (16) 
 
     enum DNP_FUNCTION_CODE, values: ABORT (30), ACTIVATE_CONFIG (31), ASSIGN_CLASS (22), AUTHENTICATE (29), CLOSE_FILE (26), COLD_RESTART (13), CONFIRM (0), DELAY_MEASURE (23), DELETE_FILE (27), DIRECT_OP (5), DIRECT_OP_NOACK (6), DISABLE_UNSOL (21), ENABLE_UNSOL (20), FRZ (7), FRZ_CLEAR (9), FRZ_CLEAR_NOACK (10), FRZ_NOACK (8), GET_FILE_INFO (28), OPEN_FILE (25), OPERATE (4), READ (1), RECORD_TIME (24), SELECT (3), WARM_RESTART (14), WRITE (2) 

     CreateInstance(elementType: Type, *lengths: Array[int]) -> Array 
     CreateInstance(elementType: Type, *lengths: Array[Int64]) -> Array 
     CreateInstance(elementType: Type, lengths: Array[int], lowerBounds: Array[int]) -> Array 
     CreateInstance(elementType: Type, length: int) -> Array 
     CreateInstance(elementType: Type, length1: int, length2: int) -> Array 
     CreateInstance(elementType: Type, length1: int, length2: int, length3: int) -> Array 

     
     """

       ctrl = Enum.ToObject(CROBInfo.CROB_CTRL, control)
       ctrl_latchOff = Enum.ToObject(CROBInfo.CROB_CTRL, 4)
       ctrl_latchOn = Enum.ToObject(CROBInfo.CROB_CTRL, 3)
       print 'ctrl_latchOn', ctrl_latchOn
       
       a = CROBInfo(point, ctrl, 0, 0)
       control_array= [(point,ctrl,0,0), (17,ctrl_latchOn,0,0)]
       # print a
       j=20        #20 is maximum that will fit in one frame
       
       #binaryArray = Array.CreateInstance(CROBInfo, 1)
       #binaryArray[0] = a
       #binaryArray = Array.CreateInstance(CROBInfo, j)
       binaryArray = Array.CreateInstance(CROBInfo, 2)
 
       #for x in range (0, j):
       #    print 'value of index j,x:', j,x
       #    binaryArray[x] = a
       
       for x in range (0, len (control_array)):
           print 'value of index x: len (control_array)', x, len (control_array)
           temp = CROBInfo(control_array[x][0], control_array[x][1], 0, 0)
           print 'binaryArray[x] = control_array[x]', binaryArray[x], control_array[x], temp
           binaryArray[x] = temp
         
       print 'done... processing array'       
 
       #req = MDNPRequest(masterSesn)
       self.MDNPReq.BinaryCommand(Enum.ToObject(MDNPRequest.DNP_FUNCTION_CODE, fc), autoOperate, feedback, feedbackDelay, Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier), 
                                  binaryArray)
       
    def ClassPoll (self,qualifier, maxQuantity, class0, class1, class2, class3, broadcast_flag = False, **kwargs):
        'bool ReadClass(self, DNP_QUALIFIER qualifier, UInt16 maxQuantity, bool class0, bool class1, bool class2, bool class3)'     
        #req = MDNPRequest(masterSesn)
        if not broadcast_flag:
            self.MDNPReq.ReadClass(Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier), maxQuantity, class0, class1, class2, class3)
        else:
            print 'sending broadcast request...'
            self.MDNPBroacastReq.ReadClass(Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier), maxQuantity, class0, class1, class2, class3)
            
        
    def clearRestart (self, broadcast_flag = False):
        #DNPClass.request.ClearRestart()
        if not broadcast_flag:
            self.MDNPReq.ClearRestart()
        else:
            print 'sending broadcast request'
            self.MDNPBroacastReq.ClearRestart()
        
    def IntegrityPoll (self, noEvents, broadcast_flag = False):
        'bool IntegrityPoll(self, bool noEvents)'   
        
        if not broadcast_flag:
            self.MDNPReq.IntegrityPoll(noEvents)
        else:
            print 'Sending Broaccast request'
            self.MDNPBroacastReq.IntegrityPoll(noEvents)
        
    def writeTime(self, broadcast_flag = False):
        
        if not broadcast_flag:
            self.MDNPReq.WriteTime()
        else:
            print 'sending broadcast request'
            self.MDNPBroacastReq.WriteTime()
         
    def EnableUnsolicited (self,Class1, Class2, Class3, broadcast_flag = False):
        
        if not broadcast_flag:
            self.MDNPReq.UnsolEnable(Class1, Class2, Class3)
        else:
            print 'Sending broadcast unsolicited request... EnabledUnsolicited'
            self.MDNPBroacastReq.UnsolEnable(Class1, Class2, Class3)
            

    def DisableUnsolicited (self,Class1, Class2, Class3, broadcast_flag = False):
        
        if not broadcast_flag:
            self.MDNPReq.UnsolDisable(Class1, Class2, Class3)
        else:
            print 'Sending broacast request...DisableUnsolicited'
            self.MDNPBroacastReq.UnsolDisable(Class1, Class2, Class3)
            
    
    def resetLink(self, broadcast_flag = False):
        self.masterSesn.SendLinkReset()
        #print 'Reset Link request sent...'
        
    def FreezeCounters(self, clearRequested, noAckRequested, qualifier, start, stop, feedbackRequested, broadcast_flag = False):
               
        if not broadcast_flag:
            self.MDNPReq.FreezeCounters (clearRequested, noAckRequested, Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier),
                                    start, stop, feedbackRequested)
        else:
            print 'Sending broadcast request'
            self.MDNPBroacastReq.FreezeCounters (clearRequested, noAckRequested, Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier),
                                    start, stop, feedbackRequested)
            
    def InitGenericRequest (self, functionCode, size = 256):
        
        self.MDNPReq.InitGenericRequest( functionCode, size)
    
    def AddObjectHeader (self,group, variation, qualifier, start, stop):
        
        self.MDNPReq.AddObjectHeader(group, variation, Enum.ToObject(MDNPRequest.DNP_QUALIFIER, qualifier),start, stop)            
        
    def AddObjectData (self, data):
        
        self.MDNPReq.AddObjectData (data)
    
    def SendGenericRequest(self):  
        
        self.MDNPReq.SendGenericRequest()
        
    def coldRestart(self):
        
        self.MDNPReq.ColdRestart()
        
    def writeRecordedTime(self):
        self.MDNPReq.WriteRecordedTime()
        
    def disableApplCON(self):
        print 'Disabling application confirm'
        self.masterSesn.AutoApplConfirm = 0
        self.masterSesn.ModifySession()
        
    def enableApplCon (self):
        print 'Enabling application confirm'
        self.masterSesn.AutoApplConfirm = 1
        self.masterSesn.ModifySession()
    
    def sendAppCon(self, SEQ, unsolicited = False):
        print 'sendAppCon> sequence number seq', SEQ
        print 'sendAppCon> unsolicited', unsolicited 
        print 'sendAppCon> SEQ byte', Byte(SEQ)
        self.masterSesn.SendConfirmation (Byte(SEQ), unsolicited)
               
    def handleResponseEvent(self,request,response):
        print 'event fired...'
        print 'printing request', request
        print 'printing response', response
    
        print 'time for request to complete', response.ResponseTime.ToString()
        #print 'printing something', response.Last()
        print 'unsolicited next'
    
        if response:
            print 'will close connection'
            self.reqEventUnSubscribe()
            self.DisableUnsolicited(True,True,True)


def writeDataToLogFile(textLines, logEnable, logFile, Filename):
    
    print 'in writeDataToLogFile logEnable', logEnable
      
    if logEnable:
        logFile.openFile(Filename.Text)
    
        for lines in textLines:
            logFile.saveToFile (lines)
        
        logFile.closeFile()
    
    print '\nend writeDataToLogFile method'      



def main():
    
    sourceIPAddress = '127.0.0.1'   #'192.168.171.182'
    sourcePort = 20182
    sourceAddress = 182
    destIPAddress = '127.0.0.1'    #'192.168.171.171' 
    destPort = 20000
    destAddress = 171

    #openLoopBackUDP(sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress)

    #req = MDNPRequest(masterSesn)
    #print 'printing req to string', req
    myTestClass = DNPClass()
    myTestClass.openLoopBackTCP(sourceIPAddress, sourcePort, sourceAddress, destIPAddress, destPort, destAddress)
    myTestClass.reqEventSubscribe()
    #myTestClass.clearRestart()
    myTestClass.writeTime()
    #myTestClass.close()
    
    #print 'master station from main', masterSesn.ToString
    #masterSesn.UnsolEvents += handleUnsolicitedEvent 
    
    #a = myTestClass(masterChan, masterSesn)
       
    #a.event()
                     

if __name__ == '__main__':
    main() 
           
    
    