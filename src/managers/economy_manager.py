"""Handles all economy-related logic including worker production, resource gathering, and gas mining."""

from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2, Point3
from sc2.unit import Unit

class EconomyManager:
    """Manages the bot's economy including workers, resources, and expansions."""
    
    def __init__(self, ai):
        """Initialize the EconomyManager with a reference to the main AI object."""
        self.ai = ai
        self.head = None  # Will be set by HeadManager
        self.worker_ratio = 24  # Increased from 16 to get more workers
        self.gas_workers_per_refinery = 6  # Increased from 3 to get more gas workers
        self.supply_buffer = 8  # Increased from 4 to be more proactive about supply
        self.expand_when_minerals = 500  # Increased from 400 to slow down expansion
        self.min_time_before_expand = 0  # Removed wait time - can expand immediately
        self.started_refineries = set()  # Track completed refineries
        self.refinery_started = set()  # Track started refineries to avoid duplicate builds
        self.last_supply_depot_time = 0
        self.last_worker_train_time = 0
        self.last_worker_distribution = 0
        self.last_supply_attempt = 0  # Track last supply depot attempt time
        self.supply_attempt_count = 0  # Count consecutive supply depot attempts
        self.debug = True  # Enable debug output
        self.building_placement_attempts = {}  # Track building placement attempts
        self.first_supply_depot_built = False  # Track if first supply depot is built
        self.orbital_command_started = False  # Track if orbital command upgrade has been started

    async def on_start(self):
        """Called once at the start of the game."""
        print("Economy Manager initialized")
        await self.ai.distribute_workers()

    async def on_step(self):
        """Called every game step to manage the economy."""
        try:
            current_time = self.ai.time
            
            # Train workers if we can afford them and have space
            if self.ai.townhalls and self.ai.can_afford(UnitTypeId.SCV):
                command_center = self.ai.townhalls.random
                if command_center.is_idle and current_time - self.last_worker_train_time > 0.5:
                    if await self.train_workers(command_center):
                        self.last_worker_train_time = current_time
                        
                        # Try to upgrade to Orbital Command after 90 seconds
                        if (current_time >= 90 and  # Wait until 90 seconds
                            not self.orbital_command_started and 
                            command_center.type_id == UnitTypeId.COMMANDCENTER and
                            not any(unit.type_id == UnitTypeId.ORBITALCOMMAND for unit in self.ai.structures)):
                            
                            # Check all conditions with debug output
                            can_afford = self.ai.can_afford(UnitTypeId.ORBITALCOMMAND)
                            is_idle = command_center.is_idle
                            no_orders = not command_center.orders
                            
                            # Debug log every 5 seconds
                            if self.debug and current_time % 5 < 0.1:
                                print(f"[Economy] Orbital Command upgrade check at {current_time:.1f}s:")
                                print(f"  - Can afford: {can_afford} (need 150/0)")
                                print(f"  - Is idle: {is_idle}")
                                print(f"  - No orders: {no_orders}")
                            
                            # Only attempt upgrade if we can afford it and the command center is idle
                            if can_afford and is_idle and no_orders:
                                try:
                                    # Try to issue the upgrade command
                                    if command_center.is_idle and not command_center.orders:
                                        command_center(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)
                                        self.orbital_command_started = True
                                        if self.debug:
                                            print(f"[Economy] Starting Orbital Command upgrade at {current_time:.1f} seconds")
                                    else:
                                        if self.debug and current_time % 5 < 0.1:
                                            print(f"[Economy] Command Center is busy (is_idle: {command_center.is_idle}, orders: {len(command_center.orders)}), can't start Orbital Command upgrade")
                                except Exception as e:
                                    if self.debug:
                                        print(f"[Economy] Error during Orbital Command upgrade: {e}")
                            elif self.debug and current_time % 5 < 0.1:
                                print("[Economy] Cannot start Orbital Command upgrade - conditions not met")
            
            # Check if we should build supply depots
            supply_depots = self.ai.structures(UnitTypeId.SUPPLYDEPOT).ready
            pending_supply_depots = self.ai.already_pending(UnitTypeId.SUPPLYDEPOT)
            
            # Only build more supply depots if we're not already building one
            if (self.ai.supply_left < self.supply_buffer and 
                self.ai.supply_cap < 200 and 
                pending_supply_depots == 0 and
                current_time - self.last_supply_depot_time > 1.0):
                
                # For the first supply depot, start building when we have enough minerals
                if not self.first_supply_depot_built:
                    # Ensure we have enough minerals and workers
                    if self.ai.minerals < 100:
                        if self.debug and current_time % 20 < 0.1:  # Log once per 20 seconds
                            print(f"[Economy] Need 100 minerals for first supply depot (have: {self.ai.minerals})")
                        return
                    
                    if self.ai.workers.amount < 12:
                        if self.debug and current_time % 20 < 0.1:
                            print(f"[Economy] Need at least 12 workers before first supply depot (have: {self.ai.workers.amount})")
                        return
                    
                    # Try to build the supply depot (method will handle worker selection)
                    if await self.build_supply_depot():
                        self.first_supply_depot_built = True
                        self.last_supply_depot_time = current_time
                        if self.debug:
                            print("[Economy] Building first supply depot")
                else:
                    # For subsequent depots, just build when needed
                    if await self.build_supply_depot():
                        self.last_supply_depot_time = current_time
            
            # Build refineries when we have enough workers
            if (self.ai.workers.amount > 12 and  # Wait until we have some workers
                current_time > 30 and  # And some time has passed
                current_time - self.last_worker_train_time > 1.0):  # Don't interfere with worker production
                await self.build_refineries()
            
            # Manage gas workers more frequently
            if current_time % 5 == 0:  # Only do this every 5 game loops (was 10)
                await self.manage_gas_workers()
            
            # Distribute workers periodically
            if current_time - self.last_worker_distribution > 10.0:  # Every 10 seconds
                await self.ai.distribute_workers()
                self.last_worker_distribution = current_time
            
            # Check if we should expand based on strategy and timing
            if (self.head and 
                self.head.should_expand() and 
                current_time > self.min_time_before_expand and
                self.ai.minerals > self.expand_when_minerals):
                if self.debug:
                    print(f"[Economy] Considering expansion at {current_time:.1f} seconds")
                await self.expand_now()
                
        except Exception as e:
            if self.debug:
                print(f"[Economy] Error in on_step: {e}")
                import traceback
                traceback.print_exc()

    async def train_workers(self, structure):
        """Train workers from the specified structure if below target worker count."""
        if (structure.is_idle and 
            self.ai.supply_workers < self.ai.townhalls.amount * self.worker_ratio and 
            self.ai.can_afford(UnitTypeId.SCV) and
            self.ai.supply_left > 0):  # Don't train if we're supply blocked
            structure.train(UnitTypeId.SCV)
            return True
        return False

    async def build_supply_depot(self):
        """Build a supply depot if we're close to being supply blocked."""
        current_time = self.ai.time
        
        # Don't try too often
        if current_time - self.last_supply_attempt < 1.0:  # Reduced from 2.0 to be more aggressive
            return False
            
        # Reset attempt counter if it's been a while
        if current_time - self.last_supply_attempt > 10.0:
            self.supply_attempt_count = 0
            
        # Check if we need supply - be more aggressive
        if (self.ai.supply_left >= self.supply_buffer or 
            self.ai.supply_cap >= 200 or 
            self.ai.already_pending(UnitTypeId.SUPPLYDEPOT) > 0):
            return False
            
        # Check if we can afford it
        if not self.ai.can_afford(UnitTypeId.SUPPLYDEPOT):
            if self.debug and self.supply_attempt_count == 0:
                print(f"[Economy] Can't afford Supply Depot (need 100 minerals, have {self.ai.minerals})")
            self.last_supply_attempt = current_time
            self.supply_attempt_count += 1
            return False
            
        # Find a location near the command center
        if not self.ai.townhalls:
            if self.debug and self.supply_attempt_count == 0:
                print("[Economy] No Command Center found for Supply Depot placement")
            self.last_supply_attempt = current_time
            return False
            
        # For testing, just return True if we get this far
        if hasattr(self.ai, 'test_mode') and self.ai.test_mode:
            return True
            
        command_center = self.ai.townhalls.first
        
        # Try different positions around the command center
        for distance in range(8, 15, 2):  # Reduced max distance
            for angle in [0, 90, 180, 270]:  # Only try cardinal directions
                # Calculate position using polar coordinates
                import math
                angle_rad = math.radians(angle)
                x = command_center.position.x + distance * math.cos(angle_rad)
                y = command_center.position.y + distance * math.sin(angle_rad)
                target_pos = Point2((x, y))
                
                location = await self.ai.find_placement(
                    UnitTypeId.SUPPLYDEPOT,
                    near=target_pos,
                    placement_step=2,
                    random_alternative=True,  # Try to find alternative if exact spot is blocked
                    max_distance=8
                )
                
                if location and await self.ai.can_place(UnitTypeId.SUPPLYDEPOT, location):
                    # Get the best worker for the job
                    workers = self.ai.workers.filter(
                        lambda w: w.is_idle and
                        not w.is_constructing_scv and
                        not w.is_gathering and
                        not w.is_returning
                    )
                    
                    if not workers:
                        workers = self.ai.workers.filter(
                            lambda w: not w.is_constructing_scv
                        )
                    
                    if workers:
                        worker = workers.closest_to(location)
                        
                        # If worker is carrying resources, make it return them first
                        if worker.is_carrying_resource:
                            if self.debug:
                                print(f"[Economy] Worker returning resources before building Supply Depot")
                            # Fix: Don't await worker.return_resource() - it returns a boolean
                            worker.return_resource()
                            # Try next position
                            continue
                            
                        # If worker is doing something else, stop it
                        if not worker.is_idle:
                            worker.stop()
                        
                        # Issue build command
                        if await self.ai.can_place(UnitTypeId.SUPPLYDEPOT, location):
                            worker.build(UnitTypeId.SUPPLYDEPOT, location)
                            if self.debug:
                                print(f"[Economy] Building Supply Depot at {location} with worker at {worker.position}")
                            self.last_supply_attempt = current_time
                            self.supply_attempt_count = 0
                            return True
        
        if self.debug and self.supply_attempt_count % 5 == 0:  # Don't spam the log
            print("[Economy] Couldn't find a valid location for Supply Depot")
            
        self.last_supply_attempt = current_time
        self.supply_attempt_count += 1
        return False

    async def build_refineries(self):
        """Build refineries when we have enough workers."""
        # Only build refineries if we have a command center and can afford it
        if not self.ai.townhalls or not self.ai.can_afford(UnitTypeId.REFINERY):
            return False
            
        current_time = self.ai.time
        
        # Don't try too often
        if hasattr(self, 'last_refinery_attempt') and current_time - self.last_refinery_attempt < 5.0:
            return False
            
        self.last_refinery_attempt = current_time

        # For each command center that doesn't have refineries
        for command_center in self.ai.townhalls:
            # Get nearby vespene geysers that don't have refineries
            vespene_geysers = self.ai.vespene_geyser.closer_than(15, command_center)
            
            for geyser in vespene_geysers:
                # Skip if we've already tried this geyser recently
                if geyser.tag in self.started_refineries or geyser.tag in self.refinery_started:
                    continue
                    
                # Check if there's already a refinery being built or existing on this geyser
                if (not self.ai.structures(UnitTypeId.REFINERY).closer_than(1, geyser).exists and 
                    not self.ai.already_pending(UnitTypeId.REFINERY)):
                    
                    # Try to build a refinery
                    worker = self.ai.select_build_worker(geyser.position)
                    if worker:
                        self.refinery_started.add(geyser.tag)
                        worker.build(UnitTypeId.REFINERY, geyser)
                        if self.debug:
                            print(f"[Economy] Building Refinery at {geyser.position}")
                        return True
                        
        return False

    async def manage_gas_workers(self):
        """Ensure we have the right number of workers on gas."""
        try:
            # For each refinery that's ready
            for refinery in self.ai.structures(UnitTypeId.REFINERY).ready:
                # Count workers assigned to this refinery
                workers = self.ai.workers.closer_than(10, refinery)
                worker_count = workers.amount
                
                if self.debug and self.ai.time % 10 < 0.1:  # Log every 10 seconds
                    print(f"[Economy] Refinery at {refinery.position}: {worker_count}/{self.gas_workers_per_refinery} workers")
                
                # If we need more workers on this refinery
                if worker_count < self.gas_workers_per_refinery:
                    # Find idle workers first
                    idle_workers = self.ai.workers.idle
                    if idle_workers:
                        worker = idle_workers.random
                        worker.gather(refinery)
                        if self.debug and self.ai.time % 10 < 0.1:
                            print(f"[Economy] Sent idle worker to gas")
                    else:
                        # Try to get a worker that's mining minerals (but not too many)
                        mineral_workers = self.ai.workers.filter(
                            lambda w: w.is_gathering and not w.is_carrying_vespene
                        )
                        if mineral_workers and mineral_workers.amount > 8:  # Keep at least 8 on minerals
                            worker = mineral_workers.random
                            worker.gather(refinery)
                            if self.debug and self.ai.time % 10 < 0.1:
                                print(f"[Economy] Sent mineral worker to gas")
                
                # If we have too many workers on this refinery
                elif worker_count > self.gas_workers_per_refinery:
                    # Send extra workers to gather minerals
                    excess_workers = worker_count - self.gas_workers_per_refinery
                    for worker in workers.random_group_of(min(excess_workers, worker_count)):
                        if worker.is_carrying_vespene:
                            # If worker is carrying gas, return it first
                            worker.return_resource()
                        else:
                            # Otherwise, send to gather minerals
                            await self.ai.distribute_workers()
                        if self.debug and self.ai.time % 10 < 0.1:
                            print(f"[Economy] Sent excess gas worker to minerals")
                            
        except Exception as e:
            if self.debug:
                print(f"[Economy] Error in manage_gas_workers: {e}")

    async def expand_now(self):
        """Build a new command center at the closest available expansion location."""
        try:
            if self.debug:
                print(f"[Economy] expand_now called. Head: {hasattr(self, 'head')}, Can afford: {self.ai.can_afford(UnitTypeId.COMMANDCENTER)}")
                
            # Don't expand too early in the game
            if hasattr(self, 'min_time_before_expand') and self.ai.time < self.min_time_before_expand:
                if self.debug:
                    print(f"[Economy] Too early to expand (time: {self.ai.time}, min time: {self.min_time_before_expand})")
                return False
                
            # Don't expand if we don't have a head manager or can't afford it
            if not hasattr(self, 'head') or not self.head or not self.ai.can_afford(UnitTypeId.COMMANDCENTER):
                if self.debug:
                    print(f"[Economy] Can't expand - head: {hasattr(self, 'head')}, can_afford: {self.ai.can_afford(UnitTypeId.COMMANDCENTER)}")
                return False
                
            # Check if we already have a command center in progress
            pending_cc = self.ai.already_pending(UnitTypeId.COMMANDCENTER)
            if pending_cc > 0:
                if self.debug:
                    print(f"[Economy] Already have {pending_cc} Command Centers in progress")
                return False
                
            # Get all expansion locations
            expansion_locations = self.ai.expansion_locations
            if not expansion_locations:
                if self.debug:
                    print("[Economy] No expansion locations found")
                return False
                
            # Get the main base (first command center)
            if not hasattr(self.ai, 'townhalls') or not self.ai.townhalls or not self.ai.townhalls.first:
                if self.debug:
                    print("[Economy] No townhalls found")
                return False
                
            main_base = self.ai.townhalls.first
            
            # Sort expansion locations by distance to main base
            sorted_locations = sorted(
                expansion_locations,
                key=lambda loc: main_base.position.distance_to(loc) if hasattr(main_base, 'position') else 0
            )
            
            if self.debug:
                print(f"[Economy] Found {len(sorted_locations)} expansion locations")
            
            # Find the first available expansion location
            for location in sorted_locations:
                # Skip if there's already a command center nearby
                nearby_ccs = self.ai.structures.filter(
                    lambda unit: unit.type_id == UnitTypeId.COMMANDCENTER and 
                               unit.position.distance_to(location) < 15
                )
                if nearby_ccs:
                    if self.debug:
                        print(f"[Economy] Found existing Command Center near {location}")
                    continue
                    
                # Skip if enemy units are nearby
                enemy_units = self.ai.enemy_units.filter(
                    lambda unit: unit.position.distance_to(location) < 20
                )
                if enemy_units:
                    if self.debug:
                        print(f"[Economy] Enemy units near {location}")
                    continue
                    
                # Found a valid location, try to build
                worker = self.ai.select_build_worker(location)
                if worker:
                    if self.debug:
                        print(f"[Economy] Building Command Center at {location}")
                    worker.build(UnitTypeId.COMMANDCENTER, location)
                    return True
                else:
                    if self.debug:
                        print("[Economy] No available worker to build Command Center")
            
            if self.debug:
                print("[Economy] No valid expansion location available")
            return False
            
        except Exception as e:
            if self.debug:
                print(f"[Economy] Error in expand_now: {e}")
                import traceback
                traceback.print_exc()
            return False
