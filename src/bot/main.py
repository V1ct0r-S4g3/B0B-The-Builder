"""Main bot module containing the MyBot class."""
import os
import sys
import logging
from pathlib import Path
from sc2 import BotAI
from managers.head_manager import HeadManager
from managers.economy_manager import EconomyManager
from managers.military_manager import MilitaryManager

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "bot.log"

# Clear previous log file if it exists
if log_file.exists():
    try:
        os.remove(log_file)
    except Exception as e:
        print(f"Warning: Could not remove log file: {e}")

# Configure logging
def setup_logging():
    """Set up logging configuration and return the file handler for cleanup."""
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create handlers
    file_handler = logging.FileHandler(log_file, mode='w')
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler]
    )
    
    # Create and configure our logger
    logger = logging.getLogger('B0B')
    logger.setLevel(logging.DEBUG)
    
    return file_handler

# Set up logging and get the file handler for cleanup
file_handler = setup_logging()
logger = logging.getLogger('B0B')

class MyBot(BotAI):
    """Main bot class that inherits from SC2's BotAI and coordinates all managers."""
    
    def __init__(self):
        """Initialize the bot and its managers."""
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
        """Ensure resources are properly cleaned up."""
        self.close()
        
    def close(self):
        """Explicitly clean up resources."""
        if not self._closed:
            # Close any open file handlers
            for handler in logging.getLogger('B0B').handlers[:]:
                if hasattr(handler, 'close'):
                    handler.close()
            self._closed = True
            self.initialized = False
    
    async def on_start(self):
        """Called once at the start of the game."""
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
            self.military_manager = MilitaryManager(self, self.head_manager)
            self.logger.debug("MilitaryManager created")
            
            # Register managers with HeadManager
            self.logger.info("Registering managers with HeadManager...")
            self.head_manager.register_manager('economy', self.economy_manager)
            self.head_manager.register_manager('military', self.military_manager)
            self.logger.debug("Managers registered")
            
            # Initialize HeadManager
            self.logger.info("Initializing HeadManager...")
            await self.head_manager.on_start()
            
            self.initialized = True
            self.logger.info("\n" + "=" * 50)
            self.logger.info("BOT INITIALIZATION COMPLETE")
            self.logger.info("=" * 50 + "\n")
            
        except Exception as e:
            self.logger.critical("!!! CRITICAL ERROR DURING INITIALIZATION !!!")
            self.logger.error(f"Error during initialization: {str(e)}", exc_info=True)
            self.logger.critical("Bot initialization failed. The bot may not function correctly.")
            raise
    
    async def on_step(self, iteration):
        """Called on every game step."""
        step_log = []
        step_log.append(f"\n{'='*20} STEP {iteration} ({self.time:.1f}s) {'='*20}")
        
        try:
            if not self.initialized:
                step_log.append("Bot not initialized, skipping step")
                self.logger.warning("\n".join(step_log))
                return
            
            step_log.append(f"Minerals: {self.minerals} | Gas: {self.vespene} | Supply: {self.supply_used}/{self.supply_cap}")
            step_log.append(f"Workers: {self.workers.amount} | Army: {self.supply_army:.1f}")
            
            # Let HeadManager coordinate the game step
            step_log.append("\n[HeadManager] Starting step...")
            await self.head_manager.on_step()
            step_log.append("[HeadManager] Step completed")
            
            # Additional bot-wide logic can go here
            
            # Log step completion
            step_log.append(f"\nStep {iteration} completed in {self.state.game_loop} game loops")
            self.logger.info("\n".join(step_log))
            
        except Exception as e:
            step_log.append(f"\n!!! ERROR in step {iteration} !!!")
            step_log.append(f"Error: {str(e)}")
            step_log.append("Traceback will be logged separately.")
            self.logger.error("\n".join(step_log))
            self.logger.error(f"Error in game step {iteration}:", exc_info=True)
            
            # Try to recover by reinitializing managers
            try:
                self.logger.warning("Attempting to recover by reinitializing managers...")
                await self.on_start()
                self.logger.info("Recovery complete, continuing with next step")
            except Exception as recovery_error:
                self.logger.critical("!!! RECOVERY FAILED !!!")
                self.logger.error(f"Recovery error: {str(recovery_error)}", exc_info=True)

    async def on_end(self, result):
        """Called at the end of the game."""
        try:
            if self.head_manager:
                await self.head_manager.on_end(result)
            self.logger.info(f"Game ended with result: {result}")
        except Exception as e:
            self.logger.error(f"Error during game end: {str(e)}", exc_info=True)
        finally:
            await super().on_end(result)
