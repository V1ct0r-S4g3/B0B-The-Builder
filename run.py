#!/usr/bin/env python3
"""
Main entry point for running the SC2 bot.
This script provides backward compatibility with the old project structure.
It imports and runs the main bot from the new src directory structure.
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the main function from the new location
from src.scripts.run import main

if __name__ == "__main__":
    sys.exit(main())
