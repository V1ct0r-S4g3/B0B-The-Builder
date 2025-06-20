"""Main bot module containing the MyBot class."""

import logging
import os
from pathlib import Path

from sc2.bot_ai import BotAI

from managers.economy_manager import EconomyManager
from managers.head_manager import HeadManager
from managers.military_manager import MilitaryManager

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


class MyBot(BotAI):
    """Main bot class that inherits from SC2's BotAI and coordinates all managers."""

    def __init__(self):
        """Initialize the bot and its managers."""
        print("[DEBUG] MyBot __init__ called")
        logger.info("[DEBUG] MyBot __init__ called")
        print(f"[DEBUG] BotAI module: {BotAI.__module__}")
        print(f"[DEBUG] BotAI file: {getattr(BotAI, '__file__', 'N/A')}")
        logger.info(f"[DEBUG] BotAI module: {BotAI.__module__}")
        logger.info(f"[DEBUG] BotAI file: {getattr(BotAI, '__file__', 'N/A')}")
        super().__init__()
        self._closed = False
        self.logger = logger.getChild('MyBot')
        self.logger.info("Initializing B0B bot...")
        # Initialize managers
        self.head_manager = None
        self.economy_manager = None
        self.military_manager = None
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

            self.logger.info("Initializing managers...")

            # Initialize managers with detailed logging
            self.logger.debug("Creating HeadManager...")
            self.head_manager = HeadManager(self)
            self.logger.debug("HeadManager created")

            self.logger.debug("Creating EconomyManager...")
            self.economy_manager = EconomyManager(self)
            self.logger.debug("EconomyManager created")

            self.logger.debug("Creating MilitaryManager...")
            self.military_manager = MilitaryManager(self)
            self.logger.debug("MilitaryManager created")

            # Register managers with HeadManager
            self.logger.debug("Registering managers with HeadManager...")
            self.head_manager.register_manager('economy', self.economy_manager)
            self.head_manager.register_manager('military', self.military_manager)
            self.logger.debug("Managers registered successfully")

            # Initialize the HeadManager
            self.logger.debug("Calling HeadManager.on_start()...")
            await self.head_manager.on_start()
            self.logger.debug("HeadManager.on_start() completed")

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
            # Log step information
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

            # Delegate to head manager
            if self.head_manager:
                await self.head_manager.on_step()

        except Exception as e:
            self.logger.error(f"Error in on_step: {e}")
            self.logger.exception("Full traceback:")

    async def on_end(self, result):
        """Called when the game ends."""
        try:
            self.logger.info(f"Game ended with result: {result}")
            if self.head_manager:
                await self.head_manager.on_end(result)
        except Exception as e:
            self.logger.error(f"Error in on_end: {e}")
            self.logger.exception("Full traceback:")
