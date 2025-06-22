"""Handles all Terran economy-related logic including SCV production, resource gathering, and gas mining."""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2

class TerranEconomyManager:
    """Manages the Terran bot's economy including SCVs, resources, and gas mining."""
    
    def __init__(self, ai):
        """Initialize the TerranEconomyManager with a reference to the main AI object."""
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
        
        # Track worker assignments to refineries
        self.refinery_assignments = {}  # refinery_tag -> set of worker_tags
        self.worker_refinery_map = {}   # worker_tag -> refinery_tag

    async def on_start(self):
        """Called once at the start of the game."""
        print("Terran Economy Manager initialized")
        await self.ai.distribute_workers()

    async def on_step(self):
        current_time = self.ai.time
        
        # DEBUG: Count refineries and bunkers every step
        refineries_count = self.ai.structures(UnitTypeId.REFINERY).ready.amount
        bunkers_count = self.ai.structures(UnitTypeId.BUNKER).ready.amount
        bunkers_pending = self.ai.structures(UnitTypeId.BUNKER).not_ready.amount
        print(f"[DEBUG] === TERRAN ECONOMY COUNTS === Time: {current_time:.1f}s | Refineries: {refineries_count} | Bunkers (ready): {bunkers_count} | Bunkers (building): {bunkers_pending}")
        
        try:
            # Train workers
            for cc in self.ai.townhalls.ready:
                await self.train_workers(cc)

            # Build supply depot
            await self.build_supply_depot()

            # Build refineries
            await self.build_refineries()
            
            # Manage gas workers
            await self.manage_gas_workers()
            
            # Distribute workers periodically
            if current_time - self.last_worker_distribution > 10.0:
                await self.ai.distribute_workers()
                self.last_worker_distribution = current_time

            # Check if we should expand
            if (self.head and self.head.should_expand() and current_time > self.min_time_before_expand and self.ai.minerals > self.expand_when_minerals):
                await self.expand_now()
                
        except Exception as e:
            if self.debug:
                print(f"[Terran Economy] Error in on_step: {e}")
                import traceback
                traceback.print_exc()

    async def train_workers(self, structure):
        """Train SCVs from the specified structure if below target worker count."""
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
        if current_time - self.last_supply_attempt < 1.0:
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
                print(f"[Terran Economy] Can't afford Supply Depot (need 100 minerals, have {self.ai.minerals})")
            self.last_supply_attempt = current_time
            self.supply_attempt_count += 1
            return False
            
        # Find a location near the command center
        if not self.ai.townhalls:
            if self.debug and self.supply_attempt_count == 0:
                print("[Terran Economy] No Command Center found for Supply Depot placement")
            self.last_supply_attempt = current_time
            return False
            
        command_center = self.ai.townhalls.first
        
        # Get all mineral patches and gas geysers to avoid them
        mineral_patches = self.ai.mineral_field
        gas_geysers = self.ai.vespene_geyser
        existing_structures = self.ai.structures
        
        # Try to find a good location for the supply depot
        location = await self._find_safe_building_location(
            UnitTypeId.SUPPLYDEPOT,
            command_center.position,
            mineral_patches,
            gas_geysers,
            existing_structures
        )
        
        if location:
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
                        print(f"[Terran Economy] Worker returning resources before building Supply Depot")
                    worker.return_resource()
                    self.last_supply_attempt = current_time
                    return False
                    
                # If worker is doing something else, stop it
                if not worker.is_idle:
                    worker.stop()
                
                # Issue build command
                worker.stop()
                await worker.build(UnitTypeId.SUPPLYDEPOT, location)
                if self.debug:
                    print(f"[Terran Economy] Building Supply Depot at {location} with worker at {worker.position}")
                self.last_supply_attempt = current_time
                self.supply_attempt_count = 0
                return True
        
        if self.debug and self.supply_attempt_count % 5 == 0:
            print("[Terran Economy] Couldn't find a valid location for Supply Depot")
            
        self.last_supply_attempt = current_time
        self.supply_attempt_count += 1
        return False

    async def _find_safe_building_location(self, unit_type, near_position, mineral_patches, gas_geysers, existing_structures):
        """Find a safe location for building that avoids resources and other structures."""
        import math
        
        # Define safe distances
        MINERAL_SAFE_DISTANCE = 3.0  # Don't build too close to minerals
        GAS_SAFE_DISTANCE = 3.0      # Don't build too close to gas
        STRUCTURE_SAFE_DISTANCE = 2.0 # Don't build too close to other structures
        BASE_DISTANCE_MIN = 8.0       # Minimum distance from base
        BASE_DISTANCE_MAX = 20.0      # Maximum distance from base
        
        # Try different positions around the base
        for distance in range(int(BASE_DISTANCE_MIN), int(BASE_DISTANCE_MAX), 2):
            for angle in range(0, 360, 15):  # Try every 15 degrees
                # Calculate position using polar coordinates
                angle_rad = math.radians(angle)
                x = near_position.x + distance * math.cos(angle_rad)
                y = near_position.y + distance * math.sin(angle_rad)
                target_pos = Point2((x, y))
                
                # Check if this position is safe
                if self._is_position_safe(target_pos, mineral_patches, gas_geysers, existing_structures, 
                                        MINERAL_SAFE_DISTANCE, GAS_SAFE_DISTANCE, STRUCTURE_SAFE_DISTANCE):
                    
                    # Try to find a valid placement near this position
                    location = await self.ai.find_placement(
                        unit_type,
                        near=target_pos,
                        placement_step=1,
                        random_alternative=True,
                        max_distance=3
                    )
                    
                    if location and await self.ai.can_place(unit_type, location):
                        # Double-check that the final location is also safe
                        if self._is_position_safe(location, mineral_patches, gas_geysers, existing_structures,
                                                MINERAL_SAFE_DISTANCE, GAS_SAFE_DISTANCE, STRUCTURE_SAFE_DISTANCE):
                            return location
        
        return None

    def _is_position_safe(self, position, mineral_patches, gas_geysers, existing_structures, 
                         mineral_safe_dist, gas_safe_dist, structure_safe_dist):
        """Check if a position is safe to build on (not too close to resources or structures)."""
        
        # Check distance to mineral patches
        for mineral in mineral_patches:
            if position.distance_to(mineral.position) < mineral_safe_dist:
                return False
        
        # Check distance to gas geysers
        for geyser in gas_geysers:
            if position.distance_to(geyser.position) < gas_safe_dist:
                return False
        
        # Check distance to existing structures
        for structure in existing_structures:
            if position.distance_to(structure.position) < structure_safe_dist:
                return False
        
        return True

    async def build_refineries(self):
        """Build refineries when we have enough workers."""
        # Only build refineries if we have a command center and can afford it
        if not self.ai.townhalls or not self.ai.can_afford(UnitTypeId.REFINERY):
            return False
            
        current_time = self.ai.time
        
        # Don't try too often
        if hasattr(self, 'last_refinery_attempt') and current_time - self.last_refinery_attempt < 5.0:
            return False
            
        # Get all vespene geysers near our base
        geysers = self.ai.vespene_geyser.closer_than(15, self.ai.townhalls.first)
        
        for geyser in geysers:
            # Check if we already have a refinery here or are building one
            if (not self.ai.structures(UnitTypeId.REFINERY).closer_than(1, geyser).exists and
                not self.ai.already_pending(UnitTypeId.REFINERY)):
                
                # Get a worker to build the refinery
                worker = self.ai.select_build_worker(geyser.position)
                if worker:
                    worker.build(UnitTypeId.REFINERY, geyser)
                    if self.debug:
                        print(f"[Terran Economy] Building Refinery at {geyser.position}")
                    self.last_refinery_attempt = current_time
                    return True
        
        return False

    async def manage_gas_workers(self):
        """Manage worker distribution between minerals and gas."""
        try:
            # Update worker assignments
            self._update_refinery_assignments()
            
            # Get all refineries
            for refinery in self.ai.structures(UnitTypeId.REFINERY).ready:
                refinery_tag = refinery.tag
                worker_count = len(self.refinery_assignments.get(refinery_tag, set()))
                
                # If we have too few workers on this refinery
                if worker_count < self.gas_workers_per_refinery:
                    # Find mineral workers to send to gas
                    mineral_workers = self.ai.workers.filter(
                        lambda w: w.is_gathering and w.is_carrying_minerals
                    )
                    if mineral_workers and mineral_workers.amount > 8:  # Keep at least 8 on minerals
                        worker = mineral_workers.random
                        worker.gather(refinery)
                        if self.debug and self.ai.time % 10 < 0.1:
                            print(f"[Terran Economy] Sent mineral worker to gas")
                
                # If we have too many workers on this refinery
                elif worker_count > self.gas_workers_per_refinery:
                    # Send extra workers to gather minerals
                    excess_workers = worker_count - self.gas_workers_per_refinery
                    for worker in self.ai.workers.random_group_of(min(excess_workers, worker_count)):
                        if worker.is_carrying_vespene:
                            # If worker is carrying gas, return it first
                            worker.return_resource()
                        else:
                            # Otherwise, send to gather minerals
                            await self.ai.distribute_workers()
                            if self.debug and self.ai.time % 10 < 0.1:
                                print(f"[Terran Economy] Sent excess gas worker to minerals")
                            
        except Exception as e:
            if self.debug:
                print(f"[Terran Economy] Error in manage_gas_workers: {e}")

    def _update_refinery_assignments(self):
        """Update the tracking of which workers are assigned to which refineries."""
        try:
            # Clear old assignments
            self.refinery_assignments.clear()
            self.worker_refinery_map.clear()
            
            # Get all refineries
            refineries = self.ai.structures(UnitTypeId.REFINERY).ready
            
            # For each refinery, find workers that are gathering from it
            for refinery in refineries:
                refinery_tag = refinery.tag
                self.refinery_assignments[refinery_tag] = set()
                
                # Find workers gathering from this refinery
                workers_at_refinery = self.ai.workers.filter(
                    lambda w: w.is_gathering and 
                    w.order_target and 
                    hasattr(w.order_target, 'tag') and
                    w.order_target.tag == refinery_tag
                )
                
                for worker in workers_at_refinery:
                    self.refinery_assignments[refinery_tag].add(worker.tag)
                    self.worker_refinery_map[worker.tag] = refinery_tag
                    
        except Exception as e:
            if self.debug:
                print(f"[Terran Economy] Error in _update_refinery_assignments: {e}")

    async def expand_now(self):
        """Build a new command center at the closest available expansion location."""
        try:
            # Don't expand too early in the game
            if hasattr(self, 'min_time_before_expand') and self.ai.time < self.min_time_before_expand:
                return False
                
            # Don't expand if we don't have a head manager or can't afford it
            if not hasattr(self, 'head') or not self.head or not self.ai.can_afford(UnitTypeId.COMMANDCENTER):
                return False
                
            # Check if we already have a command center in progress
            pending_cc = self.ai.already_pending(UnitTypeId.COMMANDCENTER)
            if pending_cc > 0:
                return False
                
            # Get all expansion locations
            expansion_locations = self.ai.expansion_locations
            if not expansion_locations:
                return False
                
            # Get the main base (first command center)
            if not hasattr(self.ai, 'townhalls') or not self.ai.townhalls or not self.ai.townhalls.first:
                return False
                
            main_base = self.ai.townhalls.first
            
            # Sort expansion locations by distance to main base
            sorted_locations = sorted(
                expansion_locations,
                key=lambda loc: main_base.position.distance_to(loc) if hasattr(main_base, 'position') else 0
            )
            
            # Find the first available expansion location
            for location in sorted_locations:
                # Skip if there's already a command center nearby
                nearby_cc = self.ai.structures.filter(
                    lambda unit: unit.type_id == UnitTypeId.COMMANDCENTER and 
                               unit.position.distance_to(location) < 15
                )
                if nearby_cc:
                    continue
                    
                # Skip if enemy units are nearby
                enemy_units = self.ai.enemy_units.filter(
                    lambda unit: unit.position.distance_to(location) < 25
                )
                if enemy_units:
                    continue
                    
                # Skip if enemy structures are nearby
                enemy_structures = self.ai.enemy_structures.filter(
                    lambda unit: unit.position.distance_to(location) < 30
                )
                if enemy_structures:
                    continue
                    
                # Found a valid location, try to build
                worker = self.ai.select_build_worker(location)
                if worker:
                    if self.debug:
                        print(f"[Terran Economy] Building Command Center at {location}")
                    worker.build(UnitTypeId.COMMANDCENTER, location)
                    return True
            
            return False
            
        except Exception as e:
            if self.debug:
                print(f"[Terran Economy] Error in expand_now: {e}")
            return False 