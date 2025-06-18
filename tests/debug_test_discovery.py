"""Debug script to understand test discovery and execution."""
import io
import os
import sys
import unittest
import logging
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test_runner')

class StreamToLogger:
    """Fake file-like stream object that redirects writes to a logger instance."""
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
    
    def flush(self):
        pass

def run_single_test(test_path):
    """Run a single test file and return the result."""
    logger.info(f"\n{'='*80}")
    logger.info(f"RUNNING TEST: {test_path}")
    logger.info(f"{'='*80}")
    
    # Capture output
    output = io.StringIO()
    error = io.StringIO()
    
    with redirect_stdout(StreamToLogger(logger, logging.INFO)), \
         redirect_stderr(StreamToLogger(logger, logging.ERROR)):
        
        # Load and run the test
        loader = unittest.TestLoader()
        suite = loader.discover(
            start_dir=str(test_path.parent),
            pattern=test_path.name,
            top_level_dir=str(test_path.parent.parent)
        )
        
        # Run the test
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=output,
            resultclass=unittest.TextTestResult,
            failfast=False,
            buffer=False,
            warnings=None
        )
        
        result = runner.run(suite)
        
        # Log the output
        logger.info("\nTEST OUTPUT:")
        logger.info("-" * 40)
        logger.info(output.getvalue())
        
        logger.info("\nTEST ERRORS:")
        logger.info("-" * 40)
        logger.info(error.getvalue())
        
        logger.info("\nTEST RESULT:")
        logger.info("-" * 40)
        logger.info(f"Tests run: {result.testsRun}")
        logger.info(f"Failures: {len(result.failures)}")
        logger.info(f"Errors: {len(result.errors)}")
        logger.info(f"Skipped: {len(result.skipped)}")
        
        return result

def main():
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    # Set up test directory
    test_dir = project_root.parent / "src" / "tests"
    logger.info(f"Looking for tests in: {test_dir}")
    
    # Check if directory exists
    if not test_dir.exists():
        logger.error(f"Error: Test directory not found: {test_dir}")
        return 1
    
    # List all test files
    test_files = sorted(list(test_dir.glob("test_*.py")))
    logger.info(f"Found {len(test_files)} test files")
    
    # Run each test file individually
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'errors': 0,
        'skipped': 0
    }
    
    for test_file in test_files:
        result = run_single_test(test_file)
        
        # Update results
        results['total'] += result.testsRun
        results['failed'] += len(result.failures)
        results['errors'] += len(result.errors)
        results['skipped'] += len(result.skipped)
        results['passed'] += (result.testsRun - len(result.failures) - 
                            len(result.errors) - len(result.skipped))
    
    # Print summary
    logger.info("\n" + "="*80)
    logger.info("TEST EXECUTION SUMMARY")
    logger.info("="*80)
    logger.info(f"Total test files: {len(test_files)}")
    logger.info(f"Total tests run: {results['total']}")
    logger.info(f"Passed: {results['passed']}")
    logger.info(f"Failed: {results['failed']}")
    logger.info(f"Errors: {results['errors']}")
    logger.info(f"Skipped: {results['skipped']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
