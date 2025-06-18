"""Debug script for expand_now test."""
import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from sc2.position import Point2
from sc2.ids.unit_typeid import UnitTypeId

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the EconomyManager
try:
    from managers.economy_manager import EconomyManager
    print("Successfully imported EconomyManager")
except ImportError as e:
    print(f"Error importing EconomyManager: {e}")
    print(f"Current sys.path: {sys.path}")
    raise

async def debug_expand_now():
    """Debug the expand_now method."""
    # Redirect stdout to a file
    original_stdout = sys.stdout
    with open('debug_output.txt', 'w', encoding='utf-8') as f:
        sys.stdout = f
        
        print("=== Starting debug_expand_now ===")
        
        # Create a mock AI object
        mock_ai = MagicMock()
        print("Created mock_ai")
        
        # Set up basic attributes
        mock_ai.time = 200
        mock_ai.minerals = 600
        mock_ai.expansion_locations = [Point2((100, 100))]
        mock_ai.can_afford = MagicMock(return_value=True)
        print("Set basic attributes")
        
        # Mock worker
        mock_worker = MagicMock()
        mock_worker.is_gathering = True
        mock_worker.is_idle = False
        mock_worker.is_constructing = False
        mock_worker.is_carrying_resource = False
        mock_worker.position = Point2((50, 50))
        mock_ai.select_build_worker = MagicMock(return_value=mock_worker)
        print("Created mock worker")
        
        # Mock other required methods
        mock_ai.can_place = AsyncMock(return_value=True)
        mock_ai.find_placement = AsyncMock(return_value=Point2((100, 100)))
        print("Mocked async methods")
        
        # Mock structures
        mock_structures = MagicMock()
        mock_structures.filter.return_value = []
        mock_ai.structures = MagicMock(return_value=mock_structures)
        print("Mocked structures")
        
        # Mock already_pending
        mock_ai.already_pending = MagicMock(return_value=0)
        print("Mocked already_pending")
        
        # Mock townhalls
        mock_cc = MagicMock()
        mock_cc.position = Point2((0, 0))
        mock_ai.townhalls = MagicMock()
        mock_ai.townhalls.first = mock_cc
        mock_ai.townhalls.amount = 1
        print("Mocked townhalls")
        
        # Mock enemy_units
        mock_enemy_units = MagicMock()
        mock_enemy_units.filter.return_value = []
        mock_ai.enemy_units = mock_enemy_units
        print("Mocked enemy_units")
        
        # Create EconomyManager instance
        try:
            economy_manager = EconomyManager(mock_ai)
            economy_manager.debug = True
            print("Created EconomyManager instance")
        except Exception as e:
            print(f"Error creating EconomyManager: {e}")
            raise
        
        # Add head attribute
        economy_manager.head = MagicMock()
        print("Added head attribute")
        
        print("=== Calling expand_now ===")
        try:
            result = await economy_manager.expand_now()
            print(f"expand_now result: {result}")
            
            if result:
                mock_worker.build.assert_called_once_with(UnitTypeId.COMMANDCENTER, mock_ai.expansion_locations[0])
                print("Build method called correctly")
            else:
                print("Build method was not called")
            
            print("\n=== Debug Info ===")
            print(f"hasattr(self, 'head'): {hasattr(economy_manager, 'head')}")
            print(f"self.head: {getattr(economy_manager, 'head', 'N/A')}")
            print(f"can_afford: {mock_ai.can_afford(UnitTypeId.COMMANDCENTER)}")
            print(f"already_pending: {mock_ai.already_pending(UnitTypeId.COMMANDCENTER)}")
            print(f"townhalls: {hasattr(mock_ai, 'townhalls')}")
            print(f"townhalls.first: {getattr(mock_ai.townhalls, 'first', 'N/A')}")
            
        except Exception as e:
            print(f"Error in expand_now: {e}")
            import traceback
            traceback.print_exc()
            
    # Restore stdout
    sys.stdout = original_stdout
    print("Debug output written to debug_output.txt")

if __name__ == "__main__":
    print("Starting debug script...")
    asyncio.run(debug_expand_now())
