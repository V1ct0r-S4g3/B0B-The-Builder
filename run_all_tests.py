"""
Test runner script for the SC2 bot project.

This script discovers and runs all tests in the project.
"""
import os
import sys
import unittest
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_runner.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('test_runner')

def discover_and_run_tests():
    """Discover and run all tests in the project."""
    logger.info("Starting test discovery...")
    
    # Add the project root to the Python path
    project_root = str(Path(__file__).parent.resolve())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        start_dir=os.path.join(project_root, 'src', 'tests'),
        pattern='test_*.py',
        top_level_dir=project_root
    )
    
    logger.info(f"Discovered {test_suite.countTestCases()} test cases")
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2, failfast=False)
    result = test_runner.run(test_suite)
    
    # Log the results
    if result.wasSuccessful():
        logger.info("All tests passed!")
    else:
        logger.error("Some tests failed!")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("STARTING TEST RUN")
    logger.info("=" * 50)
    
    success = discover_and_run_tests()
    
    logger.info("=" * 50)
    logger.info("TEST RUN COMPLETED")
    logger.info("=" * 50)
    
    sys.exit(0 if success else 1)
