 Get-Item  | Select FullName, LastWriteTime,                                                                                 
      @{n='SizeMB'; e={[math]::Round($_.Length/1MB, 2)}}                                                                                                          
                                                          
