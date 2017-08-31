import random
from functools import partial

from .position import Point2, Point3
from .data import Race, ActionResult, Attribute, race_worker
from .action import UnitCommand
from .unit import Unit
from .ids.unit_typeid import UnitTypeId
from .ids.ability_id import AbilityId

from .tmpfix import creation_ability_from_unit_id

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
    def known_enemy_structures(self):
        return self.state.units.enemy.structure

    def can_afford(self, unit_type_id):
        unit_type = self._game_data.units[unit_type_id.value]
        return unit_type.cost.minerals <= self.minerals and unit_type.cost.vespene <= self.vespene

    def select_build_worker(self, pos, force=False):
        workers = self.workers.closer_than(20, pos) or self.workers
        for worker in workers.prefer_close_to(pos).prefer_idle:
            if not worker.orders or len(worker.orders) == 1 and worker.orders[0].ability.id in [AbilityId.MOVE, AbilityId.HARVEST_GATHER, AbilityId.HARVEST_RETURN]:
                return worker

        return workers.random if force else None

    async def can_place(self, building, position):
        assert isinstance(building, (AbilityId, UnitTypeId))
        if isinstance(building, UnitTypeId):
            building = creation_ability_from_unit_id(building)
        r = await self._client.query_building_placement(building, [position])
        return r[0] == ActionResult.Success

    async def find_placement(self, building, near, max_distance=20):
        assert isinstance(building, (AbilityId, UnitTypeId))
        assert self.can_afford(building)
        assert isinstance(near, Point2)

        if isinstance(building, UnitTypeId):
            building = creation_ability_from_unit_id(building)


        if await self.can_place(building, near):
            return near

        for distance in range(2, max_distance, 2):
            possible_positions = [Point2(p).offset(near).to2 for p in (
                [(dx, -distance) for dx in range(-distance, distance+1, 2)] +
                [(dx,  distance) for dx in range(-distance, distance+1, 2)] +
                [(-distance, dy) for dy in range(-distance, distance+1, 2)] +
                [( distance, dy) for dy in range(-distance, distance+1, 2)]
            )]
            res = await self._client.query_building_placement(building, possible_positions)
            possible = [p for r, p in zip(res, possible_positions) if r == ActionResult.Success]
            if not possible:
                continue

            for p in possible:
                p = Point3((*p, self.workers.random.position.z))

            return random.choice(possible)
        return None

    def already_pending(self, unit_type):
        ability = creation_ability_from_unit_id(unit_type)
        if self.units(unit_type).not_ready.exists:
            return True
        elif any(o.ability == ability for w in self.workers for o in w.orders):
            return True
        return False

    async def build(self, building, near, max_distance=20, unit=None):
        if isinstance(near, Unit):
            near = near.position.to2
        elif near is not None:
            near = near.to2

        p = await self.find_placement(building, near.rounded, max_distance)
        if p is None:
            return ActionResult.CantFindPlacementLocation

        unit = unit or self.select_build_worker(p)
        if unit is None:
            return ActionResult.Error
        return await self.do(unit.build(building, p))

    async def do(self, action):
        r = await self._client.actions(action, game_data=self._game_data)

        if not r: # success
            cost = self._game_data.calculate_ability_cost(action.ability)
            self.minerals -= cost.minerals
            self.vespene -= cost.vespene

        else:
            print(f"Error: {r} (action: {action})")

        # if r:
            # print("!a", action)
            # print("!r", r)
            # p = Point3((*action.target.to2, self.workers.random.position.z))
            # await self._client.debug_text("HERE", p)
            # exit("do::cannot")
        return r

    def _prepare_step(self, state):
        self.state = state
        self.units = state.units.owned
        self.workers = self.units(race_worker[self.race])

        self.minerals = state.common.minerals
        self.vespene = state.common.vespene
        self.supply_used = state.common.food_used
        self.supply_cap = state.common.food_cap
        self.supply_left = self.supply_cap - self.supply_used

    def on_start(self):
        pass

    async def on_step(self, do, state, game_loop):
        raise NotImplementedError
