"""
Unit tests for the MilitaryManager class.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock, call
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2
from sc2.units import Units

# Import the manager to test
from managers.military_manager import MilitaryManager

class TestMilitaryManager:
    """Test suite for MilitaryManager functionality."""

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
        
        # Mock structures and units
        ai.units = MagicMock()
        ai.structures = MagicMock()
        ai.townhalls = MagicMock()
        ai.enemy_units = []
        ai.enemy_structures = []
        ai.game_info = MagicMock()
        ai.game_info.map_center = Point2((50, 50))
        
        # Mock common methods
        ai.can_afford = MagicMock(return_value=True)
        ai.already_pending = MagicMock(return_value=0)
        ai.find_placement = AsyncMock(return_value=Point2((55, 55)))
        ai.can_place = AsyncMock(return_value=True)
        ai.select_build_worker = MagicMock(return_value=MagicMock())
        
        # Mock townhalls
        mock_cc = MagicMock()
        mock_cc.position = Point2((0, 0))
        mock_cc.is_idle = True
        ai.townhalls.ready = [mock_cc]
        ai.townhalls.first = mock_cc
        
        # Mock structures
        ai.structures.return_value = MagicMock()
        ai.structures.return_value.ready = MagicMock(return_value=MagicMock(amount=0))
        ai.structures.return_value.filter.return_value = MagicMock(amount=0)
        
        # Mock units
        ai.units.return_value = MagicMock()
        ai.units.return_value.filter.return_value = MagicMock(amount=0)
        
        return ai

    @pytest.fixture
    def military_manager(self, mock_ai):
        """Create a MilitaryManager instance with a mock AI."""
        manager = MilitaryManager(mock_ai)
        manager.debug = False
        return manager

    @pytest.mark.asyncio
    async def test_initialization(self, military_manager):
        """Test that the military manager initializes correctly."""
        assert military_manager is not None
        assert military_manager.strategy == "bio_rush"  # Default strategy

    @pytest.mark.asyncio
    async def test_emergency_supply(self, military_manager, mock_ai):
        """Test emergency supply depot construction."""
        # Setup
        mock_ai.supply_left = 1  # Very low supply
        mock_ai.supply_cap = 15  # Set supply cap to avoid the supply_cap < 200 check
        
        # Mock structures to return an empty list for supply depots
        mock_ai.structures.return_value.filter.return_value = MagicMock(amount=0)
        
        # Mock can_afford to return True for supply depots
        mock_ai.can_afford.return_value = True
        
        # Mock already_pending to return 0 (no pending supply depots)
        mock_ai.already_pending.return_value = 0
        
        # Test emergency supply when needed
        await military_manager._emergency_supply()
        
        # Verify build was attempted
        mock_ai.find_placement.assert_called_once()
        mock_ai.select_build_worker.assert_called_once()
        
        # Get the build call arguments
        build_call_args = mock_ai.select_build_worker.return_value.build.call_args
        assert build_call_args[0][0] == UnitTypeId.SUPPLYDEPOT
        
        # Reset mocks for second test
        mock_ai.find_placement.reset_mock()
        mock_ai.select_build_worker.reset_mock()
        
        # Test when not needed (enough supply)
        mock_ai.supply_left = 5
        await military_manager._emergency_supply()
        
        # Should not have called find_placement or build again
        mock_ai.find_placement.assert_not_called()
        mock_ai.select_build_worker.assert_not_called()
        
        # Test when supply depot is already being built
        mock_ai.supply_left = 1
        mock_ai.already_pending.return_value = 1  # Supply depot already being built
        mock_ai.find_placement.reset_mock()
        
        await military_manager._emergency_supply()
        mock_ai.find_placement.assert_not_called()
        mock_ai.select_build_worker.assert_not_called()

    @pytest.mark.asyncio
    async def test_control_army(self, military_manager, mock_ai):
        """Test army control logic."""
        # Setup mock army units
        marine = MagicMock()
        marine.position = Point2((30, 30))
        marine.type_id = UnitTypeId.MARINE
        marine.health_percentage = 1.0
        marine.is_ready = True
        marine.is_moving = False
        marine.distance_to = MagicMock(return_value=10)  # Within attack range
        
        medic = MagicMock()
        medic.position = Point2((31, 31))
        medic.type_id = UnitTypeId.MEDIVAC
        medic.health_percentage = 0.8
        medic.is_ready = True
        medic.is_moving = False
        medic.distance_to = MagicMock(return_value=10)  # Within attack range
        
        # Mock units filter to return our mock units
        mock_units = MagicMock()
        mock_units.filter.return_value = [marine, medic]
        mock_ai.units = mock_units
        
        # Mock enemy units
        enemy = MagicMock()
        enemy.position = Point2((40, 40))
        enemy.type_id = UnitTypeId.ZERGLING
        
        # Mock enemy units and structures
        mock_ai.enemy_units = [enemy]
        mock_ai.enemy_structures = []
        
        # Set attack_started to True to trigger attack behavior
        military_manager.attack_started = True
        
        # Set a rally point
        military_manager.rally_point = Point2((50, 50))
        
        # Test army control
        await military_manager._control_army()
        
        # Verify units received attack or move commands
        # Marine should attack since we have enemies and attack_started is True
        marine.attack.assert_called_once()
        
        # Medivac should either attack (to heal) or move to follow
        assert medic.attack.called or medic.move.called()
        
        # Test with no enemies - should move to rally point
        marine.reset_mock()
        medic.reset_mock()
        mock_ai.enemy_units = []
        
        await military_manager._control_army()
        
        # Should move to rally point when no enemies
        marine.move.assert_called_once_with(military_manager.rally_point)
        medic.move.assert_called_once_with(military_manager.rally_point)

    @pytest.mark.asyncio
    async def test_execute_build_order(self, military_manager, mock_ai):
        """Test build order execution."""
        print("\n=== Starting test_execute_build_order ===")
        
        # Setup initial build order
        military_manager.build_order = [
            (UnitTypeId.SUPPLYDEPOT, 1, "Build Supply Depot"),
            (UnitTypeId.BARRACKS, 1, "Build Barracks"),
            (UnitTypeId.FACTORY, 2, "Build Factory"),
            (UnitTypeId.STARPORT, 3, "Build Starport")
        ]
        military_manager.build_order_index = 0
        
        # Mock supply and other requirements
        mock_ai.supply_used = 10
        mock_ai.supply_cap = 20
        mock_ai.can_afford.return_value = True
        
        # Mock structures to return 0 for initial checks
        mock_ai.structures.return_value.amount = 0
        
        # Mock townhalls
        mock_cc = MagicMock()
        mock_cc.position = Point2((0, 0))
        mock_ai.townhalls.first = mock_cc
        
        # Enable debug output
        military_manager.debug = True
        
        # --- Test 1: Build Supply Depot ---
        print("\n--- Test 1: Building Supply Depot ---")
        await military_manager._execute_build_order()
        
        # Verify supply depot build was attempted
        print("\n--- Verifying supply depot build was attempted ---")
        mock_ai.find_placement.assert_called_with(
            UnitTypeId.SUPPLYDEPOT,
            near=mock_ai.townhalls.first.position,
            placement_step=2
        )
        
        # Simulate supply depot being built
        mock_ai.structures.return_value.amount = 1
        military_manager._first_depot_completed = True
        military_manager.build_order_index = 1  # Move to next item in build order
        
        # Reset mock for next test
        mock_ai.reset_mock()
        
        # --- Test 2: Build Barracks ---
        print("\n--- Test 2: Building Barracks ---")
        # Mock that we don't have any barracks yet
        def mock_structures_filter(unit_type):
            mock = MagicMock()
            if unit_type == UnitTypeId.BARRACKS:
                mock.amount = 0
            else:
                mock.amount = 1 if unit_type == UnitTypeId.SUPPLYDEPOT else 0
            return mock
            
        mock_ai.structures.side_effect = mock_structures_filter
        
        await military_manager._execute_build_order()
        
        # Verify barracks build was attempted
        print("\n--- Verifying barracks build was attempted ---")
        mock_ai.find_placement.assert_called_with(
            UnitTypeId.BARRACKS,
            near=mock_ai.townhalls.first.position,
            placement_step=2
        )
        
        # --- Test 3: Move to next item when barracks is already built ---
        print("\n--- Test 3: Moving to next item when barracks exists ---")
        # Mock that we have a barracks now
        def mock_structures_filter_with_barracks(unit_type):
            mock = MagicMock()
            if unit_type in [UnitTypeId.BARRACKS, UnitTypeId.SUPPLYDEPOT]:
                mock.amount = 1
            else:
                mock.amount = 0
            return mock
            
        mock_ai.structures.side_effect = mock_structures_filter_with_barracks
        
        # Reset mock and call again
        mock_ai.reset_mock()
        await military_manager._execute_build_order()
        
        # Verify we moved to the next build order item (Starport)
        print("\n--- Verifying build order index updated ---")
        print(f"Current build order index: {military_manager.build_order_index}")
        print(f"Expected next build item: {UnitTypeId.STARPORT}")
        print(f"Actual next build item: {military_manager.build_order[military_manager.build_order_index][0]}")
        
        # The index should be 3 because we built the Barracks and Factory
        assert military_manager.build_order_index == 3, "Build order index should increment after building all structures"
        assert military_manager.build_order[military_manager.build_order_index][0] == UnitTypeId.STARPORT, "Next build item should be Starport"
        
    @pytest.mark.asyncio
    async def test_train_units(self, military_manager, mock_ai):
        """Test unit training logic."""
        # Setup mock production facilities
        mock_barracks = MagicMock()
        mock_barracks.is_idle = True
        mock_barracks.type_id = UnitTypeId.BARRACKS
        mock_barracks.train = MagicMock(return_value=True)
        
        mock_factory = MagicMock()
        mock_factory.is_idle = True
        mock_factory.type_id = UnitTypeId.FACTORY
        mock_factory.train = MagicMock(return_value=True)
        
        # Test training marines from idle barracks
        mock_ai.structures.return_value.filter.return_value = [mock_barracks]
        mock_ai.can_afford.return_value = True
        
        await military_manager._train_army()
        mock_barracks.train.assert_called_once_with(UnitTypeId.MARINE)
        
        # Test training siege tanks from factory with tech lab
        military_manager.tech_buildings['factory_tech'] = True
        mock_ai.structures.return_value.filter.return_value = [mock_factory]
        mock_barracks.train.reset_mock()
        
        await military_manager._train_army()
        mock_factory.train.assert_called_once_with(UnitTypeId.SIEGETANK)
        
    @pytest.mark.asyncio
    async def test_manage_upgrades(self, military_manager, mock_ai):
        """Test upgrade management logic."""
        # Setup mock engineering bay with tech lab
        mock_ebay = MagicMock()
        mock_ebay.is_idle = True
        mock_ebay.noqueue = True
        mock_ebay.type_id = UnitTypeId.ENGINEERINGBAY
        
        mock_techlab = MagicMock()
        mock_techlab.is_idle = True
        mock_techlab.noqueue = True
        mock_techlab.type_id = UnitTypeId.TECHLAB
        
        # Mock structures to return our buildings
        def mock_structures_filter(unit_type):
            mock = MagicMock()
            if unit_type == UnitTypeId.ENGINEERINGBAY:
                mock.ready = MagicMock(return_value=[mock_ebay])
            elif unit_type == UnitTypeId.TECHLAB:
                mock.ready = MagicMock(return_value=[mock_techlab])
            else:
                mock.ready = MagicMock(return_value=[])
            return mock
            
        mock_ai.structures.side_effect = mock_structures_filter
        
        # Test researching infantry upgrades
        mock_ai.can_afford.return_value = True
        await military_manager._manage_upgrades()
        
        # Should have attempted to research +1 infantry weapons
        mock_ebay.research.assert_called_once_with(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1)
        
    @pytest.mark.asyncio
    async def test_army_composition(self, military_manager, mock_ai):
        """Test army composition management."""
        # Setup mock army units
        marines = [MagicMock(type_id=UnitTypeId.MARINE) for _ in range(10)]
        medivacs = [MagicMock(type_id=UnitTypeId.MEDIVAC) for _ in range(2)]
        
        # Mock units filter to return our mock units
        def mock_units_filter(unit_type):
            mock = MagicMock()
            if unit_type == UnitTypeId.MARINE:
                mock.filter.return_value = marines
            elif unit_type == UnitTypeId.MEDIVAC:
                mock.filter.return_value = medivacs
            else:
                mock.filter.return_value = []
            return mock
            
        mock_ai.units.side_effect = mock_units_filter
        
        # Test army composition tracking
        military_manager._update_army_composition()
        assert military_manager.army_composition[UnitTypeId.MARINE] == 10
        assert military_manager.army_composition[UnitTypeId.MEDIVAC] == 2
        
    @pytest.mark.asyncio
    async def test_attack_logic(self, military_manager, mock_ai):
        """Test attack logic and target selection."""
        # Setup mock army units
        marine = MagicMock()
        marine.position = Point2((30, 30))
        marine.type_id = UnitTypeId.MARINE
        marine.health_percentage = 1.0
        marine.is_ready = True
        marine.is_moving = False
        marine.distance_to = MagicMock(return_value=10)
        
        # Mock enemy structures
        enemy_cc = MagicMock()
        enemy_cc.position = Point2((100, 100))
        enemy_cc.type_id = UnitTypeId.COMMANDCENTER
        enemy_cc.health_percentage = 1.0
        
        # Set up mocks
        mock_ai.units.return_value.filter.return_value = [marine]
        mock_ai.enemy_structures = [enemy_cc]
        
        # Test attack logic when attack is triggered
        military_manager.attack_started = True
        await military_manager._control_army()
        
        # Marine should attack the enemy command center
        marine.attack.assert_called_once_with(enemy_cc.position)
        
        # Test retreat when health is low
        marine.health_percentage = 0.3
        marine.attack.reset_mock()
        
        await military_manager._control_army()
        
        # Marine should retreat (move towards rally point)
        marine.move.assert_called_once()
        marine.attack.assert_not_called()
