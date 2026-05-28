$botPath = "C:\Users\kames\OneDrive\Documents\Bussiness Automation\run_bot.bat"

$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c start `"Instagram Bot`" `"$botPath`""

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0)

Register-ScheduledTask `
    -TaskName "InstagramBot24x7" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -RunLevel Highest `
    -Force

Write-Host "SUCCESS: Bot will now auto-start every time Windows boots!" -ForegroundColor Green
