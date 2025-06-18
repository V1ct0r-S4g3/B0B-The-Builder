"""
Pytest configuration and fixtures for SC2 bot tests.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Result
from sc2.maps import get as get_map

# Import your bot implementation
from bot.main import MyBot

# Test configuration
TEST_MAP = "Simple128"
TEST_RACE = Race.Terran
TEST_ENEMY_RACE = Race.Random
TEST_DIFFICULTY = Difficulty.Easy

# Create required directories
REPLAYS_PATH = Path("replays")
REPLAYS_PATH.mkdir(parents=True, exist_ok=True)

@pytest.fixture
def bot_ai():
    """Fixture that provides a bot instance for testing."""
    return MyBot()

@pytest.fixture
def test_map():
    """Fixture that provides the test map."""
    return TEST_MAP

@pytest.fixture
def player_configuration(bot_ai):
    """Fixture that provides the player configuration."""
    return [
        Bot(TEST_RACE, bot_ai),
        Computer(TEST_ENEMY_RACE, TEST_DIFFICULTY)
    ]

@pytest.mark.asyncio
async def test_bot_starts(bot_ai, test_map):
    """Test that the bot can start a game."""
    try:
        result = await run_game(
            get_map(test_map),
            [Bot(TEST_RACE, bot_ai),
             Computer(TEST_ENEMY_RACE, TEST_DIFFICULTY)],
            realtime=False,
            save_replay_as=str(REPLAYS_PATH / "test_replay.SC2Replay")
        )
        assert result in [Result.Victory, Result.Defeat, Result.Tie]
    except Exception as e:
        pytest.fail(f"Bot failed to start: {e}")
