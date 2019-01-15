import math
import random

import logging
from typing import List, Dict, Set, Tuple, Any, Optional, Union # mypy type checking

# imports for mypy and pycharm autocomplete
from .game_state import GameState
from .game_data import GameData

logger = logging.getLogger(__name__)

from .position import Point2, Point3
from .data import Race, ActionResult, Attribute, race_worker, race_townhalls, race_gas, Target, Result
from .unit import Unit
from .cache import property_cache_forever, property_cache_once_per_frame
from .game_data import AbilityData
from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId
from .ids.upgrade_id import UpgradeId
from .units import Units


class BotAI:
    """Base class for bots."""

    EXPANSION_GAP_THRESHOLD = 15

    def __init__(self):
        # Specific opponent bot ID used in sc2ai ladder games http://sc2ai.net/
        # The bot ID will stay the same each game so your bot can "adapt" to the opponent
        self.opponent_id: int = None

    @property
    def enemy_race(self) -> Race:
        self.enemy_id = 3 - self.player_id
        return Race(self._game_info.player_races[self.enemy_id])

    @property
    def time(self) -> Union[int, float]:
        """ Returns time in seconds, assumes the game is played on 'faster' """
        return self.state.game_loop / 22.4  # / (1/1.4) * (1/16)

    @property
    def time_formatted(self) -> str:
        """ Returns time as string in min:sec format """
        t = self.time
        return f"{int(t // 60):02}:{int(t % 60):02}"

    @property
    def game_info(self) -> "GameInfo":
        return self._game_info

    @property
    def start_location(self) -> Point2:
        return self._game_info.player_start_location

    @property
    def enemy_start_locations(self) -> List[Point2]:
        """Possible start locations for enemies."""
        return self._game_info.start_locations

    @property_cache_once_per_frame
    def known_enemy_units(self) -> Units:
        """List of known enemy units, including structures."""
        return self.state.enemy_units

    @property_cache_once_per_frame
    def known_enemy_structures(self) -> Units:
        """List of known enemy units, structures only."""
        return self.state.enemy_units.structure

    @property
    def main_base_ramp(self) -> "Ramp":
        """ Returns the Ramp instance of the closest main-ramp to start location. Look in game_info.py for more information """
        if hasattr(self, "cached_main_base_ramp"):
            return self.cached_main_base_ramp
        self.cached_main_base_ramp = min(
            {ramp for ramp in self.game_info.map_ramps if len(ramp.upper2_for_ramp_wall) == 2},
            key=(lambda r: self.start_location.distance_to(r.top_center)),
        )
        return self.cached_main_base_ramp

    @property_cache_forever
    def expansion_locations(self) -> Dict[Point2, Units]:
        """List of possible expansion locations."""
        # RESOURCE_SPREAD_THRESHOLD = 144
        RESOURCE_SPREAD_THRESHOLD = 225
        geysers = self.state.vespene_geyser
        all_resources = self.state.resources

        # Group nearby minerals together to form expansion locations
        resource_groups = []
        for mf in all_resources:
            mf_height = self.get_terrain_height(mf.position)
            for cluster in resource_groups:
                # bases on standard maps dont have more than 10 resources
                if len(cluster) == 10:
                    continue
                if mf.position._distance_squared(
                    cluster[0].position
                ) < RESOURCE_SPREAD_THRESHOLD and mf_height == self.get_terrain_height(cluster[0].position):
                    cluster.append(mf)
                    break
            else:  # not found
                resource_groups.append([mf])
        # Filter out bases with only one mineral field
        resource_groups = [cluster for cluster in resource_groups if len(cluster) > 1]
        # distance offsets from a gas geysir
        offsets = [(x, y) for x in range(-9, 10) for y in range(-9, 10) if 75 >= x ** 2 + y ** 2 >= 49]
        centers = {}
        # for every resource group:
        for resources in resource_groups:
            # possible expansion points
            # resources[-1] is a gas geysir which always has (x.5, y.5) coordinates, just like an expansion
            possible_points = (
                Point2((offset[0] + resources[-1].position.x, offset[1] + resources[-1].position.y))
                for offset in offsets
            )
            # filter out points that are too near
            possible_points = [
                point
                for point in possible_points
                if all(point.distance_to(resource) >= (7 if resource in geysers else 6) for resource in resources)
            ]
            # choose best fitting point
            result = min(possible_points, key=lambda p: sum(p.distance_to(resource) for resource in resources))
            centers[result] = resources
        """ Returns dict with center of resources as key, resources (mineral field, vespene geyser) as value """
        return centers

    async def get_available_abilities(self, units: Union[List[Unit], Units], ignore_resource_requirements=False) -> List[List[AbilityId]]:
        """ Returns available abilities of one or more units. """
        # right know only checks cooldown, energy cost, and whether the ability has been researched
        return await self._client.query_available_abilities(units, ignore_resource_requirements)

    async def expand_now(self, building: UnitTypeId=None, max_distance: Union[int, float]=10, location: Optional[Point2]=None):
        """Takes new expansion."""

        if not building:
            # self.race is never Race.Random
            start_townhall_type = {Race.Protoss: UnitTypeId.NEXUS, Race.Terran: UnitTypeId.COMMANDCENTER, Race.Zerg: UnitTypeId.HATCHERY}
            building = start_townhall_type[self.race]

        assert isinstance(building, UnitTypeId)

        if not location:
            location = await self.get_next_expansion()
        
        if location:
            await self.build(building, near=location, max_distance=max_distance, random_alternative=False, placement_step=1)

    async def get_next_expansion(self) -> Optional[Point2]:
        """Find next expansion location."""

        closest = None
        distance = math.inf
        for el in self.expansion_locations:
            def is_near_to_expansion(t):
                return t.position.distance_to(el) < self.EXPANSION_GAP_THRESHOLD

            if any(map(is_near_to_expansion, self.townhalls)):
                # already taken
                continue

            startp = self._game_info.player_start_location
            d = await self._client.query_pathing(startp, el)
            if d is None:
                continue

            if d < distance:
                distance = d
                closest = el

        return closest

    async def distribute_workers(self):
        """
        Distributes workers across all the bases taken.
        WARNING: This is quite slow when there are lots of workers or multiple bases.
        """

        # TODO:
        # OPTIMIZE: Assign idle workers smarter
        # OPTIMIZE: Never use same worker mutltiple times
        owned_expansions = self.owned_expansions
        worker_pool = []
        actions = []

        for idle_worker in self.workers.idle:
            mf = self.state.mineral_field.closest_to(idle_worker)
            actions.append(idle_worker.gather(mf))

        for location, townhall in owned_expansions.items():
            workers = self.workers.closer_than(20, location)
            actual = townhall.assigned_harvesters
            ideal = townhall.ideal_harvesters
            excess = actual - ideal
            if actual > ideal:
                worker_pool.extend(workers.random_group_of(min(excess, len(workers))))
                continue
        for g in self.geysers:
            workers = self.workers.closer_than(5, g)
            actual = g.assigned_harvesters
            ideal = g.ideal_harvesters
            excess = actual - ideal
            if actual > ideal:
                worker_pool.extend(workers.random_group_of(min(excess, len(workers))))
                continue

        for g in self.geysers:
            actual = g.assigned_harvesters
            ideal = g.ideal_harvesters
            deficit = ideal - actual

            for _ in range(deficit):
                if worker_pool:
                    w = worker_pool.pop()
                    if len(w.orders) == 1 and w.orders[0].ability.id is AbilityId.HARVEST_RETURN:
                        actions.append(w.move(g))
                        actions.append(w.return_resource(queue=True))
                    else:
                        actions.append(w.gather(g))

        for location, townhall in owned_expansions.items():
            actual = townhall.assigned_harvesters
            ideal = townhall.ideal_harvesters

            deficit = ideal - actual
            for x in range(0, deficit):
                if worker_pool:
                    w = worker_pool.pop()
                    mf = self.state.mineral_field.closest_to(townhall)
                    if len(w.orders) == 1 and w.orders[0].ability.id is AbilityId.HARVEST_RETURN:
                        actions.append(w.move(townhall))
                        actions.append(w.return_resource(queue=True))
                        actions.append(w.gather(mf, queue=True))
                    else:
                        actions.append(w.gather(mf))

        await self.do_actions(actions)

    @property
    def owned_expansions(self):
        """List of expansions owned by the player."""

        owned = {}
        for el in self.expansion_locations:
            def is_near_to_expansion(t):
                return t.position.distance_to(el) < self.EXPANSION_GAP_THRESHOLD

            th = next((x for x in self.townhalls if is_near_to_expansion(x)), None)
            if th:
                owned[el] = th

        return owned

    def can_feed(self, unit_type: UnitTypeId) -> bool:
        """ Checks if you have enough free supply to build the unit """
        required = self._game_data.units[unit_type.value]._proto.food_required
        return required == 0 or self.supply_left >= required

    def can_afford(self, item_id: Union[UnitTypeId, UpgradeId, AbilityId], check_supply_cost: bool=True) -> "CanAffordWrapper":
        """Tests if the player has enough resources to build a unit or cast an ability."""
        enough_supply = True
        if isinstance(item_id, UnitTypeId):
            unit = self._game_data.units[item_id.value]
            cost = self._game_data.calculate_ability_cost(unit.creation_ability)
            if check_supply_cost:
                enough_supply = self.can_feed(item_id)
        elif isinstance(item_id, UpgradeId):
            cost = self._game_data.upgrades[item_id.value].cost
        else:
            cost = self._game_data.calculate_ability_cost(item_id)

        return CanAffordWrapper(cost.minerals <= self.minerals, cost.vespene <= self.vespene, enough_supply)

    async def can_cast(self, unit: Unit, ability_id: AbilityId, target: Optional[Union[Unit, Point2, Point3]]=None, only_check_energy_and_cooldown: bool=False, cached_abilities_of_unit: List[AbilityId]=None) -> bool:
        """Tests if a unit has an ability available and enough energy to cast it.
        See data_pb2.py (line 161) for the numbers 1-5 to make sense"""
        assert isinstance(unit, Unit)
        assert isinstance(ability_id, AbilityId)
        assert isinstance(target, (type(None), Unit, Point2, Point3))
        # check if unit has enough energy to cast or if ability is on cooldown
        if cached_abilities_of_unit:
            abilities = cached_abilities_of_unit
        else:
            abilities = (await self.get_available_abilities([unit]))[0]

        if ability_id in abilities:
            if only_check_energy_and_cooldown:
                return True
            cast_range = self._game_data.abilities[ability_id.value]._proto.cast_range
            ability_target = self._game_data.abilities[ability_id.value]._proto.target
            # Check if target is in range (or is a self cast like stimpack)
            if ability_target == 1 or ability_target == Target.PointOrNone.value and isinstance(target, (Point2, Point3)) and unit.distance_to(target) <= cast_range: # cant replace 1 with "Target.None.value" because ".None" doesnt seem to be a valid enum name
                return True
            # Check if able to use ability on a unit
            elif ability_target in {Target.Unit.value, Target.PointOrUnit.value} and isinstance(target, Unit) and unit.distance_to(target) <= cast_range:
                return True
            # Check if able to use ability on a position
            elif ability_target in {Target.Point.value, Target.PointOrUnit.value} and isinstance(target, (Point2, Point3)) and unit.distance_to(target) <= cast_range:
                return True
        return False

    def select_build_worker(self, pos: Union[Unit, Point2, Point3], force: bool=False) -> Optional[Unit]:
        """Select a worker to build a bulding with."""

        workers = self.workers.closer_than(20, pos) or self.workers
        for worker in workers.prefer_close_to(pos).prefer_idle:
            if not worker.orders or len(worker.orders) == 1 and worker.orders[0].ability.id in {AbilityId.MOVE,
                                                                                                AbilityId.HARVEST_GATHER,
                                                                                                AbilityId.HARVEST_RETURN}:
                return worker

        return workers.random if force else None

    async def can_place(self, building: Union[AbilityData, AbilityId, UnitTypeId], position: Point2) -> bool:
        """Tests if a building can be placed in the given location."""

        assert isinstance(building, (AbilityData, AbilityId, UnitTypeId))

        if isinstance(building, UnitTypeId):
            building = self._game_data.units[building.value].creation_ability
        elif isinstance(building, AbilityId):
            building = self._game_data.abilities[building.value]

        r = await self._client.query_building_placement(building, [position])
        return r[0] == ActionResult.Success

    async def find_placement(self, building: UnitTypeId, near: Union[Unit, Point2, Point3], max_distance: int=20, random_alternative: bool=True, placement_step: int=2) -> Optional[Point2]:
        """Finds a placement location for building."""

        assert isinstance(building, (AbilityId, UnitTypeId))
        assert isinstance(near, Point2)

        if isinstance(building, UnitTypeId):
            building = self._game_data.units[building.value].creation_ability
        else:  # AbilityId
            building = self._game_data.abilities[building.value]

        if await self.can_place(building, near):
            return near

        if max_distance == 0:
            return None

        for distance in range(placement_step, max_distance, placement_step):
            possible_positions = [Point2(p).offset(near).to2 for p in (
                    [(dx, -distance) for dx in range(-distance, distance + 1, placement_step)] +
                    [(dx, distance) for dx in range(-distance, distance + 1, placement_step)] +
                    [(-distance, dy) for dy in range(-distance, distance + 1, placement_step)] +
                    [(distance, dy) for dy in range(-distance, distance + 1, placement_step)]
            )]
            res = await self._client.query_building_placement(building, possible_positions)
            possible = [p for r, p in zip(res, possible_positions) if r == ActionResult.Success]
            if not possible:
                continue

            if random_alternative:
                return random.choice(possible)
            else:
                return min(possible, key=lambda p: p.distance_to(near))
        return None

    def already_pending_upgrade(self, upgrade_type: UpgradeId) -> Union[int, float]:
        """ Check if an upgrade is being researched
        Return values:
        0: not started
        0 < x < 1: researching
        1: finished
        """
        assert isinstance(upgrade_type, UpgradeId)
        if upgrade_type in self.state.upgrades:
            return 1
        level = None
        if "LEVEL" in upgrade_type.name:
            level = upgrade_type.name[-1]
        creationAbilityID = self._game_data.upgrades[upgrade_type.value].research_ability.id
        for structure in self.units.structure.ready:
            for order in structure.orders:
                if order.ability.id is creationAbilityID:
                    if level and order.ability.button_name[-1] != level:
                        return 0
                    return order.progress
        return 0

    def already_pending(self, unit_type: Union[UpgradeId, UnitTypeId], all_units: bool=False) -> int:
        """
        Returns a number of buildings or units already in progress, or if a
        worker is en route to build it. This also includes queued orders for
        workers and build queues of buildings.

        If all_units==True, then build queues of other units (such as Carriers
        (Interceptors) or Oracles (Stasis Ward)) are also included.
        """

        # TODO / FIXME: SCV building a structure might be counted as two units

        if isinstance(unit_type, UpgradeId):
            return self.already_pending_upgrade(unit_type)
            
        ability = self._game_data.units[unit_type.value].creation_ability

        amount = len(self.units(unit_type).not_ready)

        if all_units:
            amount += sum([o.ability == ability for u in self.units for o in u.orders])
        else:
            amount += sum([o.ability == ability for w in self.workers for o in w.orders])
            amount += sum([egg.orders[0].ability == ability for egg in self.units(UnitTypeId.EGG)])

        return amount

    async def build(self, building: UnitTypeId, near: Union[Point2, Point3], max_distance: int=20, unit: Optional[Unit]=None, random_alternative: bool=True, placement_step: int=2):
        """Build a building."""

        if isinstance(near, Unit):
            near = near.position.to2
        elif near is not None:
            near = near.to2
        else:
            return

        p = await self.find_placement(building, near.rounded, max_distance, random_alternative, placement_step)
        if p is None:
            return ActionResult.CantFindPlacementLocation

        unit = unit or self.select_build_worker(p)
        if unit is None or not self.can_afford(building):
            return ActionResult.Error
        return await self.do(unit.build(building, p))

    async def do(self, action):
        if not self.can_afford(action):
            logger.warning(f"Cannot afford action {action}")
            return ActionResult.Error

        r = await self._client.actions(action, game_data=self._game_data)

        if not r:  # success
            cost = self._game_data.calculate_ability_cost(action.ability)
            self.minerals -= cost.minerals
            self.vespene -= cost.vespene

        else:
            logger.error(f"Error: {r} (action: {action})")

        return r

    async def do_actions(self, actions: List["UnitCommand"]):
        if not actions:
            return None
        for action in actions:
            cost = self._game_data.calculate_ability_cost(action.ability)
            self.minerals -= cost.minerals
            self.vespene -= cost.vespene

        r = await self._client.actions(actions, game_data=self._game_data)
        return r

    async def chat_send(self, message: str):
        """Send a chat message."""
        assert isinstance(message, str)
        await self._client.chat_send(message, False)

    # For the functions below, make sure you are inside the boundries of the map size.
    def get_terrain_height(self, pos: Union[Point2, Point3, Unit]) -> int:
        """ Returns terrain height at a position. Caution: terrain height is not anywhere near a unit's z-coordinate. """
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self._game_info.terrain_height[pos] # returns int

    def in_placement_grid(self, pos: Union[Point2, Point3, Unit]) -> bool:
        """ Returns True if you can place something at a position. Remember, buildings usually use 2x2, 3x3 or 5x5 of these grid points.
        Caution: some x and y offset might be required, see ramp code:
        https://github.com/Dentosal/python-sc2/blob/master/sc2/game_info.py#L17-L18 """
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self._game_info.placement_grid[pos] != 0

    def in_pathing_grid(self, pos: Union[Point2, Point3, Unit]) -> bool:
        """ Returns True if a unit can pass through a grid point. """
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self._game_info.pathing_grid[pos] == 0

    def is_visible(self, pos: Union[Point2, Point3, Unit]) -> bool:
        """ Returns True if you have vision on a grid point. """
        # more info: https://github.com/Blizzard/s2client-proto/blob/9906df71d6909511907d8419b33acc1a3bd51ec0/s2clientprotocol/spatial.proto#L19
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self.state.visibility[pos] == 2

    def has_creep(self, pos: Union[Point2, Point3, Unit]) -> bool:
        """ Returns True if there is creep on the grid point. """
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self.state.creep[pos] != 0

    def _prepare_start(self, client, player_id, game_info, game_data):
        """Ran until game start to set game and player data."""
        self._client: "Client" = client
        self._game_info: "GameInfo" = game_info
        self._game_data: GameData = game_data

        self.player_id: int = player_id
        self.race: Race = Race(self._game_info.player_races[self.player_id])
        self._units_previous_map: dict = dict()
        self.units: Units = Units([], game_data)

    def _prepare_first_step(self):
        """First step extra preparations. Must not be called before _prepare_step."""
        if self.townhalls:
            self._game_info.player_start_location = self.townhalls.first.position
        self._game_info.map_ramps = self._game_info._find_ramps()

    def _prepare_step(self, state):
        """Set attributes from new state before on_step."""
        self.state: GameState = state
        # Required for events
        self._units_previous_map.clear()
        for unit in self.units:
            self._units_previous_map[unit.tag] = unit

        self.units: Units = state.own_units
        self.workers: Units = self.units(race_worker[self.race])
        self.townhalls: Units = self.units(race_townhalls[self.race])
        self.geysers: Units = self.units(race_gas[self.race])

        self.minerals: Union[float, int] = state.common.minerals
        self.vespene: Union[float, int] = state.common.vespene
        self.supply_used: Union[float, int] = state.common.food_used
        self.supply_cap: Union[float, int] = state.common.food_cap
        self.supply_left: Union[float, int] = self.supply_cap - self.supply_used
        # reset cached values
        self.cached_known_enemy_structures = None
        self.cached_known_enemy_units = None

    async def issue_events(self):
        """ This function will be automatically run from main.py and triggers the following functions:
        - on_unit_created
        - on_unit_destroyed
        - on_building_construction_complete
        """
        await self._issue_unit_dead_events()
        await self._issue_unit_added_events()
        for unit in self.units.structure:
            await self._issue_building_complete_event(unit)

    async def _issue_unit_added_events(self):
        for unit in self.units.not_structure:
            if unit.tag not in self._units_previous_map:
                await self.on_unit_created(unit)
        for unit in self.units.structure:
            if unit.tag not in self._units_previous_map:
                await self.on_building_construction_started(unit)

    async def _issue_building_complete_event(self, unit):
        if unit.build_progress < 1:
            return
        if unit.tag not in self._units_previous_map:
            return
        unit_prev = self._units_previous_map[unit.tag]
        if unit_prev.build_progress < 1:
            await self.on_building_construction_complete(unit)

    async def _issue_unit_dead_events(self):
        event = self.state.observation.raw_data.event
        if event is not None:
            for tag in event.dead_units:
                await self.on_unit_destroyed(tag)

    async def on_unit_destroyed(self, unit_tag):
        """ Override this in your bot class. """
        pass

    async def on_unit_created(self, unit: Unit):
        """ Override this in your bot class. """
        pass

    async def on_building_construction_started(self, unit: Unit):
        """ Override this in your bot class. """
        pass

    async def on_building_construction_complete(self, unit: Unit):
        """ Override this in your bot class. """
        pass

    def on_start(self):
        """Allows initializing the bot when the game data is available."""
        pass

    async def on_step(self, iteration: int):
        """Ran on every game step (looped in realtime mode)."""
        raise NotImplementedError

    def on_end(self, game_result: Result):
        """Ran at the end of a game."""
        pass


class CanAffordWrapper:
    def __init__(self, can_afford_minerals, can_afford_vespene, have_enough_supply):
        self.can_afford_minerals = can_afford_minerals
        self.can_afford_vespene = can_afford_vespene
        self.have_enough_supply = have_enough_supply

    def __bool__(self):
        return self.can_afford_minerals and self.can_afford_vespene and self.have_enough_supply

    @property
    def action_result(self):
        if not self.can_afford_vespene:
            return ActionResult.NotEnoughVespene
        elif not self.can_afford_minerals:
            return ActionResult.NotEnoughMinerals
        elif not self.have_enough_supply:
            return ActionResult.NotEnoughFood
        else:
            return None
