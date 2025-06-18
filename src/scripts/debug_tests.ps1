Write-Host "=== Python Environment Debug ==="
Write-Host "Python Version:" -NoNewline
python --version

Write-Host "`nPython Executable:" -NoNewline
python -c "import sys; print(sys.executable)"

Write-Host "`nPython Path:"
python -c "import sys; print('\n'.join(sys.path))"

Write-Host "`n=== Running Simple Test ==="
python -c "print('Hello from Python!'); import pytest; print(f'pytest version: {pytest.__version__}')"

Write-Host "`n=== Running Basic Test File ==="
python -m pytest tests/test_discovery.py -v -s

Write-Host "`n=== Running MilitaryManager Test ==="
python -m pytest tests/test_military_simple.py -v -s

Write-Host "`nDebug information written to debug_output.txt"
Read-Host -Prompt "Press Enter to continue"
