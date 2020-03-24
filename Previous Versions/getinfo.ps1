$SetpointPath = "C:\Users\patrick.talley\Documents\Setpoints\"
$Path = $SetpointPath + "SG68023pm all setpoint fixed deadbands.xspt"

$xml = [xml](get-content $Path)
$xml.Load($Path)
$product = $xml.appdata.profilename
$rev = $xml.appdata.profilerevision
$revSpl = $rev.split(".")
$revProf = $revSpl[0] + "." + $revSpl[1]

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

$hmiPath = $HDTDIR + "\S&C Electric\Products\" + $product + "\HMI\" + $revProf + "\" 
Get-ChildItem -Path $hmiPath | Where-Object{$_.extension -eq ".hmidef"}| foreach-object {$_.Fullname}
