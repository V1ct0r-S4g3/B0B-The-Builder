"""Tests for the MilitaryManager class."""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2

# Import the manager to test
from src.managers.military_manager import MilitaryManager

class TestMilitaryManager(unittest.IsolatedAsyncioTestCase):
    """Test cases for the MilitaryManager class."""

    async def asyncSetUp(self):
        """Set up the test environment before each test method."""
        # Create a mock AI object
        self.ai = MagicMock()
        self.ai.time = 0.0
        self.ai.minerals = 200
        self.ai.vespene = 100
        self.ai.supply_used = 10
        self.ai.supply_cap = 15
        
        # Mock units and structures
        self.ai.units = MagicMock()
        self.ai.structures = MagicMock()
        self.ai.townhalls = MagicMock()
        self.ai.gas_buildings = MagicMock()
        
        # Create the manager instance
        self.manager = MilitaryManager(self.ai, strategy="bio_rush")
        
        # Mock the head manager
        self.manager.head = AsyncMock()

    async def test_initialization(self):
        """Test that the MilitaryManager initializes correctly."""
        self.assertEqual(self.manager.strategy, "bio_rush")
        self.assertEqual(len(self.manager.army_tags), 0)
        self.assertIsNone(self.manager.attack_target)
        self.assertFalse(self.manager.attack_started)
        self.assertIsNone(self.manager.rally_point)

    async def test_on_start(self):
        """Test the on_start method initializes correctly."""
        await self.manager.on_start()
        # Verify any initial setup in on_start
        self.assertTrue(True)  # Placeholder for actual assertions

    async def test_manage_army_composition(self):
        """Test army composition management."""
        # Setup
        self.ai.structures.return_value = [MagicMock(type_id=UnitTypeId.BARRACKS, is_idle=True)]
        self.ai.can_afford.return_value = True
        
        # Test marine production
        await self.manager.manage_army_composition()
        self.ai.structures().train.assert_called_once_with(UnitTypeId.MARINE)

    async def test_manage_upgrades(self):
        """Test upgrade management."""
        # Setup
        engineering_bay = MagicMock()
        engineering_bay.type_id = UnitTypeId.ENGINEERINGBAY
        engineering_bay.is_idle = True
        self.ai.structures.return_value = [engineering_bay]
        self.ai.can_afford.return_value = True
        
        # Test infantry weapons upgrade
        await self.manager.manage_upgrades()
        engineering_bay.research.assert_called_once_with(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1)

    async def test_handle_combat(self):
        """Test combat handling logic."""
        # Setup
        marine = MagicMock()
        marine.position = Point2((10, 10))
        marine.weapon_cooldown = 0
        marine.weapon_ready = True
        
        enemy = MagicMock()
        enemy.position = Point2((11, 11))
        
        self.ai.units.of_type.return_value = [marine]
        self.ai.enemy_units = [enemy]
        
        # Test combat behavior
        await self.manager.handle_combat()
        marine.attack.assert_called_once_with(enemy.position)

    async def test_attack_enemy_base(self):
        """Test attack logic."""
        # Setup
        marine = MagicMock()
        marine.position = Point2((10, 10))
        
        self.manager.army_tags = {1}
        self.ai.units.tags_in.return_value = [marine]
        
        # Test attack move
        self.manager.attack_target = Point2((50, 50))
        await self.manager.attack_enemy_base()
        marine.attack.assert_called_once_with(self.manager.attack_target)

    async def test_manage_tech_labs(self):
        """Test tech lab management."""
        # Setup
        barracks = MagicMock()
        barracks.type_id = UnitTypeId.BARRACKS
        barracks.add_on_tag = None
        barracks.position = Point2((10, 10))
        
        tech_lab = MagicMock()
        tech_lab.type_id = UnitTypeId.TECHLAB
        
        self.ai.structures.return_value = [barracks]
        self.ai.find_placement.return_value = Point2((10, 11))
        self.ai.can_afford.return_value = True
        
        # Test tech lab construction
        await self.manager.manage_tech_labs()
        self.ai.build.assert_called_once_with(UnitTypeId.TECHLAB, near=barracks.position.offset((2.5, 0.5)))

    async def test_manage_reactors(self):
        """Test reactor management."""
        # Setup
        barracks = MagicMock()
        barracks.type_id = UnitTypeId.BARRACKS
        barracks.add_on_tag = None
        barracks.position = Point2((10, 10))
        
        reactor = MagicMock()
        reactor.type_id = UnitTypeId.REACTOR
        
        self.ai.structures.return_value = [barracks]
        self.ai.find_placement.return_value = Point2((10, 11))
        self.ai.can_afford.return_value = True
        
        # Test reactor construction
        await self.manager.manage_reactors()
        self.ai.build.assert_called_once_with(UnitTypeId.REACTOR, near=barracks.position.offset((2.5, 0.5)))

if __name__ == "__main__":
    unittest.main()
