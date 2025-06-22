"""Handles all Zerg military-related logic including unit production, build orders, and army control."""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2

class ZergMilitaryManager:
    """Manages the Zerg bot's military including unit production and army control."""
    
    def __init__(self, ai):
        """Initialize the ZergMilitaryManager with a reference to the main AI object."""
        self.ai = ai
        self.head = None  # Will be set by HeadManager
        self.debug = True  # Enable debug output
        
        # Build order tracking
        self.build_order_completed = False
        self.build_order_step = 0
        self.last_build_time = 0
        
        # Spawning Pool tracking
        self.spawning_pool_built = False
        self.roach_warren_built = False
        
        # Army control
        self.army_gathered = False
        self.attack_started = False
        self.last_wave_time = 0
        self.wave_size_threshold = 6  # Attack with 6+ units per wave
        self.wave_cooldown = 10  # Cooldown between waves
        
        # Rally point
        self.rally_point = None
        
        # Production tracking
        self.hatcheries = []

    async def on_start(self):
        """Called once at the start of the game."""
        print("Zerg Military Manager initialized")
        # Set rally point near the hatchery
        if self.ai.townhalls:
            hatchery = self.ai.townhalls.first
            self.rally_point = hatchery.position.towards(self.ai.game_info.map_center, 8)  # Closer to hatchery

    async def on_step(self):
        """Called every game step."""
        current_time = self.ai.time
        
        try:
            # Execute build order
            if not self.build_order_completed:
                await self._execute_build_order()
            
            # Train units
            await self._train_units()
            
            # Control army
            await self._control_army()
            
        except Exception as e:
            if self.debug:
                print(f"[Zerg Military] Error in on_step: {e}")
                import traceback
                traceback.print_exc()

    async def _execute_build_order(self):
        """Execute a basic Zerg build order."""
        current_time = self.ai.time
        
        # Don't build too frequently
        if current_time - self.last_build_time < 2.0:
            return
            
        self.last_build_time = current_time
        
        # Update structure tracking
        self.spawning_pool_built = self.ai.structures(UnitTypeId.SPAWNINGPOOL).exists
        self.roach_warren_built = self.ai.structures(UnitTypeId.ROACHWARREN).exists
        
        if self.debug and self.ai.time % 10 < 0.1:
            print(f"[Zerg Military] Spawning Pool: {self.spawning_pool_built}, Roach Warren: {self.roach_warren_built}")
        
        # Build order: Spawning Pool -> Roach Warren
        if not self.spawning_pool_built:
            # Build Spawning Pool
            if await self._try_build_structure(UnitTypeId.SPAWNINGPOOL):
                if self.debug:
                    print("[Zerg Military] Spawning Pool built")
                    
        elif not self.roach_warren_built:
            # Build Roach Warren
            if await self._try_build_structure(UnitTypeId.ROACHWARREN):
                self.build_order_completed = True
                if self.debug:
                    print("[Zerg Military] Roach Warren built - Build order completed")

    async def _try_build_structure(self, structure_type):
        """Try to build a structure."""
        if self.debug:
            print(f"[Zerg Military] === Starting _try_build_structure for {structure_type} ===")
            
        # Check if we can afford it
        if not self.ai.can_afford(structure_type):
            if self.debug:
                print(f"[Zerg Military] Cannot afford {structure_type}")
            return False
            
        # Check if we already have one or are building one
        if self.ai.structures(structure_type).exists or self.ai.already_pending(structure_type) > 0:
            if self.debug:
                print(f"[Zerg Military] Already have {structure_type}")
            return False
            
        # Find a location near the hatchery
        if not self.ai.townhalls:
            return False
            
        hatchery = self.ai.townhalls.first
        
        # Get mineral patches and gas geysers to avoid worker paths
        mineral_patches = self.ai.mineral_field
        gas_geysers = self.ai.vespene_geyser
        existing_structures = self.ai.structures
        
        # Try to find a good location for the structure
        location = await self._find_safe_building_location(
            structure_type,
            hatchery.position,
            mineral_patches,
            gas_geysers,
            existing_structures
        )
        
        if location:
            # Get a drone to build
            drone = self.ai.select_build_worker(location)
            if drone:
                drone.build(structure_type, location)
                if self.debug:
                    print(f"[Zerg Military] Building {structure_type} at {location}")
                return True
            
        return False

    async def _find_safe_building_location(self, unit_type, near_position, mineral_patches, gas_geysers, existing_structures):
        """Find a safe location for building that avoids worker paths and resources."""
        import math
        
        # Define safe distances
        MINERAL_SAFE_DISTANCE = 5.0  # Don't build too close to minerals
        GAS_SAFE_DISTANCE = 4.0      # Don't build too close to gas
        STRUCTURE_SAFE_DISTANCE = 3.0 # Don't build too close to other structures
        BASE_DISTANCE_MIN = 6.0       # Closer to base
        BASE_DISTANCE_MAX = 15.0      # Not too far from base
        
        # Calculate the center of mineral patches to find the "mineral side"
        if mineral_patches:
            mineral_center_x = sum(mineral.position.x for mineral in mineral_patches) / len(mineral_patches)
            mineral_center_y = sum(mineral.position.y for mineral in mineral_patches) / len(mineral_patches)
            mineral_center = Point2((mineral_center_x, mineral_center_y))
            
            # Calculate the direction from hatchery to mineral center
            hatchery_to_minerals = mineral_center - near_position
            mineral_direction = math.atan2(hatchery_to_minerals.y, hatchery_to_minerals.x)
            
            # The opposite side is 180 degrees from the mineral direction
            opposite_direction = mineral_direction + math.pi
            
            # Try positions on the opposite side of the base from minerals
            preferred_angles = [
                opposite_direction,  # Directly opposite
                opposite_direction + math.pi/6,  # 30 degrees from opposite
                opposite_direction - math.pi/6,  # -30 degrees from opposite
                opposite_direction + math.pi/3,  # 60 degrees from opposite
                opposite_direction - math.pi/3,  # -60 degrees from opposite
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
                        max_distance=2
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

    async def _train_units(self):
        """Train military units."""
        # Train Zerglings from Hatcheries (if Spawning Pool is ready)
        if self.spawning_pool_built:
            for hatchery in self.ai.townhalls.ready:
                if self.ai.can_afford(UnitTypeId.ZERGLING):
                    # Use larva to train zerglings
                    larva = self.ai.larva
                    if larva:
                        larva.random.train(UnitTypeId.ZERGLING)
                        if self.debug and self.ai.time % 10 < 0.1:
                            print("[Zerg Military] Training Zergling")
                        
        # Train Roaches from Hatcheries (if Roach Warren is ready)
        if self.roach_warren_built:
            for hatchery in self.ai.townhalls.ready:
                if self.ai.can_afford(UnitTypeId.ROACH):
                    # Use larva to train roaches
                    larva = self.ai.larva
                    if larva:
                        larva.random.train(UnitTypeId.ROACH)
                        if self.debug and self.ai.time % 10 < 0.1:
                            print("[Zerg Military] Training Roach")

    async def _control_army(self):
        """Control the army - gather units and attack."""
        current_time = self.ai.time
        
        # Get all military units
        army = self.ai.units.filter(
            lambda unit: unit.type_id in [UnitTypeId.ZERGLING, UnitTypeId.ROACH]
        )
        
        army_size = army.amount
        
        if self.debug and self.ai.time % 10 < 0.1:
            print(f"[Zerg Military] Army size: {army_size}")
        
        # Update rally point to be closer to the nearest hatchery
        if self.ai.townhalls:
            hatchery = self.ai.townhalls.first
            self.rally_point = hatchery.position.towards(self.ai.game_info.map_center, 8)
        
        # Check for enemy units near our base (defensive trigger)
        enemy_units_near_base = self.ai.enemy_units.filter(
            lambda unit: unit.position.distance_to(self.ai.townhalls.first.position) < 30
        )
        
        # If enemy units are near our base, go full defensive mode
        if enemy_units_near_base and army_size > 0:
            if self.debug:
                print(f"[Zerg Military] DEFENSIVE MODE: {enemy_units_near_base.amount} enemy units near base!")
            
            # Attack the closest enemy unit to our base
            closest_enemy = enemy_units_near_base.closest_to(self.ai.townhalls.first)
            
            for unit in army:
                unit.attack(closest_enemy)
            
            if self.debug and self.ai.time % 5 < 0.1:
                print(f"[Zerg Military] Army attacking enemy at {closest_enemy.position}")
            return
        
        # Check for enemy units in a wider radius (counter-attack range)
        enemy_units_in_range = self.ai.enemy_units.filter(
            lambda unit: unit.position.distance_to(self.ai.townhalls.first.position) < 50
        )
        
        # If enemy units are in counter-attack range and we have a decent army, pursue them
        if enemy_units_in_range and army_size >= 3:
            if self.debug and self.ai.time % 10 < 0.1:
                print(f"[Zerg Military] COUNTER-ATTACK: Pursuing {enemy_units_in_range.amount} enemy units!")
            
            # Attack the closest enemy unit
            closest_enemy = enemy_units_in_range.closest_to(self.ai.townhalls.first)
            
            for unit in army:
                unit.attack(closest_enemy)
            return
        
        # If we have units and haven't gathered them yet, gather at rally point
        if army_size > 0 and not self.army_gathered and self.rally_point:
            for unit in army:
                if unit.distance_to(self.rally_point) > 5:
                    unit.move(self.rally_point)
            if self.debug and self.ai.time % 10 < 0.1:
                print(f"[Zerg Military] Gathering {army_size} units at rally point")
            return
            
        # Mark army as gathered if they're close to rally point
        if army_size > 0 and self.rally_point:
            units_at_rally = army.filter(lambda unit: unit.distance_to(self.rally_point) <= 5)
            if units_at_rally.amount == army_size:
                self.army_gathered = True
        
        # Check if we should attack
        should_attack = (
            self.army_gathered and
            army_size >= self.wave_size_threshold and
            current_time - self.last_wave_time >= self.wave_cooldown and
            not self.attack_started
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
            elif self.ai.enemy_units and army_size >= 12:  # Only attack nearby enemies if we have a large army
                # Attack nearby enemy units (defensive)
                target = self.ai.enemy_units.closest_to(self.ai.townhalls.first)
                attack_type = "DEFENSIVE"
            else:
                # No good target, stay at rally point
                self.attack_started = False
                return
            
            # Issue attack command
            for unit in army:
                unit.attack(target)
            
            if self.debug:
                print(f"[Zerg Military] {attack_type} ATTACKING with {army_size} units")
            
            # Reset attack flag after a delay
            self.attack_started = False 