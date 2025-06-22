# B0B Template Guide

## Overview
B0B (The Builder) is designed as a **template bot** that other StarCraft II bots can use as a foundation. It provides a solid, working economy management system with a simple military manager that can be easily customized.

## Quick Start

### 1. Copy the Template
```bash
# Copy the entire B0B directory
cp -r B0B/ your_new_bot/
cd your_new_bot/
```

### 2. Rename and Customize
```bash
# Rename the bot
mv src/bot/main.py src/bot/your_bot.py
# Update the class name in the file
```

### 3. Modify Configuration
Edit `src/config/config.py` to customize:
- Build orders
- Army compositions  
- Economy settings
- Strategy selection

## Key Components

### Economy Manager (`src/managers/economy_manager.py`)
**What it does:**
- Manages worker production and distribution
- Handles supply depot construction
- Controls expansion timing
- Manages gas worker allocation

**Customization points:**
```python
# In config.py
economy = EconomyConfig(
    max_workers=80,
    gas_workers_per_refinery=6,
    min_time_before_expand=120.0
)
```

### Military Manager (`src/managers/military_manager.py`)
**What it does:**
- Executes build orders
- Trains army units
- Controls army movement and combat
- Manages production facilities

**Customization points:**
```python
# Add new build order
config.add_build_order('my_strategy', [
    (UnitTypeId.SUPPLYDEPOT, 13, "Supply Depot"),
    (UnitTypeId.BARRACKS, 14, "Barracks"),
    # ... more steps
])

# Add new army composition
config.add_army_composition('my_strategy', {
    UnitTypeId.MARINE: 30,
    UnitTypeId.MEDIVAC: 5,
})
```

### Head Manager (`src/managers/head_manager.py`)
**What it does:**
- Coordinates all other managers
- Handles game state management
- Provides logging and debugging

## Customization Examples

### Example 1: Mech Strategy
```python
# In config.py
config.add_build_order('mech_rush', [
    (UnitTypeId.SUPPLYDEPOT, 13, "Supply Depot"),
    (UnitTypeId.BARRACKS, 14, "Barracks"),
    (UnitTypeId.FACTORY, 20, "Factory"),
    (UnitTypeId.REFINERY, 15, "Refinery"),
    (UnitTypeId.FACTORY, 25, "Second Factory"),
])

config.add_army_composition('mech_rush', {
    UnitTypeId.SIEGETANK: 8,
    UnitTypeId.HELLION: 12,
    UnitTypeId.THOR: 2,
})

# Set as default strategy
config.default_strategy = 'mech_rush'
```

### Example 2: Air Strategy
```python
config.add_build_order('air_rush', [
    (UnitTypeId.SUPPLYDEPOT, 13, "Supply Depot"),
    (UnitTypeId.BARRACKS, 14, "Barracks"),
    (UnitTypeId.STARPORT, 18, "Starport"),
    (UnitTypeId.REFINERY, 15, "Refinery"),
    (UnitTypeId.STARPORT, 22, "Second Starport"),
])

config.add_army_composition('air_rush', {
    UnitTypeId.VIKINGFIGHTER: 8,
    UnitTypeId.BANSHEE: 4,
    UnitTypeId.MEDIVAC: 2,
})
```

## File Structure
```
src/
├── bot/
│   └── main.py              # Main bot class
├── managers/
│   ├── economy_manager.py   # Economy management
│   ├── military_manager.py  # Military management
│   └── head_manager.py      # Coordination
├── config/
│   └── config.py            # Configuration system
└── utils/                   # Utility functions
```

## Best Practices

### 1. Keep Economy Manager Intact
The economy manager is the core strength of B0B. Don't modify it unless absolutely necessary.

### 2. Customize Through Configuration
Use the config system instead of modifying manager code directly.

### 3. Test Incrementally
Make small changes and test frequently to ensure stability.

### 4. Document Your Changes
Add comments explaining your customizations for future reference.

## Common Customizations

### Adding New Units
1. Add unit to army composition in config
2. Add training logic in `_train_army` method
3. Add unit to `_update_army_composition` method

### Adding New Strategies
1. Create build order in config
2. Create army composition in config
3. Optionally add strategy-specific logic

### Modifying Combat Logic
Edit the `_control_army` method in military manager to implement your combat style.

## Troubleshooting

### Bot Not Building Units
- Check if build order is properly defined
- Verify army composition includes the units
- Ensure training logic exists in `_train_army`

### Economy Issues
- Check worker counts in config
- Verify expansion timing settings
- Review gas worker allocation

### Performance Issues
- Reduce debug logging
- Optimize manager execution frequency
- Check for infinite loops in custom code

## Support
For questions or issues with the template:
1. Check this guide first
2. Review the example configurations
3. Look at the inline documentation in the code

## Version History
- **v1.0**: Initial template release with economy and military managers
- **v1.1**: Added configuration system and documentation
- **v1.2**: Improved army control and template guide

---

**Happy Bot Building! 🚀** 