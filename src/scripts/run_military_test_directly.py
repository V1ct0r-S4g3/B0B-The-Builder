"""Directly run the military manager test with detailed output."""
import sys
import asyncio
from tests.test_military_simple import test_military_manager_initialization, test_async_military_manager

async def run_tests():
    print("=== Starting MilitaryManager Tests ===")
    
    # Run the sync test
    print("\n--- Running test_military_manager_initialization ---")
    try:
        test_military_manager_initialization()
        print("PASS: test_military_manager_initialization")
    except Exception as e:
        print(f"FAIL: test_military_manager_initialization - {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Run the async test
    print("\n--- Running test_async_military_manager ---")
    try:
        await test_async_military_manager()
        print("PASS: test_async_military_manager")
    except Exception as e:
        print(f"FAIL: test_async_military_manager - {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_tests())
