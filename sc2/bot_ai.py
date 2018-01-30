import random
from functools import partial

import logging
logger = logging.getLogger(__name__)

from .constants import EGG

from .position import Point2, Point3
from .data import Race, ActionResult, Attribute, race_worker, race_townhalls
from .unit import Unit
from .cache import property_cache_forever
from .game_data import AbilityData, Cost
from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId
from .ids.upgrade_id import UpgradeId

class BotAI(object):
    def _prepare_start(self, client, player_id, game_info, game_data):
        self._client = client
        self._game_info = game_info
        self._game_data = game_data

        self.player_id = player_id
        self.race = Race(self._game_info.player_races[self.player_id])

    @property
    def game_info(self):
        return self._game_info

    @property
    def enemy_start_locations(self):
        return self._game_info.start_locations

    @property
    def known_enemy_units(self):
        return self.state.units.enemy

    @property
    def known_enemy_structures(self):
        return self.state.units.enemy.structure

    @property
    @property_cache_forever
    def expansion_locations(self):
        DISTANCE_THRESHOLD = 8.0 # Tried with Abyssal Reef LE, this was fine
        resources = [
            r.position.to2
            for r in self.state.mineral_field | self.state.vespene_geyser
        ]

        # Group nearby minerals together to form expansion locations
        r_groups = []
        for mf in resources:
            for g in r_groups:
                if any(mf.distance_to(p) < DISTANCE_THRESHOLD for p in g):
                    g.add(mf)
                    break
            else: # not found
                r_groups.append({mf})

        # Filter out bases with only one mineral field
        r_groups = [g for g in r_groups if len(g) > 1]

        # Find centers
        avg = lambda l: sum(l) / len(l)
        centers = [Point2(tuple(map(avg, zip(*g)))) for g in r_groups]

        # Not always accurate, but good enought for now.
        return [c.rounded for c in centers]

    async def expand_now(self, building=None, max_distance=10):
        if not building:
            building = self.townhalls.first.type_id

        assert isinstance(building, UnitTypeId)

        location = await self.get_next_expansion()
        await self.build(building, near=location, max_distance=max_distance, random_alternative=False,
                         placement_step=1)

    async def get_next_expansion(self):
        DISTANCE_THRESHOLD = 15.0
        closest = None
        distance = float("inf")
        for el in self.expansion_locations:
            def is_near_to_expansion(t): return t.position.distance_to(el) < DISTANCE_THRESHOLD
            if any([t for t in map(is_near_to_expansion, self.townhalls)]):
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


    def can_afford(self, item_id):
        if isinstance(item_id, UnitTypeId):
            unit = self._game_data.units[item_id.value]
            cost = self._game_data.calculate_ability_cost(unit.creation_ability)
        elif isinstance(item_id, UpgradeId):
            cost = self._game_data.upgrades[item_id.value].cost
        else:
            cost = self._game_data.calculate_ability_cost(item_id)

        return cost.minerals <= self.minerals and cost.vespene <= self.vespene

    def select_build_worker(self, pos, force=False):
        workers = self.workers.closer_than(20, pos) or self.workers
        for worker in workers.prefer_close_to(pos).prefer_idle:
            if not worker.orders or len(worker.orders) == 1 and worker.orders[0].ability.id in [AbilityId.MOVE, AbilityId.HARVEST_GATHER, AbilityId.HARVEST_RETURN]:
                return worker

        return workers.random if force else None

    async def can_place(self, building, position):
        assert isinstance(building, (AbilityData, AbilityId, UnitTypeId))

        if isinstance(building, UnitTypeId):
            building = self._game_data.units[building.value].creation_ability
        elif isinstance(building, AbilityId):
            building = self._game_data.abilities[building.value]

        r = await self._client.query_building_placement(building, [position])
        return r[0] == ActionResult.Success

    async def find_placement(self, building, near, max_distance=20, random_alternative=True, placement_step=2):
        assert isinstance(building, (AbilityId, UnitTypeId))
        assert self.can_afford(building)
        assert isinstance(near, Point2)

        if isinstance(building, UnitTypeId):
            building = self._game_data.units[building.value].creation_ability
        else: # AbilityId
            building = self._game_data.abilities[building.value]

        if await self.can_place(building, near):
            return near

        for distance in range(placement_step, max_distance, placement_step):
            possible_positions = [Point2(p).offset(near).to2 for p in (
                [(dx, -distance) for dx in range(-distance, distance+1, placement_step)] +
                [(dx,  distance) for dx in range(-distance, distance+1, placement_step)] +
                [(-distance, dy) for dy in range(-distance, distance+1, placement_step)] +
                [( distance, dy) for dy in range(-distance, distance+1, placement_step)]
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

    def already_pending(self, unit_type):
        ability = self._game_data.units[unit_type.value].creation_ability
        if self.units(unit_type).not_ready.exists:
            return True
        elif any(o.ability == ability for w in self.workers for o in w.orders):
            return True
        elif any(egg.orders[0].ability == ability for egg in self.units(EGG)):
            return True
        return False

    async def build(self, building, near, max_distance=20, unit=None, random_alternative=True, placement_step=2):
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

        if not r: # success
            cost = self._game_data.calculate_ability_cost(action.ability)
            self.minerals -= cost.minerals
            self.vespene -= cost.vespene

        else:
            logger.error(f"Error: {r} (action: {action})")

        return r

    async def chat_send(self, message):
        assert isinstance(message, str)
        await self._client.chat_send(message, False)

    def _prepare_step(self, state):
        self.state = state
        self.units = state.units.owned
        self.workers = self.units(race_worker[self.race])
        self.townhalls = self.units(race_townhalls[self.race])

        self.minerals = state.common.minerals
        self.vespene = state.common.vespene
        self.supply_used = state.common.food_used
        self.supply_cap = state.common.food_cap
        self.supply_left = self.supply_cap - self.supply_used

    def on_start(self):
        pass

    async def on_step(self, iteration):
        raise NotImplementedError
