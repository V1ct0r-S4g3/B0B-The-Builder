"""
Functional tests for the complete SC2 bot.
"""
import pytest
import asyncio
from sc2 import maps
from sc2.data import Race, Difficulty, Result
from sc2.main import run_game
from sc2.player import Bot, Computer

# Import your bot implementation
from bot.main import MyBot

class TestFullGame:
    """Test the complete bot in a game scenario."""
    
    @pytest.mark.asyncio
    async def test_bot_vs_easy_ai(self):
        """Test the bot against the built-in AI on easy difficulty."""
        # This test will run a complete game against the AI
        try:
            # Run the game
            result = await run_game(
                maps.get("Simple128"),
                [
                    Bot(Race.Terran, MyBot()),
                    Computer(Race.Random, Difficulty.Easy)
                ],
                realtime=False,
                save_replay_as="test_replay.SC2Replay"
            )
            
            # Check that the game completed (regardless of win/loss)
            assert result in [Result.Victory, Result.Defeat, Result.Tie]
            
        except Exception as e:
            pytest.fail(f"Game failed to run: {e}")
    
    @pytest.mark.asyncio
    async def test_early_game_economy(self):
        """Test that the bot can establish an early game economy."""
        bot = MyBot()
        
        async def early_stop(iteration):
            # Stop after 3 minutes of game time
            return bot.time > 180  # 3 minutes
            
        try:
            result = await run_game(
                maps.get("Simple128"),
                [
                    Bot(Race.Terran, bot),
                    Computer(Race.Random, Difficulty.VeryEasy)
                ],
                realtime=False,
                step_time_limit=2,
                game_time_limit=(60 * 3),  # 3 minute time limit
                save_replay_as="test_early_game.SC2Replay"
            )
            
            # Check that we have a reasonable economy by 3 minutes
            assert bot.time >= 180, "Game didn't run for full 3 minutes"
            assert bot.workers.amount >= 16, "Not enough workers by 3 minutes"
            assert bot.townhalls.amount >= 1, "No command center"
            
        except Exception as e:
            pytest.fail(f"Early game test failed: {e}")
