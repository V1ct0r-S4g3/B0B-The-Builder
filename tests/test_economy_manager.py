"""Tests for the EconomyManager class."""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2
from sc2.unit import Unit

# Import the manager to test
from src.managers.economy_manager import EconomyManager

class TestEconomyManager(unittest.IsolatedAsyncioTestCase):
    """Test cases for the EconomyManager class."""

    async def asyncSetUp(self):
        """Set up the test environment before each test method."""
        # Create a mock AI object
        self.ai = MagicMock()
        self.ai.time = 0.0
        self.ai.minerals = 50
        self.ai.vespene = 0
        self.ai.supply_used = 10
        self.ai.supply_cap = 15
        
        # Mock units and structures
        self.ai.units = MagicMock()
        self.ai.townhalls = MagicMock()
        self.ai.gas_buildings = MagicMock()
        self.ai.structures = MagicMock()
        
        # Create the manager instance
        self.manager = EconomyManager(self.ai)
        
        # Mock the head manager
        self.manager.head = AsyncMock()

    async def test_initialization(self):
        """Test that the EconomyManager initializes correctly."""
        self.assertEqual(self.manager.worker_ratio, 16)
        self.assertEqual(self.manager.gas_workers_per_refinery, 3)
        self.assertEqual(self.manager.supply_buffer, 4)
        self.assertFalse(self.manager.first_supply_depot_built)
        self.assertFalse(self.manager.orbital_command_started)

    async def test_on_start(self):
        """Test the on_start method initializes correctly."""
        await self.manager.on_start()
        self.ai.distribute_workers.assert_called_once()

    async def test_train_workers(self):
        """Test worker training logic."""
        # Setup
        command_center = MagicMock()
        command_center.is_idle = True
        command_center.train.return_value = True
        self.ai.can_afford.return_value = True
        
        # Test successful worker train
        result = await self.manager.train_workers(command_center)
        self.assertTrue(result)
        command_center.train.assert_called_once_with(UnitTypeId.SCV, queue=False)
        
        # Test when already training
        command_center.train.reset_mock()
        command_center.is_idle = False
        result = await self.manager.train_workers(command_center)
        self.assertFalse(result)
        command_center.train.assert_not_called()

    async def test_manage_supply_depots(self):
        """Test supply depot construction logic."""
        # Setup
        self.ai.structures = MagicMock()
        self.ai.structures().amount = 0  # No supply depots yet
        self.ai.can_afford.return_value = True
        self.ai.find_placement.return_value = Point2((10, 10))
        
        # Test first supply depot
        self.manager.first_supply_depot_built = False
        await self.manager.manage_supply_depots()
        self.ai.build.assert_called_once()
        self.assertTrue(self.manager.first_supply_depot_built)
        
        # Test subsequent supply depots
        self.ai.build.reset_mock()
        self.manager.first_supply_depot_built = True
        self.ai.supply_used = 14  # Close to supply cap
        self.ai.supply_cap = 16
        
        await self.manager.manage_supply_depots()
        self.ai.build.assert_called_once()

    async def test_manage_refineries(self):
        """Test refinery construction logic."""
        # Setup
        vespene_geyser = MagicMock()
        vespene_geyser.position = Point2((10, 10))
        self.ai.vespene_geyser = MagicMock()
        self.ai.vespene_geyser.closer_than.return_value = [vespene_geyser]
        self.ai.can_afford.return_value = True
        self.ai.structures().closer_than.return_value = []
        
        # Test refinery construction
        await self.manager.manage_refineries()
        self.ai.build.assert_called_once_with(UnitTypeId.REFINERY, vespene_geyser)

    async def test_upgrade_to_orbital_command(self):
        """Test orbital command upgrade logic."""
        # Setup
        command_center = MagicMock()
        command_center.type_id = UnitTypeId.COMMANDCENTER
        command_center.is_idle = True
        self.ai.structures.return_value = [command_center]
        self.ai.can_afford.return_value = True
        
        # Test upgrading to orbital command
        await self.manager.upgrade_to_orbital_command()
        command_center.assert_has_calls([
            call(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)
        ])
        self.assertTrue(self.manager.orbital_command_started)

    async def test_expand(self):
        """Test expansion logic."""
        # Setup
        self.ai.minerals = 500
        self.ai.time = 200  # Past minimum expand time
        self.ai.townhalls.amount = 1
        self.ai.expansion_locations = [Point2((50, 50))]
        self.ai.can_afford.return_value = True
        
        # Test expansion
        await self.manager.expand()
        self.ai.expand_now.assert_called_once()

if __name__ == "__main__":
    unittest.main()
