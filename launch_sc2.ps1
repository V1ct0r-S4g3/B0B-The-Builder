# Simple SC2 Launcher
$logPath = "D:\SC2 Bot\B0B\sc2_launch.log"
$sc2Path = "D:\Battle.net\StarCraft2\Versions\Base94137\SC2_x64.exe"
$arguments = @(
    "-listen", "127.0.0.1",
    "-port", "8167",
    "-displayMode", "0",
    "-windowwidth", "1024",
    "-windowheight", "768",
    "-noaudio"
)

# Log start
"Starting SC2 at $(Get-Date)" | Out-File $logPath -Force
"SC2 Path: $sc2Path" | Out-File $logPath -Append
"Working Directory: $(Get-Location)" | Out-File $logPath -Append
"Arguments: $($arguments -join ' ')" | Out-File $logPath -Append

try {
    # Start SC2 process
    $process = Start-Process -FilePath $sc2Path -ArgumentList $arguments -PassThru -NoNewWindow -Wait
    
    # Log process info
    "Process ID: $($process.Id)" | Out-File $logPath -Append
    "Exit Code: $($process.ExitCode)" | Out-File $logPath -Append
    "Exit Time: $(Get-Date)" | Out-File $logPath -Append
    
    if ($process.ExitCode -eq 0) {
        "SC2 exited successfully" | Out-File $logPath -Append
    } else {
        "SC2 failed with exit code: $($process.ExitCode)" | Out-File $logPath -Append
    }
}
catch {
    "Error starting SC2: $_" | Out-File $logPath -Append
}

# Show the log
Get-Content $logPath
