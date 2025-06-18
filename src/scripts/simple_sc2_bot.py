"""A simple SC2 bot that saves its output to a file."""
import os
import sys
import time
from pathlib import Path

# Set up output file
output_file = Path("bot_output.txt")
if output_file.exists():
    output_file.unlink()

def log(message):
    """Log a message to both console and file."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # Replace any non-ASCII characters
    safe_message = message.encode('ascii', 'replace').decode('ascii')
    line = f"[{timestamp}] {safe_message}"
    try:
        print(line)
        with open(output_file, "a", encoding="ascii", errors="replace") as f:
            f.write(line + "\n")
    except Exception as e:
        # If we can't write to the file, at least try to print the error
        print(f"Error writing to log: {e}")

def main():
    """Main function to run the simple bot."""
    try:
        log("=" * 50)
        log("SIMPLE SC2 BOT STARTING")
        log("=" * 50)
        
        # Basic Python check
        log(f"Python version: {sys.version}")
        log(f"Working directory: {os.getcwd()}")
        
        # Try importing SC2
        log("\nAttempting to import SC2...")
        try:
            import sc2
            log(f"[OK] SC2 imported successfully (version: {getattr(sc2, '__version__', 'unknown')})")
            log(f"SC2 module location: {os.path.dirname(sc2.__file__)}")
        except ImportError as e:
            log(f"[ERROR] Failed to import SC2: {e}")
            log("Make sure you have installed the python-sc2 package")
            log("Install it with: pip install sc2")
            return 1
        
        log("\nBot execution completed successfully!")
        return 0
        
    except Exception as e:
        log(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        import traceback
        log(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
