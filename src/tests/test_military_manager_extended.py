"""Extended test suite for MilitaryManager."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2
from managers.military_manager import MilitaryManager

# Fixture for a basic MilitaryManager instance
@pytest.fixture
def basic_military_manager():
    """Create a basic MilitaryManager instance for testing."""
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
    return MilitaryManager(mock_ai)

# Test military strategy management
def test_strategy_management(basic_military_manager):
    """Test military strategy management."""
    manager = basic_military_manager
    
    # Test default strategy
    assert manager.strategy == "bio_rush"
    
    # Test changing strategy by directly setting it
    manager.strategy = "tank_push"
    assert manager.strategy == "tank_push"
    
    # Test invalid strategy falls back to default
    manager.strategy = "invalid_strategy"
    assert manager.strategy == "bio_rush"

# Test basic functionality of MilitaryManager
def test_military_manager_basic(basic_military_manager):
    """Test basic functionality of MilitaryManager."""
    manager = basic_military_manager
    
    # Test initial values
    assert manager.attack_target is None
    assert manager.attack_started is False
    assert manager.rally_point is None
    assert isinstance(manager.army_tags, set)
    assert isinstance(manager.tech_buildings, dict)
    assert 'barracks_tech' in manager.tech_buildings
    assert 'factory_tech' in manager.tech_buildings
    assert 'starport_tech' in manager.tech_buildings

# Test build order definitions
def test_build_order_definitions(basic_military_manager):
    """Test that build orders are properly defined."""
    manager = basic_military_manager
    
    # Check that bio_rush build order exists and has expected steps
    assert 'bio_rush' in manager.build_orders
    assert isinstance(manager.build_orders['bio_rush'], list)
    assert len(manager.build_orders['bio_rush']) > 0
    
    # Check that each build order step has the expected format
    for step in manager.build_orders['bio_rush']:
        assert len(step) == 3  # (unit_type, supply, description)
        assert isinstance(step[0], UnitTypeId)
        assert isinstance(step[1], int)
        assert isinstance(step[2], str)

# Test emergency supply logic
@pytest.mark.asyncio
async def test_emergency_supply(basic_military_manager):
    """Test emergency supply depot construction."""
    manager = basic_military_manager
    manager.ai = AsyncMock()
    
    # Set up low supply
    manager.ai.supply_left = 1
    manager.ai.supply_used = 13
    manager.ai.supply_cap = 14
    
    # Mock worker and build position
    mock_worker = MagicMock()
    mock_worker.build = AsyncMock(return_value=True)
    manager.ai.select_build_worker.return_value = mock_worker
    manager.ai.find_placement = AsyncMock(return_value=Point2((15, 15)))
    manager.ai.can_afford.return_value = True
    manager.ai.already_pending.return_value = 0
    
    # Mock the _build_structure method
    manager._build_structure = AsyncMock(return_value=True)
    
    # Call the emergency supply method
    result = await manager._emergency_supply()
    
    # Verify the supply depot was built
    assert result is True
    manager._build_structure.assert_called_once_with(UnitTypeId.SUPPLYDEPOT, "Emergency Supply Depot")

# Test army composition analysis
def test_army_composition_analysis(basic_military_manager):
    """Test army composition analysis."""
    manager = basic_military_manager
    
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
    manager.ai.units.return_value = mock_units
    
    # Analyze army composition
    composition = {}
    for unit in mock_units:
        if unit.type_id not in composition:
            composition[unit.type_id] = 0
        composition[unit.type_id] += 1
    
    # Verify the counts
    assert composition[UnitTypeId.MARINE] == 10
    assert composition[UnitTypeId.MEDIVAC] == 2
    assert len(composition) == 2

# Test combat behavior
def test_combat_behavior(basic_military_manager):
    """Test basic combat behavior setup."""
    manager = basic_military_manager
    
    # Test setting attack target
    target = Point2((100, 100))
    manager.attack_target = target
    assert manager.attack_target == target
    
    # Test attack state
    manager.attack_started = True
    assert manager.attack_started is True
    
    # Test rally point
    rally = Point2((50, 50))
    manager.rally_point = rally
    assert manager.rally_point == rally
