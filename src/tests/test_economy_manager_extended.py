"""
Extended unit tests for the EconomyManager class.
"""
import asyncio
import pytest
import math
from unittest.mock import MagicMock, patch, AsyncMock, call
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2, Point3

# Add parent directory to path to allow importing from managers
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the manager to test
from managers.economy_manager import EconomyManager

# Enable async test support
pytestmark = pytest.mark.asyncio

class TestEconomyManagerExtended:
    """Extended test suite for EconomyManager functionality."""

    @pytest.fixture
    def mock_ai(self):
        """Create a mock AI instance for testing."""
        ai = MagicMock()
        ai.time = 0
        ai.minerals = 1000
        ai.vespene = 0
        ai.supply_used = 10
        ai.supply_cap = 20
        ai.supply_left = 10
        ai.supply_workers = 10
        
        # Mock workers
        ai.workers = MagicMock()
        ai.workers.amount = 12
        ai.workers.idle = MagicMock(return_value=[])
        ai.workers.filter = MagicMock(return_value=MagicMock())
        ai.workers.random = MagicMock()
        ai.workers.closer_than = MagicMock(return_value=MagicMock(amount=0))
        
        # Mock townhalls
        cc = MagicMock()
        cc.position = Point2((50, 50))
        cc.is_idle = True
        cc.orders = []
        cc.type_id = UnitTypeId.COMMANDCENTER
        cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)  # Mock callable
        
        ai.townhalls = MagicMock()
        ai.townhalls.amount = 1
        ai.townhalls.first = cc
        ai.townhalls.random = cc
        
        # Mock structures
        ai.structures = MagicMock()
        ai.structures.return_value.exists = False
        ai.structures.return_value.ready = MagicMock()
        ai.structures.return_value.ready.amount = 0
        ai.structures.return_value.closer_than = MagicMock(return_value=MagicMock(amount=0))
        ai.structures.filter = MagicMock(return_value=MagicMock(amount=0))
        
        # Mock enemy units
        ai.enemy_units = MagicMock()
        ai.enemy_units.filter = MagicMock(return_value=MagicMock(amount=0))
        
        # Mock vespene geysers
        ai.vespene_geyser = MagicMock()
        geyser = MagicMock()
        geyser.tag = 123
        geyser.position = Point2((60, 60))
        ai.vespene_geyser.closer_than = MagicMock(return_value=[geyser])
        
        # Mock expansion locations
        ai.expansion_locations = [Point2((100, 100)), Point2((200, 200))]
        
        # Mock methods
        ai.already_pending = MagicMock(return_value=0)
        ai.can_afford = MagicMock(return_value=True)
        ai.can_place = AsyncMock(return_value=True)
        ai.find_placement = AsyncMock(return_value=Point2((55, 55)))
        ai.select_build_worker = MagicMock(return_value=MagicMock())
        ai.distribute_workers = AsyncMock()
        ai.do = AsyncMock()
        
        return ai

    @pytest.fixture
    def economy_manager(self, mock_ai):
        """Create an EconomyManager instance with a mock AI."""
        manager = EconomyManager(mock_ai)
        manager.debug = True
        return manager

    @pytest.mark.asyncio
    async def test_orbital_command_upgrade(self, economy_manager, mock_ai):
        """Test orbital command upgrade logic."""
        # Setup
        mock_ai.time = 100  # Past 90 seconds
        mock_ai.townhalls.first.type_id = UnitTypeId.COMMANDCENTER
        mock_ai.townhalls.first.is_idle = True
        mock_ai.can_afford.return_value = True
        
        # Test orbital command upgrade
        await economy_manager.on_step()
        mock_ai.townhalls.first.assert_has_calls([call(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)])
        
        # Test orbital command already started
        economy_manager.orbital_command_started = True
        mock_ai.townhalls.first.reset_mock()
        await economy_manager.on_step()
        mock_ai.townhalls.first.assert_not_called()

    @pytest.mark.asyncio
    async def test_worker_distribution(self, economy_manager, mock_ai):
        """Test periodic worker distribution."""
        # First call - should trigger distribution
        economy_manager.last_worker_distribution = 0
        await economy_manager.on_step()
        mock_ai.distribute_workers.assert_called_once()
        
        # Second call - too soon, should not trigger
        mock_ai.distribute_workers.reset_mock()
        await economy_manager.on_step()
        mock_ai.distribute_workers.assert_not_called()
        
        # Third call - after cooldown, should trigger
        economy_manager.last_worker_distribution = -20  # Force update
        await economy_manager.on_step()
        mock_ai.distribute_workers.assert_called_once()

    @pytest.mark.asyncio
    async def test_expansion_logic(self, economy_manager, mock_ai):
        """Test expansion logic."""
        # Setup head manager mock
        head_mock = MagicMock()
        head_mock.should_expand.return_value = True
        economy_manager.head = head_mock
        
        # Test expansion when conditions are met
        mock_ai.time = 200  # Past min_time_before_expand
        mock_ai.minerals = 600  # More than expand_when_minerals
        
        # Mock select_build_worker to return a worker
        worker = MagicMock()
        worker.build = MagicMock()
        mock_ai.select_build_worker.return_value = worker
        
        # Trigger expansion
        result = await economy_manager.expand_now()
        
        # Verify expansion was attempted
        assert result is True
        worker.build.assert_called_once_with(UnitTypeId.COMMANDCENTER, mock_ai.expansion_locations[0])
        
        # Test expansion blocked by enemy units
        mock_ai.enemy_units.filter.return_value = [MagicMock()]  # Enemy nearby
        result = await economy_manager.expand_now()
        assert result is False

    @pytest.mark.asyncio
    async def test_supply_depot_placement(self, economy_manager, mock_ai):
        """Test supply depot placement logic."""
        # Setup
        economy_manager.first_supply_depot_built = False
        mock_ai.supply_left = 2
        
        # Mock worker for building
        worker = MagicMock()
        worker.is_idle = True
        worker.is_carrying_resource = False
        worker.position = Point2((50, 50))
        mock_ai.workers.filter.return_value = [worker]
        
        # Test successful build
        result = await economy_manager.build_supply_depot()
        assert result is True
        mock_ai.find_placement.assert_called_once()
        
        # Test no valid placement found
        mock_ai.find_placement.return_value = None
        result = await economy_manager.build_supply_depot()
        assert result is False

    @pytest.mark.asyncio
    async def test_refinery_management(self, economy_manager, mock_ai):
        """Test refinery construction and worker assignment."""
        # Setup
        mock_ai.time = 120  # 2 minutes in
        mock_ai.workers.amount = 20  # Enough workers
        
        # Mock a geyser
        geyser = MagicMock()
        geyser.tag = 123
        geyser.position = Point2((60, 60))
        mock_ai.vespene_geyser.closer_than.return_value = [geyser]
        
        # Test successful refinery build
        result = await economy_manager.build_refineries()
        assert result is True
        mock_ai.select_build_worker.assert_called_once()
        
        # Test worker assignment to refinery
        refinery = MagicMock()
        refinery.type_id = UnitTypeId.REFINERY
        refinery.position = Point2((60, 60))
        mock_ai.structures.return_value.ready = [refinery]
        
        # Mock workers for assignment
        worker = MagicMock()
        worker.is_carrying_vespene = False
        workers = MagicMock()
        workers.amount = 1  # Need more workers
        mock_ai.workers.closer_than.return_value = workers
        mock_ai.workers.random = worker
        
        await economy_manager.manage_gas_workers()
        worker.gather.assert_called_once_with(refinery)

    @pytest.mark.asyncio
    async def test_error_handling(self, economy_manager, mock_ai):
        """Test error handling in on_step."""
        # Test error in on_step
        mock_ai.time.side_effect = Exception("Test error")
        
        # Should not raise an exception
        await economy_manager.on_step()
        
        # Test error in expand_now
        mock_ai.time = 200
        mock_ai.time.side_effect = None
        mock_ai.select_build_worker.side_effect = Exception("Build error")
        
        result = await economy_manager.expand_now()
        assert result is False
