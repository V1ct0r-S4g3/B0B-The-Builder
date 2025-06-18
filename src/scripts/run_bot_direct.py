"""Run the bot directly with output redirection."""
import sys
import os
import logging
from pathlib import Path

# Set up logging to file
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "bot_direct.log"

# Remove previous log file if it exists
if log_file.exists():
    try:
        os.remove(log_file)
    except Exception as e:
        print(f"Warning: Could not remove log file: {e}")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('B0B')

def main():
    """Main function to run the bot."""
    try:
        logger.info("=" * 50)
        logger.info("STARTING B0B BOT")
        logger.info("=" * 50)
        
        # Import bot after setting up logging
        from bot.main import MyBot
        
        logger.info("Bot class imported successfully")
        
        # Create bot instance
        bot = MyBot()
        logger.info("Bot instance created")
        
        # Mock required attributes
        class MockAI:
            def __init__(self):
                self.time = 0.0
                self.state = type('State', (), {'game_loop': 0})
                self.minerals = 50
                self.vespene = 0
                self.supply_used = 10
                self.supply_cap = 15
                self.supply_army = 0
                self.workers = type('Workers', (), {'amount': 12})()
                self.townhalls = type('Townhalls', (), {'amount': 1})()
                self.units = type('Units', (), {'of_type': lambda *_: type('Units', (), {'amount': 0})})()
                self.enemy_units = type('EnemyUnits', (), {'amount': 0})()
                self.game_info = type('GameInfo', (), {'map_name': 'Test Map'})()
                self.game_data = type('GameData', (), {'units': {}})()
                self.state = type('State', (), {
                    'score': type('Score', (), {
                        'collection_rate_minerals': 0,
                        'collection_rate_vespene': 0
                    })(),
                    'game_loop': 0
                })()
        
        bot.ai = MockAI()
        logger.info("Mock AI attributes set")
        
        # Test on_start
        logger.info("\n" + "-" * 20 + " Testing on_start " + "-" * 20)
        try:
            import asyncio
            asyncio.run(bot.on_start())
            logger.info("✅ Bot started successfully")
        except Exception as e:
            logger.error("❌ Bot start failed")
            logger.exception("Error details:")
            return 1
        
        logger.info("\n" + "=" * 50)
        logger.info("BOT TEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
        return 0
        
    except Exception as e:
        logger.critical("!!! UNHANDLED EXCEPTION !!!")
        logger.exception("Error details:")
        return 1

if __name__ == "__main__":
    sys.exit(main())
