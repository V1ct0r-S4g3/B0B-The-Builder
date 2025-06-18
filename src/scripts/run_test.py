"""Simple test runner to verify test execution."""
import sys
import os
import subprocess

def run_test():
    """Run a test and capture its output."""
    # Print Python and pytest info
    print("Python and Pytest Info:")
    print("-" * 50)
    subprocess.run([sys.executable, "--version"], check=True)
    subprocess.run([sys.executable, "-m", "pytest", "--version"], check=True)
    
    # Run a simple test
    print("\nRunning simple test:")
    print("-" * 50)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_async_simple.py", "-v", "-s"],
        check=False,
        capture_output=True,
        text=True
    )
    
    # Print the results
    print("\nTest Output:")
    print("-" * 50)
    print(result.stdout)
    
    if result.stderr:
        print("\nError Output:")
        print("-" * 50)
        print(result.stderr)
    
    print("-" * 50)
    print(f"Test completed with return code: {result.returncode}")
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_test())
