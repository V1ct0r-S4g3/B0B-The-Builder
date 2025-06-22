"""Handles all Zerg economy-related logic including drone production, resource gathering, and gas mining."""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2

class ZergEconomyManager:
    """Manages the Zerg bot's economy including drones, resources, and gas mining."""
    
    def __init__(self, ai):
        """Initialize the ZergEconomyManager with a reference to the main AI object."""
        self.ai = ai
        self.head = None  # Will be set by HeadManager
        self.worker_ratio = 24  # Target drone count per hatchery
        self.gas_workers_per_extractor = 3  # Zerg uses 3 drones per extractor
        self.supply_buffer = 8  # Overlord buffer to avoid supply block
        self.expand_when_minerals = 500  # When to expand
        self.min_time_before_expand = 0  # Can expand immediately
        self.extractor_started = set()  # Track started extractors
        self.last_overlord_time = 0
        self.last_drone_train_time = 0
        self.last_worker_distribution = 0
        self.last_overlord_attempt = 0  # Track last overlord attempt time
        self.overlord_attempt_count = 0  # Count consecutive overlord attempts
        self.debug = True  # Enable debug output
        self.building_placement_attempts = {}  # Track building placement attempts
        self.first_overlord_built = False  # Track if first overlord is built
        
        # Track drone assignments to extractors
        self.extractor_assignments = {}  # extractor_tag -> set of drone_tags
        self.drone_extractor_map = {}   # drone_tag -> extractor_tag

    async def on_start(self):
        """Called once at the start of the game."""
        print("Zerg Economy Manager initialized")
        await self.ai.distribute_workers()

    async def on_step(self):
        current_time = self.ai.time
        
        # DEBUG: Count extractors and overlords every step
        extractors_count = self.ai.structures(UnitTypeId.EXTRACTOR).ready.amount
        overlords_count = self.ai.units(UnitTypeId.OVERLORD).ready.amount
        overlords_pending = self.ai.units(UnitTypeId.OVERLORD).not_ready.amount
        print(f"[DEBUG] === ZERG ECONOMY COUNTS === Time: {current_time:.1f}s | Extractors: {extractors_count} | Overlords (ready): {overlords_count} | Overlords (building): {overlords_pending}")
        
        try:
            # Train drones
            for hatchery in self.ai.townhalls.ready:
                await self.train_drones(hatchery)

            # Build overlords
            await self.build_overlords()

            # Build extractors
            await self.build_extractors()
            
            # Manage gas drones
            await self.manage_gas_drones()
            
            # Distribute workers periodically
            if current_time - self.last_worker_distribution > 10.0:
                await self.ai.distribute_workers()
                self.last_worker_distribution = current_time

            # Check if we should expand
            if (self.head and self.head.should_expand() and current_time > self.min_time_before_expand and self.ai.minerals > self.expand_when_minerals):
                await self.expand_now()
                
        except Exception as e:
            if self.debug:
                print(f"[Zerg Economy] Error in on_step: {e}")
                import traceback
                traceback.print_exc()

    async def train_drones(self, structure):
        """Train drones from the specified structure if below target drone count."""
        if (self.ai.supply_workers < self.ai.townhalls.amount * self.worker_ratio and 
            self.ai.can_afford(UnitTypeId.DRONE) and
            self.ai.supply_left > 0):  # Don't train if we're supply blocked
            
            # For Zerg, we need to use larva to train drones
            larva = self.ai.larva
            if larva:
                larva.random.train(UnitTypeId.DRONE)
                if self.debug and self.ai.time % 10 < 0.1:
                    print(f"[Zerg Economy] Training Drone from larva")
                return True
        return False

    async def build_overlords(self):
        """Morph overlords from larva if we're close to being supply blocked."""
        current_time = self.ai.time

        # Don't try too often
        if current_time - self.last_overlord_attempt < 1.0:
            return False

        # Reset attempt counter if it's been a while
        if current_time - self.last_overlord_attempt > 10.0:
            self.overlord_attempt_count = 0

        # Check if we need supply - be more aggressive
        if (self.ai.supply_left >= self.supply_buffer or 
            self.ai.supply_cap >= 200 or 
            self.ai.already_pending(UnitTypeId.OVERLORD) > 0):
            return False

        # Check if we can afford it
        if not self.ai.can_afford(UnitTypeId.OVERLORD):
            if self.debug and self.overlord_attempt_count == 0:
                print(f"[Zerg Economy] Can't afford Overlord (need 100 minerals, have {self.ai.minerals})")
            self.last_overlord_attempt = current_time
            self.overlord_attempt_count += 1
            return False

        # Morph Overlord from larva
        larva = self.ai.larva
        if larva:
            larva.random.train(UnitTypeId.OVERLORD)
            if self.debug:
                print(f"[Zerg Economy] Morphing Overlord from larva")
            self.last_overlord_attempt = current_time
            self.overlord_attempt_count = 0
            return True
        else:
            if self.debug and self.overlord_attempt_count == 0:
                print("[Zerg Economy] No larva available to morph Overlord")
            self.last_overlord_attempt = current_time
            self.overlord_attempt_count += 1
            return False

    async def build_extractors(self):
        """Build extractors when we have enough drones."""
        # Only build extractors if we have a hatchery and can afford it
        if not self.ai.townhalls or not self.ai.can_afford(UnitTypeId.EXTRACTOR):
            return False
            
        # Get all vespene geysers
        geysers = self.ai.vespene_geyser.closer_than(15, self.ai.townhalls.first)
        
        for geyser in geysers:
            # Check if we already have an extractor here or are building one
            if (not self.ai.structures(UnitTypeId.EXTRACTOR).closer_than(1, geyser).exists and
                not self.ai.already_pending(UnitTypeId.EXTRACTOR)):
                
                # Get a drone to build the extractor
                drone = self.ai.select_build_worker(geyser.position)
                if drone:
                    drone.build(UnitTypeId.EXTRACTOR, geyser)
                    if self.debug:
                        print(f"[Zerg Economy] Building Extractor at {geyser.position}")
                    return True
        
        return False

    async def manage_gas_drones(self):
        """Manage drone distribution between minerals and gas."""
        try:
            # Update drone assignments
            self._update_extractor_assignments()
            
            # Get all extractors
            for extractor in self.ai.structures(UnitTypeId.EXTRACTOR).ready:
                extractor_tag = extractor.tag
                worker_count = len(self.extractor_assignments.get(extractor_tag, set()))
                
                # If we have too few workers on this extractor
                if worker_count < self.gas_workers_per_extractor:
                    # Find mineral drones to send to gas
                    mineral_drones = self.ai.workers.filter(
                        lambda w: w.is_gathering and w.is_carrying_minerals
                    )
                    if mineral_drones and mineral_drones.amount > 8:  # Keep at least 8 on minerals
                        drone = mineral_drones.random
                        drone.gather(extractor)
                        if self.debug and self.ai.time % 10 < 0.1:
                            print(f"[Zerg Economy] Sent mineral drone to gas")
                
                # If we have too many workers on this extractor
                elif worker_count > self.gas_workers_per_extractor:
                    # Send extra workers to gather minerals
                    excess_workers = worker_count - self.gas_workers_per_extractor
                    for drone in self.ai.workers.random_group_of(min(excess_workers, worker_count)):
                        if drone.is_carrying_vespene:
                            # If drone is carrying gas, return it first
                            drone.return_resource()
                        else:
                            # Otherwise, send to gather minerals
                            await self.ai.distribute_workers()
                            if self.debug and self.ai.time % 10 < 0.1:
                                print(f"[Zerg Economy] Sent excess gas drone to minerals")
                            
        except Exception as e:
            if self.debug:
                print(f"[Zerg Economy] Error in manage_gas_drones: {e}")

    def _update_extractor_assignments(self):
        """Update the tracking of which drones are assigned to which extractors."""
        try:
            # Clear old assignments
            self.extractor_assignments.clear()
            self.drone_extractor_map.clear()
            
            # Get all extractors
            extractors = self.ai.structures(UnitTypeId.EXTRACTOR).ready
            
            # For each extractor, find drones that are gathering from it
            for extractor in extractors:
                extractor_tag = extractor.tag
                self.extractor_assignments[extractor_tag] = set()
                
                # Find drones gathering from this extractor
                drones_at_extractor = self.ai.workers.filter(
                    lambda w: w.is_gathering and 
                    w.order_target and 
                    w.order_target.tag == extractor_tag
                )
                
                for drone in drones_at_extractor:
                    self.extractor_assignments[extractor_tag].add(drone.tag)
                    self.drone_extractor_map[drone.tag] = extractor_tag
                    
        except Exception as e:
            if self.debug:
                print(f"[Zerg Economy] Error in _update_extractor_assignments: {e}")

    async def expand_now(self):
        """Build a new hatchery at the closest available expansion location."""
        try:
            # Don't expand too early in the game
            if hasattr(self, 'min_time_before_expand') and self.ai.time < self.min_time_before_expand:
                return False
                
            # Don't expand if we don't have a head manager or can't afford it
            if not hasattr(self, 'head') or not self.head or not self.ai.can_afford(UnitTypeId.HATCHERY):
                return False
                
            # Check if we already have a hatchery in progress
            pending_hatchery = self.ai.already_pending(UnitTypeId.HATCHERY)
            if pending_hatchery > 0:
                return False
                
            # Get all expansion locations
            expansion_locations = self.ai.expansion_locations
            if not expansion_locations:
                return False
                
            # Get the main base (first hatchery)
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
                # Skip if there's already a hatchery nearby
                nearby_hatchery = self.ai.structures.filter(
                    lambda unit: unit.type_id == UnitTypeId.HATCHERY and 
                               unit.position.distance_to(location) < 15
                )
                if nearby_hatchery:
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
                drone = self.ai.select_build_worker(location)
                if drone:
                    if self.debug:
                        print(f"[Zerg Economy] Building Hatchery at {location}")
                    drone.build(UnitTypeId.HATCHERY, location)
                    return True
            
            return False
            
        except Exception as e:
            if self.debug:
                print(f"[Zerg Economy] Error in expand_now: {e}")
            return False 