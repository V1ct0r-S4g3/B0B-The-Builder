"""
Enhanced test runner script to execute all tests and capture detailed outputs.
"""
import os
import sys
import unittest
import logging
import traceback
from datetime import datetime
from pathlib import Path
from io import StringIO

# Set up directories
TEST_RESULTS_DIR = Path(__file__).parent / 'results'
TEST_LOGS_DIR = Path(__file__).parent / 'logs'

# Create directories if they don't exist
TEST_RESULTS_DIR.mkdir(exist_ok=True)
TEST_LOGS_DIR.mkdir(exist_ok=True)

class TestResultWithLogging(unittest.TextTestResult):
    """Custom test result class with enhanced logging."""
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.successes = []
        self.test_outputs = {}
        
    def startTest(self, test):
        """Called when the given test is about to be run."""
        super().startTest(test)
        self._test_output = StringIO()
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = sys.stderr = self._test_output
        
    def stopTest(self, test):
        """Called when the given test has been run."""
        super().stopTest(test)
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        self.test_outputs[test] = self._test_output.getvalue()
        self._test_output.close()
        
    def addSuccess(self, test):
        """Called when a test passes."""
        super().addSuccess(test)
        self.successes.append(test)
        
    def printErrors(self):
        """Print all the error and failure messages."""
        self.stream.writeln()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)
        
        # Print summary
        self.stream.writeln(self.separator2)
        run = self.testsRun
        self.stream.writeln(f"Ran {run} test{'s' if run != 1 else ''} in "
                          f"{self.getTotalTime():.3f}s")
        self.stream.writeln()
        
        # Print success count if there are any
        if self.successes:
            self.stream.writeln(f"OK (successes={len(self.successes)})")
        
        # Print failure and error counts if any
        if self.failures:
            self.stream.writeln(f"FAILED (failures={len(self.failures)})")
        if self.errors:
            self.stream.writeln(f"ERRORS (errors={len(self.errors)})")
        if self.skipped:
            self.stream.writeln(f"SKIPPED (skipped={len(self.skipped)})")
        
        self.stream.writeln()

def setup_logging():
    """Set up logging configuration."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = TEST_LOGS_DIR / f'test_run_{timestamp}.log'
    
    # Clear previous log handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('test_runner')

def run_tests():
    """Run all tests and return the test result."""
    logger = setup_logging()
    logger.info("Starting test suite...")
    
    # Set up test suite
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('src/tests', pattern='test_*.py')
    
    # Run tests with custom result class
    test_runner = unittest.TextTestRunner(
        verbosity=2,
        resultclass=TestResultWithLogging,
        stream=sys.stdout
    )
    
    logger.info("Running tests...")
    result = test_runner.run(test_suite)
    
    # Log test results
    logger.info("\n" + "="*80)
    logger.info("TEST EXECUTION SUMMARY")
    logger.info("="*80)
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Successes: {len(result.successes)}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Skipped: {len(result.skipped)}")
    
    # Log detailed failure information
    if result.failures or result.errors:
        logger.info("\n" + "="*80)
        logger.info("DETAILED FAILURE/ERROR INFORMATION")
        logger.info("="*80)
        
        for test, trace in result.failures + result.errors:
            logger.info(f"\n{'*'*40}")
            logger.info(f"FAILED: {test.id()}")
            logger.info(''.join(trace))
    
    return result

if __name__ == "__main__":
    result = run_tests()
    sys.exit(not result.wasSuccessful())
