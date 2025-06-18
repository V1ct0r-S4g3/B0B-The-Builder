"""A simple bot that connects to a running StarCraft II client."""
import sys
import os
import platform
import asyncio
from pathlib import Path

# SC2 imports
import sc2
from sc2 import maps
from sc2.data import Race, Difficulty
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.client import Client
from sc2.protocol import ConnectionAlreadyClosed

# Set up basic logging
log_file = Path("bot_connection.log")
if log_file.exists():
    log_file.unlink()

def log(message):
    """Log a message to file."""
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    except Exception as e:
        print(f"Error writing to log: {e}", file=sys.stderr)

class SimpleBot(sc2.BotAI):
    """A simple SC2 bot that connects to a running game."""
    
    def __init__(self):
        """Initialize the bot."""
        super().__init__()
        self.client = None
        self.portconfig = None
        log("SimpleBot initialized")
    
    async def connect(self, host="127.0.0.1", port=8167):
        """Connect to a running StarCraft II instance."""
        try:
            from sc2.client import Client
            from sc2.portconfig import Portconfig
            from sc2.protocol import ConnectionAlreadyClosed, ProtocolError
            
            log(f"Connecting to StarCraft II at {host}:{port}...")
            
            # Create port configuration for the client
            self.portconfig = Portconfig()
            self.portconfig.shared = port  # The port SC2 is listening on
            
            # Create the client
            self.client = Client(host, self.portconfig)
            
            # Connect to the game
            try:
                log("Attempting to connect to StarCraft II...")
                await self.client.ping()
                log("✅ Successfully connected to StarCraft II!")
                
                # Join the game
                log("Joining the game...")
                join_game = sc2.data.JoinGame()
                join_game.race = sc2.data.Race.Terran
                join_game.options.raw = True
                
                result = await self.client.join_game(
                    race=sc2.data.Race.Terran,
                    name="SimpleBot",
                    options=join_game.options
                )
                
                if result.HasField("error"):
                    log(f"❌ Failed to join game: {result.error}")
                    return False
                
                log("✅ Successfully joined the game!")
                return True
                
            except ConnectionAlreadyClosed:
                log("❌ Connection closed by StarCraft II")
                return False
            except ProtocolError as e:
                log(f"❌ Protocol error: {e}")
                return False
            except Exception as e:
                log(f"❌ Error connecting to StarCraft II: {e}")
                import traceback
                log(traceback.format_exc())
                return False
                
        except ImportError as e:
            log(f"❌ Error importing SC2 modules: {e}")
            log("Make sure you have python-sc2 installed: pip install sc2")
            return False
        except Exception as e:
            log(f"❌ Unexpected error: {e}")
            import traceback
            log(traceback.format_exc())
            return False
    
    async def run(self):
        """Run the bot's main loop."""
        if not self.client:
            log("❌ Not connected to StarCraft II")
            return False
        
        try:
            log("Bot is running. Press Ctrl+C to exit.")
            
            # Simple loop to keep the bot running
            while True:
                try:
                    # Get game state
                    observation = await self.client.observe()
                    
                    # Log some basic game state
                    if observation.observation.player_common:
                        player_id = observation.observation.player_common.player_id
                        minerals = observation.observation.player_common.minerals
                        vespene = observation.observation.player_common.vespene
                        supply_used = observation.observation.player_common.food_used
                        supply_max = observation.observation.player_common.food_cap
                        
                        log(f"Player {player_id}: {minerals} minerals, {vespene} vespene, "
                            f"Supply: {supply_used}/{supply_max}")
                    
                    # Sleep to prevent high CPU usage
                    await asyncio.sleep(1.0)
                    
                except asyncio.CancelledError:
                    log("Bot stopped by user")
                    return True
                except ConnectionAlreadyClosed:
                    log("❌ Connection to StarCraft II was closed")
                    return False
                except Exception as e:
                    log(f"Error in bot loop: {e}")
                    import traceback
                    log(traceback.format_exc())
                    return False
                    
        except Exception as e:
            log(f"❌ Error in bot run loop: {e}")
            import traceback
            log(traceback.format_exc())
            return False
    
    async def close(self):
        """Close the connection to StarCraft II."""
        if self.client:
            try:
                await self.client.quit()
                log("Sent quit command to StarCraft II")
            except Exception as e:
                log(f"Error during client quit: {e}")
            
            try:
                await self.client.leave()
                log("Left the game")
            except Exception as e:
                log(f"Error leaving game: {e}")
            
            self.client = None
            log("Disconnected from StarCraft II")

async def main():
    """Main function to run the bot."""
    log("=" * 50)
    log("SIMPLE SC2 BOT STARTING".center(50))
    log("=" * 50)
    
    # Default connection settings
    host = "127.0.0.1"
    port = 8167
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            log(f"Invalid port number: {sys.argv[2]}. Using default port {port}.")
    
    log(f"Connecting to StarCraft II at {host}:{port}")
    log("-" * 50)
    
    bot = SimpleBot()
    
    try:
        # Connect to StarCraft II
        log("\nStep 1: Connecting to StarCraft II...")
        if not await bot.connect(host=host, port=port):
            log("\n❌ Failed to connect to StarCraft II")
            log("Possible causes:")
            log("1. StarCraft II is not running")
            log("2. StarCraft II is not accepting connections")
            log("3. The port number is incorrect")
            log("4. Firewall is blocking the connection")
            log("\nMake sure to run start_sc2.py first to launch StarCraft II with the correct parameters.")
            return 1
        
        log("\n✅ Successfully connected to StarCraft II!")
        log("\nStep 2: Starting bot main loop...")
        log("Press Ctrl+C to exit\n")
        
        # Run the bot
        await bot.run()
        return 0
        
    except KeyboardInterrupt:
        log("\n\nBot stopped by user")
        return 0
    except Exception as e:
        log(f"\n❌ Unexpected error: {e}")
        import traceback
        log(traceback.format_exc())
        return 1
    finally:
        log("\nShutting down...")
        await bot.close()
        log("✅ Bot shutdown complete")

if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        sys.exit(0)
