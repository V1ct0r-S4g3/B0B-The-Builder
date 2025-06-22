"""
Configuration system for B0B - The Builder Bot

This module provides a centralized configuration system that allows
easy customization of bot behavior without modifying code.

USAGE FOR OTHER BOTS:
1. Copy this config file to your bot
2. Modify the values to match your strategy
3. Import and use in your managers

EXAMPLE:
from config.config import BotConfig
config = BotConfig()
print(config.military.build_orders['bio_rush'])
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from sc2.ids.unit_typeid import UnitTypeId


@dataclass
class EconomyConfig:
    """Economy-related configuration settings."""
    
    # Worker management
    max_workers: int = 80
    gas_workers_per_refinery: int = 6
    min_time_before_expand: float = 120.0  # seconds
    
    # Supply management
    supply_buffer: int = 5
    emergency_supply_threshold: int = 2
    
    # Resource collection
    target_mineral_workers: int = 16
    target_gas_workers: int = 6


@dataclass
class MilitaryConfig:
    """Military-related configuration settings."""
    
    # Build orders - easily customizable
    build_orders: Dict[str, List[Tuple]] = None
    
    # Army composition targets
    army_compositions: Dict[str, Dict] = None
    
    # Combat settings
    attack_army_size: int = 15
    rally_distance: int = 10
    
    # Production settings
    max_barracks: int = 3
    max_factories: int = 2
    max_starports: int = 1
    
    def __post_init__(self):
        """Initialize default values if not provided."""
        if self.build_orders is None:
            self.build_orders = {
                'bio_rush': [
                    (UnitTypeId.SUPPLYDEPOT, 13, "Supply Depot at 13 supply"),
                    (UnitTypeId.BARRACKS, 14, "First Barracks at 14 supply"),
                    (UnitTypeId.REFINERY, 15, "First Refinery"),
                    (UnitTypeId.BUNKER, 17, "Bunker for defense"),
                    (UnitTypeId.BARRACKS, 19, "Second Barracks"),
                    (UnitTypeId.STARPORT, 22, "Starport for air units"),
                    (UnitTypeId.BARRACKS, 23, "Third Barracks"),
                ],
                'mech_rush': [
                    (UnitTypeId.SUPPLYDEPOT, 13, "Supply Depot at 13 supply"),
                    (UnitTypeId.BARRACKS, 14, "First Barracks"),
                    (UnitTypeId.FACTORY, 20, "Factory for mech units"),
                    (UnitTypeId.REFINERY, 15, "First Refinery"),
                    (UnitTypeId.BARRACKS, 19, "Second Barracks"),
                    (UnitTypeId.FACTORY, 25, "Second Factory"),
                ]
            }
        
        if self.army_compositions is None:
            self.army_compositions = {
                'bio_rush': {
                    UnitTypeId.MARINE: 20,
                    UnitTypeId.MARAUDER: 5,
                    UnitTypeId.MEDIVAC: 2,
                },
                'mech_rush': {
                    UnitTypeId.SIEGETANK: 8,
                    UnitTypeId.HELLION: 12,
                    UnitTypeId.THOR: 2,
                }
            }


@dataclass
class HeadConfig:
    """Head manager configuration settings."""
    
    # Manager priorities (higher = more important)
    economy_priority: int = 3
    military_priority: int = 2
    
    # Debug settings
    enable_debug: bool = True
    log_level: str = "INFO"
    
    # Performance settings
    step_interval: float = 0.1  # seconds


@dataclass
class BotConfig:
    """Main bot configuration class."""
    
    # Bot identity
    bot_name: str = "B0B - The Builder"
    bot_version: str = "1.0"
    
    # Strategy selection
    default_strategy: str = "bio_rush"
    
    # Sub-configurations
    economy: EconomyConfig = None
    military: MilitaryConfig = None
    head: HeadConfig = None
    
    def __post_init__(self):
        """Initialize sub-configurations if not provided."""
        if self.economy is None:
            self.economy = EconomyConfig()
        if self.military is None:
            self.military = MilitaryConfig()
        if self.head is None:
            self.head = HeadConfig()
    
    def get_build_order(self, strategy: str = None) -> List[Tuple]:
        """Get build order for specified strategy."""
        if strategy is None:
            strategy = self.default_strategy
        return self.military.build_orders.get(strategy, [])
    
    def get_army_composition(self, strategy: str = None) -> Dict:
        """Get army composition for specified strategy."""
        if strategy is None:
            strategy = self.default_strategy
        return self.military.army_compositions.get(strategy, {})
    
    def add_build_order(self, name: str, build_order: List[Tuple]):
        """Add a new build order."""
        self.military.build_orders[name] = build_order
    
    def add_army_composition(self, name: str, composition: Dict):
        """Add a new army composition."""
        self.military.army_compositions[name] = composition


# Global configuration instance
config = BotConfig()
