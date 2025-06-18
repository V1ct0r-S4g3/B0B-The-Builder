import os
import subprocess
import sys
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_launch.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    sc2_path = r'D:\Battle.net\StarCraft2\Versions\Base94137\SC2_x64.exe'
    sc2_dir = os.path.dirname(sc2_path)
    
    logger.info("Starting SC2 with minimal arguments...")
    
    # Try with minimal arguments first
    args = [
        sc2_path,
        '-listen', '127.0.0.1',
        '-port', '8167',
        '-displayMode', '0',
        '-noaudio',
        '-verbose'
    ]
    
    logger.info(f"Command: {' '.join(args)}")
    
    try:
        # Try with shell=True which might help with process creation
        process = subprocess.Popen(
            args,
            cwd=sc2_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,  # Try with shell=True
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        logger.info(f"SC2 started with PID {process.pid}")
        
        # Wait a bit to see if it stays running
        time.sleep(5)
        
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            logger.error(f"SC2 process ended with code {process.returncode}")
            if stdout:
                logger.error(f"STDOUT: {stdout}")
            if stderr:
                logger.error(f"STDERR: {stderr}")
            return 1
            
        logger.info("SC2 process is still running. Waiting for 10 more seconds...")
        time.sleep(10)
        
        if process.poll() is None:
            logger.info("SC2 process is still running successfully!")
            process.terminate()
            return 0
        else:
            stdout, stderr = process.communicate()
            logger.error(f"SC2 process ended with code {process.returncode}")
            if stdout:
                logger.error(f"STDOUT: {stdout}")
            if stderr:
                logger.error(f"STDERR: {stderr}")
            return 1
            
    except Exception as e:
        logger.error(f"Error starting SC2: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
