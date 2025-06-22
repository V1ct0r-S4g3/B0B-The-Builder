# Warlord SC2 Bot - Setup Guide

## Prerequisites

1. **StarCraft II**
   - Install StarCraft II from [Battle.net](https://battle.net/)
   - Launch the game at least once to complete the initial setup
   - Install the latest patches

2. **Python 3.8+**
   - Download and install Python from [python.org](https://www.python.org/downloads/)
   - Ensure Python is added to your system PATH

## Environment Setup

### 1. Set SC2PATH Environment Variable

The bot needs to know where StarCraft II is installed. Set the `SC2PATH` environment variable to your StarCraft II installation directory.

#### Windows (Command Prompt):
```cmd
setx SC2PATH "D:\Battle.net\StarCraft2"
```

#### Windows (PowerShell):
```powershell
[System.Environment]::SetEnvironmentVariable('SC2PATH', 'D:\Battle.net\StarCraft2', 'User')
```

#### Linux/macOS:
```bash
export SC2PATH="$HOME/StarCraftII"
echo 'export SC2PATH="$HOME/StarCraftII"' >> ~/.bashrc  # For permanent setup
```

### 2. Install Python Dependencies

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Install required packages
pip install -r requirements.txt
```

## Verifying the Setup

1. **Check SC2PATH**:
   ```bash
   # Windows
   echo %SC2PATH%
   
   # Linux/macOS
   echo $SC2PATH
   ```
   This should print the path to your StarCraft II installation.

2. **Run a Test Game**:
   ```bash
   python -m run_bot --realtime --game-time 60 --map "(2)16-BitLE"
   ```
   This should start a game on the 16-Bit LE map in realtime mode for 60 seconds.

## Common Issues

### 1. SC2PATH Not Set
**Error**: `SC2PATH environment variable is not set`
**Solution**: Set the `SC2PATH` environment variable as shown above.

### 2. Map Not Found
**Error**: `Map file not found`
**Solution**: Ensure the map exists in your StarCraft II maps directory. You may need to download ladder maps.

### 3. Python Module Not Found
**Error**: `ModuleNotFoundError: No module named 'sc2'`
**Solution**: Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Next Steps

1. Try running the bot against the built-in AI
2. Experiment with different maps and game settings
3. Check the `docs/` directory for more detailed documentation
4. Review the bot's strategy in `src/warlord/strategies/`

## Support

For additional help, please refer to the project's [GitHub Issues](https://github.com/yourusername/warlord/issues) or join our community Discord.
