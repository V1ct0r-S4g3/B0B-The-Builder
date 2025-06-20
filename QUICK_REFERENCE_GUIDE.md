# Quick Reference Guide - StarCraft II Bot Development

## Essential Code Patterns

### 1. Bot Main Class Structure
```python
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from src.managers.head_manager import HeadManager

class MyBot(sc2.BotAI):
    def __init__(self):
        super().__init__()
        self.head_manager = None

    async def on_start(self):
        """Initialize managers when game starts"""
        self.head_manager = HeadManager(self)
        await self.head_manager.on_start()

    async def on_step(self, iteration: int):
        """Main game loop - delegate to managers"""
        if self.head_manager:
            await self.head_manager.on_step(iteration)
```

### 2. HeadManager Pattern
```python
class HeadManager:
    def __init__(self, ai):
        self.ai = ai
        self.managers = []
        self.economy_manager = None
        self.military_manager = None

    async def on_start(self):
        """Initialize all managers"""
        self.economy_manager = EconomyManager(self.ai)
        self.military_manager = MilitaryManager(self.ai)
        
        self.managers = [self.economy_manager, self.military_manager]
        
        for manager in self.managers:
            await manager.on_start()

    async def on_step(self, iteration: int):
        """Run all managers each step"""
        for manager in self.managers:
            await manager.on_step(iteration)
```

### 3. Manager Base Class
```python
class BaseManager:
    def __init__(self, ai):
        self.ai = ai
        self.debug = True

    async def on_start(self):
        """Override in subclasses"""
        pass

    async def on_step(self, iteration: int):
        """Override in subclasses"""
        pass
```

### 4. Building Placement Strategy
```python
async def _get_building_placement(self, building_type, base_position, forward_direction):
    """Strategic building placement - keep close to base"""
    try:
        # Calculate placement area (4-6 units from base)
        placement_area = base_position + forward_direction * 4
        
        placement = await self.ai.find_placement(
            building_type,
            near=placement_area,
            placement_step=2,
            max_distance=6  # Keep buildings close
        )
        
        if placement:
            return placement
            
        # Fallback to near base
        return await self.ai.find_placement(building_type, near=base_position, placement_step=2)
        
    except Exception as e:
        if self.debug:
            print(f"Error in building placement: {e}")
        return None
```

### 5. Worker Distribution
```python
async def manage_workers(self):
    """Optimal worker distribution between minerals and gas"""
    # Target 6 workers per refinery
    refineries = self.ai.gas_buildings
    for refinery in refineries:
        workers = self.ai.workers.closer_than(10, refinery)
        if workers.amount > 6:
            # Send excess workers to minerals
            excess_workers = workers[6:]
            for worker in excess_workers:
                worker.gather(self.ai.mineral_field.closest_to(worker))
```

### 6. Supply Management
```python
async def build_supply_depots(self):
    """Proactive supply depot building"""
    if (self.ai.supply_left < 5 and 
        self.ai.can_afford(UnitTypeId.SUPPLYDEPOT) and
        not self.ai.already_pending(UnitTypeId.SUPPLYDEPOT)):
        
        worker = self.ai.select_build_worker(self.ai.townhalls.first.position)
        if worker:
            placement = await self._get_supply_depot_placement(
                self.ai.townhalls.first.position,
                self.ai.game_info.map_center - self.ai.townhalls.first.position
            )
            if placement:
                worker.build(UnitTypeId.SUPPLYDEPOT, placement)
```

### 7. Rally Point Setting
```python
async def set_rally_points(self):
    """Set rally points for all production buildings"""
    forward_position = self.ai.townhalls.first.position.towards(
        self.ai.game_info.map_center, 10
    )
    
    for barracks in self.ai.structures(UnitTypeId.BARRACKS):
        if barracks.orders:
            continue
        barracks(AbilityId.RALLY_BUILDING, forward_position)
```

### 8. Build Order System
```python
class BuildOrder:
    def __init__(self):
        self.steps = [
            "Supply Depot at 13 supply",
            "First Barracks at 14 supply", 
            "First Refinery",
            "Bunker for defense",
            "Second Barracks",
            "Factory for tech",
            "Starport for air units",
            "Third Barracks"
        ]
        self.current_step = 0

    def is_completed(self, ai):
        """Check if current build order step is completed"""
        return self.current_step >= len(self.steps)

    def get_next_step(self):
        """Get the next build order step"""
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
```

## Critical Fixes

### 1. Import Issues
```python
# OLD (python-sc2)
from sc2 import BotAI, run_game, maps
from sc2.unit import Unit
from sc2.units import Units

# NEW (BurnySc2)
from sc2 import BotAI, run_game, maps
from sc2.unit import Unit
from sc2.units import Units
```

### 2. Async/Await Pattern
```python
# CORRECT - Always use async/await
async def on_start(self):
    await self.initialize_managers()

async def on_step(self, iteration: int):
    await self.run_managers()

# WRONG - Don't mix sync/async
def on_start(self):
    self.initialize_managers()  # Missing await
```

### 3. Error Handling
```python
async def safe_build(self, building_type, position):
    """Safe building with error handling"""
    try:
        worker = self.ai.select_build_worker(position)
        if worker and self.ai.can_afford(building_type):
            worker.build(building_type, position)
            return True
    except Exception as e:
        if self.debug:
            print(f"Build error: {e}")
    return False
```

## Performance Tips

### 1. Efficient Unit Selection
```python
# GOOD - Use filters
workers = self.ai.workers.filter(lambda w: w.is_gathering)
barracks = self.ai.structures(UnitTypeId.BARRACKS).ready

# BAD - Iterate through all units
for unit in self.ai.units:
    if unit.type_id == UnitTypeId.SCV:
        # Process worker
```

### 2. Caching Positions
```python
# Cache frequently used positions
self.base_position = self.ai.townhalls.first.position
self.forward_direction = self.ai.game_info.map_center - self.base_position
```

### 3. Conditional Execution
```python
# Only run expensive operations when needed
if iteration % 10 == 0:  # Every 10 steps
    await self.update_strategy()
```

## Testing Commands

```bash
# Basic bot test
python run_simple_bot.py

# Environment check
python check_env.py

# Run with specific map
python -m sc2.main --map "2000AtmospheresAIE" --races terran terran --ai sc2.bot_ai.BotAI src.bot.main:MyBot
```

## Success Metrics

- **Game Duration**: > 3 minutes
- **Economy**: > 1000 minerals/min
- **Army**: > 15 supply
- **Supply**: No blocking (always < 90% capacity)
- **Stability**: No crashes

## Common Pitfalls

1. **Forgetting await**: Always await async functions
2. **No error handling**: Wrap critical operations in try-catch
3. **Poor placement**: Keep buildings close to base
4. **Supply blocking**: Build supply depots proactively
5. **Manager not running**: Check initialization sequence

---

**Use this guide when starting new bot projects!** 