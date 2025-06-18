"""Managers package for organizing different aspects of the bot's behavior."""

# This file makes the managers directory a Python package
# Import all manager classes here to make them easily accessible
from .economy_manager import EconomyManager
from .military_manager import MilitaryManager

__all__ = ['EconomyManager', 'MilitaryManager']
