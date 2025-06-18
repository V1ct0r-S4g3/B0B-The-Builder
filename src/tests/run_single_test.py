"""Run a single test file with detailed debugging."""
import os
import sys
import importlib.util

def run_test(test_path):
    """Run a single test file with detailed output."""
    print("=" * 80)
    print(f"RUNNING TEST: {test_path}")
    print("=" * 80)
    
    if not os.path.exists(test_path):
        print(f"Error: Test file not found: {test_path}")
        return False
    
    # Add the src directory to the Python path
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    # Get the module name from the file path
    module_name = os.path.splitext(os.path.basename(test_path))[0]
    
    try:
        print(f"\nImporting module: {module_name}")
        spec = importlib.util.spec_from_file_location(module_name, test_path)
        if spec is None:
            print("Error: Could not create module spec")
            return False
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        print(f"Successfully imported {module_name}")
        
        # Try to run test functions
        test_functions = [name for name in dir(module) if name.startswith('test_')]
        print(f"\nFound test functions: {test_functions}")
        
        for func_name in test_functions:
            func = getattr(module, func_name)
            if callable(func):
                print(f"\nRunning {func_name}...")
                try:
                    if func.__code__.co_argcount == 0:  # No arguments
                        func()
                        print(f"{func_name} completed successfully")
                    else:
                        print(f"Skipping {func_name} - requires arguments")
                except Exception as e:
                    print(f"Error in {func_name}: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
        
        return True
        
    except Exception as e:
        print(f"Error running test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        # Default to running test_simple.py if no argument is provided
        test_file = os.path.join('src', 'tests', 'test_simple.py')
    
    success = run_test(test_file)
    print("\n" + "=" * 40)
    print("TEST COMPLETED" if success else "TEST FAILED")
    print("=" * 40)
    sys.exit(0 if success else 1)
