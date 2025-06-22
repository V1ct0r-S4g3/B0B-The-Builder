"""Main bot module containing the MyBot class."""

import logging
import os
from pathlib import Path

# Import the race-aware bot instead of hardcoded managers
from src.bot.bot import CompetitiveBot

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "bot.log"

# Clear previous log file if it exists
if log_file.exists():
    try:
        os.remove(log_file)
    except OSError as e:
        print(f"Warning: Could not remove log file: {e}")


# Configure logging
def setup_logging():
    """Set up logging configuration and return the file logger."""
    logger = logging.getLogger("B0B")
    logger.setLevel(logging.DEBUG)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Initialize logger
logger = setup_logging()


class MyBot(CompetitiveBot):
    """Main bot class that inherits from the race-aware CompetitiveBot."""
    
    def __init__(self):
        """Initialize the bot and its managers."""
        print("[DEBUG] MyBot __init__ called")
        logger.info("[DEBUG] MyBot __init__ called")
        super().__init__()
        self._closed = False
        self.logger = logger.getChild('MyBot')
        self.logger.info("Initializing B0B bot...")
        self.initialized = False
        self.logger.info("Bot instance created")
    
    def __del__(self):
        self.close()
        
    def close(self):
        if not self._closed:
            for handler in logging.getLogger('B0B').handlers[:]:
                if hasattr(handler, 'close'):
                    handler.close()
                logging.getLogger('B0B').removeHandler(handler)
            self._closed = True
    
    async def on_start(self):
        """Called once at the start of the game."""
        print("[DEBUG] MyBot on_start called")
        logger.info("[DEBUG] MyBot on_start called")

        try:
            self.logger.info("=" * 50)
            self.logger.info("GAME STARTED - INITIALIZING BOT")
            self.logger.info("=" * 50)
            
            # Use the parent class's on_start which handles race-aware initialization
            await super().on_start()
            
            # Mark bot as initialized
            self.initialized = True
            self.logger.info("Bot initialization complete!")
            
        except Exception as e:
            self.logger.error(f"Error during bot initialization: {e}")
            self.logger.exception("Full traceback:")
            raise
    
    async def on_step(self, iteration):
        """Called every game step."""
        if not self.initialized:
            self.logger.warning("Bot not initialized, skipping step")
            return

        try:
            # Only log every 10 seconds (224 steps at faster speed)
            if iteration % 224 == 0:
                self.logger.info(
                    f"\n{'='*20} STEP {iteration} ({self.time:.1f}s) {'='*20}"
                )
                self.logger.info(
                    f"Minerals: {self.minerals} | Gas: {self.vespene} | "
                    f"Supply: {self.supply_used}/{self.supply_cap}"
                )
                self.logger.info(
                    f"Workers: {self.workers.amount} | Army: {self.supply_army}"
                )
            
            # Delegate to parent class's on_step
            await super().on_step(iteration)
            
        except Exception as e:
            self.logger.error(f"Error in on_step: {e}")
            self.logger.exception("Full traceback:")

    async def on_end(self, result):
        """Called when the game ends."""
        try:
            self.logger.info(f"Game ended with result: {result}")
            # Delegate to parent class's on_end
            await super().on_end(result)
        except Exception as e:
            self.logger.error(f"Error in on_end: {e}")
            self.logger.exception("Full traceback:")
