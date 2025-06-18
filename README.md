# SC2 AI Bot

A StarCraft II AI bot built using the [python-sc2](https://github.com/BurnySc2/python-sc2) framework. This project implements a Terran bot with modular managers for different aspects of gameplay.

## Quick Start

### Prerequisites
- StarCraft II installed (via Battle.net)
- Python 3.7+
- Required Python packages (install with `pip install -r requirements.txt`)

### Running the Bot (One-Command Method)

1. **First, set the SC2PATH environment variable** (one-time setup):
   ```
   setx SC2PATH "D:\Battle.net\StarCraft2"
   ```
   (Replace with your actual StarCraft II installation path if different)

2. **Run the bot with a single command**:
   ```
   python run_bot.py
   ```
   This will automatically:
   - Start StarCraft II
   - Wait for it to initialize
   - Launch the bot
   - Clean up when done

### Alternative: Manual Two-Step Process

If you need to run StarCraft II and the bot separately:

1. **Start StarCraft II**:
   ```
   python -m src.scripts.start_sc2
   ```

2. **In a separate terminal, run the bot**:
   ```
   python -m src.scripts.run
   ```

### Troubleshooting
- If you get a module not found error, try installing the package in development mode:
  ```
  pip install -e .
  ```
- Make sure StarCraft II is fully launched before running the bot
- Check the logs in `src/scripts/logs/` for any errors

---

## Project Structure

```
sc2-bot/
├── src/                    # Source code
│   ├── bot/               # Main bot implementation
│   ├── config/            # Configuration files (including pytest.ini)
│   ├── managers/          # Manager classes (economy, military, etc.)
│   ├── scripts/          # Utility scripts and entry points
│   └── tests/             # Test files
│       ├── functional/    # Functional test files
│       └── test_outputs/  # Test output files
├── replays/               # Game replay files
├── logs/                  # Log files
├── requirements.txt       # Python dependencies
├── setup.py              # Package installation script
├── run.py                # Main entry point (legacy)
└── README.md             # This file
```

## Running Tests

The test suite uses `pytest` and is configured in `src/config/pytest.ini`. Tests are located in the `src/tests/` directory.

### Running All Tests

```bash
# From the project root
cd src
python -m pytest tests/

# Or using the test runner script
python tests/run_tests.py
```

### Running Specific Tests

```bash
# Run a specific test file
python -m pytest tests/test_military_manager.py

# Run tests matching a pattern
python -m pytest tests/ -k "test_military"

# Run tests with specific markers
python -m pytest tests/ -m "not slow"
```

### Test Coverage

To generate a coverage report:

```bash
# From the src/ directory
python -m pytest --cov=src.managers --cov=src.bot --cov-report=term-missing
```

### Running Military Tests

A batch file is provided to run military-specific tests:

```bash
# From the src/ directory
cd src
tests\run_military_tests.bat
```

This will run military tests and save the output to `tests/test_outputs/military_test_output.txt`.

## Features

- Modular architecture with separate managers for different game aspects
- Configurable through environment variables and config files
- Detailed logging for debugging and analysis
- Support for custom maps and AI opponents
- Replay saving and analysis

## Prerequisites

- [Python](https://www.python.org/downloads/) 3.8 or newer
- [Git](https://git-scm.com/downloads)
- [StarCraft II](https://battle.net/account/download/)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sc2-bot
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Install StarCraft II if you haven't already from [Battle.net](https://battle.net/account/download/)

## Configuration

1. Set the `SC2PATH` environment variable to your StarCraft II installation directory:
   - Windows: `setx SC2PATH "D:\Battle.net\StarCraft2"`
   - Linux/macOS: `export SC2PATH=~/StarCraft2`

2. Copy the example config file (if available):
   ```bash
   copy src\config\config.example.py src\config\config.py
   ```

## Running the Bot

### Development Mode

1. Start StarCraft II with the correct parameters:
   ```bash
   python -m src.scripts.start_sc2
   ```

2. In a separate terminal, run the bot:
   ```bash
   python -m src.scripts.run
   ```

### Using the Entry Point

After installing the package, you can also run:

```bash
sc2-bot
```

## Running Tests

To run the test suite:

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### StarCraft II Installation

- **Windows**: Install through the Battle.net app
- **Linux**: 
  - Option 1: Use the [Blizzard SC2 Linux package](https://github.com/Blizzard/s2client-proto#linux-packages)
  - Option 2: Set up Battle.net via WINE using [Lutris](https://lutris.net/games/battlenet/)

### Required Maps

Download the StarCraft 2 Maps from [here](https://github.com/Blizzard/s2client-proto#map-packs). You'll at least need the 'Melee' pack.

By default, the bot will look for maps in the standard installation location. If your maps are in a different location, update the `MAP_PATH` in `config.py`.

## Linux (Lutris) Setup

If you're using Lutris on Linux, set these environment variables (replace placeholders with your actual paths):

```bash
export SC2PF=WineLinux
export SC2PATH="/home/YOUR_USERNAME/Games/battlenet/drive_c/Program Files (x86)/StarCraft II/"
export WINE="/home/YOUR_USERNAME/.local/share/lutris/runners/wine/YOUR_WINE_VERSION/bin/wine"
```

## Configuration

Edit `config.py` to customize your bot's behavior. The configuration file includes options for:

- **Bot Settings**: Name and race (Terran/Protoss/Zerg/Random)
- **Game Settings**: Map paths and map pool selection
- **Opponent Settings**: AI difficulty and race selection
- **Game Mode**: Toggle between realtime and faster simulation

For advanced configuration, refer to the comments in `config.py`.

## Getting Started

1. **Create your repository**
   - Click the `Use this template` button above to create your own copy

2. **Clone your repository**
   ```bash
   git clone <your-repository-url>
   cd <repository-name>
   ```

3. **Set up a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the bot**
   ```bash
   python run.py
   ```
   The bot should start and begin playing against the AI opponent.

## Customizing Your Bot

### Basic Configuration
Edit `config.py` to change:
- Bot name and race
- Game settings and map pool
- Opponent difficulty and race
- Game mode (realtime or faster simulation)

### Adding Logic
Modify `bot/bot.py` to implement your bot's behavior. The `on_step` method is where you'll add most of your bot's logic.

### Adding new code

As you add features to your bot make sure all your new code files are in the `bot` folder. This folder is included when creating the ladder.zip for upload to the bot ladders.

## Upgrading to Ares Framework

Ares-sc2 is a library that extends python-sc2, offering advanced tools and functionalities to give you greater control over your bot's strategic decisions. If you want more sophisticated and nuanced gameplay tactics, upgrading to Ares-sc2 is the way to go.

### Running the Upgrade Script

Run the following command:
```bash
python upgrade_to_ares.py
```

### Code Changes

#### Updating the Bot Object

The main bot object should inherit from `ares-sc2` instead of `python-sc2`.

**python-sc2:**
```python
from sc2.bot_ai import BotAI

class MyBot(BotAI):
    pass
```

**ares-sc2:**
```python
from ares import AresBot

class MyBot(AresBot):
    pass
```

#### Adding Super Calls to Hook Methods

For any `python-sc2` hook methods you use, add a `super` call. Only convert the hooks you actually use.

**python-sc2:**
```python
class MyBot(AresBot):
    async def on_step(self, iteration: int) -> None:
        pass

    async def on_start(self, iteration: int) -> None:
        pass

    async def on_end(self, game_result: Result) -> None:
        pass

    async def on_building_construction_complete(self, unit: Unit) -> None:
        pass

    async def on_unit_created(self, unit: Unit) -> None:
        pass

    async def on_unit_destroyed(self, unit_tag: int) -> None:
        pass

    async def on_unit_took_damage(self, unit: Unit, amount_damage_taken: float) -> None:
        pass
```

**ares-sc2:**
```python
class MyBot(AresBot):
    async def on_step(self, iteration: int) -> None:
        await super(MyBot, self).on_step(iteration)
        # on_step logic here ...

    async def on_start(self, iteration: int) -> None:
        await super(MyBot, self).on_start(iteration)
        # on_start logic here ...

    async def on_end(self, game_result: Result) -> None:
        await super(MyBot, self).on_end(game_result)
        # custom on_end logic here ...

    async def on_building_construction_complete(self, unit: Unit) -> None:
        await super(MyBot, self).on_building_construction_complete(unit)
        # custom on_building_construction_complete logic here ...

    async def on_unit_created(self, unit: Unit) -> None:
        await super(MyBot, self).on_unit_created(unit)
        # custom on_unit_created logic here ...

    async def on_unit_destroyed(self, unit_tag: int) -> None:
        await super(MyBot, self).on_unit_destroyed(unit_tag)
        # custom on_unit_destroyed logic here ...

    async def on_unit_took_damage(self, unit: Unit, amount_damage_taken: float) -> None:
        await super(MyBot, self).on_unit_took_damage(unit, amount_damage_taken)
        # custom on_unit_took_damage logic here ...
```

## Competing with your bot

To compete with your bot, you will first need zip up your bot, ready for distribution.   
You can do this using the `create_ladder_zip.py` script like so:
```
python create_ladder_zip.py
```
This will create the zip file`publish\bot.zip`.
You can then distribute this zip file to competitions.
