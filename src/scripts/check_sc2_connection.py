"""Check connection to StarCraft II client."""
import os
import sys
import platform
import time
from pathlib import Path

def log(message):
    """Log a message to console and file."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    try:
        with open("sc2_connection.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"Error writing to log: {e}", file=sys.stderr)

def check_sc2_installation():
    """Check if SC2 is installed and accessible."""
    log("=" * 50)
    log("STARCRAFT II CONNECTION TEST")
    log("=" * 50)
    
    log(f"Python: {sys.executable}")
    log(f"Version: {sys.version}")
    log(f"Platform: {platform.platform()}")
    log(f"Current directory: {os.getcwd()}")
    
    # Check if SC2 is installed
    sc2_path = r"D:\Battle.net\StarCraft2"
    if not os.path.exists(sc2_path):
        log(f"❌ StarCraft II not found at: {sc2_path}")
        return False
    
    log(f"✅ StarCraft II found at: {sc2_path}")
    
    # Check if SC2 executable exists
    sc2_exe = os.path.join(sc2_path, "Versions", "Base*", "SC2_x64.exe")
    import glob
    exe_files = glob.glob(sc2_exe)
    if not exe_files:
        log(f"❌ SC2 executable not found at: {sc2_exe}")
        return False
    
    log(f"✅ SC2 executable found: {exe_files[0]}")
    return True

def check_python_sc2():
    """Check if python-sc2 package is installed and working."""
    log("\nChecking python-sc2 package...")
    try:
        import sc2
        log(f"✅ python-sc2 version: {getattr(sc2, '__version__', 'unknown')}")
        log(f"✅ SC2 module path: {os.path.dirname(sc2.__file__)}")
        return True
    except ImportError as e:
        log(f"❌ python-sc2 not installed: {e}")
        log("Install it with: pip install sc2")
        return False
    except Exception as e:
        log(f"❌ Error importing python-sc2: {e}")
        return False

def main():
    """Main function to check SC2 connection."""
    if not check_sc2_installation():
        log("\n❌ StarCraft II installation check failed")
        return 1
    
    if not check_python_sc2():
        log("\n❌ python-sc2 package check failed")
        return 1
    
    log("\n✅ All checks passed!")
    log("You should be able to run the bot now.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
