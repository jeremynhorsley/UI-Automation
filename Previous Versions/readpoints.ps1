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
$dataProvider = Get-DataProvider -VMProvider $device
#$lib = (Get-DataProvider -VMProvider $device).Profile.Interfaces.Uri 
#$pm = $lib | Where-Object {$_ -match "DAProductLib1\\Communications\\PointMapping_SG6800_Base"} 

$xsptFile = "C:\Users\patrick.talley\Documents\AutomationProj\test2.xspt"
"saving setpoints to " + $xsptFile + " ..."
$result = $dataProvider.SaveSetpoints([string[]]("Communication.PointMapping"), $xsptFile)
if (!$result) {
    “Cannot save set points: ” + $dataProvider.LastError
    return
}

$xml = [xml](get-content $xsptFile)
$xml.Load($xsptFile)

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
Get-Content .\points.txt | Where-Object {$_ -notmatch 'name'} | Set-Content points2.txt
Remove-Item points.txt
Get-Content .\points2.txt | Where-Object {$_ -notmatch '--'} | Set-Content points3.txt
Remove-Item points2.txt
Get-Content .\points3.txt | Where-Object {$_ -notmatch '^\s*$'} | Set-Content points4.txt
Remove-Item points3.txt
Get-Content .\points4.txt | Foreach-Object {$_ -replace 'PointIndex', "`nPointIndex"} | Set-Content  ("AnalogInputs.csv")
Remove-Item points4.txt

