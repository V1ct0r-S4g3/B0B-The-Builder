"""
Pytest configuration and fixtures for testing.
"""
import os
import sys
import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def pytest_configure(config):
    """Pytest configuration hook."""
    # Set environment variables for testing
    os.environ["PYTHONPATH"] = str(project_root) + os.pathsep + os.environ.get("PYTHONPATH", "")
    os.environ["SC2PATH"] = r"D:\Battle.net\StarCraft2"
    os.environ["SC2PF"] = "WineLinux" if sys.platform == "linux" else "Windows"

# Fixtures
@pytest.fixture
def mock_ai():
    """Create a mock AI object with common attributes."""
    ai = MagicMock()
    ai.time = 0.0
    ai.minerals = 50
    ai.vespene = 0
    ai.supply_used = 10
    ai.supply_cap = 15
    ai.start_location = (0, 0)
    ai.enemy_race = "Terran"
    ai.units = MagicMock()
    ai.structures = MagicMock()
    ai.townhalls = MagicMock()
    ai.workers = MagicMock()
    ai.game_info = MagicMock()
    ai.enemy_units = MagicMock()
    ai.enemy_structures = MagicMock()
    ai.distribute_workers = AsyncMock()
    return ai

@pytest.fixture
def bot(mock_ai):
    """Create a bot instance with a mock AI."""
    from src.bot.bot import CompetitiveBot
    bot = CompetitiveBot()
    bot.ai = mock_ai
    return bot

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Configure asyncio to be less verbose in test output
@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    import logging
    logging.basicConfig(level=logging.WARNING)
