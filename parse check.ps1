 $err = $null                                                                                                                                                      
  $null = [System.Management.Automation.Language.Parser]::ParseFile(                                                                                                
      '', [ref]$null, [ref]$err)                                                                                     
  $err | Format-List Message, Extent            

========
$err = $null                                                                                                                                                      
  $null = [System.Management.Automation.Language.Parser]::ParseFile(                                                                                                
      '', [ref]$null, [ref]$err)
  if ($err) { Write-Host 'STILL BROKEN' -F Red; $err } else { Write-Host 'OK' -F Green }  
