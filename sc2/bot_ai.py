from functools import partial

from .data import ActionResult

class BotAI(object):
    def _prepare_start(self, client, game_info, game_data):
        self._client = client
        self._game_info = game_info
        self._game_data = game_data
        self.do = partial(self._client.actions, game_data=game_data)

    @property
    def game_info(self):
        return self._game_info

    @property
    def enemy_start_locations(self):
        return self._game_info.start_locations

    async def can_place(self, building, position):
        ability_id = self._game_data.find_ability_by_name(f"Build {building}").id
        r = await self._client.query_building_placement(ability_id, [position])
        return r[0] == ActionResult.Success

    async def select_placement(self, building, positions):
        ability_id = self._game_data.find_ability_by_name(f"Build {building}").id
        r = await self._client.query_building_placement(ability_id, positions)
        print(r)
        exit("!!!!")

    def _prepare_step(self, state):
        self.units = state.units.owned
        self.minerals = state.common.minerals
        self.vespnene = state.common.vespene

    def on_start(self):
        pass

    async def on_step(self, do, state, game_loop):
        raise NotImplementedError
