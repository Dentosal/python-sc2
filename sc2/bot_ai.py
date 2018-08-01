import math
import random
from functools import partial

import logging
from typing import List, Dict, Set, Tuple, Any, Optional, Union # mypy type checking

# imports for mypy and pycharm autocomplete
from .game_state import GameState
from .game_data import GameData

logger = logging.getLogger(__name__)

from .position import Point2, Point3
from .data import Race, ActionResult, Attribute, race_worker, race_townhalls, race_gas
from .unit import Unit
from .cache import property_cache_forever
from .game_data import AbilityData, Cost
from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId
from .ids.upgrade_id import UpgradeId
from .units import Units


class BotAI(object):
    """Base class for bots."""

    EXPANSION_GAP_THRESHOLD = 15

    @property
    def enemy_race(self) -> Race:
        self.enemy_id = 3 - self.player_id
        return Race(self._game_info.player_races[self.enemy_id])

    @property
    def time(self) -> Union[int, float]:
        """ Returns time in seconds, assumes the game is played on 'faster' """
        return self.state.game_loop / 22.4 # / (1/1.4) * (1/16)

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

    @property
    def known_enemy_units(self) -> Units:
        """List of known enemy units, including structures."""
        return self.state.units.enemy

    @property
    def known_enemy_structures(self) -> Units:
        """List of known enemy units, structures only."""
        return self.state.units.enemy.structure

    @property
    def main_base_ramp(self) -> "Ramp":
        """ Returns the Ramp instance of the closest main-ramp to start location. Look in game_info.py for more information """
        return min(
            {ramp for ramp in self.game_info.map_ramps if len(ramp.upper) == 2},
            key=(lambda r: self.start_location.distance_to(r.top_center))
        )

    @property_cache_forever
    def expansion_locations(self) -> Dict[Point2, Units]:
        """List of possible expansion locations."""

        RESOURCE_SPREAD_THRESHOLD = 8.0  # Tried with Abyssal Reef LE, this was fine
        resources = self.state.mineral_field | self.state.vespene_geyser

        # Group nearby minerals together to form expansion locations
        r_groups = []
        for mf in resources:
            for g in r_groups:
                if any(mf.position.to2.distance_to(p.position.to2) < RESOURCE_SPREAD_THRESHOLD for p in g):
                    g.add(mf)
                    break
            else:  # not found
                r_groups.append({mf})

        # Filter out bases with only one mineral field
        r_groups = [g for g in r_groups if len(g) > 1]

        # Find centers
        avg = lambda l: sum(l) / len(l)
        pos = lambda u: u.position.to2
        centers = {Point2(tuple(map(avg, zip(*map(pos, g))))).rounded: g for g in r_groups}
        """ Returns dict with center of resources as key, resources (mineral field, vespene geyser) as value """
        return centers

    async def get_available_abilities(self, units: Union[List[Unit], Units], ignore_resource_requirements=False) -> List[List[AbilityId]]:
        """ Returns available abilities of one or more units. """
        # right know only checks cooldown, energy cost, and whether the ability has been researched
        return await self._client.query_available_abilities(units, ignore_resource_requirements)

    async def expand_now(self, building: Optional[UnitTypeId]=None, max_distance: Union[int, float]=10, location: Optional[Point2]=None):
        """Takes new expansion."""

        if not building:
            building = self.townhalls.first.type_id

        assert isinstance(building, UnitTypeId)

        if not location:
            location = await self.get_next_expansion()

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

            th = self.townhalls.first
            d = await self._client.query_pathing(th.position, el)
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

        expansion_locations = self.expansion_locations
        owned_expansions = self.owned_expansions
        worker_pool = []
        for idle_worker in self.workers.idle:
            mf = self.state.mineral_field.closest_to(idle_worker)
            await self.do(idle_worker.gather(mf))

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

            for x in range(0, deficit):
                if worker_pool:
                    w = worker_pool.pop()
                    if len(w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_RETURN]:
                        await self.do(w.move(g))
                        await self.do(w.return_resource(queue=True))
                    else:
                        await self.do(w.gather(g))

        for location, townhall in owned_expansions.items():
            actual = townhall.assigned_harvesters
            ideal = townhall.ideal_harvesters

            deficit = ideal - actual
            for x in range(0, deficit):
                if worker_pool:
                    w = worker_pool.pop()
                    mf = self.state.mineral_field.closest_to(townhall)
                    if len(w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_RETURN]:
                        await self.do(w.move(townhall))
                        await self.do(w.return_resource(queue=True))
                        await self.do(w.gather(mf, queue=True))
                    else:
                        await self.do(w.gather(mf))

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

    def can_afford(self, item_id: Union[UnitTypeId, UpgradeId, AbilityId]) -> "CanAffordWrapper":
        """Tests if the player has enough resources to build a unit or cast an ability."""
        if isinstance(item_id, UnitTypeId):
            unit = self._game_data.units[item_id.value]
            cost = self._game_data.calculate_ability_cost(unit.creation_ability)
        elif isinstance(item_id, UpgradeId):
            cost = self._game_data.upgrades[item_id.value].cost
        else:
            cost = self._game_data.calculate_ability_cost(item_id)

        return CanAffordWrapper(cost.minerals <= self.minerals, cost.vespene <= self.vespene)

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
            # check if target is in range (or is a self cast like stimpack)
            if ability_target == 1 or ability_target == 5 and isinstance(target, (Point2, Point3)) and unit.distance_to(target) <= cast_range: # TODO: replace numbers with enums
                return True
            elif ability_target in [3, 4] and isinstance(target, Unit) and unit.distance_to(target) <= cast_range:
                return True
            elif ability_target in [2, 4] and isinstance(target, (Point2, Point3)) and unit.distance_to(target) <= cast_range:
                return True
        return False

    def select_build_worker(self, pos: Union[Unit, Point2, Point3], force: bool=False) -> Optional[Unit]:
        """Select a worker to build a bulding with."""

        workers = self.workers.closer_than(20, pos) or self.workers
        for worker in workers.prefer_close_to(pos).prefer_idle:
            if not worker.orders or len(worker.orders) == 1 and worker.orders[0].ability.id in [AbilityId.MOVE,
                                                                                                AbilityId.HARVEST_GATHER,
                                                                                                AbilityId.HARVEST_RETURN]:
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
        assert self.can_afford(building)
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
        creationAbilityID = self._game_data.upgrades[upgrade_type.value].research_ability.id
        for s in self.units.structure.ready:
            for o in s.orders:
                if o.ability.id == creationAbilityID:
                    return o.progress
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

        p = await self.find_placement(building, near.rounded, max_distance, random_alternative, placement_step)
        if p is None:
            return ActionResult.CantFindPlacementLocation

        unit = unit or self.select_build_worker(p)
        if unit is None:
            return ActionResult.Error
        return await self.do(unit.build(building, p))

    async def do(self, action):
        assert self.can_afford(action)
        r = await self._client.actions(action, game_data=self._game_data)

        if not r:  # success
            cost = self._game_data.calculate_ability_cost(action.ability)
            self.minerals -= cost.minerals
            self.vespene -= cost.vespene

        else:
            logger.error(f"Error: {r} (action: {action})")

        return r

    async def do_actions(self, actions: List["UnitCommand"]):
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

    def _prepare_start(self, client, player_id, game_info, game_data):
        """Ran until game start to set game and player data."""
        self._client: "Client" = client
        self._game_info: "GameInfo" = game_info
        self._game_data: GameData = game_data

        self.player_id: int = player_id
        self.race: Race = Race(self._game_info.player_races[self.player_id])
        self._units_previous_map = dict()
        self.units: Units = Units([], game_data)

    def _prepare_first_step(self):
        """First step extra preparations. Must not be called before _prepare_step."""
        assert len(self.townhalls) == 1
        self._game_info.player_start_location = self.townhalls.first.position

    def _prepare_step(self, state):
        """Set attributes from new state before on_step."""
        self.state: GameState = state
        # need this for checking for new units
        self._units_previous_map.clear()
        for unit in self.units:
            self._units_previous_map[unit.tag] = unit

        self.units: Units = state.units.owned
        self.workers: Units = self.units(race_worker[self.race])
        self.townhalls: Units = self.units(race_townhalls[self.race])
        self.geysers: Units = self.units(race_gas[self.race])

        self.minerals: Union[float, int] = state.common.minerals
        self.vespene: Union[float, int] = state.common.vespene
        self.supply_used: Union[float, int] = state.common.food_used
        self.supply_cap: Union[float, int] = state.common.food_cap
        self.supply_left: Union[float, int] = self.supply_cap - self.supply_used

    def issue_events(self):
        self._issue_unit_dead_events()
        self._issue_unit_added_events()
        for unit in self.units:
            self._issue_building_complete_event(unit)

    def _issue_unit_added_events(self):
        for unit in self.units:
            if unit.tag not in self._units_previous_map:
                self.on_unit_created(unit)

    def _issue_building_complete_event(self, unit):
        if unit.build_progress < 1:
            return
        if unit.tag not in self._units_previous_map:
            return
        unit_prev = self._units_previous_map[unit.tag]
        if unit_prev.build_progress < 1:
            self.on_building_construction_complete(unit)

    def _issue_unit_dead_events(self):
        event = self.state.observation.raw_data.event
        if event is not None:
            for tag in event.dead_units:
                self.on_unit_destroyed(tag)

    def on_start(self):
        """Allows initializing the bot when the game data is available."""
        pass

    async def on_step(self, iteration):
        """Ran on every game step (looped in realtime mode)."""
        raise NotImplementedError

    def on_unit_destroyed(self, unit_tag):
        """ Override this in your bot class """
        pass

    def on_unit_created(self, unit):
        """ Override this in your bot class """
        pass

    def on_building_construction_complete(self, unit):
        """ Override this in your bot class """
        pass


class CanAffordWrapper(object):
    def __init__(self, can_afford_minerals, can_afford_vespene):
        self.can_afford_minerals = can_afford_minerals
        self.can_afford_vespene = can_afford_vespene

    def __bool__(self):
        return self.can_afford_minerals and self.can_afford_vespene

    @property
    def action_result(self):
        if not self.can_afford_vespene:
            return ActionResult.NotEnoughVespene
        elif not self.can_afford_minerals:
            return ActionResult.NotEnoughMinerals
        else:
            return None
