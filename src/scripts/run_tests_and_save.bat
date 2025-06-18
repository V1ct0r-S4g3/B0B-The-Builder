@echo off
setlocal enabledelayedexpansion

set OUTPUT_FILE=test_output_%DATE:/=-%_%TIME::=-%.txt
echo Running tests and saving output to %OUTPUT_FILE%

:: Run the tests and capture output
python -c "
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

try:
    # Import and run the test module directly
    import run_military_tests_verbose
    success = True
except Exception as e:
    success = False
    print(f'Error running tests: {e}', file=old_stderr)

# Get the captured output
out = sys.stdout.getvalue()
err = sys.stderr.getvalue()

# Restore stdout/stderr
sys.stdout = old_stdout
sys.stderr = old_stderr

# Print the output
print(out)
if err:
    print('Errors:', err, file=old_stderr)

# Write to file
with open(r'%OUTPUT_FILE%', 'w', encoding='utf-8') as f:
    f.write('=== TEST OUTPUT ===\n')
    f.write(out)
    if err:
        f.write('\n=== ERRORS ===\n')
        f.write(err)
    f.write('\n=== END OF TEST OUTPUT ===')
"

echo.
echo Test output saved to %OUTPUT_FILE%
pause
