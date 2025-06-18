#!/usr/bin/env python3
"""
Script to update import statements after project reorganization.
This script helps update import paths to match the new project structure.
"""
import os
import re
from pathlib import Path

# Define the root directory of the project
ROOT_DIR = Path(__file__).parent.absolute()
SRC_DIR = ROOT_DIR / 'src'

# Define the import mappings (old_import: new_import)
IMPORT_MAPPINGS = {
    # Update imports for modules moved to src/scripts
    'from run ': 'from scripts.run ',
    'import run': 'from scripts import run',
    'from simple_bot': 'from scripts.simple_bot',
    'import simple_bot': 'from scripts import simple_bot',
    'from start_sc2': 'from scripts.start_sc2',
    'import start_sc2': 'from scripts import start_sc2',
    
    # Update imports for manager modules
    'from managers.': 'from src.managers.',
    'import managers.': 'from src import managers.',
    
    # Update imports for config
    'from config': 'from src.config',
    'import config': 'from src import config',
}

def update_file_imports(file_path):
    """Update import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply import mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated imports in {file_path.relative_to(ROOT_DIR)}")
            return True
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return False

def main():
    """Update imports in all Python files in the project."""
    updated_count = 0
    
    # Walk through all Python files in the project
    for root, _, files in os.walk(ROOT):
        # Skip virtual environment and cache directories
        if any(part.startswith(('.', '_')) for part in Path(root).parts):
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                if update_file_imports(file_path):
                    updated_count += 1
    
    print(f"\nUpdated imports in {updated_count} files.")
    print("\nNote: You may need to manually verify and fix some imports.")
    print("Run 'python -m pytest' to check for import errors.")

if __name__ == "__main__":
    main()
