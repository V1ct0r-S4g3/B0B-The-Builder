from sc2.bot_ai import BotAI
from sc2.data import Result, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from managers.economy_manager import EconomyManager
from managers.military_manager import MilitaryManager
from managers.head_manager import HeadManager
import random

class CompetitiveBot(BotAI):
    """Main bot class that handles the game logic and coordinates managers."""
    
    def __init__(self):
        super().__init__()
        # Initialize the HeadManager first
        self.head = HeadManager(self)
        
        # Initialize all managers with reference to head
        self.economy_manager = EconomyManager(self)
        self.military_manager = MilitaryManager(self)
        
        # Register managers with the HeadManager
        self.head.register_manager('economy', self.economy_manager)
        self.head.register_manager('military', self.military_manager)
        
        # Track game state
        self.game_started = False

    async def on_start(self):
        """Initialize the game and all managers."""
        print("Game started")
        self.game_started = True
        
        # Let the HeadManager handle manager initialization
        await self.head.on_start()
        
        # Log initial game state
        print(f"Starting position: {self.start_location}")
        print(f"Enemy race: {self.enemy_race if hasattr(self, 'enemy_race') else 'Unknown'}")

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
