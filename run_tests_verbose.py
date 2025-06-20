"""Test runner script with detailed output for debugging test execution."""
import sys
import os
import subprocess
import unittest
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"{title:^80}")
    print("=" * 80 + "\n")

def run_command(command, cwd=None):
    """Run a command and return its output."""
    print(f"Running: {command}")
    print(f"Working directory: {cwd or os.getcwd()}")
    print("-" * 40)
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Main function to run tests with different configurations."""
    project_root = Path(__file__).parent.absolute()
    tests_dir = project_root / 'tests'
    
    print_header("TEST RUNNER STARTED")
    print(f"Project root: {project_root}")
    print(f"Tests directory: {tests_dir}")
    
    # Add src to Python path if not already there
    src_dir = project_root / 'src'
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    # Run tests with different configurations
    test_configs = [
        # Run with unittest discover
        {
            'name': 'Unittest Discover',
            'command': f'python -m unittest discover -s {tests_dir} -p "test_*.py" -v'
        },
        # Run with pytest
        {
            'name': 'pytest',
            'command': 'python -m pytest tests/ -v'
        },
        # Run with python -m unittest directly
        {
            'name': 'Direct Unittest',
            'command': f'python -m unittest {tests_dir}/test_environment.py -v'
        },
        # Run with nose2
        {
            'name': 'nose2',
            'command': 'python -m nose2 -v'
        }
    ]
    
    # Run each test configuration
    for config in test_configs:
        print_header(f"RUNNING TESTS WITH: {config['name']}")
        success = run_command(config['command'], cwd=project_root)
        status = "SUCCEEDED" if success else "FAILED"
        print(f"\n{config['name']} {status}")
    
    print_header("TEST RUNNER COMPLETED")

if __name__ == "__main__":
    main()
