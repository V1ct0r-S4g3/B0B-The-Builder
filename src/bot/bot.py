from sc2.bot_ai import BotAI
from sc2.data import Result, Race

# Add the src directory to the Python path
import sys
from pathlib import Path
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

# Import all race-specific economy managers
from managers.terran_economy_manager import TerranEconomyManager  # Terran
from managers.protoss_economy_manager import ProtossEconomyManager  # Protoss
from managers.zerg_economy_manager import ZergEconomyManager  # Zerg
from managers.military_manager import MilitaryManager  # Terran military
from managers.protoss_military_manager import ProtossMilitaryManager  # Protoss
from managers.zerg_military_manager import ZergMilitaryManager  # Zerg military
from managers.head_manager import HeadManager


class CompetitiveBot(BotAI):
    """Main bot class that handles the game logic and coordinates managers."""
    
    def __init__(self):
        super().__init__()
        # Initialize the HeadManager first
        self.head = HeadManager(self)
        
        # Military manager will be set based on race in on_start
        self.military_manager = None
        
        # Economy manager will be set based on race in on_start
        self.economy_manager = None
        
        # Track game state
        self.game_started = False

    async def on_start(self):
        """Initialize the game and all managers."""
        print("Game started")
        self.game_started = True
        
        # Initialize the appropriate economy manager based on race
        await self._initialize_economy_manager()
        
        # Initialize the appropriate military manager based on race
        await self._initialize_military_manager()
        
        # Register managers with the HeadManager
        if self.economy_manager:
            self.head.register_manager('economy', self.economy_manager)
        if self.military_manager:
            self.head.register_manager('military', self.military_manager)
        
        # Let the HeadManager handle manager initialization
        await self.head.on_start()
        
        # Log initial game state
        print(f"Starting position: {self.start_location}")
        print(f"Bot race: {self.race}")
        print(f"Enemy race: {self.enemy_race if hasattr(self, 'enemy_race') else 'Unknown'}")

    async def _initialize_economy_manager(self):
        """Initialize the appropriate economy manager based on the bot's race."""
        if self.race == Race.Terran:
            self.economy_manager = TerranEconomyManager(self)
            print("Initialized Terran Economy Manager")
        elif self.race == Race.Protoss:
            self.economy_manager = ProtossEconomyManager(self)
            print("Initialized Protoss Economy Manager")
        elif self.race == Race.Zerg:
            self.economy_manager = ZergEconomyManager(self)
            print("Initialized Zerg Economy Manager")
        else:
            # Default to Terran if race is unknown
            self.economy_manager = TerranEconomyManager(self)
            print(f"Unknown race {self.race}, defaulting to Terran Economy Manager")

    async def _initialize_military_manager(self):
        """Initialize the appropriate military manager based on the bot's race."""
        if self.race == Race.Terran:
            self.military_manager = MilitaryManager(self)
            print("Initialized Terran Military Manager")
        elif self.race == Race.Protoss:
            self.military_manager = ProtossMilitaryManager(self)
            print("Initialized Protoss Military Manager")
        elif self.race == Race.Zerg:
            self.military_manager = ZergMilitaryManager(self)
            print("Initialized Zerg Military Manager")
        else:
            # Default to Terran if race is unknown
            self.military_manager = MilitaryManager(self)
            print(f"Unknown race {self.race}, defaulting to Terran Military Manager")

    async def on_step(self, iteration: int):
        """Process each game step by delegating to the HeadManager."""
        try:
            # Let the HeadManager coordinate all managers
            await self.head.on_step()
            
            # Debug output every 10 seconds
            if iteration % 224 == 0:  # ~10 seconds at 'faster' speed
                self._log_game_state()
                
        except Exception as e:
            print(f"Error in on_step: {str(e)}")
            import traceback
            traceback.print_exc()

    async def on_end(self, result: Result):
        """Handle game end and clean up resources."""
        print(f"\n=== Game Over ===")
        print(f"Result: {result}")
        print(f"Game time: {self.time_formatted}")
        print(f"Final supply: {self.supply_used}/{self.supply_cap}")
        print(f"Workers: {self.workers.amount}")
        print(f"Bases: {self.townhalls.amount}")
        
        # Let the HeadManager handle cleanup
        if hasattr(self, 'head') and self.head:
            await self.head.on_end(result)
    
    def _log_game_state(self):
        """Log the current game state for debugging."""
        if not self.game_started:
            return
            
        state = self.head.get_state()
        print(f"\n--- Game State ({self.time_formatted}) ---")
        print(f"Minerals: {self.minerals}, Gas: {self.vespene}")
        print(f"Income: {state['economy']['mineral_income']:.1f} min/min, {state['economy']['gas_income']:.1f} gas/min")
        print(f"Workers: {state['economy']['worker_count']} (Saturation: {state['economy']['saturation']*100:.1f}%)")
        print(f"Army Supply: {state['military']['army_supply']}, Tech Level: {state['military']['tech_level']}")
        print(f"Upgrades: {', '.join(state['military']['upgrades']) or 'None'}")
        
        # Log army composition
        if state['military']['army_composition']:
            print("Army composition:")
            for unit_type, count in state['military']['army_composition'].items():
                print(f"  {unit_type.name}: {count}")
        
        # Log current strategy
        print(f"Strategy: {self.head.strategy} ({self.head.strategies[self.head.strategy]['description']})")
        
    @property
    def time_formatted(self) -> str:
        """Return the current game time in MM:SS format."""
        minutes = int(self.time // 60)
        seconds = int(self.time % 60)
        return f"{minutes:02d}:{seconds:02d}"
