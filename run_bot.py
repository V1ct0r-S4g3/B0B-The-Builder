"""
Run the SC2 bot with a single command.
This script starts the StarCraft II client and then runs the bot.
"""
import os
import subprocess
import sys
import time
import logging
import signal
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_launch.log')
    ]
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def find_sc2_install():
    """Try to find the StarCraft II installation path."""
    # Check common installation paths
    possible_paths = [
        os.environ.get('SC2PATH'),
        r'D:\Battle.net\StarCraft2',
        r'C:\Program Files (x86)\StarCraft II',
        r'C:\Program Files\StarCraft II',
        os.path.expanduser(r'~\StarCraft II'),
    ]
    
    logger.info("Searching for StarCraft II installation...")
    for path in possible_paths:
        if not path:
            continue
            
        logger.debug(f"Checking path: {path}")
        # Check both root and Versions/Base* for the executable
        base_paths = [
            Path(path) / 'Versions' / 'Base94137' / 'SC2_x64.exe',
            Path(path) / 'Versions' / 'Base*' / 'SC2_x64.exe',
            Path(path) / 'SC2_x64.exe',
        ]
        
        for base_path in base_paths:
            # Handle wildcard in path
            if '*' in str(base_path):
                import glob
                matches = glob.glob(str(base_path))
                if matches:
                    exe_path = Path(matches[0])
                    if exe_path.exists():
                        logger.info(f"Found StarCraft II at: {exe_path}")
                        return exe_path
            else:
                if base_path.exists():
                    logger.info(f"Found StarCraft II at: {base_path}")
                    return base_path
    
    logger.error("Could not find StarCraft II installation in any of the expected locations.")
    return None

def terminate_process(process):
    """Terminate a process and its children."""
    try:
        if process and process.poll() is None:
            # Try to terminate gracefully first
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                process.kill()
    except Exception as e:
        logger.error(f"Error terminating process: {e}")

def main():
    # Set up signal handler for clean exit
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal. Shutting down...")
        if 'sc2_process' in locals() and sc2_process.poll() is None:
            terminate_process(sc2_process)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting bot launcher...")
    
    # Try to find the StarCraft II executable
    sc2_executable = find_sc2_install()
    
    if not sc2_executable or not sc2_executable.exists():
        logger.error("Could not find StarCraft II installation.")
        print("\nError: Could not find StarCraft II installation.")
        print("Please ensure StarCraft II is installed and set the SC2PATH environment variable.")
        print("Example:")
        print('    setx SC2PATH "D:\\Battle.net\\StarCraft2"')
        print("\nCommon installation paths:")
        print("- D:\\Battle.net\\StarCraft2")
        print("- C:\\Program Files (x86)\\StarCraft II")
        sys.exit(1)
    
    # Kill any existing SC2 processes
    try:
        if sys.platform == 'win32':
            os.system('taskkill /f /im SC2_x64.exe >nul 2>&1')
        else:
            os.system('pkill -f SC2_x64')
        time.sleep(2)  # Give it a moment to close
    except Exception as e:
        logger.warning(f"Error killing existing SC2 processes: {e}")
    
    logger.info("Starting StarCraft II...")
    
    # Prepare the SC2 executable path with proper escaping for command line
    sc2_path = str(sc2_executable).replace('\\', '\\\\')
    
    # Prepare environment variables
    env = os.environ.copy()
    env['SC2PF'] = 'Microsoft Windows'  # Set platform
    
    # Set working directory to the SC2 executable's directory
    sc2_dir = os.path.dirname(sc2_path)
    
    # Start StarCraft II with diagnostic parameters
    sc2_args = [
        sc2_path,
        '-listen', '127.0.0.1',
        '-port', '8167',
        '-displayMode', '0',  # Windowed mode
        '-windowwidth', '1024',
        '-windowheight', '768',
        '-noaudio',  # Disable audio
        '-verbose',  # Enable verbose logging
        '-debug',    # Enable debug mode
        '-dataVersion', 'B89B5D6FA7CBFEF2EE84396DDDD9D678',  # Force specific data version
        '-tempDir', str(Path.home() / 'Documents' / 'StarCraftII')  # Use standard temp dir
    ]
    
    # Set environment variables for debugging
    env['SC2_NO_FMOD'] = '1'  # Disable FMOD audio system
    env['SC2_NO_OPENGL'] = '1'  # Disable OpenGL
    env['SC2_NO_VULKAN'] = '1'  # Disable Vulkan
    env['SC2_NO_MT'] = '1'  # Disable multi-threading
    env['SC2_LOCALFONT'] = '1'  # Use local fonts
    
    logger.info(f"Launching StarCraft II with: {' '.join(sc2_args)}")
    
    try:
        sc2_process = subprocess.Popen(
            sc2_args,
            cwd=sc2_dir,  # Set working directory
            env=env,      # Pass environment variables
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
        )
    except Exception as e:
        logger.error(f"Failed to start StarCraft II: {e}")
        raise
    
    # Start a thread to read and log the output
    def log_output(pipe, logger_func, log_type='OUT'):
        """Read and log output from the process."""
        try:
            while True:
                line = pipe.readline()
                if not line:  # EOF
                    break
                line = line.strip()
                if line:
                    logger_func(f'SC2 {log_type}: {line}')
        except Exception as e:
            logger_func(f'Error reading {log_type} pipe: {e}')
        finally:
            pipe.close()
    
    import threading
    # Start output logging threads
    stdout_thread = threading.Thread(
        target=log_output,
        args=(sc2_process.stdout, logger.info, 'STDOUT'),
        daemon=True
    )
    stderr_thread = threading.Thread(
        target=log_output,
        args=(sc2_process.stderr, logger.error, 'STDERR'),
        daemon=True
    )
    stdout_thread.start()
    stderr_thread.start()
    
    logger.info(f"StarCraft II started with PID {sc2_process.pid}")
    logger.info("Waiting for StarCraft II to initialize...")
    
    # Log process status periodically
    def monitor_process(process):
        while process.poll() is None:
            time.sleep(1)
        logger.warning(f"SC2 process ended with code {process.returncode}")
    
    monitor_thread = threading.Thread(
        target=monitor_process,
        args=(sc2_process,),
        daemon=True
    )
    monitor_thread.start()
    
    # Wait for SC2 to start with a timeout
    max_wait_time = 120  # Increased timeout to 120 seconds
    start_time = time.time()
    sc2_ready = False
    crash_file = Path(sc2_dir) / 'Crash.dmp'
    
    # Clean up any existing crash dump
    if crash_file.exists():
        try:
            crash_file.unlink()
            logger.info("Removed existing crash dump file")
        except Exception as e:
            logger.warning(f"Could not remove crash dump file: {e}")
    
    while (time.time() - start_time) < max_wait_time:
        # Check if process is still running
        if sc2_process.poll() is not None:
            # Check for crash dump file
            if crash_file.exists():
                logger.error(f"Crash dump detected at: {crash_file}")
                try:
                    with open(crash_file, 'rb') as f:
                        crash_data = f.read(1024)  # Read first KB of crash dump
                        logger.error(f"Crash dump header: {crash_data[:200].decode('ascii', 'ignore')}...")
                except Exception as e:
                    logger.error(f"Could not read crash dump: {e}")
            
            # Try to read any remaining output
            try:
                stdout, stderr = sc2_process.communicate(timeout=5)
                if stdout:
                    logger.error(f"Final STDOUT: {stdout}")
                if stderr:
                    logger.error(f"Final STDERR: {stderr}")
            except subprocess.TimeoutExpired:
                logger.error("Timed out waiting for process to terminate")
            
            logger.error(f"StarCraft II process ended unexpectedly. Exit code: {sc2_process.returncode}")
            logger.error("Common causes:")
            logger.error("1. Missing or corrupted game files")
            logger.error("2. Graphics driver issues")
            logger.error("3. Permission problems")
            logger.error("4. Incompatible SC2 version")
            logger.error("5. Missing dependencies")
            
            sys.exit(1)
        
        # Check if port is open (crude way to check if SC2 is ready)
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex(('127.0.0.1', 8167)) == 0:
                    sc2_ready = True
                    break
        except Exception as e:
            logger.debug(f"Port check failed: {e}")
        
        time.sleep(2)  # Check every 2 seconds
    
    if not sc2_ready:
        logger.error("Timed out waiting for StarCraft II to start")
        terminate_process(sc2_process)
        sys.exit(1)
    
    logger.info("StarCraft II is ready")
    
    try:
        logger.info("Starting the bot...")
        # Add the src directory to the Python path
        src_dir = os.path.join(project_root, 'src')
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        # Ensure the current directory is in the Python path
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Try to import the bot
        try:
            logger.info("Importing bot...")
            from scripts.run import main as run_bot
            logger.info("Running bot...")
            run_bot()
        except ModuleNotFoundError as e:
            logger.error(f"Error importing bot: {e}")
            print(f"\nError importing bot: {e}")
            print("Trying to install the package in development mode...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logger.info("Installation complete. Restarting bot...")
                print("Installation complete. Restarting bot...")
                from scripts.run import main as run_bot
                run_bot()
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install package: {e}")
                if e.stdout:
                    logger.error(f"STDOUT: {e.stdout}")
                if e.stderr:
                    logger.error(f"STDERR: {e.stderr}")
                raise
        except Exception as e:
            logger.error(f"Error in bot execution: {e}", exc_info=True)
            raise
            
    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user...")
        print("\nShutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nError: {e}")
        if hasattr(e, '__traceback__'):
            import traceback
            traceback.print_exc()
    finally:
        logger.info("Cleaning up...")
        print("\nTerminating StarCraft II...")
        terminate_process(sc2_process)
        logger.info("Cleanup complete")
        print("Done.")

if __name__ == "__main__":
    main()
