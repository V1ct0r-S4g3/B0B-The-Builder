import subprocess
import os
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('batch_launch.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    batch_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'launch_sc2.bat')
    
    try:
        logger.info(f"Launching SC2 via batch file: {batch_file}")
        
        # Run the batch file
        process = subprocess.Popen(
            [batch_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        
        # Wait for the process to complete
        stdout, stderr = process.communicate()
        
        logger.info(f"Batch file completed with return code: {process.returncode}")
        if stdout:
            logger.info(f"Batch output: {stdout}")
        if stderr:
            logger.error(f"Batch error: {stderr}")
        
        if process.returncode == 0:
            logger.info("SC2 should be running now. Check your task manager for SC2_x64.exe")
            logger.info("Waiting 30 seconds to see if SC2 stays running...")
            time.sleep(30)
            
            # Check if SC2 is still running
            try:
                check_process = subprocess.Popen(
                    ['tasklist', '/FI', 'IMAGENAME eq SC2_x64.exe'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                out, _ = check_process.communicate()
                if 'SC2_x64.exe' in out:
                    logger.info("SC2 is still running successfully!")
                else:
                    logger.warning("SC2 is no longer running")
            except Exception as e:
                logger.error(f"Error checking process status: {e}")
        
        return process.returncode
        
    except Exception as e:
        logger.error(f"Error running batch file: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
