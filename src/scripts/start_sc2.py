"""Start StarCraft II client for bot connection."""
import os
import sys
import subprocess
import time
from pathlib import Path

def find_sc2_executable():
    """Find the SC2 executable."""
    sc2_path = r"D:\Battle.net\StarCraft2"
    versions_dir = os.path.join(sc2_path, "Versions")
    
    if not os.path.exists(versions_dir):
        print(f"Error: SC2 Versions directory not found at {versions_dir}")
        return None
    
    # Look for the latest version
    base_dirs = [d for d in os.listdir(versions_dir) if d.startswith("Base")]
    if not base_dirs:
        print("Error: No Base* directories found in Versions folder")
        return None
    
    # Sort to get the latest version (highest number)
    base_dirs.sort(reverse=True)
    base_dir = os.path.join(versions_dir, base_dirs[0])
    sc2_exe = os.path.join(base_dir, "SC2_x64.exe")
    
    if not os.path.exists(sc2_exe):
        print(f"Error: SC2 executable not found at {sc2_exe}")
        return None
    
    return sc2_exe

def start_sc2():
    """Start the SC2 client with detailed error handling."""
    sc2_exe = find_sc2_executable()
    if not sc2_exe:
        return False
    
    print(f"Starting StarCraft II from: {sc2_exe}")
    
    try:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Generate a timestamp for log files
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f"sc2_launch_{timestamp}.log")
        
        # Start SC2 with necessary parameters for bot connection
        cmd = [
            sc2_exe,
            "-listen", "127.0.0.1",
            "-port", "8167",
            "-displayMode", "0",  # Windowed mode
            "-windowwidth", "1024",
            "-windowheight", "768",
            "-windowx", "0",
            "-windowy", "0",
            "-verbose",  # Enable verbose logging
            "-dataVersion", "B89B5D6FA7CBF6452E4EF456CFAF4F280E0D39B4"  # Force specific game version
        ]
        
        print("Launching StarCraft II with command:")
        print(" ".join(f'"{arg}"' if ' ' in arg else arg for arg in cmd))
        
        # Start the process with output redirection
        with open(log_file, 'w') as log_f:
            log_f.write(f"Launch command: {' '.join(cmd)}\n\n")
            log_f.flush()
            
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(sc2_exe),
                stdout=log_f,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # Line buffered
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # For better process handling on Windows
            )
        
        print(f"StarCraft II started with PID: {process.pid}")
        print(f"Logging output to: {log_file}")
        print("Please wait for the game to fully load...")
        
        # Check if process is still running after a short delay
        time.sleep(5)
        if process.poll() is not None:
            print(f"Error: StarCraft II process exited with code {process.returncode}")
            print(f"Check the log file for details: {log_file}")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error starting StarCraft II: {e}")
        import traceback
        print("Traceback:")
        print(traceback.format_exc())
        return False

def main():
    """Main function."""
    print("=" * 50)
    print("STARCRAFT II CLIENT LAUNCHER".center(50))
    print("=" * 50)
    
    if start_sc2():
        print("\n✅ StarCraft II started successfully!")
        print("You can now run your bot to connect to the game.")
        return 0
    else:
        print("\n❌ Failed to start StarCraft II")
        return 1

if __name__ == "__main__":
    sys.exit(main())
