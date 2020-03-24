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

$IL6DIR = $HDTDIR + "\S&C Electric\IntelliLink6\"

$DLLPath = $IL6DIR + "SandC.WinKit6.Scripting.dll"

Import-Module $DLLPath

$device = Get-Device -Proto "DNP" -LocalAddress 65432 -PeerAddress 65532
$device.Timeout = 5000
$device.Retries = 0
"device connect..."
if (!$device.ConnectSerial("COM1"))
#if (!$device.ConnectTcp("192.168.150.150", 20000))
{
    Write-Warning $device.Status.Description;
    Exit;
} 

$device.Info | out-file "info.txt"


$SetpointPath = "C:\Users\patrick.talley\Documents\Setpoints\"
$Path = $SetpointPath + "SG68023pm all setpoint fixed deadbands.xspt"

## Read set point 
$xml = [xml](get-content $Path)
$xml.Load($Path)

$xmlAI = ($xml.AppData.Interface.Group.Array | Where-Object {$_.name -match "AnalogInputMap"})
If (Test-Path points.txt){
	Remove-Item points.txt
}
foreach ($index in $xmlAI.Group){
    
    if ($index.Object.'#text' -contains "NoEvent"){}
    else{
        "PointIndex    " + $index.index | out-file points.txt -Append
        $index.Object +  "`n" | out-file points.txt -Append
    }
}
Get-Content .\points.txt | Where-Object {$_ -notmatch 'name'} | Set-Content cleanpoints.csv

## Loading set point into machine
$hmiDef = $HDTDIR + "\S&C Electric\Products\SG68023PM\HMI\6.3\SG68023PM-6.3.9.hmidef"
$dataProvider = Get-DataProvider -HmiDef $hmiDef -VMProvider $device

$res = $dataProvider.LoadSetpoints($Path)
If ($res -eq $false)
{
	Write-Error “Cannot load set points.”
	Exit 1
}


## Generate wave form
# Set basic starting point
# Get analog inputs > write to file
# Go by each index > convert to change for wave form > add delta to original where needed
# Get unsolicited > write to file
# Subtract delta > get unsolicited > write to file