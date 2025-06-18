"""Direct test runner for extended MilitaryManager tests."""
import asyncio
import sys
from importlib import import_module
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def run_test(test_func, test_name):
    """Run a single test with error handling."""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}".center(80, '='))
    print(f"{'='*80}")
    
    try:
        if asyncio.iscoroutinefunction(test_func):
            await test_func
        else:
            test_func()
        print(f"\n✅ {test_name} - PASSED")
        return True, None
    except Exception as e:
        error = f"{type(e).__name__}: {str(e)}"
        print(f"\n❌ {test_name} - FAILED")
        print(f"Error: {error}")
        import traceback
        traceback.print_exc()
        return False, error

async def main():
    """Run all tests and report results."""
    # Import the test module
    test_module = import_module("tests.test_military_manager_extended")
    
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
    print("RUNNING MILITARY MANAGER TESTS".center(80, '='))
    print("="*80 + "\n")
    
    results = {}
    for test_func, test_name in test_functions:
        success, error = await run_test(test_func, test_name)
        results[test_name] = (success, error)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY".center(80, '='))
    print("="*80 + "\n")
    
    passed = sum(1 for result in results.values() if result[0])
    total = len(results)
    
    for test_name, (success, error) in results.items():
        status = "✅ PASS" if success else f"❌ FAIL: {error}"
        print(f"{test_name}: {status}")
    
    print(f"\n{passed}/{total} tests passed")
    print("\n" + "="*80 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
