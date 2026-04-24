  Get-ChildItem 'C:\Windows\System32\Tasks' -Recurse -File |                                                                                                                                                              
    Where-Object { $_.Name -match '' } |                                                                                                                                              
    Select-Object FullName, LastWriteTime, CreationTime,                                                                                                                                                                  
                  @{n='Author';e={([xml](Get-Content $_.FullName)).Task.RegistrationInfo.Author}},                                                                                                                        
                  @{n='RegDate';e={([xml](Get-Content $_.FullName)).Task.RegistrationInfo.Date}},                                                                                                                         
                  @{n='Trigger';e={([xml](Get-Content $_.FullName)).Task.Triggers.CalendarTrigger.StartBoundary}}  



    Get-WinEvent -LogName 'Microsoft-Windows-TaskScheduler/Operational' -MaxEvents 5000 |                                                                                                                                   
    Where-Object { $_.Message -match '' -and $_.Id -in 106,140,141,142 } |                                                                                                                            
    Select-Object TimeCreated, Id,                                                                                                                                                                                        
                  @{n='Event';e={ switch($_.Id){106='REGISTERED';140='UPDATED';141='DELETED';142='DISABLED'} }},                                                                                                          
                  @{n='User';e={ try { ([System.Security.Principal.SecurityIdentifier]$_.UserId).Translate([System.Security.Principal.NTAccount]).Value } catch { $_.UserId } }} |                                        
    Sort-Object TimeCreated       



     Get-WinEvent -LogName Security -FilterHashtable @{Id=4698,4702; StartTime=(Get-Date).AddYears(-2)} -ErrorAction SilentlyContinue |                                                                                      
    Where-Object { $_.Message -match '' } |                                                                                                                                                           
    Select-Object TimeCreated, Id,                                                                                                                                                                                        
                  @{n='Event';e={ switch($_.Id){4698='CREATED';4702='UPDATED'} }},                                                                                                                                        
                  @{n='User';e={ "$($_.Properties[1].Value)\$($_.Properties[2].Value)" }} |                                                                                                                               
    Sort-Object TimeCreated  
