"""
Integration tests for the HeadManager class and its coordination with other managers.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from sc2.ids.unit_typeid import UnitTypeId

# Import the managers to test
from managers.head_manager import HeadManager
from managers.economy_manager import EconomyManager
from managers.military_manager import MilitaryManager

class TestHeadManagerIntegration:
    """Test suite for HeadManager integration with other managers."""

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
        ai.workers = MagicMock()
        ai.workers.amount = 12
        ai.townhalls = MagicMock()
        ai.townhalls.amount = 1
        ai.townhalls.first = MagicMock()
        ai.structures = MagicMock()
        ai.units = MagicMock()
        ai.enemy_units = MagicMock()
        ai.enemy_structures = MagicMock()
        ai.can_afford = MagicMock(return_value=True)
        ai.already_pending = MagicMock(return_value=0)
        ai.distribute_workers = AsyncMock()
        return ai

    @pytest.fixture
    def managers(self, mock_ai):
        """Set up all managers with a shared mock AI."""
        head = HeadManager(mock_ai)
        economy = EconomyManager(mock_ai)
        military = MilitaryManager(mock_ai)
        
        # Register managers with head
        head.register_manager('economy', economy)
        head.register_manager('military', military)
        
        return {
            'head': head,
            'economy': economy,
            'military': military,
            'ai': mock_ai
        }

    @pytest.mark.asyncio
    async def test_manager_registration(self, managers):
        """Test that managers are properly registered with the head."""
        assert managers['head'].managers.get('economy') is not None
        assert managers['head'].managers.get('military') is not None
        assert managers['economy'].head == managers['head']
        assert managers['military'].head == managers['head']

    @pytest.mark.asyncio
    async def test_economy_military_coordination(self, managers):
        """Test that economy and military managers coordinate through head."""
        # Setup mocks
        managers['ai'].time = 100  # Past initial build time
        managers['ai'].supply_left = 2  # Low supply
        
        # Run a step
        await managers['head'].on_step()
        
        # Verify economy manager was called (supply depot should be built)
        assert managers['ai'].find_placement.called
        
        # Verify military manager received the strategy
        assert managers['military'].strategy == "bio_rush"  # Default strategy

    @pytest.mark.asyncio
    async def test_strategy_selection(self, managers):
        """Test that strategy changes affect both managers."""
        # Change strategy
        managers['head'].strategy = "mech"
        
        # Verify military manager received the update
        assert managers['military'].strategy == "mech"
        
        # Verify build order was updated
        # (This assumes MilitaryManager updates its build order when strategy changes)
        assert any(building[0] == UnitTypeId.FACTORY 
                  for building in managers['military'].build_order)

    @pytest.mark.asyncio
    async def test_resource_allocation(self, managers):
        """Test that resources are properly allocated between managers."""
        # Set up mocks for resource allocation test
        managers['ai'].minerals = 150  # Enough for one thing at a time
        managers['ai'].supply_left = 2  # Need supply
        managers['military'].build_order = [
            (UnitTypeId.BARRACKS, 1, "Test")
        ]
        
        # Run a step
        await managers['head'].on_step()
        
        # Verify economy manager took priority (supply first)
        assert managers['ai'].find_placement.called
        
        # Reset and test military priority
        managers['ai'].minerals = 150
        managers['ai'].supply_left = 5  # Plenty of supply
        managers['ai'].find_placement.reset_mock()
        
        await managers['head'].on_step()
        
        # Verify military manager built something
        assert managers['ai'].find_placement.called
