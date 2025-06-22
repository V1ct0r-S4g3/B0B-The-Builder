"""Manager modules for the bot."""

# This file makes the managers directory a Python package
# Import all manager classes here to make them easily accessible
from .terran_economy_manager import TerranEconomyManager
from .protoss_economy_manager import ProtossEconomyManager
from .zerg_economy_manager import ZergEconomyManager
from .military_manager import MilitaryManager
from .head_manager import HeadManager

__all__ = [
    'TerranEconomyManager', 
    'ProtossEconomyManager', 
    'ZergEconomyManager', 
    'MilitaryManager', 
    'HeadManager'
]
