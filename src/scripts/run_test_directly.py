"""Run tests directly with detailed output."""
import sys
import importlib.util
import inspect
from pathlib import Path

def run_test_module(module_path):
    """Run all test functions in a module directly."""
    # Convert path to module path
    module_path = Path(module_path).resolve()
    module_name = module_path.stem
    
    # Import the module
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find all test functions
    test_functions = []
    for name, obj in inspect.getmembers(module):
        if name.startswith('test_') and inspect.isfunction(obj):
            test_functions.append((name, obj))
    
    # Run each test
    print(f"\nRunning {len(test_functions)} tests from {module_name}...")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for name, test_func in test_functions:
        print(f"\nRunning test: {name}")
        print("-" * 60)
        
        try:
            # Check if the function is a coroutine
            if inspect.iscoroutinefunction(test_func):
                import asyncio
                asyncio.run(test_func())
            else:
                test_func()
            print(f"[PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Print summary
    print("\n" + "=" * 80)
    print(f"Test Summary: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return 1 if failed > 0 else 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_test_directly.py <test_file_path>")
        sys.exit(1)
    
    test_file = sys.argv[1]
    sys.exit(run_test_module(test_file))
