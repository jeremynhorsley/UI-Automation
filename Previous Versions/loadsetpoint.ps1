if ($Env:PROCESSOR_ARCHITECTURE -eq "x86") {
    $HDTDIR = $Env:ProgramFiles;
} else {
    $HDTDIR = ${Env:ProgramFiles(x86)}
}
if ($HDTDIR -eq $null) {
	"Could not find path to Scripting dll path: $HDTDIR"	
	return
}

$moduleName = "SandC.WinKit6.Scripting"

$DLLPath = $HDTDIR + "\S&C Electric\IntelliLink6\" + $moduleName + ".dll"

If (!(Get-module $moduleName)) { 
    Import-Module $DLLPath
}

"get-device ..."
$device = Get-Device -Proto "DNP" -LocalAddress 2 -PeerAddress 65532

#if (!$device.ConnectUdp("192.168.0.100", 20000))
#if (!$device.ConnectTcp("192.168.0.100", 20000))

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

"get-dataprovider ..."
$dataProvider = Get-DataProvider -VMProvider $device

if ($dataProvider -eq $null) {
    "Cannot create a data provider"
    return
}

$xsptFile = "C:\Users\igor.elenskiy\Documents\sg6801-1.xspt"

#"saving setpoints to " + $xsptFile + " ..."
#$result = $dataProvider.SaveSetpoints([string[]]("Communication.PointMapping", "Communication.Other"), $xsptFile)
#if (!$result) {
#    “Cannot save set points: ” + $dataProvider.LastError
#    return
#}

"loading setpoints from " + $xsptFile + " ..."
$conversionResult = $dataProvider.LoadSetpoints($xsptFile)

if (-not $conversionResult) {
    "Cannot load setpoints: " + $dataProvider.LastError
    return
}

if ($conversionResult.NotConverted.Count -ne 0 -or  $conversionResult.NotFound.Count -ne 0) {
    "Not Converted AppObjects: " + $conversionResult.NotConverted.Count
    "Not Found AppObjects: " + $conversionResult.NotFound.Count
    return
}

"writing ..."
if (!$dataProvider.WriteObjects($conversionResult.Converted)) {
    "Cannot write setpoint objects: " + $dataProvider.LastError
    return
}

"applying ..."
if (!$dataProvider.WriteObject("SetupMgmtBase.CMD.SetupMgrCommand", "Apply")) {
    "Cannot apply settings: " + $dataProvider.LastError
    return
}

"verifying ..."
$object = $dataProvider.ReadObject("SetupMgmt.DATA.SettingsChangeStatus")

if ($object -eq $null) {
    "Impossible upload setpoints: " + $dataProvider.LastError
    return
}
if ($object.Status -ne "Ok" -or $object.Value -ne "CompletedSuccessfully") {
    "Impossible upload setpoints: " + $dataProvider.Value
    return
}
"Setpoints loaded."

$dataProvider.Close()

if (!$device.LogOff()) {
    "Cannot logoff: " + $device.Status.VerboseDescription
}

$device.Close()

