#!/usr/bin/env python3
"""
Test runner script for the SC2 bot.

This script discovers and runs all tests in the tests directory.
"""
import sys
import pytest
import os
from pathlib import Path

def run_tests():
    """Run all tests and return the exit code."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.absolute()
    src_dir = project_root  # The src directory is the project root
    
    # Add src to Python path
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    # Change to the src directory (where pytest.ini is located)
    os.chdir(src_dir)
    
    # Run pytest with coverage for our packages
    return pytest.main([
        '--cov=src.managers',  # Generate coverage for managers package
        '--cov=src.bot',       # Generate coverage for bot package
        '--cov-report=term-missing',  # Show missing lines in coverage
    ])

if __name__ == "__main__":
    sys.exit(run_tests())
