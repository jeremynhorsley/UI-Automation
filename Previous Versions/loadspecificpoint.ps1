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

#########################################################################################
####################### Setup temporary data provider  ############################################
#########################################################################################

#$xsptLoadFile = Read-Host -Prompt 'Input path to setpoint file'

$xsptLoadFile = "C:\Users\patrick.talley\Documents\SetPoints\SG68023pm all setpoint fixed deadbands.xspt"
#$hmiDef = "C:\Program Files (x86)\S&C Electric\Products\SG68023PM\HMI\6.3\SG68023PM-6.3.9.hmidef"

$xml = [xml](get-content $xsptLoadFile)
$xml.Load($xsptLoadFile)
$product = $xml.appdata.profilename
$rev = $xml.appdata.profilerevision
$revSpl = $rev.split(".")
$revProf = $revSpl[0] + "." + $revSpl[1]

$hmiPath = $HDTDIR + "\S&C Electric\Products\" + $product + "\HMI\" + $revProf + "\" 
$hmiDef = Get-ChildItem -Path $hmiPath | Where-Object{$_.extension -eq ".hmidef"}| foreach-object {$_.Fullname}
 if (!(Test-Path $hmiDef))
{
     $msg = "Could not find path to hmi: $hmiDef"
     $success = $false
     $pfarr = $fail             
}

"Setting up temporary profile ..."
$tempProvider = Get-DataProvider -HmiDef $hmiDef
$saveProfs = $tempProvider.Profile.SaveRestoreGroups.RootGroups.Children.FullName 
$saveProfs = $saveProfs | Where-object {$_ -notmatch "Other" -and $_ -notmatch "DNPRouting"}

if ($tempProvider -eq $null) {
    "Cannot create a data provider"    
}

"loading setpoints from " + $xsptLoadFile + " ..."
$conversionResult = $tempProvider.LoadSetpoints($xsptLoadFile)

if (-not $conversionResult) {
    "Cannot load setpoints: " + $tempProvider.LastError    
}

if ($conversionResult.NotConverted.Count -ne 0 -or  $conversionResult.NotFound.Count -ne 0) {
    "Not Converted AppObjects: " + $conversionResult.NotConverted.Count
    "Found AppObjects: " + $conversionResult.NotFound.Count    
}

"writing ..."
if (!$tempProvider.WriteObjects($conversionResult.Converted)) {
    "Cannot write setpoint objects: " + $tempProvider.LastError    
}

$xsptSaveFile = "C:\Users\patrick.talley\Documents\AutomationProj\testload.xspt"
"saving setpoints to " + $xsptSaveFile + " ..."
$result = $tempProvider.SaveSetpoints([string[]]($saveProfs), $xsptSaveFile)
if (!$result) {
    "Cannot save set points: " + $tempProvider.LastError
}

#########################################################################################
####################### Load setpoints wanted into controller ########################################
#########################################################################################

$device = Get-Device -Proto "DNP" -LocalAddress 65432 -PeerAddress 65532
$device.Timeout = 5000
$device.Retries = 0
"device connect ..."
if (!$device.ConnectSerial("COM1")) {
    "Cannot connect: " + $device.Status.VerboseDescription
    return
} else {
	"Connected: " + $device.Info.AppIdent + " (" +
        $device.Info.OSVersion + "," +
        $device.Info.Series + "," +
        $device.Info.AppVersion + ")"
}

if (-not $device.LoggedOn) {
    "device logging ..."
     if (!$device.Logon("Admin", "1135Atlantic")) {
        "Not logged on: " + $device.Status.VerboseDescription
        return
    }
}
"get-dataprovider to controller ..."
$dataProvider = Get-DataProvider -VMProvider $device
$conversionResult = $dataProvider.LoadSetpoints($xsptSaveFile)

if (-not $conversionResult) {
    "Cannot load setpoints: " + $dataProvider.LastError
}

if ($conversionResult.NotConverted.Count -ne 0 -or  $conversionResult.NotFound.Count -ne 0) {
    "Not Converted AppObjects: " + $conversionResult.NotConverted.Count
    "Found AppObjects: " + $conversionResult.NotFound.Count
}

"writing ..."
if (!$dataProvider.WriteObjects($conversionResult.Converted)) {
    $dataProvider.LastError.InnerError # | Get-Member 
    "Cannot write setpoint objects: " + $dataProvider.LastError
}

"applying ..."
if (!$dataProvider.WriteObject("SetupMgmtBase.CMD.SetupMgrCommand", "Apply")) {
    "Cannot apply settings: " + $dataProvider.LastError
}

"verifying ..."
$object = $dataProvider.ReadObject("SetupMgmt.DATA.SettingsChangeStatus")

if ($object -eq $null) {
    "Impossible upload setpoints: " + $dataProvider.LastError
}
if ($object.Status -ne "Ok" -or $object.Value -ne "CompletedSuccessfully") {
    "Impossible upload setpoints: " + $dataProvider.Value
}
"Setpoints loaded."

$dataProvider.Close()

if ($device -ne $null)
	{
		$device.Close()
	}
$hash = @{
    "ConnectType" =  $ConnectType
    "Connect" = $Connect
    "port" =  $port
    "LocalAddr" = $localaddr
    "peeraddr" =  $peeraddr
    "SetPointPath" = $SetpointPath
    "hmiPath" =  $hmipath
    "PassFail" = $pfarr
}

$newRow = New-Object PsObject -Property $hash
Export-Csv out.csv -inputobject $newrow -append -Force

ScriptExit $success $msg