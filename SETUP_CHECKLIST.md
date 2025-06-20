# StarCraft II Bot Setup Checklist

## Pre-Setup Requirements
- [ ] Python 3.10+ installed
- [ ] StarCraft II game installed
- [ ] Git installed (for version control)

## 1. Project Structure Setup
```
your_bot_project/
├── src/
│   ├── __init__.py
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── bot.py          # Main bot class
│   │   └── main.py         # Entry point
│   ├── managers/
│   │   ├── __init__.py
│   │   ├── head_manager.py
│   │   ├── economy_manager.py
│   │   └── military_manager.py
│   └── config/
│       ├── __init__.py
│       └── config.py
├── tests/
├── requirements.txt
├── run_bot.py
├── check_env.py
└── README.md
```

## 2. Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install burnysc2>=5.0.0
pip install aiohttp
pip install asyncio

# Create requirements.txt
pip freeze > requirements.txt
```

## 3. Dependencies (requirements.txt)
```txt
burnysc2>=5.0.0
aiohttp>=3.8.0
asyncio
```

## 4. Core Files to Create

### 4.1 Main Bot Class (src/bot/bot.py)
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

### 4.2 Entry Point (src/bot/main.py)
```python
from src.bot.bot import MyBot

if __name__ == "__main__":
    from sc2 import run_game, maps
    from sc2.player import Bot, Computer
    
    run_game(
        maps.get("2000AtmospheresAIE"),
        [
            Bot(Race.Terran, MyBot()),
            Computer(Race.Terran, Difficulty.Medium)
        ],
        realtime=False
    )
```

### 4.3 Head Manager (src/managers/head_manager.py)
```python
from src.managers.economy_manager import EconomyManager
from src.managers.military_manager import MilitaryManager

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

### 4.4 Economy Manager (src/managers/economy_manager.py)
```python
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2

class EconomyManager:
    def __init__(self, ai):
        self.ai = ai
        self.debug = True

    async def on_start(self):
        """Initialize economy manager"""
        pass

    async def on_step(self, iteration: int):
        """Run economy logic each step"""
        await self.manage_workers()
        await self.build_supply_depots()

    async def manage_workers(self):
        """Manage worker distribution"""
        # Implement worker management logic
        pass

    async def build_supply_depots(self):
        """Build supply depots proactively"""
        # Implement supply depot building logic
        pass
```

### 4.5 Military Manager (src/managers/military_manager.py)
```python
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2

class MilitaryManager:
    def __init__(self, ai):
        self.ai = ai
        self.debug = True
        self.build_order_completed = False

    async def on_start(self):
        """Initialize military manager"""
        pass

    async def on_step(self, iteration: int):
        """Run military logic each step"""
        if not self.build_order_completed:
            await self.execute_build_order()
        else:
            await self.continuous_production()
        
        await self.set_rally_points()

    async def execute_build_order(self):
        """Execute build order"""
        # Implement build order logic
        pass

    async def continuous_production(self):
        """Continuous unit production"""
        # Implement continuous production logic
        pass

    async def set_rally_points(self):
        """Set rally points for production buildings"""
        # Implement rally point logic
        pass
```

## 5. Utility Files

### 5.1 Environment Check (check_env.py)
```python
import sys
import subprocess

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10+ required")
        return False
    print(f"✓ Python {sys.version}")
    return True

def check_dependencies():
    """Check required packages"""
    try:
        import sc2
        print("✓ BurnySc2 installed")
        return True
    except ImportError:
        print("ERROR: BurnySc2 not installed")
        return False

def main():
    print("Checking environment...")
    python_ok = check_python_version()
    deps_ok = check_dependencies()
    
    if python_ok and deps_ok:
        print("Environment check passed!")
    else:
        print("Environment check failed!")

if __name__ == "__main__":
    main()
```

### 5.2 Bot Runner (run_bot.py)
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.bot.main import main

if __name__ == "__main__":
    main()
```

## 6. Testing Setup

### 6.1 Basic Test (test_basic.py)
```python
import unittest
from src.bot.bot import MyBot

class TestBot(unittest.TestCase):
    def test_bot_creation(self):
        """Test that bot can be created"""
        bot = MyBot()
        self.assertIsNotNone(bot)

if __name__ == "__main__":
    unittest.main()
```

## 7. Configuration

### 7.1 Config File (src/config/config.py)
```python
class Config:
    # Debug settings
    DEBUG = True
    
    # Economy settings
    WORKERS_PER_REFINERY = 6
    SUPPLY_BUFFER = 5
    
    # Military settings
    MAX_BARRACKS = 3
    BUILDING_PLACEMENT_DISTANCE = 4
    
    # Performance settings
    LOGGING_INTERVAL = 10
```

## 8. Git Setup
```bash
# Initialize git repository
git init

# Create .gitignore
echo "*.pyc" > .gitignore
echo "__pycache__/" >> .gitignore
echo ".venv/" >> .gitignore
echo "*.log" >> .gitignore
echo "replays/" >> .gitignore

# Initial commit
git add .
git commit -m "Initial bot setup"
```

## 9. Testing Checklist
- [ ] Environment check passes
- [ ] Bot can be imported without errors
- [ ] Bot runs for at least 1 minute without crashing
- [ ] Managers are properly initialized
- [ ] Basic economy functions work
- [ ] Basic military functions work

## 10. Performance Validation
- [ ] Game runs for 3+ minutes
- [ ] Economy collection rate > 500 minerals/min
- [ ] No supply blocking
- [ ] Buildings placed near base
- [ ] No crashes or errors

## 11. Common Issues & Solutions

### Import Errors
```bash
# Solution: Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Manager Not Running
```python
# Solution: Check initialization sequence
# Make sure HeadManager.on_start() is called in bot.on_start()
```

### Building Placement Failures
```python
# Solution: Reduce placement distances and add fallbacks
placement = await self.ai.find_placement(building_type, near=base_position, max_distance=6)
```

### Supply Blocking
```python
# Solution: Build supply depots more aggressively
if self.ai.supply_left < 5:  # Reduced from 10
    # Build supply depot
```

## 12. Next Steps
- [ ] Implement basic economy logic
- [ ] Implement basic military logic
- [ ] Add error handling
- [ ] Add logging
- [ ] Test against AI
- [ ] Optimize performance
- [ ] Add advanced features

---

**Follow this checklist when setting up new bot projects!** 