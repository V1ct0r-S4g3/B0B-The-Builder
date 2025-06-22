# Warlord Bot - Developer Documentation

This document contains detailed technical documentation for developers working on the Warlord bot.

## 🏗️ Architecture

Warlord uses a modern component-based architecture with clear separation of concerns:

### Core Components
- **WarlordBot**: Main bot class that coordinates all components
- **HighArbiter**: Makes high-level strategic decisions and game state analysis
- **HighCommand**: Translates strategies into executable commands
- **CommandBus**: Manages communication between components

### Subsystems
- **Economy**: Comprehensive resource management including workers, expansions, and resource allocation
- **Military**: Advanced army composition, positioning, and combat tactics
- **Defense**: Base protection and static defense placement
- **Scouting**: Information gathering and map control
- **History**: Game state tracking and performance metrics
- **Intel**: Game state analysis and threat assessment

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_economy.py

# Run with coverage report
pytest --cov=warlord tests/

# Run with detailed output
pytest -v tests/
```

### Test Structure

Tests are organized by component in the `tests/` directory:
```
tests/
├── commands/           # Tests for command modules
├── core/              # Core functionality tests
├── economy/           # Economy system tests
├── military/          # Military system tests
├── scouting/         # Scouting system tests
└── test_*.py         # Top-level test files
```

### Writing Tests

When writing new tests, follow these guidelines:
1. Test one specific piece of functionality per test
2. Use descriptive test names
3. Include proper setup and teardown
4. Mock external dependencies
5. Test both success and error cases

## Project Structure

```
6r3tt4/
├── src/                   # Source code
│   └── warlord/          # Main package
│       ├── commands/     # Command implementations
│       ├── core/         # Core functionality
│       ├── economy/      # Economy system
│       ├── military/     # Military system
│       ├── scouting/     # Scouting system
│       └── warlord_bot.py # Main bot class
│
├── tests/               # Test files
├── scripts/              # Utility scripts
│   ├── analyze_strategies.py
│   ├── strategy_analyzer_cli.py
│   ├── visualize_military.py
│   └── visualize_strategies.py
│
├── legacy/               # Legacy code (for reference)
│   ├── components/       # Old component implementations
│   └── old_scripts/      # Previous versions of scripts
│
├── data/                # Game data and logs
│   ├── logs/
│   └── replays/
│
├── docs/                # Documentation
│   ├── architecture.md
│   └── development.md
├── .venv/               # Python virtual environment
└── requirements.txt      # Python dependencies
```

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 style guide
   - Use type hints for all function signatures
   - Document all public functions and classes with docstrings

2. **Version Control**
   - Create feature branches for new features
   - Write clear, descriptive commit messages
   - Open pull requests for code review

3. **Dependencies**
   - Add new dependencies to `requirements.txt`
   - Document any new dependencies in the PR description

4. **Documentation**
   - Update relevant documentation when making changes
   - Add docstrings for new functions and classes
   - Update this developer guide as needed
