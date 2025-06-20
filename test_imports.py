"""Test script to verify imports and basic functionality."""
import sys
import os
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"{title:^80}")
    print("=" * 80)

def print_section(title):
    """Print a section header."""
    print(f"\n{'-'*40}")
    print(f"{title}")
    print(f"{'-'*40}")

# Print script header
print_header("TEST SCRIPT STARTED")

# Print system information
print_section("System Information")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Print Python path
print_section("Python Path")
for i, path in enumerate(sys.path, 1):
    print(f"{i:2d}. {path}")

# Check for src directory
project_root = Path(__file__).parent.absolute()
src_dir = project_root / 'src'
print_section("Project Structure")
print(f"Project root: {project_root}")
print(f"Source directory: {src_dir} (exists: {src_dir.exists()})")

# Check for required directories and files
required_dirs = [
    src_dir / 'bot',
    src_dir / 'managers'
]

required_files = [
    src_dir / 'bot' / 'bot.py',
    src_dir / 'managers' / 'head_manager.py',
    src_dir / 'managers' / 'economy_manager.py',
    src_dir / 'managers' / 'military_manager.py'
]

print_section("Required Directories")
for dir_path in required_dirs:
    print(f"- {dir_path.relative_to(project_root)}: "
          f"{'EXISTS' if dir_path.exists() else 'MISSING'}")

print_section("Required Files")
for file_path in required_files:
    print(f"- {file_path.relative_to(project_root)}: "
          f"{'EXISTS' if file_path.exists() else 'MISSING'}")

# Try to import the bot and managers
print_section("Import Tests")
try:
    # Add src to Python path if not already there
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    print("Attempting to import bot and managers...")
    from src.bot.bot import CompetitiveBot
    from src.managers.head_manager import HeadManager
    from src.managers.economy_manager import EconomyManager
    from src.managers.military_manager import MilitaryManager
    
    print("\nSUCCESS: All imports completed successfully!")
    print("\nImported classes:")
    print(f"- CompetitiveBot: {CompetitiveBot}")
    print(f"- HeadManager: {HeadManager}")
    print(f"- EconomyManager: {EconomyManager}")
    print(f"- MilitaryManager: {MilitaryManager}")
    
    # Test creating instances
    print("\nTesting instance creation...")
    try:
        bot = CompetitiveBot()
        print("- Successfully created CompetitiveBot instance")
        print(f"  - Head manager: {hasattr(bot, 'head')}")
        print(f"  - Economy manager: {hasattr(bot, 'economy_manager')}")
        print(f"  - Military manager: {hasattr(bot, 'military_manager')}")
    except Exception as e:
        print(f"- Failed to create CompetitiveBot instance: {e}")
    
except ImportError as e:
    print(f"\nERROR: Import failed: {e}")
    print("\nTroubleshooting information:")
    
    # Check if src is in Python path
    print("\nIs 'src' in Python path?", 
          "Yes" if any('src' in p for p in sys.path) else "No")
    
    # Check if we can find the modules manually
    print("\nSearching for modules...")
    for root, dirs, files in os.walk('.'):
        if 'bot.py' in files:
            print(f"Found bot.py at: {os.path.abspath(os.path.join(root, 'bot.py'))}")
        if 'head_manager.py' in files:
            print(f"Found head_manager.py at: {os.path.abspath(os.path.join(root, 'head_manager.py'))}")

print_header("TEST SCRIPT COMPLETED")
