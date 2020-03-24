if(test-path comparison.csv)
{
    Remove-Item comparison.csv
}
$headers = "Label", "ScreenValue","DNPValue","PassFail"
$psObject = New-Object psObject
foreach($header in $headers)
{
    Add-Member -InputObject $psObject -MemberType noteproperty -Name $header -Value ""
}
$psObject | Export-csv "comparison.csv" -NoTypeInformation

$screencsv = import-csv "meteringData.csv" 
$dnpcsv = import-csv "output.csv"
$swRegex = '([Sw].[1-9])'

foreach($reading in $screencsv)
{
    $current = $FALSE
    $neutral = $FALSE
    $voltage = $FALSE
    $angle = $FALSE
    $cosangle = $FALSE
    $kvar = $FALSE

    $screenLabel = $reading.Label
    if ($screenLabel.contains('Sw'))
    {
        $screenValue = $reading.Value
        $screenLabel -match $swRegex | out-null
        $screenSwitch = $matches[0]
        $screenSwitch = $screenSwitch.Substring($screenSwitch.Length-1)
        
        if ($screenLabel.contains('Current'))
        {
            if ($screenLabel.contains('CurFlow'))
            {
            }
            else
            {
                $current = $TRUE
                $phase = $screenLabel.Substring($screenLabel.Length-1)
            }
        }
        elseif ($screenLabel.contains('Neutral'))
        {
            $neutral = $TRUE
            $phase = "neutral"
        }
        elseif ($screenLabel.contains('Voltage'))
        {
            $voltage = $TRUE
            $phase = $screenLabel.Substring($screenLabel.Length-1)
        }
        elseif ($screenLabel.contains('Angle') -and ($screenLabel.contains('Cos')))
        {
            $cosangle = $TRUE
            $phase = $screenLabel.Substring($screenLabel.Length-2, 1)
        }
        elseif ($screenLabel.contains('Angle'))
        {
            $angle = $TRUE
            $phase = $screenLabel.Substring($screenLabel.Length-1)
        }
        elseif ($screenLabel.contains('kVAR'))
        {
            $kvar = $TRUE
            $phase = $screenLabel.Substring($screenLabel.Length-1)
        }
        
        foreach($response in $dnpcsv)
        {
            $dnpLabel = $response.label
            $dnpValue = $response.value
            if ($current)
            {
                if ($dnpLabel.contains("CurrentPole") -and $dnpLabel.contains($phase) -and $dnpLabel.contains($screenSwitch))
                {
                    $passfail = ($dnpValue -eq $screenValue)
                    $hash = @{
                        "Label" =  $dnpLabel
                        "ScreenValue" = $screenValue
                        "DNPValue" =  $dnpValue
                        "PassFail" = $passfail
                    }

                    $newRow = New-Object PsObject -Property $hash
                    Export-Csv comparison.csv -inputobject $newrow -append -Force
                }
            }
            elseif ($neutral)
            {
                if ($dnpLabel.contains("Neutral") -and $dnpLabel.contains($screenSwitch))
                {
                    $passfail = ($dnpValue -eq $screenValue)
                    $hash = @{
                        "Label" =  $dnpLabel
                        "ScreenValue" = $screenValue
                        "DNPValue" =  $dnpValue
                        "PassFail" = $passfail
                    }

                    $newRow = New-Object PsObject -Property $hash
                    Export-Csv comparison.csv -inputobject $newrow -append -Force
                }
            }
            elseif ($voltage)
            {
                if ($dnpLabel.contains("VoltagePole") -and $dnpLabel.contains($phase) -and $dnpLabel.contains($screenSwitch))
                {
                    $passfail = ($dnpValue -eq $screenValue)
                    $hash = @{
                        "Label" =  $dnpLabel
                        "ScreenValue" = $screenValue
                        "DNPValue" =  $dnpValue
                        "PassFail" = $passfail
                    }

                    $newRow = New-Object PsObject -Property $hash
                    Export-Csv comparison.csv -inputobject $newrow -append -Force
                }
            }
            elseif ($cosangle)
            {
                if ($dnpLabel.contains("CurrentPole") -and $dnpLabel.contains($phase) -and $dnpLabel.contains($screenSwitch))
                {
                    $passfail = ($dnpValue -eq $screenValue)
                    $hash = @{
                        "Label" =  $dnpLabel
                        "ScreenValue" = $screenValue
                        "DNPValue" =  $dnpValue
                        "PassFail" = $passfail
                    }

                    $newRow = New-Object PsObject -Property $hash
                    Export-Csv comparison.csv -inputobject $newrow -append -Force
                }
            }
            elseif ($angle)
            {
                if ($dnpLabel.contains("PhaseAngle") -and $dnpLabel.contains($phase) -and $dnpLabel.contains($screenSwitch))
                {
                    $passfail = ($dnpValue -eq $screenValue)
                    $hash = @{
                        "Label" =  $dnpLabel
                        "ScreenValue" = $screenValue
                        "DNPValue" =  $dnpValue
                        "PassFail" = $passfail
                    }

                    $newRow = New-Object PsObject -Property $hash
                    Export-Csv comparison.csv -inputobject $newrow -append -Force
                }
            }
            elseif ($kvar)
            {
                if ($dnpLabel.contains("KVARs") -and $dnpLabel.contains($phase) -and $dnpLabel.contains($screenSwitch))
                {
                    $passfail = ($dnpValue -eq $screenValue)
                    $hash = @{
                        "Label" =  $dnpLabel
                        "ScreenValue" = $screenValue
                        "DNPValue" =  $dnpValue
                        "PassFail" = $passfail
                    }

                    $newRow = New-Object PsObject -Property $hash
                    Export-Csv comparison.csv -inputobject $newrow -append -Force
                }
            }
        }
    }
}

$data = Import-CSV comparison.csv |  sort Label -Unique
$data | Export-Csv cleancomparison.csv
Remove-Item comparison.csv
