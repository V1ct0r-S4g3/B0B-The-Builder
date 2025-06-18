"""Run the bot in a test environment."""
import os
import asyncio
import logging
from sc2 import maps
from sc2.data import Race, Difficulty
from sc2.main import run_game
from sc2.player import Bot, Computer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('B0B')

# Import the bot after setting up logging
from bot.main import MyBot

async def main():
    """Run the bot in a test game."""
    try:
        logger.info("Starting test game...")
        
        # Run the game
        result = await run_game(
            maps.get("AutomatonLE"),
            [
                Bot(Race.Terran, MyBot(), name="B0B"),
                Computer(Race.Zerg, Difficulty.Easy)
            ],
            realtime=False,
            step_time_limit=2.0,
            game_time_limit=(60 * 10),  # 10 minute limit
            save_replay_as="test_replay.SC2Replay"
        )
        
        logger.info(f"Game finished with result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
