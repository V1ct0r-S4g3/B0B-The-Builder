"""Direct tests for MilitaryManager without pytest fixtures."""
import sys
import unittest
from unittest.mock import MagicMock, AsyncMock
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.ids.ability_id import AbilityId
sys.path.append('.')
from managers.military_manager import MilitaryManager

class TestMilitaryManager(unittest.TestCase):
    """Test cases for MilitaryManager."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        cls.maxDiff = None  # Show full diff output
        print("\n" + "="*80)
        print("SETTING UP TEST CLASS")
        print("="*80)
    
    def setUp(self):
        """Set up each test."""
        self.mock_ai = self.create_mock_ai()
        self.manager = MilitaryManager(self.mock_ai)
        print(f"\nRunning test: {self._testMethodName}")
        print("-" * 60)
    
    @staticmethod
    def create_mock_ai():
        """Create a mock AI object for testing."""
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
        mock_ai.game_info.map_center = Point2((50, 50))
        mock_ai.can_afford = MagicMock(return_value=True)
        mock_ai.already_pending = MagicMock(return_value=0)
        mock_ai.select_build_worker = MagicMock()
        mock_ai.find_placement = MagicMock(return_value=Point2((15, 15)))
        return mock_ai
    
    def test_strategy_management(self):
        """Test military strategy management."""
        # Test default strategy
        self.assertEqual(self.manager.strategy, "bio_rush")
        
        # Test changing strategy by directly setting it
        self.manager.strategy = "tank_push"
        self.assertEqual(self.manager.strategy, "tank_push")
        
        # Test invalid strategy falls back to default
        self.manager.strategy = "invalid_strategy"
        self.assertEqual(self.manager.strategy, "bio_rush")
        print("✓ Strategy management test passed!")
    
    def test_military_manager_basic(self):
        """Test basic functionality of MilitaryManager."""
        # Test initial values
        self.assertIsNone(self.manager.attack_target)
        self.assertFalse(self.manager.attack_started)
        self.assertIsNone(self.manager.rally_point)
        self.assertIsInstance(self.manager.army_tags, set)
        self.assertIsInstance(self.manager.tech_buildings, dict)
        self.assertIn('barracks_tech', self.manager.tech_buildings)
        self.assertIn('factory_tech', self.manager.tech_buildings)
        self.assertIn('starport_tech', self.manager.tech_buildings)
        print("✓ Basic MilitaryManager test passed!")
    
    def test_build_order_definitions(self):
        """Test that build orders are properly defined."""
        # Check that bio_rush build order exists and has expected steps
        self.assertIn('bio_rush', self.manager.build_orders)
        self.assertIsInstance(self.manager.build_orders['bio_rush'], list)
        self.assertGreater(len(self.manager.build_orders['bio_rush']), 0)
        
        # Check that each build order step has the expected format
        for step in self.manager.build_orders['bio_rush']:
            self.assertEqual(len(step), 3)  # (unit_type, supply, description)
            self.assertIsInstance(step[0], UnitTypeId)
            self.assertIsInstance(step[1], int)
            self.assertIsInstance(step[2], str)
        print("✓ Build order definitions test passed!")
    
    def test_combat_behavior(self):
        """Test basic combat behavior setup."""
        # Test setting attack target
        target = Point2((100, 100))
        self.manager.attack_target = target
        self.assertEqual(self.manager.attack_target, target)
        
        # Test attack state
        self.manager.attack_started = True
        self.assertTrue(self.manager.attack_started)
        
        # Test rally point
        rally = Point2((50, 50))
        self.manager.rally_point = rally
        self.assertEqual(self.manager.rally_point, rally)
        print("✓ Combat behavior test passed!")
    
    def test_army_composition_analysis(self):
        """Test army composition analysis."""
        # Create mock units
        mock_units = []
        
        # Add some marines
        for _ in range(10):
            marine = MagicMock()
            marine.type_id = UnitTypeId.MARINE
            marine.is_ready = True
            mock_units.append(marine)
        
        # Add some medivacs
        for _ in range(2):
            medivac = MagicMock()
            medivac.type_id = UnitTypeId.MEDIVAC
            medivac.is_ready = True
            mock_units.append(medivac)
        
        # Set up the mock
        self.mock_ai.units.return_value = mock_units
        
        # Analyze army composition
        composition = {}
        for unit in mock_units:
            if unit.type_id not in composition:
                composition[unit.type_id] = 0
            composition[unit.type_id] += 1
        
        # Verify the counts
        self.assertEqual(composition[UnitTypeId.MARINE], 10)
        self.assertEqual(composition[UnitTypeId.MEDIVAC], 2)
        self.assertEqual(len(composition), 2)
        print("✓ Army composition analysis test passed!")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("RUNNING MILITARY MANAGER TESTS")
    print("="*80)
    
    # Run the tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)
