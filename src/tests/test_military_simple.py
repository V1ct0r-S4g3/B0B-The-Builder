"""Simplified test for MilitaryManager."""
import pytest
from unittest.mock import MagicMock, AsyncMock
from sc2.ids.unit_typeid import UnitTypeId
from managers.military_manager import MilitaryManager

# Test case outside of class
def test_military_manager_initialization():
    """Test that MilitaryManager initializes correctly."""
    # Create a mock AI instance
    mock_ai = MagicMock()
    mock_ai.time = 0
    mock_ai.minerals = 1000
    mock_ai.vespene = 0
    mock_ai.supply_used = 10
    mock_ai.supply_cap = 20
    mock_ai.supply_left = 10
    mock_ai.units = MagicMock()
    mock_ai.structures = MagicMock()
    mock_ai.townhalls = MagicMock()
    mock_ai.enemy_units = []
    mock_ai.enemy_structures = []
    mock_ai.game_info = MagicMock()
    mock_ai.game_info.map_center = (50, 50)
    
    # Create the manager
    manager = MilitaryManager(mock_ai)
    
    # Basic assertions
    assert manager is not None
    assert hasattr(manager, 'strategy')
    assert manager.strategy == "bio_rush"  # Default strategy

# Async test case
@pytest.mark.asyncio
async def test_async_military_manager():
    """Test async functionality with MilitaryManager."""
    print("\n=== Starting test_async_military_manager ===")
    # Create a mock AI instance
    mock_ai = MagicMock()
    print("Created mock AI instance")
    mock_ai.time = 0
    mock_ai.minerals = 1000
    mock_ai.vespene = 0
    mock_ai.supply_used = 10
    mock_ai.supply_cap = 20
    mock_ai.supply_left = 2  # Low supply to trigger emergency supply
    
    # Mock units and structures
    mock_ai.units = MagicMock()
    mock_ai.structures = MagicMock()
    
    # Create a mock command center
    mock_cc = MagicMock()
    mock_cc.position = MagicMock(return_value=MagicMock(towards=MagicMock(return_value=(10, 10))))
    mock_cc.ready = True
    mock_ai.townhalls = MagicMock()
    mock_ai.townhalls.ready = [mock_cc]
    
    # Mock enemy units and structures
    mock_ai.enemy_units = []
    mock_ai.enemy_structures = []
    
    # Mock game info
    mock_ai.game_info = MagicMock()
    mock_ai.game_info.map_center = (50, 50)
    
    # Setup mocks for supply depot building
    mock_ai.can_afford = MagicMock(return_value=True)
    mock_ai.already_pending = MagicMock(return_value=0)
    
    # Mock find_placement to return a valid position
    mock_ai.find_placement = AsyncMock(return_value=(15, 15))
    
    # Mock select_build_worker
    mock_worker = MagicMock()
    mock_worker.build = MagicMock()
    mock_ai.select_build_worker = MagicMock(return_value=mock_worker)
    
    # Create the manager
    manager = MilitaryManager(mock_ai)
    
    # Test the emergency supply function
    result = await manager._emergency_supply()
    
    # Verify the expected calls were made
    mock_ai.can_afford.assert_called_once_with(UnitTypeId.SUPPLYDEPOT)
    mock_ai.already_pending.assert_called_once_with(UnitTypeId.SUPPLYDEPOT)
    mock_ai.find_placement.assert_called_once()
    mock_ai.select_build_worker.assert_called_once()
    mock_worker.build.assert_called_once_with(UnitTypeId.SUPPLYDEPOT, (15, 15))
    
    # Verify the function returned True (success)
    print(f"Test completed with result: {result}")
    assert result is True, "Expected _emergency_supply to return True"
