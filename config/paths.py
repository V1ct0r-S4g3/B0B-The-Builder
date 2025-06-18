"""
Configuration for file paths used by the SC2 bot.

This file contains all path configurations to ensure consistent path usage
across the project and to make it easy to update paths in one place.
"""
from pathlib import Path

# Base directory of the project
PROJECT_ROOT = Path(__file__).parent.parent

# SC2 Installation Paths
# Update these paths to match your system's installation
SC2_PATH = Path(r"D:\Battle.net\StarCraft2")  # Main SC2 installation directory
SC2_EXECUTABLE = SC2_PATH / "Versions\Base*\SC2_x64.exe"  # Path to SC2 executable
MAPS_PATH = SC2_PATH / "Maps"  # Directory containing SC2 maps
REPLAYS_PATH = PROJECT_ROOT / "replays"  # Where to save replay files

# Ensure required directories exist
for path in [MAPS_PATH, REPLAYS_PATH]:
    path.mkdir(parents=True, exist_ok=True)

# Export the paths that other modules will use
__all__ = [
    'PROJECT_ROOT',
    'SC2_PATH',
    'SC2_EXECUTABLE',
    'MAPS_PATH',
    'REPLAYS_PATH'
]
