# Parameters
$taskName = "AINewsUpdateTask"
$taskDescription = "Runs the AI News Automation update script"
$scriptPath = "$PSScriptRoot\run_news_update.bat"
$workingDir = $PSScriptRoot

# Create the scheduled task action
$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument "/c `"$scriptPath`"" -WorkingDirectory $workingDir

# Create the scheduled task trigger (runs every 30 minutes)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30)

# Register the scheduled task
Register-ScheduledTask -TaskName $taskName -Description $taskDescription -Action $action -Trigger $trigger -RunLevel Highest -Force

Write-Host "Scheduled task '$taskName' has been created successfully." -ForegroundColor Green
Write-Host "The task will run every 30 minutes."
