class ScoreDetails(object):
    """ Accessable in self.state.score during step function """
    def __init__(self, proto):
        self._data = proto
        self._proto = proto.score_details

    @property
    def score_type(self):
        return self._data.score_type

    @property
    def score(self):
        return self._data.score

    @property
    def idle_production_time(self):
        return self._proto.idle_production_time

    @property
    def idle_worker_time(self):
        return self._proto.idle_worker_time

    @property
    def total_value_units(self):
        return self._proto.total_value_units

    @property
    def total_value_structures(self):
        return self._proto.total_value_structures

    @property
    def killed_value_units(self):
        return self._proto.killed_value_units

    @property
    def killed_value_structures(self):
        return self._proto.killed_value_structures

    @property
    def collected_minerals(self):
        return self._proto.collected_minerals

    @property
    def collected_vespene(self):
        return self._proto.collected_vespene

    @property
    def collection_rate_minerals(self):
        return self._proto.collection_rate_minerals

    @property
    def collection_rate_vespene(self):
        return self._proto.collection_rate_vespene

    @property
    def spent_minerals(self):
        return self._proto.spent_minerals

    @property
    def spent_vespene(self):
        return self._proto.spent_vespene

    @property
    def food_used_none(self):
        return self._proto.food_used.none

    @property
    def food_used_army(self):
        return self._proto.food_used.army

    @property
    def food_used_economy(self):
        return self._proto.food_used.economy

    @property
    def food_used_technology(self):
        return self._proto.food_used.technology

    @property
    def food_used_upgrade(self):
        return self._proto.food_used.upgrade

    @property
    def killed_minerals_none(self):
        return self._proto.killed_minerals.none

    @property
    def killed_minerals_army(self):
        return self._proto.killed_minerals.army

    @property
    def killed_minerals_economy(self):
        return self._proto.killed_minerals.economy

    @property
    def killed_minerals_technology(self):
        return self._proto.killed_minerals.technology

    @property
    def killed_minerals_upgrade(self):
        return self._proto.killed_minerals.upgrade

    @property
    def killed_vespene_none(self):
        return self._proto.killed_vespene.none

    @property
    def killed_vespene_army(self):
        return self._proto.killed_vespene.army

    @property
    def killed_vespene_economy(self):
        return self._proto.killed_vespene.economy

    @property
    def killed_vespene_technology(self):
        return self._proto.killed_vespene.technology

    @property
    def killed_vespene_upgrade(self):
        return self._proto.killed_vespene.upgrade

    @property
    def lost_minerals_none(self):
        return self._proto.lost_minerals.none

    @property
    def lost_minerals_army(self):
        return self._proto.lost_minerals.army

    @property
    def lost_minerals_economy(self):
        return self._proto.lost_minerals.economy

    @property
    def lost_minerals_technology(self):
        return self._proto.lost_minerals.technology

    @property
    def lost_minerals_upgrade(self):
        return self._proto.lost_minerals.upgrade

    @property
    def lost_vespene_none(self):
        return self._proto.lost_vespene.none

    @property
    def lost_vespene_army(self):
        return self._proto.lost_vespene.army

    @property
    def lost_vespene_economy(self):
        return self._proto.lost_vespene.economy

    @property
    def lost_vespene_technology(self):
        return self._proto.lost_vespene.technology

    @property
    def lost_vespene_upgrade(self):
        return self._proto.lost_vespene.upgrade

    # TODO: friendly fire minerals, vespene, used minerals, vespene, total used minerals, vespene

    @property
    def total_damage_dealt_life(self):
        return self._proto.total_damage_dealt.life

    @property
    def total_damage_dealt_shields(self):
        return self._proto.total_damage_dealt.shields

    @property
    def total_damage_dealt_energy(self):
        return self._proto.total_damage_dealt.energy

    @property
    def total_damage_taken_life(self):
        return self._proto.total_damage_taken.life

    @property
    def total_damage_taken_shields(self):
        return self._proto.total_damage_taken.shields

    @property
    def total_damage_taken_energy(self):
        return self._proto.total_damage_taken.energy

    @property
    def total_healed_life(self):
        return self._proto.total_healed.life

    @property
    def total_healed_shields(self):
        return self._proto.total_healed.shields

    @property
    def total_healed_energy(self):
        return self._proto.total_healed.energy