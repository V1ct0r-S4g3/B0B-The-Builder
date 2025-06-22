# B0B Template Guide

## 🎯 Template Overview

This is a clean, production-ready StarCraft II bot template with multi-race support. The template provides a solid foundation for building competitive SC2 bots with modular architecture and race-specific implementations.

## 🏗️ Template Structure

```
B0B/
├── src/
│   ├── bot/
│   │   ├── bot.py          # Main bot class with race detection
│   │   └── main.py         # Bot entry point
│   ├── managers/
│   │   ├── head_manager.py           # Coordinates all managers
│   │   ├── terran_economy_manager.py # Terran economy logic
│   │   ├── protoss_economy_manager.py # Protoss economy logic
│   │   ├── zerg_economy_manager.py   # Zerg economy logic
│   │   ├── military_manager.py       # Terran military logic
│   │   ├── protoss_military_manager.py # Protoss military logic
│   │   └── zerg_military_manager.py  # Zerg military logic
│   └── config/
│       └── config.py       # Configuration settings
├── run_simple_bot.py       # Quick start launcher
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── LICENSE                # MIT License
└── .gitignore            # Git ignore rules
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd B0B
pip install -r requirements.txt
```

### 2. Run the Bot
```bash
# Run with auto-race detection
python run_simple_bot.py

# Run specific race
python run_simple_bot.py --race Zerg
```

## 🎮 Race Support

### Terran
- **Economy**: SCV production, Supply Depot building, Refinery management
- **Military**: Barracks with Reactors, Marine/Marauder production, Medivac support
- **Strategy**: Bio ball composition with fast expand

### Protoss
- **Economy**: Probe production, Pylon building, Assimilator management
- **Military**: Gateway spam (4 gateways), Zealot/Stalker production
- **Strategy**: Gateway timing attack with defensive positioning

### Zerg
- **Economy**: Drone production from larva, Overlord morphing, Extractor building
- **Military**: Spawning Pool → Roach Warren, Zergling/Roach production
- **Strategy**: Larva-based economy with wave attacks

## 🔧 Architecture

### Manager System
The bot uses a modular manager architecture:

- **HeadManager**: Central coordinator that initializes and manages all other managers
- **Economy Managers**: Race-specific economy logic (workers, supply, gas)
- **Military Managers**: Race-specific military logic (units, buildings, strategy)

### Race-Aware Initialization
The bot automatically detects its race and initializes the appropriate managers:

```python
if self.race == Race.Terran:
    self.economy_manager = TerranEconomyManager(self)
    self.military_manager = MilitaryManager(self)
elif self.race == Race.Protoss:
    self.economy_manager = ProtossEconomyManager(self)
    self.military_manager = ProtossMilitaryManager(self)
elif self.race == Race.Zerg:
    self.economy_manager = ZergEconomyManager(self)
    self.military_manager = ZergMilitaryManager(self)
```

## 📊 Features

### Economy Management
- **Worker Saturation**: 100% mineral saturation across all races
- **Gas Management**: Optimal worker distribution between minerals and gas
- **Supply Management**: Automatic supply production (Supply Depots, Pylons, Overlords)
- **Expansion Logic**: Intelligent timing for additional bases

### Military Strategy
- **Race-Specific Build Orders**: Each race has unique unit compositions
- **Defensive AI**: Aggressive defense when enemies are within 30 units of base
- **Counter-Attack Logic**: Pursues enemies within 50 units when army size ≥ 3
- **Wave Attacks**: Launches coordinated attacks with 6+ units minimum
- **Smart Building Placement**: Avoids blocking worker paths and resources

### Technical Features
- **Modular Architecture**: Clean separation of concerns
- **Error Handling**: Robust error handling with graceful degradation
- **Debug Output**: Comprehensive logging for development and analysis
- **Performance Optimized**: Efficient game loop with minimal overhead

## 🛠️ Customization

### Adding New Races
1. Create new economy and military managers in `src/managers/`
2. Update the bot initialization in `src/bot/bot.py`
3. Implement race-specific logic in the new managers

### Modifying Existing Races
1. Edit the appropriate manager files in `src/managers/`
2. Test changes with `python run_simple_bot.py --race <Race>`
3. Update documentation as needed

### Configuration
Key settings can be modified in `src/config/config.py`:
- Worker ratios per race
- Supply buffer sizes
- Attack thresholds
- Expansion timing
- Debug output levels

## 🐛 Debugging

Enable debug output by setting `debug = True` in manager classes. Output includes:
- Economy counts and worker distribution
- Military unit production and army actions
- Building placement attempts
- Error messages and stack traces

## 📈 Performance

### Economy Metrics
- **Worker Saturation**: 100% mineral saturation, optimal gas worker ratios
- **Income Rate**: 800+ minerals/minute, 100+ gas/minute
- **Expansion Timing**: Fast expand with proper worker distribution

### Military Metrics
- **Army Composition**: Race-appropriate unit mixes
- **Attack Timing**: Wave attacks with 6+ units minimum
- **Defensive Response**: Immediate reaction to threats within 30 units

## 🎯 Best Practices

### Code Organization
- Keep race-specific logic in dedicated managers
- Use clear, descriptive method names
- Add debug output for development
- Handle errors gracefully

### Performance
- Minimize API calls in the game loop
- Use efficient unit selection and caching
- Avoid blocking operations
- Optimize building placement algorithms

### Testing
- Test each race individually
- Verify economy and military functionality
- Check for supply blocking and worker efficiency
- Monitor debug output for issues

## 📚 Documentation

- **README.md**: Complete project overview and setup instructions
- **B0B_FINAL_STATUS.md**: Detailed technical status and achievements
- **BOT_IMPROVEMENTS_SUMMARY.md**: Development history and lessons learned

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**B0B Template - Ready for Your Next Bot Project! 🏗️⚔️**

*Template Version: 2.0 - Multi-Race Support*
*Last Updated: June 2025* 