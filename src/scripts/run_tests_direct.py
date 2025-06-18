"""
Direct test runner script to help debug test execution.
"""
import sys
import os
import subprocess
from pathlib import Path

def main():
    """Run tests and capture output."""
    print("Running tests with direct output capture...")
    print("-" * 50)
    
    # Run pytest with subprocess and capture output
    cmd = [
        sys.executable,  # Use the same Python interpreter
        "-m", "pytest",
        "tests/test_simple_async.py",
        "-v",
        "-s"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run the command and capture output in real-time
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(line, end='')
    
    # Wait for process to complete
    process.wait()
    print("-" * 50)
    print(f"Test process completed with exit code: {process.returncode}")
    
    return process.returncode

if __name__ == "__main__":
    sys.exit(main())
