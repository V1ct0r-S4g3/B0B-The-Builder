"""Test script to verify StarCraft II can be launched from Python."""
import os
import sys
import time
import unittest
import logging
import subprocess
from pathlib import Path

# Add src directory to Python path
src_dir = str(Path(__file__).parent.parent.absolute())
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('test_sc2_launch')

class TestSC2Launch(unittest.TestCase):
    """Test case for StarCraft II launch functionality."""
    
    # SC2 installation paths
    SC2_PATH = r"D:\\Battle.net\\StarCraft2"
    VERSIONS_DIR = os.path.join(SC2_PATH, "Versions")
    
    @classmethod
    def find_sc2_executable(cls):
        """Find the SC2 executable in the installation directory."""
        if not os.path.exists(cls.VERSIONS_DIR):
            raise FileNotFoundError(f"Could not find Versions directory in {cls.SC2_PATH}")
        
        # Look for the latest version directory
        try:
            versions = [
                d for d in os.listdir(cls.VERSIONS_DIR) 
                if os.path.isdir(os.path.join(cls.VERSIONS_DIR, d))
            ]
            if not versions:
                raise FileNotFoundError(f"No version directories found in {cls.VERSIONS_DIR}")
            
            # Sort versions to get the latest one
            versions.sort(reverse=True)
            version_path = os.path.join(cls.VERSIONS_DIR, versions[0])
            
            # Find SC2_x64.exe in the version directory
            sc2_exe = os.path.join(version_path, "SC2_x64.exe")
            if not os.path.exists(sc2_exe):
                raise FileNotFoundError(f"Could not find SC2_x64.exe in {version_path}")
                
            return sc2_exe
            
        except Exception as e:
            logger.error("Error finding SC2 executable: %s", e)
            raise
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.logger = logging.getLogger(f"test_sc2_launch.{self._testMethodName}")
        self.logger.info("-" * 50)
        self.logger.info("STARTING TEST: %s", self._testMethodName)
        self.process = None
    
    def test_find_sc2_executable(self):
        """Test that we can find the SC2 executable."""
        try:
            sc2_exe = self.find_sc2_executable()
            self.logger.info("Found SC2 executable: %s", sc2_exe)
            self.assertTrue(os.path.exists(sc2_exe), "SC2 executable does not exist")
        except Exception as e:
            self.fail(f"Failed to find SC2 executable: {e}")
    
    def test_launch_sc2(self):
        """Test that we can launch StarCraft II."""
        # Skip if running in CI environment
        if os.environ.get('CI') == 'true':
            self.skipTest("Skipping SC2 launch test in CI environment")
        
        try:
            # Find the SC2 executable
            sc2_exe = self.find_sc2_executable()
            self.logger.info("Launching SC2 from: %s", sc2_exe)
            
            # Prepare the command to launch SC2
            cmd = [
                sc2_exe,
                '-listen', '127.0.0.1',
                '-port', '5000',
                '-displayMode', '0',  # Windowed mode
                '-windowwidth', '1024',
                '-windowheight', '768',
                '-windowx', '0',
                '-windowy', '0',
                '-dataDir', self.SC2_PATH,
                '-eglpath', 'libEGL.dll',
                '-osx', '0',
                '-uid', 's2client-x64',
                '-dataVersion', 'B89B5D6FA7C55664591BE7663A7EE6D9F9049A93',
                '-window',
                '-verbose'
            ]
            
            # Start the process
            self.logger.info("Starting SC2 process...")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Give it some time to start
            self.logger.info("Waiting for SC2 to start...")
            time.sleep(10)  # Wait for 10 seconds
            
            # Check if the process is still running
            self.assertIsNone(
                self.process.poll(),
                "SC2 process terminated early"
            )
            
            self.logger.info("SC2 launched successfully!")
            
        except Exception as e:
            self.fail(f"Error launching SC2: {e}")
    
    def tearDown(self):
        """Clean up after each test method."""
        # Terminate the SC2 process if it's still running
        if hasattr(self, 'process') and self.process and self.process.poll() is None:
            self.logger.info("Terminating SC2 process...")
            try:
                self.process.terminate()
                time.sleep(2)  # Give it time to terminate
                if self.process.poll() is None:  # Still running?
                    self.process.kill()
            except Exception as e:
                self.logger.error("Error terminating SC2 process: %s", e)
        
        self.logger.info("COMPLETED TEST: %s", self._testMethodName)
        self.logger.info("-" * 50)

if __name__ == "__main__":
    unittest.main(verbosity=2)
