"""
Military Manager for B0B - The Builder Bot

This module provides military management functionality for StarCraft II bots.
It handles army production, build orders, and basic combat control.

TEMPLATE USAGE FOR OTHER BOTS:
1. Copy this file to your bot's managers directory
2. Customize the build_orders dictionary for your strategy
3. Modify the _get_desired_army_composition method for your army composition
4. Adjust the attack logic in _control_army for your combat style

CUSTOMIZATION POINTS:
- build_orders: Define your build order steps
- _get_desired_army_composition: Set your target army composition
- _control_army: Implement your combat logic
- _train_army: Add training for different unit types

EXAMPLE CUSTOMIZATION:
```python
# Add a new build order
self.build_orders['mech_rush'] = [
    (UnitTypeId.SUPPLYDEPOT, 13, "Supply Depot at 13 supply"),
    (UnitTypeId.BARRACKS, 14, "First Barracks"),
    (UnitTypeId.FACTORY, 20, "Factory for mech units"),
    # ... more steps
]

# Modify army composition
def _get_desired_army_composition(self):
    if self.current_strategy == "mech_rush":
        return {
            UnitTypeId.SIEGETANK: 8,
            UnitTypeId.HELLION: 12,
            UnitTypeId.THOR: 2
        }
```

AUTHOR: B0B Template Bot
VERSION: 1.0
"""

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2

class MilitaryManager:
    """Manages the bot's military units, production, and combat logic."""
    
    def __init__(self, ai, head_manager=None, strategy="bio_rush"):
        """Initialize the MilitaryManager with a reference to the main AI object.
        
        Args:
            ai: The main bot AI instance
            head_manager: Reference to the head manager (optional, can be set later)
            strategy: The military strategy to use (default: "bio_rush")
        """
        self.ai = ai
        self.strategy = strategy  # Store the strategy
        self.army_tags = set()  # Track all army units
        self.attack_target = None
        self.attack_started = False
        self.rally_point = None
        self.last_army_management = 0
        self.last_upgrade_check = 0
        self.attack_triggered = False
        self.debug = True  # Enable debug output
        self.head = head_manager  # Reference to head manager
        
        # Tech requirements
        self.tech_buildings = {
            'barracks_tech': False,  # Tech Lab on Barracks
            'factory_tech': False,  # Tech Lab on Factory
            'starport_tech': False  # Reactor on Starport
        }
        
        # Build order definitions
        self.build_orders = {
            'bio_rush': [
                (UnitTypeId.SUPPLYDEPOT, 13, "Supply Depot at 13 supply"),
                (UnitTypeId.BARRACKS, 14, "First Barracks at 14 supply"),
                (UnitTypeId.BARRACKS, 19, "Second Barracks"),
                (UnitTypeId.STARPORT, 22, "Starport for air units"),
                # Delay second refinery until after first attack wave
                (UnitTypeId.BARRACKS, 23, "Third Barracks"),
                (UnitTypeId.ENGINEERINGBAY, 25, "Engineering Bay for upgrades"),
                # Removed Command Center - EconomyManager handles expansion
                # Removed Refinery - EconomyManager handles gas
                # Removed Bunker - EconomyManager handles bunker for gas micro
            ],
            'mech': [
                # Different build order for mech strategy
            ],
            'air': [
                # Different build order for air strategy
            ]
        }
        
        # Current build order state
        self.build_order = []
        self.current_build_index = 0
        self.last_supply_check = 0
        self.last_attack_time = 0
        self.attack_interval = 30  # seconds between attacks
        self.build_order_started = False
        self.last_build_attempt = 0
        self.build_attempts = {}  # Track failed build attempts
        
        # Army management
        self.army_tags = set()  # Track all army units
        self.army_composition = {}  # Track unit counts by type
        self.attack_target = None
        self.attack_started = False
        self.rally_point = None
        self.last_army_management = 0
        
    async def on_start(self):
        """Initialize the military manager."""
        # Skip if already initialized
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        # Set initial rally point towards the enemy
        if self.ai.townhalls:
            self.rally_point = self.ai.townhalls.first.position.towards(
                self.ai.game_info.map_center, 10
            )
        
        # Set initialized flag first to prevent recursive calls
        self._initialized = True
        self.build_order_started = True
        
        if self.debug:
            print("[Military] Initializing military manager")
    
    def _is_first_supply_depot_started(self):
        """Check if the first supply depot has been started."""
        # Check if any supply depot is built or being built
        supply_depots = self.ai.structures(UnitTypeId.SUPPLYDEPOT).ready
        pending_supply_depots = self.ai.already_pending(UnitTypeId.SUPPLYDEPOT)
        return len(supply_depots) > 0 or pending_supply_depots > 0
        
    def _is_first_supply_depot_completed(self):
        """Check if the first supply depot has been completed."""
        try:
            # Handle both real and mock objects
            structures = self.ai.structures(UnitTypeId.SUPPLYDEPOT).ready
            if hasattr(structures, 'amount'):
                return structures.amount > 0
            elif hasattr(structures, '__len__'):
                return len(structures) > 0
            return False
        except Exception as e:
            if self.debug:
                print(f"[Military] Error checking supply depot completion: {e}")
            return False
    
    async def on_step(self):
        """Called every game step to manage military units and production."""
        try:
            # Initialize build order on first step if not already done
            if not hasattr(self, '_build_order_initialized'):
                self._update_build_order(force_update=True)
                if not self.build_order:  # If no build order from head, use default
                    self.build_order = self.build_orders.get('bio_rush', []).copy()
                    if self.debug:
                        print("[Military] Using default build order")
                        print(f"[Military] Build order: {[step[2] for step in self.build_order]}")
                self._build_order_initialized = True
                
            # Check if we need to wait for first supply depot
            if not hasattr(self, '_first_depot_started') and self.current_build_index == 0:
                if not self._is_first_supply_depot_started():
                    if self.debug and self.ai.time % 5 < 0.1:  # Log every 5 seconds
                        print("[Military] Waiting for first supply depot to be started...")
                    return
                self._first_depot_started = True
                if self.debug:
                    print("[Military] First supply depot detected, checking completion...")
                    
            # After depot is started, wait for it to complete
            if hasattr(self, '_first_depot_started') and not hasattr(self, '_first_depot_completed'):
                if self._is_first_supply_depot_completed():
                    self._first_depot_completed = True
                    if self.debug:
                        print("[Military] First supply depot completed, starting build order")
                elif self.debug and self.ai.time % 5 < 0.1:
                    print("[Military] Waiting for first supply depot to complete...")
                    return
                else:
                    return
                    
            # If we don't have a completed depot yet, don't proceed
            if not hasattr(self, '_first_depot_completed') or not self._first_depot_completed:
                return
                
            # Execute build order if we have one
            if self.build_order:
                await self._execute_build_order()
            else:
                if self.debug and self.ai.time % 10 < 0.1:  # Log every 10 seconds
                    print("[Military] No build order available, waiting...")
            
            # Build tech lab if scheduled and barracks is ready
            # REMOVED - No tech needed for simple marine build
            
            # Build reactors on other barracks for increased production
            # REMOVED - No reactors needed for simple marine build
            
            # Continuous production logic - always run regardless of build order status
            await self._continuous_production()
            
            # Train army units
            await self._train_army()
            
            # Manage upgrades
            await self._manage_upgrades()
            
            # Control army units
            await self._control_army()
            
            # Emergency supply depot if we're supply blocked
            if self.ai.supply_left < 2 and self.ai.supply_cap < 200:
                await self._emergency_supply()
                
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in on_step: {e}")
                import traceback
                traceback.print_exc()
    
    def _update_build_order(self, force_update=False):
        """Update the build order based on current game state."""
        try:
            # Use the build order from the build_orders dictionary
            if self.strategy in self.build_orders:
                # Convert the build order format from (unit_type, supply, description) to just unit_type
                self.build_order = [step[0] for step in self.build_orders[self.strategy]]
                if self.debug:
                    print(f"[Military] Using build order for strategy: {self.strategy}")
                    print(f"[Military] Build order: {[step[2] for step in self.build_orders[self.strategy]]}")
            else:
                # Fallback to bio_rush if strategy not found
                self.build_order = [step[0] for step in self.build_orders['bio_rush']]
                if self.debug:
                    print(f"[Military] Strategy {self.strategy} not found, using bio_rush")
            
            self.current_build_index = 0
            self.build_order_completed = False
                    
        except Exception as e:
            if self.debug:
                print(f"[Military] Error updating build order: {e}")
    
    async def _execute_build_order(self):
        """Execute the current build order step by step."""
        try:
            # Check if we've completed the build order
            if self.current_build_index >= len(self.build_order):
                self.build_order_completed = True
                if self.debug:
                    print("[Military] Build order completed")
                return
            
            # Get current build step
            unit_type = self.build_order[self.current_build_index]
            
            # Try to build the structure
            if await self._try_build_structure(unit_type):
                # Move to next step
                self.current_build_index += 1
                if self.debug:
                    print(f"[Military] Completed build step: {unit_type}")
                
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _execute_build_order: {e}")
    
    async def _add_tech_lab_to_first_barracks(self):
        """Add a tech lab to the first barracks for research capabilities."""
        try:
            # Add cooldown to prevent mass flying
            current_time = self.ai.time
            if hasattr(self, '_last_tech_lab_attempt') and current_time - self._last_tech_lab_attempt < 5:
                return False
            self._last_tech_lab_attempt = current_time
            
            # Find the first barracks that doesn't have a tech lab
            for barrack in self.ai.structures(UnitTypeId.BARRACKS).ready:
                if not barrack.has_add_on and self.ai.can_afford(UnitTypeId.BARRACKSTECHLAB):
                    # Check if barracks can lift off and move to make room
                    if barrack.is_ready and not barrack.orders:
                        # Try to lift off and move slightly to make room
                        barrack(AbilityId.LIFT_BARRACKS)
                        if self.debug:
                            print(f"[Military] Lifting barracks at {barrack.position} to make room for tech lab")
                    else:
                        # Try to build tech lab directly
                        barrack(AbilityId.BUILD_TECHLAB_BARRACKS)
                        if self.debug:
                            print("[Military] Adding tech lab to first barracks")
                    return True
            return False
            
        except Exception as e:
            if self.debug:
                print(f"[Military] Error adding tech lab to barracks: {e}")
            return False
    
    async def _try_build_structure(self, unit_type):
        """Try to build a structure with better placement logic."""
        try:
            if self.debug:
                print(f"\n[Military] === Starting _try_build_structure for {unit_type} ===")
                print(f"[Military] Can afford {unit_type}: {self.ai.can_afford(unit_type)}")
                
            # Skip if we don't have a completed supply depot yet (except for the depot itself)
            if unit_type != UnitTypeId.SUPPLYDEPOT:
                if not hasattr(self, '_first_depot_completed') or not self._is_first_supply_depot_completed():
                    if self.debug:
                        print(f"[Military] Waiting for first supply depot to complete before {unit_type}")
                    return False
                
            # Check if we can afford the structure
            if not self.ai.can_afford(unit_type):
                if self.debug:
                    print(f"[Military] Cannot afford {unit_type}")
                return False
                
            # Check if we have a townhall to build near
            if not self.ai.townhalls:
                if self.debug:
                    print("[Military] No townhalls found to build near")
                return False
                
            # Get strategic placement position based on structure type
            placement = await self._get_strategic_placement(unit_type)
                
            if not placement:
                if self.debug:
                    print(f"[Military] Could not find strategic placement for {unit_type}")
                return False
                
            # Find a worker to build the structure
            worker = self.ai.workers.random
            if not worker:
                if self.debug:
                    print("[Military] No workers available to build")
                return False
                
            # Check if we have enough workers before building production
            if unit_type != UnitTypeId.SUPPLYDEPOT:
                worker_count = getattr(self.ai.workers, 'amount', 0)
                if isinstance(worker_count, int) and worker_count < 16:
                    if self.debug:
                        print(f"[Military] Not enough workers ({worker_count}/16) to build {unit_type}")
                    return False
                
            if self.debug:
                print(f"[Military] Building {unit_type} at {placement}")
                
            # Issue build command
            try:
                worker.build(unit_type, placement)
                if self.debug:
                    print(f"[Military] Started building {unit_type} at {placement}")
            except Exception as build_error:
                if self.debug:
                    print(f"[Military] Build command failed: {build_error}")
                return False
            
            # Mark that we've started building the first depot if needed
            if unit_type == UnitTypeId.SUPPLYDEPOT and not hasattr(self, '_first_depot_started'):
                self._first_depot_started = True
                if self.debug:
                    print("[Military] Marked first supply depot as started")
            
            return True
            
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _try_build_structure: {e}")
                import traceback
                traceback.print_exc()
            return False
    
    async def _get_strategic_placement(self, unit_type):
        """Get strategic placement position for different structure types."""
        try:
            townhall = self.ai.townhalls.first
            base_position = townhall.position
            map_center = self.ai.game_info.map_center
            
            # Calculate forward direction (towards map center)
            forward_direction = (map_center - base_position).normalized
            
            if unit_type == UnitTypeId.SUPPLYDEPOT:
                # Place supply depots in a wall formation around the base
                return await self._get_supply_depot_placement(base_position, forward_direction)
                
            elif unit_type == UnitTypeId.BARRACKS:
                # Place barracks in a line formation towards the front
                return await self._get_barracks_placement(base_position, forward_direction)
                
            elif unit_type == UnitTypeId.FACTORY:
                # Place factories in a production area
                return await self._get_factory_placement(base_position, forward_direction)
                
            elif unit_type == UnitTypeId.STARPORT:
                # Place starports in the back of the production area
                return await self._get_starport_placement(base_position, forward_direction)
                
            elif unit_type == UnitTypeId.ENGINEERINGBAY:
                # Place Engineering Bay away from refinery paths
                return await self._get_engineering_bay_placement(base_position, forward_direction)
                
            elif unit_type == UnitTypeId.REFINERY:
                # Refineries should be built on vespene geysers, not strategic placement
                # Let the economy manager handle this
                return None
                
            elif unit_type == UnitTypeId.BUNKER:
                # Bunkers are now handled by the economy manager for gas worker micro
                # Let the economy manager handle this
                return None
                
            else:
                # Default placement near base
                return await self.ai.find_placement(unit_type, near=base_position, placement_step=2)
                
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _get_strategic_placement: {e}")
            return None
    
    async def _get_supply_depot_placement(self, base_position, forward_direction):
        """Get placement for supply depots."""
        try:
            # Simple placement near base
            placement = await self.ai.find_placement(
                UnitTypeId.SUPPLYDEPOT,
                near=base_position,
                placement_step=2,
                max_distance=8
            )
            
            if placement:
                return placement
                
            # Fallback to near base
            return await self.ai.find_placement(UnitTypeId.SUPPLYDEPOT, near=base_position, placement_step=2)
            
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _get_supply_depot_placement: {e}")
            return None
    
    async def _get_barracks_placement(self, base_position, forward_direction):
        """Get placement for barracks."""
        try:
            # Simple placement near base
            placement = await self.ai.find_placement(
                UnitTypeId.BARRACKS,
                near=base_position,
                placement_step=2,
                max_distance=10
            )
            
            if placement and await self.ai.can_place(UnitTypeId.BARRACKS, placement):
                if self.debug:
                    print(f"[Military] Found barracks placement at {placement}")
                return placement
            
            # Fallback: try any valid placement near the base
            fallback_placement = await self.ai.find_placement(
                UnitTypeId.BARRACKS,
                near=base_position,
                placement_step=3,
                max_distance=15
            )
            
            if fallback_placement and await self.ai.can_place(UnitTypeId.BARRACKS, fallback_placement):
                if self.debug:
                    print(f"[Military] Found fallback barracks placement at {fallback_placement}")
                return fallback_placement
                
            return None
            
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _get_barracks_placement: {e}")
            return None
    
    async def _get_factory_placement(self, base_position, forward_direction):
        """Get placement for factories in production area."""
        try:
            # Place factories closer to base
            factory_area = base_position + forward_direction * 4 + Point2((0, 4))  # Reduced distances
            
            placement = await self.ai.find_placement(
                UnitTypeId.FACTORY,
                near=factory_area,
                placement_step=2,
                max_distance=6  # Reduced from 10
            )
            
            if placement:
                return placement
                
            # Fallback to near base
            return await self.ai.find_placement(UnitTypeId.FACTORY, near=base_position, placement_step=2)
            
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _get_factory_placement: {e}")
            return None
    
    async def _get_starport_placement(self, base_position, forward_direction):
        """Get placement for Starports."""
        try:
            # Place starports near barracks but not blocking them
            starport_position = base_position + forward_direction * 8 + Point2((4, 0))
            
            placement = await self.ai.find_placement(
                UnitTypeId.STARPORT,
                near=starport_position,
                placement_step=2,
                max_distance=6
            )
            
            if placement:
                return placement
                
            # Fallback to near base
            return await self.ai.find_placement(UnitTypeId.STARPORT, near=base_position, placement_step=2)
            
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _get_starport_placement: {e}")
            return None
    
    async def _get_engineering_bay_placement(self, base_position, forward_direction):
        """Get placement for Engineering Bay away from refinery paths."""
        try:
            # Place Engineering Bay away from refinery paths
            engineering_bay_position = base_position + forward_direction * 5 + Point2((0, 4))  # Reduced distances
            
            placement = await self.ai.find_placement(
                UnitTypeId.ENGINEERINGBAY,
                near=engineering_bay_position,
                placement_step=2,
                max_distance=6  # Reduced from 10
            )
            
            if placement:
                return placement
                
            # Fallback to near base
            return await self.ai.find_placement(UnitTypeId.ENGINEERINGBAY, near=base_position, placement_step=2)
            
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _get_engineering_bay_placement: {e}")
            return None
    
    async def _train_army(self):
        """Train army units from production facilities."""
        try:
            # Don't queue units if we're supply blocked
            if self.ai.supply_left < 2 and self.ai.supply_cap < 200:
                return
                
            # Get current army composition if not set
            if not hasattr(self, 'army_composition'):
                self._update_army_composition()
            
            # Count current production to avoid overproduction
            production = {}
            for unit in self.ai.units.not_structure.not_ready:
                if unit.type_id in production:
                    production[unit.type_id] += 1
                else:
                    production[unit.type_id] = 1
            
            # Calculate desired composition - SIMPLE: just marines
            desired_comp = self._get_desired_army_composition()
            
            # Train units based on desired composition
            for unit_type, desired_count in desired_comp.items():
                # Check if we need more of this unit type
                current = self.army_composition.get(unit_type, 0) + production.get(unit_type, 0)
                if current >= desired_count:
                    continue
                    
                # Find suitable production facility - ONLY BARRACKS
                if unit_type == UnitTypeId.MARINE:
                    for barrack in self.ai.structures(UnitTypeId.BARRACKS).idle:
                        if self.ai.can_afford(UnitTypeId.MARINE):
                            barrack.train(UnitTypeId.MARINE)
                            if self.debug:
                                print(f"[Military] Training {unit_type}")
                            break
                            
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _train_army: {e}")
    
    def _get_desired_army_composition(self):
        """Get the desired army composition - SIMPLE: just marines."""
        try:
                return {
                UnitTypeId.MARINE: 30  # Just build marines
                }
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _get_desired_army_composition: {e}")
            return {}
    
    async def _manage_upgrades(self):
        """Manage upgrades - REMOVED for simple marine build."""
        # No upgrades needed for simple marine build
        pass
    
    async def _emergency_supply(self):
        """Build emergency supply depots if we're close to being supply blocked."""
        try:
            if (self.ai.supply_left < 3 and 
                self.ai.already_pending(UnitTypeId.SUPPLYDEPOT) == 0 and
                self.ai.can_afford(UnitTypeId.SUPPLYDEPOT)):
                
                # Find a location near the command center
                for cc in self.ai.townhalls.ready:
                    # Get position away from the map center, but not towards natural
                    pos = cc.position.towards(self.ai.game_info.map_center, 8)
                    
                    # Try to find a valid placement location
                    location = await self.ai.find_placement(
                        UnitTypeId.SUPPLYDEPOT,
                        near=pos,
                        placement_step=3,
                        max_distance=12
                    )
                    
                    if location:
                        worker = self.ai.select_build_worker(location)
                        if worker:
                            worker.build(UnitTypeId.SUPPLYDEPOT, location)
                            if self.debug:
                                print("[Military] Building emergency Supply Depot")
                            return True
            return False
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _emergency_supply: {e}")
                import traceback
                traceback.print_exc()
            return False
    
    def _update_army_composition(self):
        """Update the count of each unit type in the army."""
        # Define combat unit types
        combat_units = {
                UnitTypeId.MARINE,
                UnitTypeId.MARAUDER,
                UnitTypeId.MEDIVAC,
                UnitTypeId.SIEGETANK,
                UnitTypeId.SIEGETANKSIEGED,
                UnitTypeId.VIKINGFIGHTER,
                UnitTypeId.VIKINGASSAULT,
                UnitTypeId.LIBERATOR,
                UnitTypeId.GHOST,
                UnitTypeId.RAVEN,
                UnitTypeId.BANSHEE,
                UnitTypeId.THOR,
                UnitTypeId.BATTLECRUISER,
        }
        
        # Update army_tags with all combat units
        self.army_tags = set()
        for unit in self.ai.units.filter(lambda u: u.type_id in combat_units and u.is_ready):
            self.army_tags.add(unit.tag)
        
        # Count army composition
        self.army_composition = {}
        for unit in self.ai.units.filter(
            lambda u: u.type_id in combat_units and u.is_ready
        ):
            self.army_composition[unit.type_id] = self.army_composition.get(unit.type_id, 0) + 1

    async def _control_army(self):
        """Control army units for combat with wave-based attacks."""
        try:
            # Define combat unit types (same as in _update_army_composition)
            combat_units = {
                UnitTypeId.MARINE,
                UnitTypeId.MARAUDER,
                UnitTypeId.MEDIVAC,
                UnitTypeId.SIEGETANK,
                UnitTypeId.SIEGETANKSIEGED,
                UnitTypeId.VIKINGFIGHTER,
                UnitTypeId.VIKINGASSAULT,
                UnitTypeId.LIBERATOR,
                UnitTypeId.GHOST,
                UnitTypeId.RAVEN,
                UnitTypeId.BANSHEE,
                UnitTypeId.THOR,
                UnitTypeId.BATTLECRUISER,
            }
            
            # Update army composition
            self._update_army_composition()
            
            # Get all combat units that are ready (including moving ones)
            army = self.ai.units.filter(
                lambda u: u.type_id in combat_units and u.is_ready 
            )
            
            # If no army, nothing to do
            if not army:
                if self.debug and self.ai.time % 10 < 0.1:
                    print("[Military] No army units available")
                return
                
            # Set rally point if not set
            if not self.rally_point and self.ai.townhalls:
                self.rally_point = self.ai.townhalls.first.position.towards(
                    self.ai.game_info.map_center, 15
                )
            
            # Find enemy units and structures
            enemies = self.ai.enemy_units | self.ai.enemy_structures
            
            # Wave-based attack logic
            army_size = army.amount
            current_time = self.ai.time
            
            # Initialize wave timing if not set
            if not hasattr(self, 'last_wave_time'):
                self.last_wave_time = 0
                self.wave_size_threshold = 6  # Attack with 6+ units per wave
                self.wave_cooldown = 10  # Reduced cooldown for more frequent attacks
            
            # Debug output every 10 seconds
            if self.debug and current_time % 10 < 0.1:
                print(f"[Military] Army control - Size: {army_size}, Threshold: {self.wave_size_threshold}, Cooldown: {current_time - self.last_wave_time:.1f}s, Enemies: {len(enemies)}")
            
            # Check if we should launch a new wave
            should_attack = (
                army_size >= self.wave_size_threshold and 
                current_time - self.last_wave_time >= self.wave_cooldown
            )
            
            # If we have enough units and cooldown is ready, launch wave
            if should_attack:
                self.attack_started = True
                self.last_wave_time = current_time
                
                # Find attack target - prioritize enemy structures for offensive attacks
                if self.ai.enemy_structures:
                    # Attack enemy base structures (offensive)
                    target = self.ai.enemy_structures.first
                    attack_type = "OFFENSIVE"
                elif enemies and army_size >= 12:  # Only attack nearby enemies if we have a large army
                    # Attack nearby enemies (defensive/cleanup)
                    target = enemies.closest_to(army.first)
                    attack_type = "DEFENSIVE"
                else:
                    # Attack towards enemy base location if no enemies visible
                    # Try to find enemy base location or use map center
                    if hasattr(self.ai, 'enemy_start_locations') and self.ai.enemy_start_locations:
                        target = self.ai.enemy_start_locations[0]
                    else:
                        target = self.ai.game_info.map_center
                    attack_type = "SCOUTING"
                
                # Command all units to attack the target
                for unit in army:
                    # Use attack command for combat units
                    unit.attack(target)
                    
                if self.debug:
                    print(f"[Military] {attack_type} ATTACK with {army_size} units to {target}")
                    
            # If not attacking, gather at rally point
            elif self.rally_point:
                for unit in army:
                    unit.move(self.rally_point)
                if self.debug and current_time % 15 < 0.1:
                    print(f"[Military] Gathering {army_size} units at rally point")
                    
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _control_army: {e}")
                import traceback
                traceback.print_exc()

    async def _continuous_production(self):
        """Continuous production logic that runs regardless of build order status."""
        try:
            current_time = self.ai.time
            
            # Only run every few seconds to avoid spam
            if current_time - getattr(self, '_last_continuous_production', 0) < 5:
                return
            self._last_continuous_production = current_time
            
            # Build basic army structures if we don't have them
            await self._ensure_basic_structures()
            
            # Build additional production facilities based on economy
            await self._expand_production()
            
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in continuous production: {e}")
    
    async def _ensure_basic_structures(self):
        """Ensure we have basic army production structures."""
        try:
            # Only run this during build order execution, not after completion
            if hasattr(self, 'build_order_completed') and self.build_order_completed:
                return
                
            # Build barracks if we don't have any
            if not self.ai.structures(UnitTypeId.BARRACKS).ready:
                if self.debug:
                    print("[Military] Building first barracks")
                await self._try_build_structure(UnitTypeId.BARRACKS)
                return
            
            # Build starport if we don't have one and have barracks
            # Check for both ready and pending starports
            existing_starports = (self.ai.structures(UnitTypeId.STARPORT).ready.amount + 
                                self.ai.already_pending(UnitTypeId.STARPORT))
            
            if self.debug and self.ai.time % 10 < 0.1:  # Log every 10 seconds
                print(f"[Military] Starport check - Ready: {self.ai.structures(UnitTypeId.STARPORT).ready.amount}, Pending: {self.ai.already_pending(UnitTypeId.STARPORT)}, Total: {existing_starports}")
            
            if (self.ai.structures(UnitTypeId.BARRACKS).ready.amount >= 1 and 
                existing_starports == 0):
                if self.debug:
                    print("[Military] Building first starport")
                await self._try_build_structure(UnitTypeId.STARPORT)
                return
                
        except Exception as e:
            if self.debug:
                print(f"[Military] Error ensuring basic structures: {e}")
    
    async def _expand_production(self):
        """Build additional production facilities based on economy."""
        try:
            # Get current structure counts
            barracks_count = self.ai.structures(UnitTypeId.BARRACKS).ready.amount
            starport_count = self.ai.structures(UnitTypeId.STARPORT).ready.amount
            worker_count = self.ai.workers.amount
            
            # Set rally points for all barracks
            await self._set_barracks_rally_points()
            
            # Build more barracks if we have enough workers and minerals (MAX 3 BARRACKS)
            if (worker_count >= 20 and barracks_count < 3 and 
                self.ai.minerals >= 150):
                if self.debug:
                    print(f"[Military] Building additional barracks ({barracks_count} -> {barracks_count + 1})")
                await self._try_build_structure(UnitTypeId.BARRACKS)
                return
                
        except Exception as e:
            if self.debug:
                print(f"[Military] Error expanding production: {e}")
    
    async def _set_barracks_rally_points(self):
        """Set rally points for all barracks so trained units know where to go."""
        try:
            # Calculate rally point towards the enemy (forward position)
            if self.ai.townhalls:
                base_position = self.ai.townhalls.first.position
                map_center = self.ai.game_info.map_center
                
                # Rally point is towards the map center from our base, at a reasonable distance
                # This ensures units gather in a forward position for attacks
                rally_point = base_position.towards(map_center, 10)
                
                # Set rally point for all barracks
                for barrack in self.ai.structures(UnitTypeId.BARRACKS).ready:
                    if not hasattr(barrack, '_rally_set') or not barrack._rally_set:
                        barrack(AbilityId.RALLY_BUILDING, rally_point)
                        barrack._rally_set = True
                        if self.debug:
                            print(f"[Military] Set rally point for barracks at {rally_point}")
                
        except Exception as e:
            if self.debug:
                print(f"[Military] Error setting barracks rally points: {e}")

    async def _add_reactors_to_barracks(self):
        """Add reactors to barracks for increased production."""
        try:
            # Add cooldown to prevent all barracks from flying at once
            current_time = self.ai.time
            if hasattr(self, '_last_reactor_attempt') and current_time - self._last_reactor_attempt < 3:
                return
            self._last_reactor_attempt = current_time
            
            # Find barracks without reactors
            barracks_without_reactors = self.ai.structures(UnitTypeId.BARRACKS).filter(lambda b: not b.has_add_on)
            
            # Only work on one barracks at a time to prevent mass flying
            for barrack in barracks_without_reactors:
                if self.ai.can_afford(UnitTypeId.REACTOR):
                    # Try to build reactor directly first (since we placed barracks with space)
                    if barrack.is_ready and not barrack.orders:
                        barrack.build(UnitTypeId.REACTOR)
                        if self.debug:
                            print(f"[Military] Building reactor on barracks at {barrack.position}")
                        break  # Only work on one barracks at a time
                    else:
                        # If direct build fails, try lifting and moving
                        if barrack.is_ready and not barrack.orders:
                            barrack(AbilityId.LIFT_BARRACKS)
                            if self.debug:
                                print(f"[Military] Lifting barracks at {barrack.position} to make room for reactor")
                        break  # Only work on one barracks at a time
            
            # Handle flying barracks - land them and build add-ons
            flying_barracks = self.ai.structures(UnitTypeId.BARRACKSFLYING)
            for flying_barrack in flying_barracks:
                if not flying_barrack.orders:  # Not already doing something
                    # Find a good landing spot near the original position
                    landing_position = flying_barrack.position
                    placement = await self.ai.find_placement(
                        UnitTypeId.BARRACKS,
                        near=landing_position,
                        placement_step=1,
                        max_distance=3
                    )
                    
                    if placement:
                        flying_barrack(AbilityId.LAND_BARRACKS, placement)
                        if self.debug:
                            print(f"[Military] Landing flying barracks at {placement}")
                    else:
                        # Fallback - land at current position
                        flying_barrack(AbilityId.LAND_BARRACKS, flying_barrack.position)
                        if self.debug:
                            print(f"[Military] Landing flying barracks at current position")
                    
        except Exception as e:
            if self.debug:
                print(f"[Military] Error adding reactors to barracks: {e}")

    async def _attack_with_army(self):
        """Send army to attack enemy base."""
        try:
            # Define combat unit types (same as in _update_army_composition)
            combat_units = {
                UnitTypeId.MARINE,
                UnitTypeId.MARAUDER,
                UnitTypeId.MEDIVAC,
                UnitTypeId.SIEGETANK,
                UnitTypeId.SIEGETANKSIEGED,
                UnitTypeId.VIKINGFIGHTER,
                UnitTypeId.VIKINGASSAULT,
                UnitTypeId.LIBERATOR,
                UnitTypeId.GHOST,
                UnitTypeId.RAVEN,
                UnitTypeId.BANSHEE,
                UnitTypeId.THOR,
                UnitTypeId.BATTLECRUISER,
            }
            
            # Get all combat units
            army_units = self.ai.units.filter(
                lambda unit: unit.type_id in combat_units
            ).ready
            
            if not army_units:
                if self.debug and self.ai.time % 10 < 0.1:
                    print("[Military] No combat units available for attack")
                return
            
            # Find enemy base
            enemy_base = None
            if self.ai.enemy_start_locations:
                enemy_base = self.ai.enemy_start_locations[0]
            else:
                # Fallback: attack towards center of map
                enemy_base = self.ai.game_info.map_center
            
            if not enemy_base:
                if self.debug:
                    print("[Military] No enemy base found for attack")
                return
            
            # SUPER AGGRESSIVE: Attack with 6+ marines in squads
            if len(army_units) >= 6:  # Attack with 6+ marines
                # Group all units and attack
                for unit in army_units:
                    unit.attack(enemy_base)
                
                if self.debug and self.ai.time % 5 < 0.1:
                    print(f"[Military] ATTACKING with {len(army_units)} marines in squad!")
                    print(f"[Military] Target: {enemy_base}")
                    
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _attack_with_army: {e}")
                import traceback
                traceback.print_exc()
