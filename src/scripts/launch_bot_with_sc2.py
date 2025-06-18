import os
import subprocess
import time
import sys
import signal

def find_sc2_executable():
    """Find the StarCraft II executable."""
    sc2_path = r"D:\\Battle.net\\StarCraft2"
    versions_dir = os.path.join(sc2_path, "Versions")
    
    if not os.path.exists(versions_dir):
        print(f"Error: Could not find Versions directory in {sc2_path}")
        return None
    
    # Look for the latest version directory
    versions = [d for d in os.listdir(versions_dir) 
               if os.path.isdir(os.path.join(versions_dir, d))]
    
    if not versions:
        print("Error: No version directories found in", versions_dir)
        return None
    
    # Sort versions to get the latest one
    versions.sort(reverse=True)
    version_path = os.path.join(versions_dir, versions[0])
    sc2_exe = os.path.join(version_path, "SC2_x64.exe")
    
    if not os.path.exists(sc2_exe):
        print(f"Error: Could not find SC2_x64.exe in {version_path}")
        return None
    
    return sc2_exe

def launch_starcraft(sc2_exe):
    """Launch StarCraft II in the background."""
    print(f"Launching StarCraft II from: {sc2_exe}")
    try:
        # Launch SC2 with -listen 127.0.0.1 to accept local connections
        process = subprocess.Popen(
            [sc2_exe, "-listen", "127.0.0.1", "-port", "8167"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        print(f"StarCraft II launched with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"Error launching StarCraft II: {e}")
        return None

def launch_bot():
    """Launch the SC2 bot."""
    print("\nLaunching SC2 bot...")
    try:
        # Set SC2PATH environment variable
        sc2_path = os.path.dirname(os.path.dirname(find_sc2_executable()))
        os.environ['SC2PATH'] = sc2_path
        
        # Launch the bot
        bot_process = subprocess.Popen(
            [sys.executable, "run.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=sys.stdout,
            stderr=subprocess.STDOUT
        )
        print(f"Bot launched with PID: {bot_process.pid}")
        return bot_process
    except Exception as e:
        print(f"Error launching bot: {e}")
        return None

def main():
    print("=== SC2 Bot Launcher ===")
    
    # Find SC2 executable
    sc2_exe = find_sc2_executable()
    if not sc2_exe:
        print("Failed to find StarCraft II executable.")
        return 1
    
    # Launch StarCraft II
    sc2_process = launch_starcraft(sc2_exe)
    if not sc2_process:
        return 1
    
    # Give SC2 some time to start up
    print("Waiting 10 seconds for StarCraft II to initialize...")
    time.sleep(10)
    
    # Launch the bot
    bot_process = launch_bot()
    if not bot_process:
        print("Failed to launch bot. Terminating StarCraft II...")
        sc2_process.terminate()
        return 1
    
    print("\n=== Both StarCraft II and the bot have been launched ===")
    print("Press Ctrl+C to terminate both processes.")
    
    try:
        # Wait for either process to terminate
        while True:
            if sc2_process.poll() is not None:
                print("\nStarCraft II has terminated.")
                if bot_process.poll() is None:
                    print("Terminating bot...")
                    bot_process.terminate()
                break
                
            if bot_process.poll() is not None:
                print("\nBot has terminated.")
                print("Terminating StarCraft II...")
                sc2_process.terminate()
                break
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nTerminating both processes...")
        sc2_process.terminate()
        bot_process.terminate()
    
    print("Cleanup complete.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
