#!/usr/bin/env python3
"""
Simple script to run the B0B bot.
"""

import os
import sys
from pathlib import Path

print('[DEBUG] Top of run_simple_bot.py')

# Add the src directory to the Python path BEFORE any other imports
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

print(f"[DEBUG] Python path after adding src: {sys.path[:3]}")

# Set the SC2PATH environment variable
os.environ['SC2PATH'] = r"D:\Program Files (x86)\StarCraft II"

# Now import the bot and sc2 modules
from sc2.main import run_game
from sc2 import maps
from sc2.data import Race, Difficulty
from sc2.player import Bot, Computer
import bot.main
print(f"[DEBUG] bot.main module: {bot.main.__file__}")
from bot.main import MyBot


def main():
    """Run the bot against a computer opponent."""
    print('[DEBUG] Entered main() in run_simple_bot.py')
    print(f"[DEBUG] MyBot class: {MyBot}")
    print(f"[DEBUG] MyBot module: {MyBot.__module__}")
    print(f"[DEBUG] MyBot bases: {MyBot.__bases__}")
    print('[DEBUG] Instantiating MyBot...')
    bot_instance = MyBot()
    print('[DEBUG] Running game...')
    run_game(
        maps.get("Simple64"),  # Use a simple built-in map
        [
            Bot(Race.Terran, bot_instance),
            Computer(Race.Random, Difficulty.Easy)
        ],
        realtime=False,
        save_replay_as="b0b_replay.SC2Replay"
    )


if __name__ == "__main__":
    print('[DEBUG] __name__ == "__main__" in run_simple_bot.py')
    main() 