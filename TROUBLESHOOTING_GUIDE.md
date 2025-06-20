# Troubleshooting Guide - StarCraft II Bot Development

## Common Issues and Solutions

### 1. Import Errors

#### Problem: ModuleNotFoundError for sc2
```
ModuleNotFoundError: No module named 'sc2'
```

**Solution:**
```bash
# Install BurnySc2 (not python-sc2)
pip install burnysc2>=5.0.0

# Verify installation
python -c "import sc2; print('SC2 imported successfully')"
```

#### Problem: Import path issues
```
ImportError: cannot import name 'BotAI' from 'sc2'
```

**Solution:**
```python
# Correct import pattern
from sc2 import BotAI, run_game, maps
from sc2.player import Bot, Computer
from sc2.ids.unit_typeid import UnitTypeId
```

### 2. Async/Await Issues

#### Problem: RuntimeError about coroutines
```
RuntimeError: coroutine 'function_name' was never awaited
```

**Solution:**
```python
# CORRECT - Always await async functions
async def on_start(self):
    await self.initialize_managers()

async def on_step(self, iteration: int):
    await self.run_managers()

# WRONG - Missing await
def on_start(self):
    self.initialize_managers()  # This will cause the error
```

#### Problem: Mixing sync and async code
```python
# WRONG - Don't do this
def some_function(self):
    result = await self.async_function()  # Can't await in sync function

# CORRECT - Make function async
async def some_function(self):
    result = await self.async_function()
```

### 3. Manager Not Running

#### Problem: Managers not executing
- No debug output from managers
- Bot runs but doesn't build anything
- Economy not working

**Solution:**
```python
# Check HeadManager initialization
class MyBot(sc2.BotAI):
    async def on_start(self):
        # CRITICAL: Initialize HeadManager
        self.head_manager = HeadManager(self)
        await self.head_manager.on_start()  # Don't forget await!

    async def on_step(self, iteration: int):
        # CRITICAL: Call HeadManager each step
        if self.head_manager:
            await self.head_manager.on_step(iteration)
```

**Debug Steps:**
```python
# Add debug logging
class HeadManager:
    async def on_start(self):
        print("[HeadManager] Starting initialization...")
        self.economy_manager = EconomyManager(self.ai)
        self.military_manager = MilitaryManager(self.ai)
        
        self.managers = [self.economy_manager, self.military_manager]
        
        for manager in self.managers:
            print(f"[HeadManager] Starting {manager.__class__.__name__}")
            await manager.on_start()
        print("[HeadManager] Initialization complete")

    async def on_step(self, iteration: int):
        for manager in self.managers:
            await manager.on_step(iteration)
```

### 4. Building Placement Issues

#### Problem: Buildings placed too far from base
- Buildings on different levels
- Vulnerable positions
- Poor efficiency

**Solution:**
```python
async def _get_building_placement(self, building_type, base_position, forward_direction):
    """Keep buildings close to base"""
    try:
        # Reduced distances (4-6 units from base)
        placement_area = base_position + forward_direction * 4
        
        placement = await self.ai.find_placement(
            building_type,
            near=placement_area,
            placement_step=2,
            max_distance=6  # Reduced from 10+
        )
        
        if placement:
            return placement
            
        # Fallback to near base
        return await self.ai.find_placement(building_type, near=base_position, placement_step=2)
        
    except Exception as e:
        if self.debug:
            print(f"Building placement error: {e}")
        return None
```

#### Problem: Building placement fails
```
No valid placement found for building
```

**Solution:**
```python
# Add fallback placement logic
async def safe_build(self, building_type, base_position):
    """Safe building with multiple fallbacks"""
    # Try strategic placement first
    placement = await self._get_strategic_placement(building_type, base_position)
    if placement:
        return placement
    
    # Try near base
    placement = await self.ai.find_placement(building_type, near=base_position, placement_step=2)
    if placement:
        return placement
    
    # Try anywhere
    placement = await self.ai.find_placement(building_type, placement_step=4)
    return placement
```

### 5. Supply Blocking

#### Problem: Bot gets supply blocked
- Can't build units
- Workers idle
- Poor performance

**Solution:**
```python
async def build_supply_depots(self):
    """Build supply depots proactively"""
    # More aggressive supply building
    if (self.ai.supply_left < 5 and  # Reduced from 10
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
                if self.debug:
                    print(f"[Economy] Building Supply Depot at {placement}")
```

### 6. Worker Distribution Issues

#### Problem: Poor worker distribution
- Too many workers on gas
- Too few workers on minerals
- Inefficient resource collection

**Solution:**
```python
async def manage_workers(self):
    """Optimal worker distribution"""
    # Target 6 workers per refinery
    refineries = self.ai.gas_buildings
    for refinery in refineries:
        workers = self.ai.workers.closer_than(10, refinery)
        if workers.amount > 6:
            # Send excess workers to minerals
            excess_workers = workers[6:]
            for worker in excess_workers:
                worker.gather(self.ai.mineral_field.closest_to(worker))
                if self.debug:
                    print(f"[Economy] Sent excess gas worker to minerals")
```

### 7. Build Order Issues

#### Problem: Build order not progressing
- Stuck on first step
- Not building structures
- Poor timing

**Solution:**
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

    def check_step_completion(self, ai):
        """Check if current step is completed"""
        if self.current_step >= len(self.steps):
            return True
            
        current_step = self.steps[self.current_step]
        
        # Check specific conditions for each step
        if "Supply Depot" in current_step:
            if ai.structures(UnitTypeId.SUPPLYDEPOT).amount > 0:
                self.current_step += 1
                return True
        elif "Barracks" in current_step:
            if ai.structures(UnitTypeId.BARRACKS).amount > 0:
                self.current_step += 1
                return True
        # Add more step checks...
        
        return False
```

### 8. Rally Point Issues

#### Problem: Units not rallying properly
- Units idle at production buildings
- No forward positioning
- Poor army control

**Solution:**
```python
async def set_rally_points(self):
    """Set rally points for all production buildings"""
    # Calculate forward position
    base_position = self.ai.townhalls.first.position
    map_center = self.ai.game_info.map_center
    forward_direction = map_center - base_position
    forward_position = base_position + forward_direction.normalized * 10
    
    # Set rally points for all barracks
    for barracks in self.ai.structures(UnitTypeId.BARRACKS):
        if barracks.orders:
            continue
        barracks(AbilityId.RALLY_BUILDING, forward_position)
        if self.debug:
            print(f"[Military] Set rally point for barracks at {forward_position}")
```

### 9. Performance Issues

#### Problem: Bot runs slowly
- High CPU usage
- Laggy performance
- Poor responsiveness

**Solution:**
```python
# Optimize unit selection
# GOOD - Use filters
workers = self.ai.workers.filter(lambda w: w.is_gathering)
barracks = self.ai.structures(UnitTypeId.BARRACKS).ready

# BAD - Iterate through all units
for unit in self.ai.units:
    if unit.type_id == UnitTypeId.SCV:
        # Process worker

# Cache frequently used values
class MilitaryManager:
    def __init__(self, ai):
        self.ai = ai
        self.base_position = None
        self.forward_direction = None

    async def on_start(self):
        # Cache positions once
        self.base_position = self.ai.townhalls.first.position
        self.forward_direction = self.ai.game_info.map_center - self.base_position

# Conditional execution
async def on_step(self, iteration: int):
    # Only run expensive operations occasionally
    if iteration % 10 == 0:  # Every 10 steps
        await self.update_strategy()
    
    # Run essential operations every step
    await self.manage_production()
```

### 10. Game Crashes

#### Problem: Bot crashes during game
- Connection errors
- Protocol errors
- Unexpected exceptions

**Solution:**
```python
# Add comprehensive error handling
async def safe_operation(self, operation_func, *args, **kwargs):
    """Wrapper for safe operations"""
    try:
        return await operation_func(*args, **kwargs)
    except Exception as e:
        if self.debug:
            print(f"Error in {operation_func.__name__}: {e}")
        return None

# Use in managers
async def on_step(self, iteration: int):
    await self.safe_operation(self.manage_workers)
    await self.safe_operation(self.build_supply_depots)
    await self.safe_operation(self.manage_production)
```

### 11. Environment Issues

#### Problem: Different behavior on different systems
- Windows vs Linux differences
- Python version issues
- Package conflicts

**Solution:**
```python
# Environment check script
import sys
import subprocess

def check_environment():
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    try:
        import sc2
        print(f"SC2 version: {sc2.__version__}")
    except ImportError:
        print("SC2 not installed")
    
    # Check other dependencies...

if __name__ == "__main__":
    check_environment()
```

### 12. Debugging Techniques

#### Enable Debug Logging
```python
class BaseManager:
    def __init__(self, ai):
        self.ai = ai
        self.debug = True  # Enable debug output

    def debug_print(self, message):
        if self.debug:
            print(f"[{self.__class__.__name__}] {message}")
```

#### Step-by-Step Debugging
```python
async def on_step(self, iteration: int):
    if iteration % 100 == 0:  # Every 100 steps
        self.debug_print(f"Step {iteration}")
        self.debug_print(f"Workers: {self.ai.workers.amount}")
        self.debug_print(f"Supply: {self.ai.supply_used}/{self.ai.supply_cap}")
        self.debug_print(f"Minerals: {self.ai.minerals}")
```

## Testing Checklist

Before considering the bot "working":

- [ ] Bot runs for 3+ minutes without crashing
- [ ] Economy collection rate > 500 minerals/min
- [ ] Army supply > 10 units
- [ ] No supply blocking (always < 90% capacity)
- [ ] Buildings placed near base (not too far out)
- [ ] Workers distributed properly (6 per gas, rest on minerals)
- [ ] Rally points set for production buildings
- [ ] Build order progresses through all steps
- [ ] No import errors or exceptions
- [ ] Debug output shows managers running

## Performance Benchmarks

**Good Performance:**
- Game Duration: 3+ minutes
- Economy: 1000+ minerals/min
- Army: 15+ supply
- Supply: < 90% capacity
- Stability: No crashes

**Poor Performance:**
- Game Duration: < 1 minute
- Economy: < 500 minerals/min
- Army: < 5 supply
- Supply: > 95% capacity
- Stability: Frequent crashes

---

**Use this guide to diagnose and fix common bot issues!** 