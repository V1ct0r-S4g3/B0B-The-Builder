<div align="center">

# 🚀 B0B - The Builder

[![CI Status](https://github.com/V1ct0r-S4g3/B0B-The-Builder/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/V1ct0r-S4g3/B0B-The-Builder/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

</div>

A competitive StarCraft II bot with multi-race support, featuring intelligent economy management, military strategy, and defensive AI.

## 🚀 Features

### Multi-Race Support
- **Terran**: Marine/Marauder/Medivac composition with fast expand
- **Protoss**: Zealot/Stalker composition with gateway spam
- **Zerg**: Zergling/Roach composition with larva management

### Economy Management
- **Race-Specific Economy Managers**: Each race has optimized worker production and resource gathering
- **Smart Gas Management**: Automatic worker distribution between minerals and gas
- **Expansion Logic**: Intelligent timing for additional bases
- **Supply Management**: Automatic supply production (Supply Depots, Pylons, Overlords)

### Military Strategy
- **Race-Specific Military Managers**: Each race has unique build orders and unit compositions
- **Defensive AI**: Aggressive defense when enemies are near base
- **Counter-Attack Logic**: Pursues enemies within range when army is sufficient
- **Wave Attacks**: Launches coordinated attacks with minimum unit thresholds
- **Smart Building Placement**: Avoids blocking worker paths and resources

### Technical Features
- **Modular Architecture**: Separate managers for economy, military, and coordination
- **Debug Output**: Comprehensive logging for development and analysis
- **Error Handling**: Robust error handling with graceful degradation
- **Performance Optimized**: Efficient game loop with minimal overhead

## 📊 Performance

### Economy Metrics
- **Worker Saturation**: 100% mineral saturation, optimal gas worker ratios
- **Income Rate**: 800+ minerals/minute, 100+ gas/minute
- **Expansion Timing**: Fast expand with proper worker distribution

### Military Metrics
- **Army Composition**: Race-appropriate unit mixes
- **Attack Timing**: Wave attacks with 6+ units minimum
- **Defensive Response**: Immediate reaction to threats within 30 units

## 🏗️ Architecture

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
├── tests/                  # Test suite
├── replays/               # Game replays
└── logs/                  # Debug logs
```

## 🎮 Race-Specific Features

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

## 🚀 Quick Start

### Prerequisites
- StarCraft II installed
- Python 3.8+
- sc2 library

### Installation
```bash
git clone https://github.com/V1ct0r-S4g3/B0B-The-Builder.git
cd B0B-The-Builder
pip install -r requirements.txt
```

### Running the Bot

#### All Races (Auto-Detect)
```bash
python run_simple_bot.py
```

#### Specific Race
```bash
# Terran
python run_simple_bot.py --race Terran

# Protoss  
python run_simple_bot.py --race Protoss

# Zerg
python run_simple_bot.py --race Zerg
```

### Testing
```bash
# Run all tests
python run_tests.py

# Run specific test
python tests/test_bot.py
```

## 📊 Performance

### Economy Metrics
- **Worker Saturation**: 100% mineral saturation, optimal gas worker ratios
- **Income Rate**: 800+ minerals/minute, 100+ gas/minute
- **Expansion Timing**: Fast expand with proper worker distribution

### Military Metrics
- **Army Composition**: Race-appropriate unit mixes
- **Attack Timing**: Wave attacks with 6+ units minimum
- **Defensive Response**: Immediate reaction to threats within 30 units

## 🔧 Configuration

Key configuration options in `src/config/config.py`:
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

## 📈 Recent Updates

### v2.0 - Multi-Race Support
- ✅ Added Protoss and Zerg economy managers
- ✅ Added Protoss and Zerg military managers  
- ✅ Fixed Zerg larva morphing for drones and overlords
- ✅ Improved building placement logic
- ✅ Enhanced defensive AI for all races
- ✅ Race-aware bot initialization

### v1.0 - Terran Foundation
- ✅ Basic Terran economy and military
- ✅ Modular manager architecture
- ✅ Debug output and logging
- ✅ Test suite and documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with the [sc2 library](https://github.com/BurnySc2/python-sc2)
- Inspired by competitive StarCraft II bot development
- Community feedback and testing

---

**B0B - Building Better Bots, One Race at a Time! 🏗️⚔️**
