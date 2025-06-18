#!/usr/bin/env python3
"""
Script to move test files from the root tests/ directory to src/tests/.
This script preserves the directory structure and skips files that already exist.
"""
import os
import shutil
from pathlib import Path

def main():
    root_dir = Path(__file__).parent.absolute()
    src_tests = root_dir / 'src' / 'tests'
    root_tests = root_dir / 'tests'
    
    if not root_tests.exists():
        print(f"No tests directory found at {root_tests}")
        return
    
    # Create src/tests if it doesn't exist
    src_tests.mkdir(parents=True, exist_ok=True)
    
    # Walk through the root tests directory
    for root, dirs, files in os.walk(root_tests):
        # Get the relative path from the root tests directory
        rel_path = Path(root).relative_to(root_tests)
        
        # Skip __pycache__ directories
        if '__pycache__' in str(rel_path):
            continue
            
        # Create corresponding directory in src/tests
        dest_dir = src_tests / rel_path
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy files that don't exist in the destination
        for file in files:
            if file == '__pycache__' or file.endswith('.pyc'):
                continue
                
            src_file = Path(root) / file
            dest_file = dest_dir / file
            
            if dest_file.exists():
                print(f"Skipping (exists): {dest_file}")
            else:
                print(f"Moving: {src_file} -> {dest_file}")
                shutil.copy2(src_file, dest_file)
    
    print("\nTest files have been moved to src/tests/")
    print("Please review the changes and update any imports or configurations as needed.")

if __name__ == "__main__":
    main()
