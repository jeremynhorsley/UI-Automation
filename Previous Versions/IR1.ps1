if ($Env:PROCESSOR_ARCHITECTURE -eq "x86")
{
    $HDTDIR = $Env:ProgramFiles;
}
else 
{
    $HDTDIR = ${Env:ProgramFiles(x86)}
}

if ($HDTDIR -eq $null)
{
	 "Could not find path to Scripting dll path: $HDTDIR"	
	exit
}

$HDTDIR = $HDTDIR + "\S&C Electric\IntelliLink6\"

$DLLPath = $HDTDIR + "SandC.WinKit6.Scripting.dll"

Import-Module $DLLPath

$DLLPath

# # Get-Module -ListAvailable 
"Get-Module -All:"
Get-Module -All

"Get-Command -Module SandC.WinKit6.Scripting:"
Get-Command -Module SandC.WinKit6.Scripting

"get-device"
$device = Get-Device -Proto "DNP" -LocalAddress 182 -PeerAddress 172
"device timeout"
$device.Timeout = 5000
"device retries"
$device.Retries = 0
"device connect..."
if (!$device.ConnectSerial("COM1"))
#if (!$device.ConnectTcp("192.168.150.150", 20000))
{
    Write-Warning $device.Status.Description;
    Exit;
} else {
	"Seems to connect OK: $device.Status.Description"
}
$file_list = $device.GetFileList("/")
$file_list 

"file_system_info:"
$file_system_info = $device.GetFileSystemInfo()

"file_system_info.ToString"
$file_system_info.ToString()

"AllocatedBlocks. Gets or sets numbers of used blocks:"
 $file_system_info.AllocatedBlocks 
  # Gets or sets numbers of used blocks.  
 
 "AllocatedBytes. Gets numbers of used bytes:"
 $file_system_info.AllocatedBytes 
 # Gets numbers of used bytes.  
 
 "BlockCount. Gets or sets disk size in blocks:"
 $file_system_info.BlockCount 
 # Gets or sets disk size in blocks.  
 
 "BlockSize. Gets or sets numbers bytes in one block:"
 $file_system_info.BlockSize 
 # Gets or sets numbers bytes in one block.  
 
 "FreeBlocks. Gets or sets numbers of free blocks:"
 $file_system_info.FreeBlocks 
 # Gets or sets numbers of free blocks.  
 
 "FreeBytes. Gets numbers of free bytes:"
 $file_system_info.FreeBytes 
 # Gets numbers of free bytes.  
 
 "Serial. Gets or sets disk name:"
 $file_system_info.Serial 
 # Gets or sets disk name  
 
 "Size. Gets disk size in bytes:"
 $file_system_info.Size 
 # Gets disk size in bytes.  
