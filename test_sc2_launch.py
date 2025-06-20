"""
Simple script to test StarCraft II launch with minimal settings.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

def main():
    # Try to find SC2 installation
    sc2_path = Path(r"D:\Battle.net\StarCraft2\Versions\Base94137\SC2_x64.exe")
    
    if not sc2_path.exists():
        print("Error: Could not find StarCraft II installation at:", sc2_path)
        return
    
    print(f"Found StarCraft II at: {sc2_path}")
    
    # Kill any existing SC2 processes
    try:
        if sys.platform == 'win32':
            os.system('taskkill /f /im SC2_x64.exe >nul 2>&1')
            time.sleep(2)
    except Exception as e:
        print(f"Warning: Error killing existing SC2 processes: {e}")
    
    print("Launching StarCraft II with minimal settings...")
    
    try:
        # Launch with minimal settings
        process = subprocess.Popen(
            [str(sc2_path), 
             '-listen', '127.0.0.1',
             '-port', '8167',
             '-displayMode', '0',  # Windowed mode
             '-windowwidth', '1024',
             '-windowheight', '768',
             '-noaudio'],  # Disable audio
            cwd=sc2_path.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"StarCraft II started with PID {process.pid}")
        print("Waiting 10 seconds to see if it stays running...")
        
        # Wait for 10 seconds to see if it crashes
        time.sleep(10)
        
        if process.poll() is None:
            print("Success! StarCraft II is running.")
            print("This suggests the issue is with the bot's launch parameters.")
        else:
            stdout, stderr = process.communicate()
            print(f"StarCraft II crashed with exit code: {process.returncode}")
            if stdout:
                print("STDOUT:", stdout)
            if stderr:
                print("STDERR:", stderr)
    
    except Exception as e:
        print(f"Error launching StarCraft II: {e}")
    finally:
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    main()
