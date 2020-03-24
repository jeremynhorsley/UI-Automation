$testcsv = import-csv "devicefile.csv" 
$pass = "Pass"
$fail = "Fail"
$pfarr = @()
foreach($test in $testcsv)
{
  
    $ConnectType = $test.ConnectType
    $Connect = $test.Connect
    $port = $test.Port
    $localaddr = $test.LocalAddr
    $peeraddr = $test.peeraddr
    $SetpointPath = $test.SetPointPath
    $hmipath = $test.hmiPath
   

    if (!(Test-Path $SetpointPath))
    {
         "Could not find path to set points: $SetpointPath"	
        $pfarr += ,$fail
    }
    else{
   
  
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
        $hmiDef = $HDTDIR + $hmipath 
         if (!(Test-Path $hmiDef))
        {
             "Could not find path to hmi: $hmiDef"
             $pfarr += ,$fail             
        }
        else{

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
                echo "$ConnectType,$Connect,$port,$localaddr,$peeraddr,$SetpointPath,$hmipath"
                $applyCmdAppObject    = "SetupMgmtBase.CMD.SetupMgrCommand"
                $applyStatusAppObject = "SetupMgmtBase.DATA.SetupMgrCommandStatus"
                $applyStatusValid     = "CompletedSuccessfully"
                $retries = 3
                do
                {
                    $retries--
                    if (!$dataProvider.WriteObject($applyCmdAppObject, "Apply") -and ($retries -eq 0))
                    {
                        $pfarr += ,$fail
                        ScriptExit $false ("Could not Apply Settings: "  + $status)
                    }
                    # Wait for the apply
                    Start-Sleep -s 8

                    $status = $dataProvider.ReadObject($applyStatusAppObject)
                    if (($status -eq $null)  -and ($retries -eq 0))
                    {
                        $pfarr += ,$fail
                        ScriptExit $false ("Could not read Apply status")
                    }
                   
                    if (($status.Value -ne $applyStatusValid)  -and ($retries -eq 0))
                    {
                        $bApplyError = $true
                    }
                    elseif ($status.Value -eq $applyStatusValid)
                    {
                        $pfarr += ,$pass
                        Write-Host "Apply completed successfully"
                        break;
                    }
                }
                while ($retries -gt 0)
            }
            else
            {
                Write-Host "Could not write converted settings"
            }
        }
    }
}

$i = 0
foreach ($item in $testcsv)  
{  
    $item | Add-Member -name "PassFail" -value $pfarr[$i] -MemberType NoteProperty  
    $i += 1
}  
$testcsv | export-csv out.csv -noType  
