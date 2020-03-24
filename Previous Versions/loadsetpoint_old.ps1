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
$SetpointPath = $SetpointPath + "SG68023pm all setpoint fixed deadbands.xspt"

## Log on 
function Logon($device)
{
	# See whether we have to log in
	if ($device.LogOnRequired -and !$device.LoggedOn)
	{
		$cnt = 0
		while ($cnt -lt 3)
		{
			try
			{
				$cred = Get-Credential -Credential admin
			}
			catch
			{
				$cred = $null
			}

			if ($cred -eq $null)
			{
				break
			}

			$pwd = 	[System.Runtime.InteropServices.Marshal]::PtrToStringBSTR([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($cred.Password))
			if ($device.Logon($cred.UserName, $pwd))
			{
				break
			}

			Write-Host $UserMessages.AuthError
			$cnt++
		}
		if ($cnt -eq 3)
		{			
			ScriptExit $false "You have tried three times. You will be locked out for 5 minutes"
		}
	}
}

Logon($device)

## Loading setpoints   
$hmiDef = $HDTDIR + "\S&C Electric\Products\SG68023PM\HMI\6.3\SG68023PM-6.3.9.hmidef"
$dataProvider = Get-DataProvider -HmiDef $hmiDef -VMProvider $device
$conversionResult = $dataProvider.LoadSetpoints($SetpointPath)

if ($conversionResult.NotConverted.Count -ne 0)
{
    $bInvalids = $false
    # Count the number of invalids
    foreach ($Unconverted in $conversionResult.NotConverted)
    {
        if ($Unconverted.Contains("Invalid"))
        {
           $bInvalids = $true
           break;
        }
    }
    if ($bInvalids)
    {
        if (YesReply "Conversion Results" "Display a list of settings not converted?")
        {
           Write-Host "`n`n-----------Not Converted-----------`n"
           foreach ($Unconverted in $conversionResult.NotConverted)
           {
               if ($Unconverted.Contains("Invalid"))
               {
                    Write-Host $Unconverted
               }                           
           }
        }
    }
}

if ($dataProvider.WriteObjects($conversionResult.Converted))
{
    #WriteDefaultCommandLabels
    
    #Apply the settings
    Write-Host "Applying Settings. This could take up to 25 seconds."     
    $applyCmdAppObject    = "SetupMgmtBase.CMD.SetupMgrCommand"
    $applyStatusAppObject = "SetupMgmtBase.DATA.SetupMgrCommandStatus"
    $applyStatusValid     = "CompletedSuccessfully"
    $retries = 3
    do
    {
        $retries--
        if (!$dataProvider.WriteObject($applyCmdAppObject, "Apply") -and ($retries -eq 0))
        {
            ScriptExit $false ("Could not Apply Settings: "  + $status)
        }
        # Wait for the apply
        Start-Sleep -s 8

        $status = $dataProvider.ReadObject($applyStatusAppObject)
        if (($status -eq $null)  -and ($retries -eq 0))
        {
            ScriptExit $false ("Could not read Apply status")
        }
       
        if (($status.Value -ne $applyStatusValid)  -and ($retries -eq 0))
        {
            $bApplyError = $true
        }
        elseif ($status.Value -eq $applyStatusValid)
        {
            Write-Host "Apply completed successfully"
            break
        }
    }
    while ($retries -gt 0)
}
else
{
    Write-Host "Could not write converted settings"
}