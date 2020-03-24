$pass = "pass"
$fail = "fail"
$tempPath = $env:TEMP
function ScriptExit($success, [string]$strError=$null)
{

#clean up 
if ($device -ne $null)
{
    $device.Close()
}

if ($success)
{
    Write-Host "Script completed successfully"
    Write-Host "$ConnectType,$Connect,$port,$localaddr,$peeraddr,`n$SetpointPath,`nUsing: $hmiDef `n"
    $returncode = 0
}
else 
{
    Write-Host "Script completed with error. $strError"
    Write-Host "$ConnectType,$Connect,$port,$localaddr,$peeraddr,`n$SetpointPath`nUsing: $hmiDef `n"
    $returncode = 4
}

Exit $returncode

}
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
                $cred = "admin"
            }
            catch
            {
                $cred = $null
            }

            if ($cred -eq $null)
            {
                ScriptExit $false "Cred was null, exiting script"
            }

            $pwd = "1135Atlantic" 	#[System.Runtime.InteropServices.Marshal]::PtrToStringBSTR([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($cred.Password))
            if ($device.Logon($cred, $pwd))
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
if (!(Test-Path $SetpointPath))
{
     $msg = "Could not find path to set points: $SetpointPath"	
     $success = $false
     $pfarr = $fail
}
if(!$pfarr)
{
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

    $device = Get-Device -Proto "DNP" -LocalAddress $localaddr -PeerAddress $peeraddr
    $device.Timeout = 5000
    $device.Retries = 0
    "device connect..."
    if($ConnectType -eq "Serial"){
        if (!$device.ConnectSerial($Connect))
        {
            Write-Warning $device.Status.Description;
            Exit;
        } 
    }
    if($ConnectType -eq "TCP"){
        if (!$device.ConnectTcp($Connect, $port))
        {
            Write-Warning $device.Status.Description;
            Exit;
        } 
    }
    
    Logon $device
    $xml = [xml](get-content $SetpointPath)
    $xml.Load($SetpointPath)
    $product = $xml.appdata.profilename
    $rev = $xml.appdata.profilerevision
    $revSpl = $rev.split(".")
    $revProf = $revSpl[0] + "." + $revSpl[1]

    $hmiPath = $HDTDIR + "\S&C Electric\Products\" + $product + "\HMI\" + $revProf + "\" 
    $hmiDef = Get-ChildItem -Path $hmiPath | Where-Object{$_.extension -eq ".hmidef"}| foreach-object {$_.Fullname}
    ## Loading setpoints   
     if (!(Test-Path $hmiDef))
    {
         $msg = "Could not find path to hmi: $hmiDef"
         $success = $false
         $pfarr = $fail             
    }
    $tempProvider = Get-DataProvider -HmiDef $hmiDef
    $saveProfs = $tempProvider.Profile.SaveRestoreGroups.RootGroups.Children.FullName 
    $saveProfs = $saveProfs | Where-object {$_ -notmatch "Other" -and $_ -notmatch "DNPRouting"}
    
    if ($tempProvider -eq $null) {
    "Cannot create a data provider"    
    }

    "loading setpoints from " + $SetpointPath + " ..."
    $conversionResult = $tempProvider.LoadSetpoints($SetpointPath)

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

    $SetpointPathNew = $tempPath + "\tempsetpoints.xspt"
    "saving setpoints to " + $SetpointPathNew + " ..."
    $result = $tempProvider.SaveSetpoints([string[]]($saveProfs), $SetpointPathNew)
    if (!$result) {
        "Cannot save set points: " + $tempProvider.LastError
    }
    else{

        $dataProvider = Get-DataProvider -HmiDef $hmiDef -VMProvider $device
        $conversionResult = $dataProvider.LoadSetpoints($SetpointPathNew)
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
                    $pfarr = $fail
                    $msg = "Could not Apply Settings: "  + $status
                    $success = $false
                }
                # Wait for the apply
                Start-Sleep -s 8

                $status = $dataProvider.ReadObject($applyStatusAppObject)
                if (($status -eq $null)  -and ($retries -eq 0))
                {
                    $pfarr = $fail
                    $msg = "Could not read apply status"
                    $success = $false
                }
               
                if (($status.Value -ne $applyStatusValid)  -and ($retries -eq 0))
                {
                    $pfarr = $fail
                    $msg = "Could not apply settings"
                    $success = $false
                }
                elseif ($status.Value -eq $applyStatusValid)
                {
                    $pfarr = $pass
                    Write-Host "Apply completed successfully"
                    $success = $true
                    break;
                }
            }
            while ($retries -gt 0)
        }
        else
        {
            $msg = "Could not write converted settings"
            $success = $false
        }
    }
}
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
