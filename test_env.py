"""
Test script to verify the Python environment and basic functionality.
"""
import os
import sys
import platform
import importlib

def check_python_version():
    """Check Python version and environment."""
    print("=" * 80)
    print("PYTHON ENVIRONMENT CHECK")
    print("=" * 80)
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Python Path: {sys.path}")

def check_imports():
    """Check if required packages are installed."""
    print("\n" + "=" * 80)
    print("IMPORT CHECKS")
    print("=" * 80)
    
    packages = [
        'sc2',
        'numpy',
        'loguru',
        'pytest',
        'unittest',
        'typing'
    ]
    
    for package in packages:
        try:
            module = importlib.import_module(package)
            print(f"✓ {package}: {getattr(module, '__version__', 'version not found')}")
        except ImportError as e:
            print(f"✗ {package}: Not installed ({e})")

def check_test_discovery():
    """Check if tests can be discovered."""
    print("\n" + "=" * 80)
    print("TEST DISCOVERY")
    print("=" * 80)
    
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    if not os.path.isdir(test_dir):
        print(f"✗ Test directory not found: {test_dir}")
        return
    
    print(f"Test directory: {test_dir}")
    
    # List Python files in test directory
    test_files = []
    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    
    if not test_files:
        print("✗ No test files found in test directory")
        return
    
    print(f"Found {len(test_files)} test files:")
    for i, test_file in enumerate(test_files, 1):
        print(f"  {i}. {os.path.relpath(test_file, os.path.dirname(__file__))}")
    
    # Try to import each test file
    print("\nTesting imports:")
    for test_file in test_files:
        rel_path = os.path.relpath(test_file, os.path.dirname(__file__))
        module_name = os.path.splitext(rel_path.replace(os.path.sep, '.'))[0]
        
        try:
            module = importlib.import_module(module_name)
            print(f"✓ Imported: {module_name}")
        except Exception as e:
            print(f"✗ Failed to import {module_name}: {str(e)}")

def main():
    """Run all checks."""
    try:
        check_python_version()
        check_imports()
        check_test_discovery()
        print("\nEnvironment check completed!")
        return 0
    except Exception as e:
        print(f"\nError during environment check: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
