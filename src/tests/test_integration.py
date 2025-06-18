"""Integration tests for the bot's manager system."""
import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

from sc2.bot_ai import BotAI
from sc2.data import Result, Race
from sc2.ids.unit_typeid import UnitTypeId

from managers.head_manager import HeadManager
from managers.economy_manager import EconomyManager
from managers.military_manager import MilitaryManager
from bot.main import MyBot

class TestIntegration(unittest.TestCase):
    """Integration tests for the bot's manager system."""
    
    def setUp(self):
        """Set up the test case."""
        self.bot = MyBot()
        self.bot.ai = MagicMock(spec=BotAI)
        self.bot.ai.time = 0.0
        self.bot.ai.state = MagicMock()
        self.bot.ai.state.game_loop = 0
        self.bot.ai.minerals = 50
        self.bot.ai.vespene = 0
        self.bot.ai.supply_used = 14
        self.bot.ai.supply_cap = 15
        self.bot.ai.supply_army = 0
        self.bot.ai.workers = MagicMock(amount=12)
        self.bot.ai.townhalls = MagicMock(amount=1)
        self.bot.ai.units = MagicMock()
        self.bot.ai.units.of_type.return_value = MagicMock(amount=0)
        self.bot.ai.structures = MagicMock()
        self.bot.ai.enemy_units = MagicMock(amount=0)
        self.bot.ai.game_info = MagicMock()
        self.bot.ai.game_info.map_name = "Test Map"
        self.bot.ai.game_data = MagicMock()
        self.bot.ai.game_data.units = {}
        
        # Mock the state.score object
        score = MagicMock()
        score.collection_rate_minerals = 100
        score.collection_rate_vespene = 50
        self.bot.ai.state.score = score

    def test_manager_initialization(self):
        """Test that all managers are properly initialized."""
        async def test():
            await self.bot.on_start()
            
            # Verify managers were created
            self.assertIsInstance(self.bot.head_manager, HeadManager)
            self.assertIsInstance(self.bot.economy_manager, EconomyManager)
            self.assertIsInstance(self.bot.military_manager, MilitaryManager)
            
            # Verify managers are registered with HeadManager
            self.assertIn('economy', self.bot.head_manager.managers)
            self.assertIn('military', self.bot.head_manager.managers)
            
            # Verify cross-references are set
            self.assertEqual(self.bot.economy_manager.head, self.bot.head_manager)
            self.assertEqual(self.bot.military_manager.head, self.bot.head_manager)
            
        asyncio.get_event_loop().run_until_complete(test())
    
    def test_game_loop_execution(self):
        """Test that the game loop executes all manager steps."""
        async def test():
            # Set up mocks
            self.bot.head_manager.on_step = AsyncMock()
            self.bot.head_manager.on_step.return_value = None
            
            # Run a game step
            await self.bot.on_step(0)
            
            # Verify HeadManager's on_step was called
            self.bot.head_manager.on_step.assert_called_once()
            
        asyncio.get_event_loop().run_until_complete(test())
    
    def test_error_handling(self):
        """Test that errors in one manager don't affect others."""
        async def test():
            # Set up mocks to simulate an error in economy manager
            self.bot.economy_manager.on_step = AsyncMock()
            self.bot.economy_manager.on_step.side_effect = Exception("Test error")
            
            self.bot.military_manager.on_step = AsyncMock()
            
            # Run a game step
            await self.bot.on_step(0)
            
            # Verify both managers were called despite the error
            self.bot.economy_manager.on_step.assert_called_once()
            self.bot.military_manager.on_step.assert_called_once()
            
        asyncio.get_event_loop().run_until_complete(test())
    
    def test_game_state_updates(self):
        """Test that game state is properly updated."""
        async def test():
            await self.bot.on_start()
            
            # Update game state
            self.bot.ai.minerals = 200
            self.bot.ai.vespene = 100
            self.bot.ai.supply_used = 20
            self.bot.ai.supply_cap = 30
            
            # Run a game step to update state
            await self.bot.on_step(0)
            
            # Verify game state was updated
            self.assertEqual(self.bot.head_manager.game_state['economy']['minerals'], 200)
            self.assertEqual(self.bot.head_manager.game_state['economy']['vespene'], 100)
            self.assertEqual(self.bot.head_manager.game_state['game']['supply_used'], 20)
            self.assertEqual(self.bot.head_manager.game_state['game']['supply_cap'], 30)
            
        asyncio.get_event_loop().run_until_complete(test())

if __name__ == '__main__':
    unittest.main()
