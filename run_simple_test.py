"""
Simple test script to verify test runner functionality.
"""
import sys
import os

def main():
    print("=" * 80)
    print("SIMPLE TEST RUNNER VERIFICATION")
    print("=" * 80)
    print(f"Python Executable: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    print("\nEnvironment Variables:")
    for key in sorted(os.environ.keys()):
        if 'PYTHON' in key or 'PATH' in key:
            print(f"{key} = {os.environ[key]}")
    
    # Try to import test module
    print("\nAttempting to import test module...")
    try:
        import tests.test_runner
        print("✓ Successfully imported tests.test_runner")
    except Exception as e:
        print(f"✗ Failed to import test module: {e}")
    
    # Try to run the test runner directly
    print("\nAttempting to run test runner...")
    try:
        from tests import test_runner
        print("✓ Successfully imported test_runner module")
        print("\nTest Runner Output:")
        print("-" * 80)
        test_runner.main()
    except Exception as e:
        print(f"✗ Failed to run test_runner: {e}")

if __name__ == "__main__":
    main()
