# System and Environment Check Script
$outputFile = "system_check.txt"

# Clear previous output
if (Test-Path $outputFile) {
    Remove-Item $outputFile
}

# Function to write output
function Write-OutputToFile {
    param([string]$Message)
    Add-Content -Path $outputFile -Value $Message
    Write-Host $Message
}

# System Information
Write-OutputToFile "=== SYSTEM INFORMATION ==="
Write-OutputToFile "Computer Name: $env:COMPUTERNAME"
Write-OutputToFile "OS Version: $([System.Environment]::OSVersion.VersionString)"
Write-OutputToFile "System Directory: $env:SystemRoot"
Write-OutputToFile "Current User: $env:USERNAME"
Write-OutputToFile "Current Directory: $(Get-Location)"

# Python Information
Write-OutputToFile "`n=== PYTHON INFORMATION ==="
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if ($pythonPath) {
    Write-OutputToFile "Python Executable: $pythonPath"
    $pythonVersion = & python --version 2>&1
    Write-OutputToFile "Python Version: $pythonVersion"
    
    # Check Python packages
    Write-OutputToFile "`nInstalled Packages:"
    & pip list --format=freeze 2>&1 | ForEach-Object { 
        if ($_ -match '^([^=]+)==([^=]+)$') {
            Write-OutputToFile "  $($matches[1]) ($($matches[2]))"
        }
    }
} else {
    Write-OutputToFile "Python is not in the system PATH"
}

# Environment Variables
Write-OutputToFile "`n=== ENVIRONMENT VARIABLES ==="
Write-OutputToFile "PATH: $env:PATH"
Write-OutputToFile "PYTHONPATH: $env:PYTHONPATH"
Write-OutputToFile "SC2PATH: $env:SC2PATH"

# Check SC2 Installation
Write-OutputToFile "`n=== STARBOT II CHECK ==="
$sc2Path = "D:\Battle.net\StarCraft2"
if (Test-Path $sc2Path) {
    Write-OutputToFile "StarCraft II found at: $sc2Path"
    
    # Check for SC2 executable
    $sc2Exe = Get-ChildItem -Path $sc2Path -Recurse -Filter "SC2_x64.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($sc2Exe) {
        Write-OutputToFile "SC2 Executable: $($sc2Exe.FullName)"
        Write-OutputToFile "SC2 Version: $($sc2Exe.VersionInfo.FileVersion)"
    } else {
        Write-OutputToFile "SC2 executable not found in: $sc2Path"
    }
} else {
    Write-OutputToFile "StarCraft II not found at: $sc2Path"
}

Write-OutputToFile "`nCheck completed. Output saved to: $(Join-Path (Get-Location) $outputFile)"
