if(test-path out.csv)
{
    Remove-Item out.csv
}
$headers = "ConnectType","Connect","port","LocalAddr","peeraddr","SetPointPath","hmiPath","PassFail"
$psObject = New-Object psObject
foreach($header in $headers)
{
    Add-Member -InputObject $psObject -MemberType noteproperty -Name $header -Value ""
}
$psObject | Export-csv "out.csv" -NoTypeInformation

$testcsv = import-csv "devicefile.csv" 
foreach($test in $testcsv)
{
    $ConnectType = $test.ConnectType
    $Connect = $test.Connect
    $port = $test.Port
    $localaddr = $test.LocalAddr
    $peeraddr = $test.peeraddr
    $SetpointPath = $test.SetPointPath
    .\loadsetpoints.ps1 -ConnectType $ConnectType -Connect $Connect -port $port -localaddr $LocalAddr -peeraddr $peeraddr -SetpointPath $SetpointPath 
}


