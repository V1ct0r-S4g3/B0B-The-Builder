"""Handles all Protoss economy-related logic including probe production, resource gathering, and gas mining."""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2

class ProtossEconomyManager:
    """Manages the Protoss bot's economy including probes, resources, and gas mining."""
    
    def __init__(self, ai):
        """Initialize the ProtossEconomyManager with a reference to the main AI object."""
        self.ai = ai
        self.head = None  # Will be set by HeadManager
        self.worker_ratio = 24  # Target probe count per nexus
        self.gas_workers_per_assimilator = 3  # Protoss uses 3 probes per assimilator
        self.supply_buffer = 8  # Pylon buffer to avoid supply block
        self.expand_when_minerals = 500  # When to expand
        self.min_time_before_expand = 0  # Can expand immediately
        self.assimilator_started = set()  # Track started assimilators
        self.last_pylon_time = 0
        self.last_probe_train_time = 0
        self.last_worker_distribution = 0
        self.last_pylon_attempt = 0  # Track last pylon attempt time
        self.pylon_attempt_count = 0  # Count consecutive pylon attempts
        self.debug = True  # Enable debug output
        self.building_placement_attempts = {}  # Track building placement attempts
        self.first_pylon_built = False  # Track if first pylon is built
        
        # Track probe assignments to assimilators
        self.assimilator_assignments = {}  # assimilator_tag -> set of probe_tags
        self.probe_assimilator_map = {}   # probe_tag -> assimilator_tag

    async def on_start(self):
        """Called once at the start of the game."""
        print("Protoss Economy Manager initialized")
        await self.ai.distribute_workers()

    async def on_step(self):
        current_time = self.ai.time
        
        # DEBUG: Count assimilators and pylons every step
        assimilators_count = self.ai.structures(UnitTypeId.ASSIMILATOR).ready.amount
        pylons_count = self.ai.structures(UnitTypeId.PYLON).ready.amount
        pylons_pending = self.ai.structures(UnitTypeId.PYLON).not_ready.amount
        print(f"[DEBUG] === PROTOSS ECONOMY COUNTS === Time: {current_time:.1f}s | Assimilators: {assimilators_count} | Pylons (ready): {pylons_count} | Pylons (building): {pylons_pending}")
        
        try:
            # Train probes
            for nexus in self.ai.townhalls.ready:
                await self.train_probes(nexus)

            # Build pylon
            await self.build_pylon()

            # Build assimilators
            await self.build_assimilators()
            
            # Manage gas probes
            await self.manage_gas_probes()
            
            # Distribute workers periodically
            if current_time - self.last_worker_distribution > 10.0:
                await self.ai.distribute_workers()
                self.last_worker_distribution = current_time

            # Check if we should expand
            if (self.head and self.head.should_expand() and current_time > self.min_time_before_expand and self.ai.minerals > self.expand_when_minerals):
                await self.expand_now()
                
        except Exception as e:
            if self.debug:
                print(f"[Protoss Economy] Error in on_step: {e}")
                import traceback
                traceback.print_exc()

    async def train_probes(self, structure):
        """Train probes from the specified structure if below target probe count."""
        if (structure.is_idle and 
            self.ai.supply_workers < self.ai.townhalls.amount * self.worker_ratio and 
            self.ai.can_afford(UnitTypeId.PROBE) and
            self.ai.supply_left > 0):  # Don't train if we're supply blocked
            structure.train(UnitTypeId.PROBE)
            return True
        return False

    async def build_pylon(self):
        """Build a pylon if we're close to being supply blocked."""
        current_time = self.ai.time
        
        # Don't try too often
        if current_time - self.last_pylon_attempt < 1.0:
            return False
            
        # Reset attempt counter if it's been a while
        if current_time - self.last_pylon_attempt > 10.0:
            self.pylon_attempt_count = 0
            
        # Check if we need supply - be more aggressive
        if (self.ai.supply_left >= self.supply_buffer or 
            self.ai.supply_cap >= 200 or 
            self.ai.already_pending(UnitTypeId.PYLON) > 0):
            return False
            
        # Check if we can afford it
        if not self.ai.can_afford(UnitTypeId.PYLON):
            if self.debug and self.pylon_attempt_count == 0:
                print(f"[Protoss Economy] Can't afford Pylon (need 100 minerals, have {self.ai.minerals})")
            self.last_pylon_attempt = current_time
            self.pylon_attempt_count += 1
            return False
            
        # Find a location near the nexus
        if not self.ai.townhalls:
            if self.debug and self.pylon_attempt_count == 0:
                print("[Protoss Economy] No Nexus found for Pylon placement")
            self.last_pylon_attempt = current_time
            return False
            
        nexus = self.ai.townhalls.first
        
        # Get mineral patches to avoid worker paths
        mineral_patches = self.ai.mineral_field
        gas_geysers = self.ai.vespene_geyser
        existing_structures = self.ai.structures
        
        # Try to find a good location for the pylon
        location = await self._find_safe_building_location(
            UnitTypeId.PYLON,
            nexus.position,
            mineral_patches,
            gas_geysers,
            existing_structures
        )
        
        if location:
            # Get the best probe for the job
            probes = self.ai.workers.filter(
                lambda w: w.is_idle and
                not w.is_constructing_scv and
                not w.is_gathering and
                not w.is_returning
            )
            
            if not probes:
                probes = self.ai.workers.filter(
                    lambda w: not w.is_constructing_scv
                )
            
            if probes:
                probe = probes.closest_to(location)
                
                # If probe is carrying resources, make it return them first
                if probe.is_carrying_resource:
                    if self.debug:
                        print(f"[Protoss Economy] Probe returning resources before building Pylon")
                    probe.return_resource()
                    self.last_pylon_attempt = current_time
                    return False
                    
                # If probe is doing something else, stop it
                if not probe.is_idle:
                    probe.stop()
                
                # Issue build command
                probe.stop()
                await probe.build(UnitTypeId.PYLON, location)
                if self.debug:
                    print(f"[Protoss Economy] Building Pylon at {location} with probe at {probe.position}")
                self.last_pylon_attempt = current_time
                self.pylon_attempt_count = 0
                return True
        
        if self.debug and self.pylon_attempt_count % 5 == 0:
            print("[Protoss Economy] Couldn't find a valid location for Pylon")
            
        self.last_pylon_attempt = current_time
        self.pylon_attempt_count += 1
        return False

    async def _find_safe_building_location(self, unit_type, near_position, mineral_patches, gas_geysers, existing_structures):
        """Find a safe location for building that avoids worker paths and resources."""
        import math
        
        # Define safe distances
        MINERAL_SAFE_DISTANCE = 4.0  # Don't build too close to minerals
        GAS_SAFE_DISTANCE = 3.0      # Don't build too close to gas
        STRUCTURE_SAFE_DISTANCE = 2.0 # Don't build too close to other structures
        BASE_DISTANCE_MIN = 8.0       # Minimum distance from base
        BASE_DISTANCE_MAX = 20.0      # Maximum distance from base
        
        # Calculate the center of mineral patches to find the "mineral side"
        if mineral_patches:
            mineral_center_x = sum(mineral.position.x for mineral in mineral_patches) / len(mineral_patches)
            mineral_center_y = sum(mineral.position.y for mineral in mineral_patches) / len(mineral_patches)
            mineral_center = Point2((mineral_center_x, mineral_center_y))
            
            # Calculate the direction from nexus to mineral center
            nexus_to_minerals = mineral_center - near_position
            mineral_direction = math.atan2(nexus_to_minerals.y, nexus_to_minerals.x)
            
            # The opposite side is 180 degrees from the mineral direction
            opposite_direction = mineral_direction + math.pi
            
            # Try positions on the opposite side of the base from minerals
            preferred_angles = [
                opposite_direction,  # Directly opposite
                opposite_direction + math.pi/4,  # 45 degrees from opposite
                opposite_direction - math.pi/4,  # -45 degrees from opposite
                opposite_direction + math.pi/2,  # 90 degrees from opposite
                opposite_direction - math.pi/2,  # -90 degrees from opposite
            ]
        else:
            # If no minerals found, use cardinal directions
            preferred_angles = [0, math.pi/2, math.pi, -math.pi/2]
        
        # Try different positions around the base
        for distance in range(int(BASE_DISTANCE_MIN), int(BASE_DISTANCE_MAX), 2):
            for angle in preferred_angles:
                # Calculate position using polar coordinates
                x = near_position.x + distance * math.cos(angle)
                y = near_position.y + distance * math.sin(angle)
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

    async def build_assimilators(self):
        """Build assimilators when we have enough probes."""
        # Only build assimilators if we have a nexus and can afford it
        if not self.ai.townhalls or not self.ai.can_afford(UnitTypeId.ASSIMILATOR):
            return False
            
        # Get all vespene geysers
        geysers = self.ai.vespene_geyser.closer_than(15, self.ai.townhalls.first)
        
        for geyser in geysers:
            # Check if we already have an assimilator here or are building one
            if (not self.ai.structures(UnitTypeId.ASSIMILATOR).closer_than(1, geyser).exists and
                not self.ai.already_pending(UnitTypeId.ASSIMILATOR)):
                
                # Get a probe to build the assimilator
                probe = self.ai.select_build_worker(geyser.position)
                if probe:
                    probe.build(UnitTypeId.ASSIMILATOR, geyser)
                    if self.debug:
                        print(f"[Protoss Economy] Building Assimilator at {geyser.position}")
                    return True
        
        return False

    async def manage_gas_probes(self):
        """Manage probe distribution between minerals and gas."""
        try:
            # Update probe assignments
            self._update_assimilator_assignments()
            
            # Get all assimilators
            for assimilator in self.ai.structures(UnitTypeId.ASSIMILATOR).ready:
                assimilator_tag = assimilator.tag
                worker_count = len(self.assimilator_assignments.get(assimilator_tag, set()))
                
                # If we have too few workers on this assimilator
                if worker_count < self.gas_workers_per_assimilator:
                    # Find mineral probes to send to gas
                    mineral_probes = self.ai.workers.filter(
                        lambda w: w.is_gathering and w.is_carrying_minerals
                    )
                    if mineral_probes and mineral_probes.amount > 8:  # Keep at least 8 on minerals
                        probe = mineral_probes.random
                        probe.gather(assimilator)
                        if self.debug and self.ai.time % 10 < 0.1:
                            print(f"[Protoss Economy] Sent mineral probe to gas")
                
                # If we have too many workers on this assimilator
                elif worker_count > self.gas_workers_per_assimilator:
                    # Send extra workers to gather minerals
                    excess_workers = worker_count - self.gas_workers_per_assimilator
                    for probe in self.ai.workers.random_group_of(min(excess_workers, worker_count)):
                        if probe.is_carrying_vespene:
                            # If probe is carrying gas, return it first
                            probe.return_resource()
                        else:
                            # Otherwise, send to gather minerals
                            await self.ai.distribute_workers()
                            if self.debug and self.ai.time % 10 < 0.1:
                                print(f"[Protoss Economy] Sent excess gas probe to minerals")
                            
        except Exception as e:
            if self.debug:
                print(f"[Protoss Economy] Error in manage_gas_probes: {e}")

    def _update_assimilator_assignments(self):
        """Update the tracking of which probes are assigned to which assimilators."""
        try:
            # Clear old assignments
            self.assimilator_assignments.clear()
            self.probe_assimilator_map.clear()
            
            # Get all assimilators
            assimilators = self.ai.structures(UnitTypeId.ASSIMILATOR).ready
            
            # For each assimilator, find probes that are gathering from it
            for assimilator in assimilators:
                assimilator_tag = assimilator.tag
                self.assimilator_assignments[assimilator_tag] = set()
                
                # Find probes gathering from this assimilator
                probes_at_assimilator = self.ai.workers.filter(
                    lambda w: w.is_gathering and 
                    w.order_target and 
                    w.order_target.tag == assimilator_tag
                )
                
                for probe in probes_at_assimilator:
                    self.assimilator_assignments[assimilator_tag].add(probe.tag)
                    self.probe_assimilator_map[probe.tag] = assimilator_tag
                    
        except Exception as e:
            if self.debug:
                print(f"[Protoss Economy] Error in _update_assimilator_assignments: {e}")

    async def expand_now(self):
        """Build a new nexus at the closest available expansion location."""
        try:
            # Don't expand too early in the game
            if hasattr(self, 'min_time_before_expand') and self.ai.time < self.min_time_before_expand:
                return False
                
            # Don't expand if we don't have a head manager or can't afford it
            if not hasattr(self, 'head') or not self.head or not self.ai.can_afford(UnitTypeId.NEXUS):
                return False
                
            # Check if we already have a nexus in progress
            pending_nexus = self.ai.already_pending(UnitTypeId.NEXUS)
            if pending_nexus > 0:
                return False
                
            # Get all expansion locations
            expansion_locations = self.ai.expansion_locations
            if not expansion_locations:
                return False
                
            # Get the main base (first nexus)
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
                # Skip if there's already a nexus nearby
                nearby_nexus = self.ai.structures.filter(
                    lambda unit: unit.type_id == UnitTypeId.NEXUS and 
                               unit.position.distance_to(location) < 15
                )
                if nearby_nexus:
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
                probe = self.ai.select_build_worker(location)
                if probe:
                    if self.debug:
                        print(f"[Protoss Economy] Building Nexus at {location}")
                    probe.build(UnitTypeId.NEXUS, location)
                    return True
            
            return False
            
        except Exception as e:
            if self.debug:
                print(f"[Protoss Economy] Error in expand_now: {e}")
            return False 