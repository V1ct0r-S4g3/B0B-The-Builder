"""Run extended military manager tests with detailed output."""
import asyncio
import importlib.util
import sys

def print_header(text):
    """Print a formatted test header."""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80)

async def run_test_case(test_func, test_name):
    """Run a single test case with error handling."""
    print(f"\nRunning test: {test_name}...")
    try:
        if asyncio.iscoroutinefunction(test_func):
            await test_func
        else:
            test_func()
        print(f"✅ PASS: {test_name}")
        return True
    except Exception as e:
        print(f"❌ FAIL: {test_name}")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def run_tests():
    """Run all test cases with detailed output."""
    # Import the test module
    spec = importlib.util.spec_from_file_location(
        "test_military_manager_extended", 
        "tests/test_military_manager_extended.py"
    )
    test_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_module)
    
    # Get all test functions
    test_functions = [
        (test_module.test_strategy_management, "Strategy Management"),
        (test_module.test_unit_production, "Unit Production"),
        (test_module.test_combat_management, "Combat Management"),
        (test_module.test_build_order_execution, "Build Order Execution"),
        (test_module.test_upgrade_management, "Upgrade Management"),
        (test_module.test_emergency_supply, "Emergency Supply"),
        (test_module.test_army_composition, "Army Composition"),
    ]
    
    # Run tests
    print_header("STARTING MILITARY MANAGER TESTS")
    passed = 0
    failed = 0
    
    for test_func, test_name in test_functions:
        success = await run_test_case(test_func, test_name)
        if success:
            passed += 1
        else:
            failed += 1
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"Total Tests: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print("\n" + "=" * 80)
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
