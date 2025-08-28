# Create or update scheduled task for news updates
$taskName = "UpdateNewsContent"
$taskDescription = "Update news website content 5 times daily"
$workingDir = "C:\Projects\ai-news-automation"
$executablePath = "$workingDir\update_news.bat"

# Create task action
$action = New-ScheduledTaskAction `
    -Execute $executablePath `
    -WorkingDirectory $workingDir

# Create trigger for running every 4.8 hours (5 times per day)
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At 12am `
    -RepetitionInterval (New-TimeSpan -Hours 4 -Minutes 48) `
    -RepetitionDuration (New-TimeSpan -Days 1)

# Set task settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -RunOnlyIfNetworkAvailable

# Create task principal (run as SYSTEM)
$principal = New-ScheduledTaskPrincipal `
    -UserID "NT AUTHORITY\SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

# Register the task
$task = Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description $taskDescription `
    -Force

Write-Host "Task '$taskName' has been created successfully."
Write-Host "Testing task..."

# Start the task
Start-ScheduledTask -TaskName $taskName

# Wait a few seconds
Start-Sleep -Seconds 5

# Get the task status
$taskInfo = Get-ScheduledTaskInfo -TaskName $taskName
Write-Host "Last run time: $($taskInfo.LastRunTime)"
Write-Host "Last result: $($taskInfo.LastTaskResult)"
