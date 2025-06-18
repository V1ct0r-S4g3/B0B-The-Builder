"""Direct test runner for EconomyManager tests."""
import sys
import unittest
import asyncio

# Add the tests directory to the path
sys.path.append('.')

# Import the test case
from tests.test_economy_direct import TestEconomyManager

async def run_tests():
    """Run the EconomyManager tests."""
    print("\n" + "="*80)
    print("RUNNING ECONOMY MANAGER TESTS")
    print("="*80)
    
    # Set up test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestEconomyManager)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    return not result.wasSuccessful()

if __name__ == "__main__":
    # Run the async test function
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
