<div align="center">

# 🚀 B0B - The Builder

[![CI Status](https://github.com/V1ct0r-S4g3/B0B-The-Builder/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/V1ct0r-S4g3/B0B-The-Builder/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

</div>

A StarCraft II Terran AI bot built using the BurnySc2 library, designed to demonstrate effective bot development patterns and strategies.

## 🚀 Features

- **Manager-based Architecture**: Clean separation of concerns with dedicated managers for economy, military, and coordination
- **Strategic Building Placement**: Buildings placed close to base for optimal defense and efficiency
- **Optimized Economy**: Smart worker distribution and proactive supply management
- **Build Order System**: Structured progression through early game development
- **Continuous Production**: Sustained unit production after build order completion
- **Error Handling**: Robust error handling and fallback mechanisms
- **Debug Logging**: Comprehensive logging for development and troubleshooting

## 📊 Performance

- **Game Duration**: 4+ minutes of stable gameplay
- **Economy**: 1200+ minerals/min collection rate
- **Military**: 20+ army supply with continuous production
- **Supply Management**: No supply blocking (46/47 supply)
- **Stability**: No crashes or critical errors

## 🏗️ Architecture

```
B0B/
├── src/
│   ├── bot/
│   │   ├── bot.py          # Main bot class
│   │   └── main.py         # Entry point
│   ├── managers/
│   │   ├── head_manager.py     # Central coordinator
│   │   ├── economy_manager.py  # Resource management
│   │   └── military_manager.py # Military production
│   └── config/
│       └── config.py       # Configuration
├── tests/                  # Test files
├── docs/                   # Documentation
└── run_simple_bot.py       # Quick start script
```

## 🛠️ Setup

### Prerequisites
- Python 3.10+
- StarCraft II game installed
- Git (for version control)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd B0B
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python check_env.py
   ```

## 🎮 Running the Bot

### Quick Start
```bash
python run_simple_bot.py
```

### Custom Game
```bash
python -m sc2.main --map "2000AtmospheresAIE" --races terran terran --ai sc2.bot_ai.BotAI src.bot.main:MyBot
```

### Testing
```bash
# Run all tests
python run_tests.py

# Run specific test
python -m pytest tests/test_bot.py
```

## 📚 Documentation

- **[Bot Improvements Summary](BOT_IMPROVEMENTS_SUMMARY.md)**: Comprehensive overview of all improvements and learnings
- **[Quick Reference Guide](QUICK_REFERENCE_GUIDE.md)**: Essential code patterns and solutions for bot development
- **[Setup Checklist](SETUP_CHECKLIST.md)**: Step-by-step guide for setting up new bot projects
- **[Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)**: Solutions for common issues and problems

## 🔧 Key Components

### HeadManager
Central coordinator that initializes and manages all other managers. Ensures proper startup sequence and step execution.

### EconomyManager
Handles worker production, resource collection, and supply management:
- Optimal worker distribution (6 per gas, rest on minerals)
- Proactive supply depot building
- Strategic building placement near base

### MilitaryManager
Manages build orders, unit production, and military strategy:
- Structured build order progression
- Continuous unit production
- Rally point management
- Building placement optimization

## 🎯 Build Order

1. Supply Depot at 13 supply
2. First Barracks at 14 supply
3. First Refinery
4. Bunker for defense
5. Second Barracks
6. Factory for tech
7. Starport for air units
8. Third Barracks

## 🏆 Achievements

This bot successfully demonstrates:

- **Environment Setup**: Proper dependency management and compatibility
- **Manager Pattern**: Clean architecture with separation of concerns
- **Building Placement**: Strategic placement close to base
- **Economy Optimization**: Efficient resource collection and worker distribution
- **Military Production**: Continuous unit production and build order execution
- **Error Handling**: Robust error handling and fallback mechanisms
- **Performance**: Stable 4+ minute gameplay with good economy and military

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure BurnySc2 is installed (not python-sc2)
2. **Manager Not Running**: Check HeadManager initialization in bot.on_start()
3. **Building Placement**: Verify placement distances are close to base (4-6 units)
4. **Supply Blocking**: Increase supply buffer and building frequency
5. **Performance Issues**: Use efficient unit selection and caching

### Debug Mode
Enable debug logging by setting `self.debug = True` in managers.

## 🔄 Development Workflow

1. **Environment Check**: Run `python check_env.py`
2. **Test Changes**: Run `python run_simple_bot.py`
3. **Validate Performance**: Ensure 3+ minute gameplay
4. **Check Metrics**: Economy > 1000 minerals/min, Army > 15 supply
5. **Commit Changes**: Use descriptive commit messages

## 📈 Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Game Duration | > 3 min | 4+ min |
| Economy Rate | > 1000/min | 1200+/min |
| Army Supply | > 15 | 20+ |
| Supply Usage | < 90% | 46/47 |
| Stability | No crashes | Stable |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- BurnySc2 library developers
- StarCraft II community
- All contributors and testers

---

**B0B - Building Better Bots! 🏗️🤖**
