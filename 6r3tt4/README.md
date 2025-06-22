# Warlord Bot

A competitive StarCraft II Terran bot built with python-sc2 (v0.11.2), designed for strategic gameplay and adaptive decision-making.

> **Version Note**: This bot is specifically designed and tested with `python-sc2==0.11.2`. Other versions may have compatibility issues.

![Warlord Bot in Action](docs/screenshots/warlord_bot.png)

## 🚀 Quick Start

### Prerequisites
- [StarCraft II](https://starcraft2.com/en-us/) (Latest version)
- Python 3.12.10
- Windows OS (for best compatibility)
- `python-sc2==0.11.2` (Required)

> **Important**: This bot requires `python-sc2` version 0.11.2. Other versions are not supported and may cause unexpected behavior. The bot takes advantage of several version-specific features and behaviors that are unique to 0.11.2.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/6r3tt4.git
   cd 6r3tt4
   ```

2. **Set up a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   \.venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   > **Note**: This will install `python-sc2==0.11.2` along with other required dependencies. If you have a different version of python-sc2 installed, it will be automatically downgraded.

4. **Set up StarCraft II**
   - Install StarCraft II from [Battle.net](https://battle.net/)
   - The bot will automatically use the default installation path
   - For custom installations, set the `SC2PATH` environment variable

## 🔄 Version Compatibility

This bot is specifically designed for `python-sc2==0.11.2`. Key version-specific features include:

- **Game Loop**: Uses the synchronous game loop model from 0.11.2
- **Unit Control**: Implements unit control patterns specific to this version
- **Build Orders**: Optimized for the balance and timings of this version
- **Map Awareness**: Uses version-specific map analysis features

### Known Limitations

- Some newer features from later versions of python-sc2 are not available
- Certain pathfinding optimizations may differ from newer versions
- Replay analysis features are limited to what's available in 0.11.2

## 🚀 Features

- **Adaptive Strategy**: Dynamically adjusts build orders and tactics based on game state
- **Efficient Economy**: Smart worker and resource management
- **Combat Tactics**: Advanced unit control and army positioning
- **Scouting**: Intelligent information gathering and map awareness
- **Defense**: Proactive base defense and expansion protection

## 🏆 Performance

- Competes against Elite AI and other bots
- Regularly updated with new strategies and improvements
- Performance metrics tracked for continuous improvement

## 🚀 Getting Started

### Basic Usage

1. **Start a game against the built-in AI**
   ```bash
   python -m warlord
   ```

2. **Play on a specific map**
   ```bash
   python -m warlord --map "AutomatonLE"
   ```

3. **Run in realtime mode** (for testing)
   ```bash
   python -m warlord --realtime
   ```

### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--map` | Map to play on | Random ladder map |
| `--opponent` | AI race (terran/zerg/protoss/random) | terran |
| `--difficulty` | AI difficulty (very-easy to elite) | very-hard |
| `--realtime` | Run in realtime mode | False |
| `--log_level` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO |

### Watching a Replay

1. After a game, find the replay in the `data/replays/` directory
2. Open it with StarCraft II to analyze the bot's performance

## 📊 Performance Tuning

The bot's behavior can be fine-tuned using configuration files in the `config/` directory. Key parameters include:

- Economy: Worker allocation, expansion timing
- Military: Unit composition, attack timing
- Scouting: Frequency, target prioritization

## 📈 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📚 Documentation

For detailed technical documentation, please see [DEVELOPER.md](DEVELOPER.md).

### Version-Specific Documentation

For information specific to python-sc2 0.11.2:
- [python-sc2 0.11.2 Documentation](https://github.com/Dentosal/python-sc2/tree/v0.11.2)
- [API Reference](https://github.com/Dentosal/python-sc2/blob/v0.11.2/README.md)
- [Changelog](https://github.com/Dentosal/python-sc2/releases/tag/v0.11.2)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-sc2 v0.11.2](https://github.com/Dentosal/python-sc2/tree/v0.11.2) - The StarCraft II API for Python
- The StarCraft II AI community for inspiration and knowledge sharing

> **Note**: This project uses python-sc2 v0.11.2, which is a fork of the main python-sc2 repository. The main repository has since been updated, but this bot is specifically designed for v0.11.2.

## 🧪 Testing with python-sc2 0.11.2

When running tests, please ensure you're using `python-sc2==0.11.2`. The test suite has been validated against this specific version.

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
├── scouting/          # Scouting system tests
└── test_*.py         # Top-level test files
└── high_command/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔍 Development Workflow

### Test Automation

We've developed several utilities to make testing more efficient and maintainable:

#### 1. Test Runner (`test_runner.py`)

The main test runner provides multiple testing options:

```bash
# Run all tests with coverage
python test_runner.py --all

# Watch for file changes and run tests automatically
python test_runner.py --watch

# Run specific test file
python test_runner.py tests/test_example.py

# Run linting checks
python test_runner.py --lint

# Run type checking
python test_runner.py --type

# Check python-sc2 version
python test_runner.py --version
```

#### 2. Test Writer (`test_writer.py`)

A utility to help create and manage test files:

```bash
# Create a new test file
python test_writer.py new my_feature_tests

# Run tests with watcher
python test_writer.py run

# Run specific test file with watcher
python test_writer.py run tests/test_my_feature.py
```

#### 3. Test Generator (`test_generator.py`)

Automatically generates test stubs for your Python modules:

```bash
# Generate tests for a specific file
python test_generator.py src/warlord/strategies/strategy_manager.py

# Generate tests for a directory
python test_generator.py src/warlord/strategies/

# Overwrite existing test files
python test_generator.py --force src/warlord/strategies/

# Specify custom output directory
python test_generator.py --output-dir my_tests/ src/warlord/
```

### Test Watcher

We use `pytest-watch` to automatically run tests when files change. The watcher is configured to:
- Show colored output for pass/fail status
- Ignore virtual environments and cache directories
- Support running specific test files or all tests
- Provide visual feedback for test results

To use the watcher:
```bash
# Watch all tests
python test_runner.py --watch

# Watch specific test file
python test_runner.py --watch tests/test_example.py
```

### Test Structure

Tests are organized in the `tests/` directory with the following structure:
```
tests/
├── __init__.py
├── test_example.py          # Example tests
├── test_strategy_manager.py # Auto-generated tests
└── test_writer.py           # Test writer tests
```

### Writing Tests

When writing new tests, follow these guidelines:
1. Test one specific piece of functionality per test
2. Use descriptive test names
3. Include proper setup and teardown
4. Mock external dependencies
5. Test both success and error cases

1. **Test Naming**:
   - Test files should start with `test_`
   - Test functions should start with `test_`
   - Test classes should start with `Test`

2. **Fixtures**:
   - Use `setUp()` for test setup
   - Use `tearDown()` for cleanup
   - Use `@pytest.fixture` for reusable test components

3. **Assertions**:
   - Use `assert` for simple checks
   - Use `unittest` assertions for more complex validations
   - Include descriptive messages in assertions

4. **Best Practices**:
   - Keep tests small and focused
   - Test one thing per test function
   - Use descriptive test names
   - Avoid test interdependencies
   - Mock external dependencies

### Continuous Integration

To set up CI, add the following to your workflow file:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    - name: Run tests
      run: |
        python test_runner.py --all
        python test_runner.py --lint
        python test_runner.py --type
```

### Debugging Tests

To debug failing tests:

1. Run a specific test with detailed output:
   ```bash
   python -m pytest tests/test_example.py -v
   ```

2. Drop into PDB on failure:
   ```bash
   python -m pytest tests/test_example.py --pdb
   ```

3. Show all output during test execution:
   ```bash
   python -m pytest tests/test_example.py -s
   ```

### Performance Testing

For performance testing, you can use:

```bash
# Run tests and show the 10 slowest tests
pytest --durations=10

# Profile a specific test
python -m cProfile -m pytest tests/test_performance.py
```

### Coverage Reports

To generate coverage reports:

```bash
# Generate HTML report
pytest --cov=src --cov-report=html

# Show coverage in terminal
pytest --cov=src --cov-report=term-missing
```

### Test Dependencies

Add these to your `requirements-dev.txt`:

```
pytest>=6.0.0
pytest-cov>=2.8.0
pytest-watch>=4.2.0
pytest-mock>=3.3.1
coverage>=5.3
mypy>=0.800
flake8>=3.8.0
```

### Troubleshooting

1. **Tests not found**:
   - Make sure test files start with `test_`
   - Check that test functions start with `test_`
   - Ensure `__init__.py` exists in test directories

2. **Import errors**:
   - Check your `PYTHONPATH`
   - Make sure the source directory is in the Python path
   - Use absolute imports

3. **Test failures**:
   - Run with `-v` for more verbose output
   - Use `--pdb` to drop into the debugger on failure
   - Check for test ordering issues with `--random-order`

### Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Python Testing with pytest](https://pythontest.com/pytest-book/)
- [Effective Python Testing with Pytest](https://realpython.com/pytest-python-testing/)

## 🔍 Development Workflow

### Test Automation

We use `pytest` with the following test runner commands:

| Command | Description |
|---------|-------------|
| `python test_runner.py --all` | Run all tests with coverage |
| `python test_runner.py --watch` | Watch for changes and run tests |
| `python test_runner.py --lint` | Run linting checks |
| `python test_runner.py --type` | Run type checking |
| `python test_runner.py --version` | Check python-sc2 version |

### Recommended Workflow
1. Start the test watcher in a terminal:
   ```bash
   .\test_watch.bat
   ```
2. Make code changes in your editor
3. Tests will automatically run when you save files
4. Check test output in the terminal

### Version Requirements
- **python-sc2 must be version 0.11.2**
- The test runner will verify this automatically
- To install the correct version:
  ```bash
  pip install sc2==0.11.2
  ```

## 🛠 Project Structure

## Project Structure

```
├── src/
│   └── warlord/           # Main source code
│       ├── commands/       # Command definitions
│       ├── core/           # Core functionality
│       ├── economy/        # Economy management
│       ├── high_arbiter/   # High-level strategy decisions
│       ├── high_command/   # Mid-level command execution
│       ├── history/        # Game history and analysis
│       ├── military/       # Military unit control
│       ├── scouting/       # Scouting and intel gathering
│       ├── strategies/     # Game strategies
│       └── utils/          # Utility functions
│
├── tests/                # Test suite
├── scripts/               # Utility scripts
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

## Getting Started

### Prerequisites

- Python 3.7+
- StarCraft II game client
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd warlord-bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Bot

1. Start the bot against the built-in AI:
   ```bash
   python -m warlord
   ```

2. For ladder games, use the appropriate ladder runner script.

## Development

### Testing

Run the test suite with pytest:
```bash
pytest tests/
```

### Code Style

This project follows PEP 8 style guidelines. Use the following tools to maintain code quality:

```bash
# Auto-format code
black .


# Check for style issues
flake8 .
```

### Project Structure Conventions

- Each module should be self-contained with clear responsibilities
- Use type hints for better code clarity
- Document public APIs with docstrings
- Write unit tests for new features

## License

[Specify your license here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
