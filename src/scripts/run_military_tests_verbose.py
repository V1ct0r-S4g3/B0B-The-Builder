"""Run military manager tests with verbose output."""
import sys
import importlib.util
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def run_test(test_func, test_name):
    """Run a single test with error handling."""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}".center(80, '='))
    print(f"{'='*80}\n")
    
    try:
        if asyncio.iscoroutinefunction(test_func):
            await test_func
        else:
            test_func()
        print(f"\n✅ {test_name} - PASSED")
        return True
    except Exception as e:
        print(f"\n❌ {test_name} - FAILED")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test runner function."""
    # Import the test module
    test_file = Path("tests/test_military_manager_extended.py")
    spec = importlib.util.spec_from_file_location("test_military_extended", test_file)
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
    print("\n" + "="*80)
    print("STARTING MILITARY MANAGER TESTS".center(80, '='))
    print("="*80 + "\n")
    
    passed = 0
    failed = 0
    
    for test_func, test_name in test_functions:
        success = await run_test(test_func, test_name)
        if success:
            passed += 1
        else:
            failed += 1
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY".center(80, '='))
    print(f"{'='*80}\n")
    print(f"Total Tests: {passed + failed}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"\n{'='*80}\n")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
