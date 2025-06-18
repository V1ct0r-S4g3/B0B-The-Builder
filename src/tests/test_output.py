"""Test script to check file output and Python environment."""
import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
import logging

class TestFileOutput(unittest.TestCase):
    """Test case for file output and environment checks."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        # Create a temporary directory for test files
        cls.test_dir = tempfile.mkdtemp()
        cls.test_file = os.path.join(cls.test_dir, "test_output.txt")
        
        # Set up logging
        cls.logger = logging.getLogger('test_output')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stdout
        )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test directory after all tests have run."""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.logger.info("-" * 50)
        self.logger.info("STARTING TEST: %s", self._testMethodName)
        
        # Ensure test file doesn't exist at the start of each test
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_environment_info(self):
        """Test that environment information is accessible."""
        self.logger.info("Python executable: %s", sys.executable)
        self.logger.info("Python version: %s", sys.version)
        self.logger.info("Current working directory: %s", os.getcwd())
        
        # Basic environment checks
        self.assertTrue(isinstance(sys.executable, str), "Python executable path should be a string")
        self.assertTrue(os.path.isabs(sys.executable), "Python executable path should be absolute")
    
    def test_file_write(self):
        """Test writing to a file."""
        test_content = "Test file write successful!\n"
        
        # Write to file
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        self.logger.info("Successfully wrote to %s", self.test_file)
        self.assertTrue(os.path.exists(self.test_file), "Test file should exist after writing")
        
        # Verify file content
        with open(self.test_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        self.assertEqual(content, test_content, "File content should match what was written")
    
    def test_file_read(self):
        """Test reading from a file."""
        test_content = "Test file content for reading\n"
        
        # Write test content
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # Read and verify
        with open(self.test_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        self.logger.info("Read content: %r", content)
        self.assertEqual(content, test_content, "Read content should match written content")
    
    def test_file_operations(self):
        """Test file operations including existence check and deletion."""
        # File should not exist initially
        self.assertFalse(os.path.exists(self.test_file), "Test file should not exist initially")
        
        # Create file
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("Test content\n")
        
        # File should now exist
        self.assertTrue(os.path.exists(self.test_file), "Test file should exist after creation")
        
        # Delete file
        os.remove(self.test_file)
        
        # File should no longer exist
        self.assertFalse(os.path.exists(self.test_file), "Test file should not exist after deletion")
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up test file if it exists
        if os.path.exists(self.test_file):
            try:
                os.remove(self.test_file)
            except Exception as e:
                self.logger.warning("Failed to remove test file: %s", e)
        
        self.logger.info("COMPLETED TEST: %s", self._testMethodName)
        self.logger.info("-" * 50)

if __name__ == "__main__":
    unittest.main()
