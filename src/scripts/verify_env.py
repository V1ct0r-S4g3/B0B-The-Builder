"""Verify Python environment and SC2 installation."""
import sys
import os
import platform
import subprocess
from pathlib import Path

def log(message):
    """Print message to console and write to log file."""
    print(message)
    with open("environment_check.log", "a", encoding="utf-8") as f:
        f.write(f"{message}\n")

def check_python():
    """Check Python version and environment."""
    log("\n" + "=" * 50)
    log("PYTHON ENVIRONMENT")
    log("=" * 50)
    log(f"Python Executable: {sys.executable}")
    log(f"Python Version: {platform.python_version()}")
    log(f"Platform: {platform.platform()}")
    log(f"Current Directory: {os.getcwd()}")
    log(f"Python Path: {sys.path}")

def check_sc2():
    """Check if SC2 is installed and accessible."""
    log("\n" + "=" * 50)
    log("STARCRAFT II CHECK")
    log("=" * 50)
    
    # Check SC2 installation
    sc2_path = Path(r"D:\Battle.net\StarCraft2")
    if sc2_path.exists():
        log(f"✅ StarCraft II found at: {sc2_path}")
    else:
        log(f"❌ StarCraft II not found at: {sc2_path}")
    
    # Check python-sc2 package
    try:
        import sc2
        log("\nSC2 Package:")
        log(f"✅ python-sc2 version: {getattr(sc2, '__version__', 'unknown')}")
        log(f"Path: {os.path.dirname(sc2.__file__)}")
        return True
    except ImportError as e:
        log(f"\n❌ python-sc2 not installed: {e}")
        log("Install it with: pip install sc2")
        return False
    except Exception as e:
        log(f"\n❌ Error importing sc2: {e}")
        return False

def main():
    """Main function."""
    # Clear previous log
    if os.path.exists("environment_check.log"):
        os.remove("environment_check.log")
    
    log("=" * 50)
    log("ENVIRONMENT VERIFICATION")
    log("=" * 50)
    
    check_python()
    sc2_ok = check_sc2()
    
    log("\n" + "=" * 50)
    if sc2_ok:
        log("✅ Environment check completed successfully!")
    else:
        log("❌ Environment check found issues. Please check the log above.")
    log("=" * 50)

if __name__ == "__main__":
    main()
