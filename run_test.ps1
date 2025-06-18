$ErrorActionPreference = "Stop"

# Set up paths
$projectRoot = $PSScriptRoot
$testFile = Join-Path $projectRoot "src\tests\test_hello.py"
$outputFile = Join-Path $projectRoot "test_output.log"

# Set Python path
$env:PYTHONPATH = $projectRoot

# Run the test and capture output
Write-Host "Running test: $testFile"
Write-Host "Output will be saved to: $outputFile"

# Run the test with unbuffered output
python -u -m unittest $testFile -v 2>&1 | Tee-Object -FilePath $outputFile

# Display the output
Write-Host "`n=== Test Output ==="
Get-Content $outputFile -Tail 20
