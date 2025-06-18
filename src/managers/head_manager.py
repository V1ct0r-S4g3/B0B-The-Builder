"""
Head Manager - The central coordinator for all bot managers.

This module contains the HeadManager class that coordinates between different
managers (Economy, Military, etc.) to make high-level strategic decisions.
"""
import logging
from typing import Dict, Any, Optional, List, Type, Union
from sc2.data import Race, Result, ActionResult
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.position import Point2

# Configure logger
logger = logging.getLogger('B0B.HeadManager')

class HeadManager:
    """
    The HeadManager is the central coordination point for all bot managers.
    It makes high-level strategic decisions and coordinates between different
    specialized managers (Economy, Military, etc.).
    """
    
    def __init__(self, ai, strategy: str = "bio_rush", debug: bool = True):
        """Initialize the HeadManager with a reference to the main AI object.
        
        Args:
            ai: The main bot AI instance
            strategy: The initial strategy to use (default: "bio_rush")
            debug: Whether to enable debug output (default: True)
        """
        self.ai = ai
        self.managers = {}  # type: Dict[str, Any]
        self.strategy = strategy
        self.debug = debug
        self._initialized = False
        self._last_step_time = 0.0
        self._step_count = 0
        
        # Game state tracking
        self.game_state = {
            'economy': {
                'mineral_income': 0,
                'gas_income': 0,
                'worker_count': 0,
                'base_count': 0,
                'saturation': 0.0,  # 0-1.0
                'minerals': 0,
                'vespene': 0,
                'mineral_fields': 0,
                'vespene_geysers': 0,
                'active_geysers': 0
            },
            'military': {
                'army_supply': 0,
                'tech_level': 1,  # 1-3
                'upgrades': [],
                'army_composition': {},
                'combat_units': 0,
                'army_value': {'minerals': 0, 'vespene': 0}
            },
            'production': {
                'production_structures': {},
                'production_queue': [],
                'tech_buildings': {}
            },
            'enemy': {
                'race': None,
                'strategy': None,
                'aggression': 0.0,  # 0-1.0
                'units': {},
                'structures': {},
                'last_seen': 0.0
            },
            'game': {
                'time': 0,
                'supply_used': 0,
                'supply_cap': 0,
                'supply_blocked': False,
                'is_competitive': True,
                'map_name': '',
                'game_loop': 0
            }
        }
        self.strategies = {
            'bio_rush': {
                'description': 'Marine/Marauder/Medivac composition with fast expand',
                'priority': ['economy', 'military'],
                'conditions': {
                    'expand_when': {'minerals': 400, 'bases': 1},
                    'attack_when': {'supply': 30, 'upgrades': ['Stimpack']}
                }
            },
            'mech': {
                'description': 'Siege Tank/Hellion composition',
                'priority': ['economy', 'tech', 'military'],
                'conditions': {
                    'expand_when': {'minerals': 500, 'bases': 1},
                    'attack_when': {'supply': 40, 'upgrades': []}
                }
            },
            'air': {
                'description': 'Viking/Banshee/Liberator composition',
                'priority': ['tech', 'economy', 'military'],
                'conditions': {
                    'expand_when': {'minerals': 600, 'bases': 2},
                    'attack_when': {'supply': 50, 'upgrades': []}
                }
            }
        }
    
    def register_manager(self, name: str, manager) -> None:
        """Register a manager with the HeadManager.
        
        Args:
            name: The name to register the manager under (e.g., 'economy', 'military')
            manager: The manager instance to register
        """
        self.managers[name] = manager
        
        # Set the head reference on the manager
        if hasattr(manager, 'head'):
            if manager.head is None:  # Only set if not already set
                manager.head = self
            elif manager.head != self and self.debug:
                print(f"[Head] Warning: Manager {name} already has a different head manager reference")
        
        # If this is the military manager, make sure it has our strategy
        if name == 'military' and hasattr(manager, 'strategy'):
            manager.strategy = self.strategy
            
        logger.debug(f"Registered manager: {name}")
    
    async def on_start(self) -> None:
        """Initialize all registered managers and set up initial state."""
        try:
            logger.info(f"Initializing HeadManager with strategy: {self.strategy}")
            
            # Initialize game state
            self._update_game_state()
            
            # Initialize all managers
            for name, manager in self.managers.items():
                try:
                    if hasattr(manager, 'on_start'):
                        if not getattr(manager, '_initialized', False):
                            logger.debug(f"Initializing {name} manager")
                            await manager.on_start()
                            setattr(manager, '_initialized', True)
                            logger.info(f"{name.capitalize()} manager initialized")
                except Exception as e:
                    # Mark as initialized to prevent repeated failed attempts
                    setattr(manager, '_initialized', True)
                    logger.error(f"Failed to initialize {name} manager: {str(e)}", exc_info=True)
            
            self._initialized = True
            logger.info("HeadManager initialization complete")
            
        except Exception as e:
            logger.critical(f"Fatal error in HeadManager.on_start: {str(e)}", exc_info=True)
            raise
    
    async def on_step(self) -> None:
        """Called every game step to update state and coordinate managers."""
        if not self._initialized:
            logger.warning("HeadManager not initialized, skipping step")
            return
            
        self._step_count += 1
        current_time = self.ai.time
        
        try:
            # Update game state first
            self._update_game_state()
            
            # Calculate time delta since last step
            time_delta = current_time - self._last_step_time
            self._last_step_time = current_time
            
            # Log performance periodically
            if self._step_count % 100 == 0:
                logger.debug(f"Step {self._step_count} at {current_time:.1f}s")
            
            # Execute manager steps in priority order
            for name, manager in sorted(self.managers.items(), 
                                     key=lambda x: getattr(x[1], 'priority', 10)):
                step_start = self.ai.time
                try:
                    if hasattr(manager, 'on_step'):
                        await manager.on_step()
                        
                    # Log slow steps
                    step_time = self.ai.time - step_start
                    if step_time > 0.1:  # 100ms threshold
                        logger.warning(f"Slow step in {name}: {step_time:.3f}s")
                        
                except Exception as e:
                    logger.error(f"Error in {name}.on_step: {str(e)}", exc_info=True)
            
        except Exception as e:
            logger.critical(f"Fatal error in HeadManager.on_step: {str(e)}", exc_info=True)
            # Try to recover by reinitializing if possible
            if not self._handle_step_error(e):
                raise
    
    async def on_end(self, result: Result) -> None:
        """Called when the game ends.
        
        Args:
            result: The game result (Result.Victory, Result.Defeat, etc.)
        """
        if not self._initialized:
            logger.warning("HeadManager not initialized, skipping on_end")
            return
            
        logger.info(f"Game ended with result: {result}")
        
        try:
            # Notify all managers of game end in reverse order of initialization
            for name, manager in reversed(list(self.managers.items())):
                try:
                    if hasattr(manager, 'on_end'):
                        logger.debug(f"Calling on_end for {name} manager")
                        await manager.on_end(result)
                except Exception as e:
                    logger.error(f"Error in {name}.on_end: {str(e)}", exc_info=True)
            
            # Log final game state
            self._log_game_summary(result)
            
        except Exception as e:
            logger.critical(f"Fatal error in HeadManager.on_end: {str(e)}", exc_info=True)
        finally:
            # Clean up resources
            self._cleanup()
    
    def _handle_step_error(self, error: Exception) -> bool:
        """Handle errors that occur during game steps.
        
        Args:
            error: The exception that occurred
            
        Returns:
            bool: True if the error was handled, False if it should be re-raised
        """
        logger.error(f"Handling step error: {str(error)}", exc_info=True)
        
        # Add custom error handling logic here
        # For now, just log the error and continue
        return True
    
    def _log_game_summary(self, result: Result) -> None:
        """Log a summary of the game."""
        if not hasattr(self, 'ai') or not hasattr(self.ai, 'state'):
            return
            
        try:
            # Log basic game info
            duration = self.ai.state.game_loop / 22.4  # Convert to seconds
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            
            logger.info("=" * 40)
            logger.info(f"GAME SUMMARY (Result: {result} | Duration: {minutes}:{seconds:02d})")
            logger.info("=" * 40)
            
            # Economy summary
            if hasattr(self.ai, 'state') and hasattr(self.ai.state, 'score'):
                score = self.ai.state.score
                logger.info(f"[ECONOMY] Workers: {self.ai.workers.amount} | "
                          f"Minerals: {self.ai.minerals} | Vespene: {self.ai.vespene}")
                logger.info(f"[ECONOMY] Collection Rate: {score.collection_rate_minerals + score.collection_rate_vespene}/min")
            
            # Military summary
            if hasattr(self.ai, 'units') and hasattr(self.ai, 'enemy_units'):
                logger.info(f"[MILITARY] Army Supply: {self.ai.supply_army:.1f}/200 | "
                          f"Enemy Army Supply: {self.ai.enemy_units.amount if hasattr(self.ai, 'enemy_units') else 0}")
            
            # Production summary
            if hasattr(self.ai, 'structures'):
                prod_buildings = self.ai.structures.filter(
                    lambda unit: unit.type_id in {
                        UnitTypeId.BARRACKS,
                        UnitTypeId.FACTORY,
                        UnitTypeId.STARPORT,
                        UnitTypeId.STARPORTTECHLAB,
                        UnitTypeId.STARPORTREACTOR
                    }
                )
                logger.info(f"[PRODUCTION] Structures: {prod_buildings.amount}")
            
            logger.info("-" * 40)
            
        except Exception as e:
            logger.error(f"Error generating game summary: {str(e)}", exc_info=True)
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            # Clear references to prevent memory leaks
            for name in list(self.managers.keys()):
                if hasattr(self.managers[name], '_initialized'):
                    setattr(self.managers[name], '_initialized', False)
            
            # Clear manager references
            self.managers.clear()
            
            # Reset state
            self._initialized = False
            self._step_count = 0
            
            logger.info("HeadManager cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}", exc_info=True)
    
    def _update_game_state(self) -> None:
        """Update the internal game state based on the current game state.
        
        This method is called every game step to keep the internal state synchronized
        with the actual game state. It updates all relevant game metrics that are
        used for decision making by the managers.
        """
        if not hasattr(self, 'ai') or not hasattr(self.ai, 'state'):
            logger.warning("Cannot update game state: AI or state not available")
            return
            
        try:
            # Update basic game state
            self.game_state['game'].update({
                'time': self.ai.time,
                'supply_used': self.ai.supply_used,
                'supply_cap': self.ai.supply_cap,
                'supply_blocked': self.ai.supply_cap - self.ai.supply_used < 2,
                'game_loop': self.ai.state.game_loop,
                'map_name': getattr(self.ai.game_info, 'map_name', 'unknown')
            })
            
            # Update economy state
            if hasattr(self.ai, 'state') and hasattr(self.ai.state, 'score'):
                self.game_state['economy'].update({
                    'mineral_income': self.ai.state.score.collection_rate_minerals,
                    'gas_income': self.ai.state.score.collection_rate_vespene,
                    'minerals': self.ai.minerals,
                    'vespene': self.ai.vespene,
                    'mineral_fields': len(self.ai.mineral_field),
                    'vespene_geysers': len(self.ai.vespene_geyser),
                    'active_geysers': len([g for g in self.ai.gas_buildings if g.vespene_contents > 0])
                })
            
            # Update worker and base counts
            self.game_state['economy'].update({
                'worker_count': self.ai.workers.amount,
                'base_count': self.ai.townhalls.amount,
                'saturation': self._calculate_saturation()
            })
            
            # Update military state
            self.game_state['military'].update({
                'army_supply': self.ai.supply_army,
                'tech_level': self._calculate_tech_level(),
                'combat_units': len(self.ai.units.of_type({
                    UnitTypeId.MARINE, UnitTypeId.MARAUDER, UnitTypeId.REAPER,
                    UnitTypeId.SIEGETANK, UnitTypeId.MEDIVAC, UnitTypeId.VIKINGFIGHTER
                })),
                'army_value': self._calculate_army_value()
            })
            
            # Update production state
            self._update_production_state()
            
            # Update enemy state if we have visibility
            self._update_enemy_state()
            
            # Log state periodically
            if self._step_count % 100 == 0:
                self._log_state_summary()
                
        except Exception as e:
            logger.error(f"Error updating game state: {str(e)}", exc_info=True)
    
    def _update_production_state(self) -> None:
        """Update the production-related state."""
        try:
            if not hasattr(self.ai, 'structures'):
                return
                
            # Count production structures
            prod_structures = {}
            for structure_type in [
                UnitTypeId.BARRACKS, UnitTypeId.FACTORY, UnitTypeId.STARPORT,
                UnitTypeId.STARPORTTECHLAB, UnitTypeId.STARPORTREACTOR
            ]:
                count = self.ai.structures.of_type(structure_type).amount
                if count > 0:
                    prod_structures[str(structure_type)] = count
            
            self.game_state['production']['production_structures'] = prod_structures
            
            # Update production queue (simplified)
            queue = []
            for structure in self.ai.structures:
                if hasattr(structure, 'orders') and structure.orders:
                    for order in structure.orders:
                        queue.append({
                            'structure': str(structure.type_id),
                            'ability': str(order.ability),
                            'progress': order.progress
                        })
            
            self.game_state['production']['production_queue'] = queue
            
        except Exception as e:
            logger.error(f"Error updating production state: {str(e)}", exc_info=True)
    
    def _update_enemy_state(self) -> None:
        """Update the enemy-related state."""
        try:
            if not hasattr(self.ai, 'enemy_units'):
                return
                
            # Update enemy units
            enemy_units = {}
            for unit in self.ai.enemy_units:
                unit_type = str(unit.type_id)
                enemy_units[unit_type] = enemy_units.get(unit_type, 0) + 1
            
            self.game_state['enemy'].update({
                'units': enemy_units,
                'last_seen': self.ai.time,
                'race': str(self.ai.enemy_race) if hasattr(self.ai, 'enemy_race') else None
            })
            
            # Update enemy structures if visible
            if hasattr(self.ai, 'enemy_structures'):
                enemy_structures = {}
                for structure in self.ai.enemy_structures:
                    struct_type = str(structure.type_id)
                    enemy_structures[struct_type] = enemy_structures.get(struct_type, 0) + 1
                
                self.game_state['enemy']['structures'] = enemy_structures
                
        except Exception as e:
            logger.error(f"Error updating enemy state: {str(e)}", exc_info=True)
    
    def _calculate_army_value(self) -> Dict[str, int]:
        """Calculate the total mineral and vespene value of the current army."""
        total_minerals = 0
        total_vespene = 0
        
        try:
            if hasattr(self.ai, 'units'):
                for unit in self.ai.units:
                    # Get unit cost from game data
                    unit_type = unit.type_id
                    if unit_type in self.ai.game_data.units:
                        unit_data = self.ai.game_data.units[unit_type]
                        total_minerals += unit_data.cost.minerals
                        total_vespene += unit_data.cost.vespene
                        
        except Exception as e:
            logger.error(f"Error calculating army value: {str(e)}", exc_info=True)
            
        return {'minerals': total_minerals, 'vespene': total_vespene}
    
    def _log_state_summary(self) -> None:
        """Log a summary of the current game state."""
        try:
            state = self.game_state
            logger.debug("-" * 40)
            logger.debug(f"[GAME] Time: {state['game']['time']:.1f}s | "
                       f"Supply: {state['game']['supply_used']}/{state['game']['supply_cap']} | "
                       f"Blocked: {state['game']['supply_blocked']}")
            
            logger.debug(f"[ECON] Min: {state['economy']['minerals']} (+{state['economy']['mineral_income']}/min) | "
                       f"Gas: {state['economy']['vespene']} (+{state['economy']['gas_income']}/min) | "
                       f"Workers: {state['economy']['worker_count']}")
            
            logger.debug(f"[MIL] Army: {state['military']['army_supply']} | "
                       f"Tech: {state['military']['tech_level']} | "
                       f"Combat Units: {state['military']['combat_units']}")
            
            if state['enemy']['units']:
                enemy_units = ", ".join([f"{k}:{v}" for k, v in state['enemy']['units'].items()])
                logger.debug(f"[ENEMY] Units: {enemy_units}")
                
        except Exception as e:
            logger.error(f"Error logging state summary: {str(e)}", exc_info=True)
    
    def _calculate_tech_level(self) -> int:
        """Calculate the current tech level (1-3)."""
        tech_level = 1
        
        # Safely get structures with error handling
        try:
            if not hasattr(self.ai, 'structures') or not callable(self.ai.structures):
                return tech_level
                
            structures = self.ai.structures
            
            # Check for tech level 3 structures first (highest priority)
            if (hasattr(structures(UnitTypeId.FUSIONCORE), 'exists') and 
                structures(UnitTypeId.FUSIONCORE).exists):
                return 3
                
            # Check for multiple armories (tech level 3)
            if (hasattr(structures(UnitTypeId.ARMORY).ready, 'amount') and 
                structures(UnitTypeId.ARMORY).ready.amount >= 2):
                return 3
                
            # Check for tech level 2 structures
            for structure_type in [UnitTypeId.TECHLAB, UnitTypeId.ENGINEERINGBAY, UnitTypeId.ARMORY]:
                if (hasattr(structures(structure_type), 'exists') and 
                    structures(structure_type).exists):
                    return 2
                    
        except Exception as e:
            if self.debug:
                print(f"[WARNING] Error calculating tech level: {str(e)}")
                
        return tech_level
    
    def _get_army_composition(self) -> Dict[UnitTypeId, int]:
        """Get the current army composition."""
        composition = {}
        combat_units = [
            UnitTypeId.MARINE, UnitTypeId.MARAUDER, UnitTypeId.REAPER,
            UnitTypeId.GHOST, UnitTypeId.HELLION, UnitTypeId.HELLIONTANK,
            UnitTypeId.SIEGETANK, UnitTypeId.CYCLONE, UnitTypeId.WIDOWMINE,
            UnitTypeId.THOR, UnitTypeId.VIKINGFIGHTER, UnitTypeId.VIKINGASSAULT,
            UnitTypeId.MEDIVAC, UnitTypeId.LIBERATOR, UnitTypeId.BANSHEE,
            UnitTypeId.RAVEN, UnitTypeId.BATTLECRUISER
        ]
        
        for unit_type in combat_units:
            count = self.ai.units(unit_type).amount
            if count > 0:
                composition[unit_type] = count
                
        return composition
    
    def get_strategy_condition(self, condition_name: str) -> Any:
        """Get a strategy condition by name."""
        strategy = self.strategies.get(self.strategy, {})
        return strategy.get('conditions', {}).get(condition_name, {})
    
    def set_strategy(self, strategy_name: str) -> bool:
        """Set the current strategy."""
        if strategy_name in self.strategies:
            old_strategy = self.strategy
            self.strategy = strategy_name
            print(f"[Head] Strategy changed from {old_strategy} to {strategy_name}")
            return True
        return False
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current game state."""
        return self.game_state
    
    def should_expand(self) -> bool:
        """Determine if we should expand based on current strategy and game state."""
        conditions = self.get_strategy_condition('expand_when')
        if not conditions:
            return False
            
        # Check if we have enough bases
        current_bases = self.game_state['economy']['base_count']
        if current_bases <= conditions.get('bases', 2):
            return True
            
        # Check if we have enough resources
        if self.ai.minerals >= conditions.get('minerals', 400):
            return True
            
        return False
    
    def should_attack(self) -> bool:
        """Determine if we should attack based on current strategy and game state."""
        conditions = self.get_strategy_condition('attack_when')
        if not conditions:
            return False
            
        # Check supply requirement
        if self.game_state['game']['supply_used'] < conditions.get('supply', 30):
            return False
            
        # Check upgrade requirements
        required_upgrades = conditions.get('upgrades', [])
        if required_upgrades and not all(upgrade in self.game_state['military']['upgrades'] 
                                       for upgrade in required_upgrades):
            return False
            
        return True
