$ErrorActionPreference='Stop'
$Run=Join-Path $PSScriptRoot 'run-device-forge.ps1'
$Action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Run`""
$Trigger=New-ScheduledTaskTrigger -AtLogOn
$Principal=New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName 'Codestra Device Forge' -Action $Action -Trigger $Trigger -Principal $Principal -Force | Out-Null
Write-Output 'Scheduled task registered.'
