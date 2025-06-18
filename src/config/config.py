"""
Configuration module that re-exports settings from scripts.config.
This module exists to maintain compatibility with the existing import structure.
"""
import os
from pathlib import Path

# Import all settings from scripts.config
from src.scripts.config import *

# Define the replay save path
REPLAY_SAVE_PATH = str(Path(__file__).parent.parent.parent / 'replays')

# Create the replays directory if it doesn't exist
os.makedirs(REPLAY_SAVE_PATH, exist_ok=True)

# Re-export everything
__all__ = [
    'BOT_NAME',
    'BOT_RACE',
    'MAP_PATH',
    'MAP_POOL',
    'OPPONENT_RACE',
    'OPPONENT_DIFFICULTY',
    'REALTIME',
    'REPLAY_SAVE_PATH'
]
