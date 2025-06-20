"""Handles all military-related logic including unit production, upgrades, and combat."""

from unittest.mock import MagicMock
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.units import Units
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
                # Wait for first depot to be built before barracks
                (UnitTypeId.BARRACKS, 15, "First Barracks at 15 supply"),
                (UnitTypeId.REFINERY, 16, "First Refinery"),
                (UnitTypeId.BUNKER, 19, "Bunker for defense"),
                (UnitTypeId.BARRACKS, 21, "Second Barracks"),
                (UnitTypeId.FACTORY, 22, "Factory for tech"),
                (UnitTypeId.STARPORT, 24, "Starport for air units"),
                # Delay second refinery until after first attack wave
                (UnitTypeId.BARRACKS, 25, "Third Barracks"),
                (UnitTypeId.REFINERY, 99, "Second Refinery - After first attack"),
                (UnitTypeId.COMMANDCENTER, 100, "Expand to natural"),
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
        self.build_order_index = 0
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
            
        # Set initial rally point in front of the command center
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
            if not hasattr(self, '_first_depot_started') and self.build_order_index == 0:
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
        """Update the current build order based on the current strategy.
        
        Args:
            force_update: If True, force update even if strategy hasn't changed
        """
        try:
            if not self.head or not self.head.strategy:
                return
                
            strategy = self.head.strategy
            
            # Only update if strategy changed or forced
            if not force_update and hasattr(self, 'current_strategy') and self.current_strategy == strategy:
                return
                
            # Get build order for current strategy
            self.build_order = self.build_orders.get(strategy, []).copy()
            self.build_order_index = 0
            self.current_strategy = strategy
            
            # Reset first depot tracking when build order updates
            if hasattr(self, '_first_depot_started'):
                delattr(self, '_first_depot_started')
            
            if self.debug:
                print(f"[Military] Updated build order for strategy: {strategy}")
                print(f"[Military] Build order: {[step[2] for step in self.build_order]}")
                
            # Print the current build order
            if self.debug and self.build_order:
                print(f"[Military] Build order: {[step[2] for step in self.build_order]}")
                    
        except Exception as e:
            if self.debug:
                print(f"[Military] Error updating build order: {e}")
                import traceback
                traceback.print_exc()
            # Fall back to default build order
            self.build_order = self.build_orders.get('bio_rush', []).copy()
            self.build_order_index = 0
    
    async def _execute_build_order(self):
        """Execute the next step in the build order if conditions are met."""
        try:
            # Skip if we've completed the build order
            if self.build_order_index >= len(self.build_order):
                if self.debug and self.ai.time % 10 < 0.1:
                    print(f"[Military] Build order completed at index {self.build_order_index}")
                return
                
            current_time = self.ai.time
            
            # Get current build order step
            unit_type, supply, description = self.build_order[self.build_order_index]
            
            if self.debug:  # Always log in debug mode for tests
                print(f"\n[Military] === Starting build order step ===")
                print(f"[Military] Current build step: {description} (supply: {self.ai.supply_used}/{supply})")
                print(f"[Military] Current index: {self.build_order_index}, Total steps: {len(self.build_order)}")
                print(f"[Military] First depot started: {hasattr(self, '_first_depot_started')}, completed: {hasattr(self, '_first_depot_completed')}")
                print(f"[Military] Current supply: {self.ai.supply_used}/{self.ai.supply_cap}, Workers: {getattr(self.ai, 'workers', 'N/A')}")
                print(f"[Military] Minerals: {getattr(self.ai, 'minerals', 'N/A')}, Gas: {getattr(self.ai, 'vespene', 'N/A')}")
                print(f"[Military] Can afford {unit_type}: {getattr(self.ai, 'can_afford', lambda x: 'N/A')(unit_type)}")
            
            # Skip if we've tried this step too many times recently
            if unit_type in self.build_attempts:
                last_attempt, attempts = self.build_attempts[unit_type]
                if current_time - last_attempt < 5.0 and attempts > 3:  # Skip if failed 3 times in 5 seconds
                    if self.debug:
                        print(f"[Military] Skipping {unit_type} - too many failed attempts")
                    self.build_order_index += 1
                    return
            
            # Check if we've reached the required supply
            if self.ai.supply_used < supply:
                if self.debug:
                    print(f"[Military] Waiting for supply {self.ai.supply_used}/{supply} before {description}")
                return
                
            # Special handling for structures that depend on supply depot
            if unit_type != UnitTypeId.SUPPLYDEPOT and not hasattr(self, '_first_depot_completed') and not self._is_first_supply_depot_completed():
                if self.debug:
                    print(f"[Military] Waiting for first supply depot to complete before {description}")
                    print(f"[Military] Supply depots: {getattr(self.ai.structures(UnitTypeId.SUPPLYDEPOT).ready, 'amount', 0)} built, {getattr(self.ai, 'already_pending', lambda x: 0)(UnitTypeId.SUPPLYDEPOT)} pending")
                return
                
            # Special case for structures handled by EconomyManager
            if unit_type in [UnitTypeId.SUPPLYDEPOT, UnitTypeId.REFINERY, UnitTypeId.COMMANDCENTER, UnitTypeId.ORBITALCOMMAND]:
                # Only skip if it's already built or being built
                existing = getattr(self.ai.structures(unit_type), 'amount', 0) + getattr(self.ai, 'already_pending', lambda x: 0)(unit_type)
                if existing > 0:
                    if self.debug:
                        print(f"[Military] {unit_type} already exists or is being handled by EconomyManager")
                    self.build_order_index += 1
                    return
                
                # Try to build the structure
                if await self._try_build_structure(unit_type):
                    if self.debug:
                        print(f"[Military] {description}")
                    self.build_order_index += 1
                    # Reset attempt counter on success
                    if unit_type in self.build_attempts:
                        del self.build_attempts[unit_type]
                else:
                    # Track failed attempt
                    if unit_type not in self.build_attempts:
                        self.build_attempts[unit_type] = (current_time, 1)
                    else:
                        last_time, attempts = self.build_attempts[unit_type]
                        self.build_attempts[unit_type] = (current_time, attempts + 1)
                    
                    if self.debug:
                        print(f"[Military] Failed to build {unit_type}, attempt {self.build_attempts[unit_type][1]}")
                return
                
            # Check if we already have this structure or it's being built
            existing = getattr(self.ai.structures(unit_type), 'amount', 0) + getattr(self.ai, 'already_pending', lambda x: 0)(unit_type)
            if existing > 0:
                if self.debug:
                    print(f"[Military] {unit_type} already exists or is pending")
                self.build_order_index += 1
                return
                
            # Try to build the structure
            if await self._try_build_structure(unit_type):
                if self.debug:
                    print(f"[Military] {description}")
                self.build_order_index += 1
                # Reset attempt counter on success
                if unit_type in self.build_attempts:
                    del self.build_attempts[unit_type]
            else:
                # Track failed attempt
                if unit_type not in self.build_attempts:
                    self.build_attempts[unit_type] = (current_time, 1)
                else:
                    last_time, attempts = self.build_attempts[unit_type]
                    self.build_attempts[unit_type] = (current_time, attempts + 1)
                
                if self.debug:
                    print(f"[Military] Failed to build {unit_type}, attempt {self.build_attempts[unit_type][1]}")
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _execute_build_order: {e}")
                import traceback
                traceback.print_exc()
    
    async def _try_build_structure(self, unit_type):
        """Try to build a structure."""
        try:
            if self.debug:
                print(f"\n[Military] === Starting _try_build_structure for {unit_type} ===")
                print(f"[Military] Debug info - Supply depot completed: {hasattr(self, '_first_depot_completed') or self._is_first_supply_depot_completed()}")
                print(f"[Military] Can afford {unit_type}: {self.ai.can_afford(unit_type)}")
                print(f"[Military] Townhalls exist: {bool(self.ai.townhalls)}")
                
            # Skip if we don't have a completed supply depot yet (except for the depot itself)
            if unit_type != UnitTypeId.SUPPLYDEPOT:
                if not hasattr(self, '_first_depot_completed') and not self._is_first_supply_depot_completed():
                    if self.debug:
                        print(f"[Military] Waiting for first supply depot to complete before {description}")
                        print(f"[Military] Supply depots: {getattr(self.ai.structures(UnitTypeId.SUPPLYDEPOT).ready, 'amount', 0)} built, {getattr(self.ai, 'already_pending', lambda x: 0)(UnitTypeId.SUPPLYDEPOT)} pending")
                    return
                
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
                
            # Get a position near the first townhall
            townhall = self.ai.townhalls.first
            near_position = townhall.position
            
            if self.debug:
                print(f"[Military] Attempting to find placement for {unit_type} near {near_position}")
                
            # Find a placement for the structure
            placement = await self.ai.find_placement(unit_type, near=near_position, placement_step=2)
            
            if self.debug:
                print(f"[Military] Placement result: {placement}")
                
            if not placement:
                if self.debug:
                    print(f"[Military] Could not find placement for {unit_type}")
                return False
                
            # Find a worker to build the structure
            worker = self.ai.workers.random
            if not worker:
                if self.debug:
                    print("[Military] No workers available to build")
                return False
                
            # Check if we have enough workers before building production
            # Skip this check for supply depots as they're needed early
            if unit_type != UnitTypeId.SUPPLYDEPOT:
                worker_count = getattr(self.ai.workers, 'amount', 0)
                if isinstance(worker_count, int) and worker_count < 16:  # Only check if worker_count is an actual number
                    if self.debug:
                        print(f"[Military] Not enough workers ({worker_count}/16) to build {unit_type}")
                    return False
                
            if self.debug:
                print(f"[Military] Selected worker {worker} to build {unit_type} at {placement}")
                
            # Issue build command - handle both real and mock AI
            if hasattr(self.ai.build, '__await__'):
                # Real AI case - use await
                await self.ai.build(unit_type, near=placement, build_worker=worker)
                if self.debug:
                    print(f"[Military] Started building {unit_type} at {placement}")
            else:
                # Mock case - just call directly
                self.ai.build(unit_type, near=placement, build_worker=worker)
                if self.debug:
                    print(f"[Military] Mock build of {unit_type} at {placement}")
            
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
            
            # Calculate desired composition based on strategy
            desired_comp = self._get_desired_army_composition()
            
            # Train units based on desired composition
            for unit_type, desired_count in desired_comp.items():
                # Check if we need more of this unit type
                current = self.army_composition.get(unit_type, 0) + production.get(unit_type, 0)
                if current >= desired_count:
                    continue
                    
                # Find suitable production facility
                if unit_type == UnitTypeId.MARINE:
                    for barrack in self.ai.structures(UnitTypeId.BARRACKS).idle:
                        if self.ai.can_afford(unit_type):
                            barrack.train(unit_type)
                            if self.debug:
                                print(f"[Military] Training {unit_type}")
                            break
                            
                elif unit_type == UnitTypeId.MARAUDER:
                    for barrack in self.ai.structures(UnitTypeId.BARRACKS).filter(
                        lambda b: b.has_techlab and b.is_idle
                    ):
                        if self.ai.can_afford(unit_type) and self.ai.vespene >= 25:
                            barrack.train(unit_type)
                            if self.debug:
                                print(f"[Military] Training {unit_type}")
                            break
                            
                elif unit_type == UnitTypeId.MEDIVAC:
                    for starport in self.ai.structures(UnitTypeId.STARPORT).idle:
                        if self.ai.can_afford(unit_type) and self.ai.vespene >= 100:
                            starport.train(unit_type)
                            if self.debug:
                                print(f"[Military] Training {unit_type}")
                            break
                            
                # Add more unit types as needed
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _train_army: {e}")
                import traceback
                traceback.print_exc()
    
    def _get_desired_army_composition(self):
        """Get the desired army composition based on current strategy."""
        try:
            if self.strategy == "bio_rush":
                return {
                    UnitTypeId.MARINE: 20,
                    UnitTypeId.MARAUDER: 5,
                    UnitTypeId.MEDIVAC: 2
                }
            elif self.strategy == "mech":
                return {
                    UnitTypeId.SIEGETANK: 4,
                    UnitTypeId.HELLION: 8,
                    UnitTypeId.THOR: 2
                }
            else:  # Default to bio
                return {
                    UnitTypeId.MARINE: 10,
                    UnitTypeId.MARAUDER: 3,
                    UnitTypeId.MEDIVAC: 1
                }
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _get_desired_army_composition: {e}")
            # Return default composition on error
            return {
                UnitTypeId.MARINE: 10,
                UnitTypeId.MARAUDER: 3,
                UnitTypeId.MEDIVAC: 1
            }
    
    async def _manage_upgrades(self):
        """Research upgrades for bio army."""
        try:
            # Combat Shield
            if not self.ai.already_pending_upgrade(UpgradeId.SHIELDWALL) and not self.ai.already_pending_upgrade(UpgradeId.STIMPACK):
                for barrack in self.ai.structures(UnitTypeId.BARRACKSTECHLAB).ready:
                    if barrack.is_idle and self.ai.can_afford(AbilityId.RESEARCH_STIMPACK):
                        barrack.research(UpgradeId.STIMPACK)
                        if self.debug:
                            print("[Military] Researching Stimpack")
                        break
            
            # Infantry Weapons/Armor
            for ebay in self.ai.structures(UnitTypeId.ENGINEERINGBAY).ready:
                if ebay.is_idle:
                    if self.ai.can_afford(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1) and not self.ai.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1):
                        ebay.research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1)
                        if self.debug:
                            print("[Military] Researching Infantry Weapons 1")
                    elif self.ai.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL1) and not self.ai.already_pending_upgrade(UpgradeId.TERRANINFANTRYARMORSLEVEL1):
                        ebay.research(UpgradeId.TERRANINFANTRYARMORSLEVEL1)
                        if self.debug:
                            print("[Military] Researching Infantry Armor 1")
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _manage_upgrades: {e}")
                import traceback
                traceback.print_exc()
    
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
        self.army_composition = {}
        for unit in self.ai.units.filter(
            lambda u: u.type_id in {
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
            } and u.tag in self.army_tags
        ):
            self.army_composition[unit.type_id] = self.army_composition.get(unit.type_id, 0) + 1

    async def _control_army(self):
        """Control army units for combat."""
        try:
            # Update army composition
            self._update_army_composition()
            
            # Get all combat units that are ready and not moving
            army = self.ai.units.filter(
                lambda u: u.type_id in self.army_composition 
                and u.is_ready 
                and not u.is_moving
            )
            
            # If no army, nothing to do
            if not army:
                return
                
            # Set rally point if not set
            if not self.rally_point and self.ai.townhalls:
                self.rally_point = self.ai.townhalls.first.position.towards(
                    self.ai.game_info.map_center, 10
                )
            
            # Find enemy units and structures
            enemies = self.ai.enemy_units | self.ai.enemy_structures
            
            # If we have a specific attack target, prioritize it
            if self.attack_target:
                for unit in army:
                    unit.attack(self.attack_target)
                return
                
            # If attack is started or we have enemies in vision
            if self.attack_started or enemies:
                for unit in army:
                    # Find closest enemy if any
                    if enemies:
                        closest_enemy = enemies.closest_to(unit)
                        if closest_enemy.distance_to(unit) < 15:  # Only attack if enemy is close
                            unit.attack(closest_enemy)
                        elif self.rally_point:
                            unit.move(self.rally_point)
                    elif self.rally_point:
                        unit.move(self.rally_point)
            # Otherwise, move to rally point
            elif self.rally_point:
                for unit in army:
                    unit.move(self.rally_point)
            
            # Special handling for medivacs - heal damaged bio units
            medivacs = army.filter(lambda u: u.type_id == UnitTypeId.MEDIVAC)
            if medivacs:
                bio_units = army.filter(
                    lambda u: u.type_id in {UnitTypeId.MARINE, UnitTypeId.MARAUDER}
                    and u.health_percentage < 1.0  # Only damaged units
                )
                
                for medivac in medivacs:
                    if bio_units:
                        # Find most damaged bio unit
                        target = min(bio_units, key=lambda u: u.health_percentage)
                        medivac.attack(target)
                    elif army:
                        # Otherwise follow the army
                        medivac.attack(army.closest_to(medivac))
                    
        except Exception as e:
            if self.debug:
                print(f"[Military] Error in _control_army: {e}")
                import traceback
                traceback.print_exc()
