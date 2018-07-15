""" 
Bot that stays on 1base, goes 4 rax mass reaper
This bot is one of the first examples that are micro intensive
Bot has a chance to win against elite (=Difficulty.VeryHard) zerg AI

Bot made by Burny
"""

import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.player import Bot, Computer
from sc2.player import Human

class MassReaperBot(sc2.BotAI):
    def __init__(self):
        self.combinedActions = []

    async def on_step(self, iteration):
        self.combinedActions = []

        # make depots when running low on remaining supply
        if self.supply_left < 5 and self.townhalls.exists and self.supply_used >= 14 and self.can_afford(SUPPLYDEPOT) and self.units(SUPPLYDEPOT).not_ready.amount + self.already_pending(SUPPLYDEPOT) < 1:
            ws = self.workers.gathering
            if ws: # if workers available
                w = ws.furthest_to(ws.center)
                loc = await self.find_placement(SUPPLYDEPOT, w.position, placement_step=3)
                if loc:
                    self.combinedActions.append(w.build(SUPPLYDEPOT, loc))

        # lower all depots
        for depot in self.units(SUPPLYDEPOT):
            self.combinedActions.append(depot(MORPH_SUPPLYDEPOT_LOWER))

        # make orbital
        if self.units(BARRACKS).ready.exists and self.can_afford(BARRACKS): # change to orbital once can_afford bug is fixed for morphing units - combined actions ignores cost
            for cc in self.units(COMMANDCENTER).idle:
                self.combinedActions.append(cc(UPGRADETOORBITAL_ORBITALCOMMAND))

        # make up to 4 barracks
        if self.units.of_type([SUPPLYDEPOT, SUPPLYDEPOTLOWERED, SUPPLYDEPOTDROP]).ready.exists and self.units(BARRACKS).amount + self.already_pending(BARRACKS) < 4 and self.can_afford(BARRACKS):
            ws = self.workers.gathering
            if ws and self.townhalls.exists: # if workers available
                w = ws.furthest_to(ws.center)
                loc = await self.find_placement(BARRACKS, self.townhalls.random.position, placement_step=4)
                if loc:
                    self.combinedActions.append(w.build(BARRACKS, loc))

        # take gas when first barracks is on the way
        if self.units(BARRACKS).amount > 0 and self.already_pending(REFINERY) < 1:
            for th in self.townhalls:
                vgs = self.state.vespene_geyser.closer_than(10, th)
                for vg in vgs:
                    if await self.can_place(REFINERY, vg.position) and self.can_afford(REFINERY):
                        ws = self.workers.gathering
                        if ws.exists:
                            w = ws.closest_to(vg)
                            self.combinedActions.append(w.build(REFINERY, vg))


        # make scvs until 18, usually you only need 1:1 mineral:gas ratio for reapers, but if you dont lose any then you will need additional depots (mule income should take care of that)
        if self.can_afford(SCV) and self.supply_left > 0 and self.units(SCV).amount < 18 and (self.units(BARRACKS).ready.amount < 1 and self.units(COMMANDCENTER).idle.exists or self.units(ORBITALCOMMAND).idle.exists):
            for th in self.townhalls.idle:
                self.combinedActions.append(th.train(SCV))

        # make reapers 
        if self.can_afford(REAPER) and self.supply_left > 0:
            for rax in self.units(BARRACKS).idle:
                self.combinedActions.append(rax.train(REAPER))

        # saturate gas
        if iteration % 25 == 0:
            await self.distribute_workers()

        # micro reapers
        for r in self.units(REAPER):

            # move to range 15 of closest unit if reaper is below 20 hp and not regenerating
            enemyThreatsClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground).closer_than(15, r) # threats that can attack the reaper
            if r.health_percentage < 2/5 and enemyThreatsClose.exists:
                retreatPoints = self.neighbors8(r.position, distance=2) | self.neighbors8(r.position, distance=4)
                # filter points that are pathable
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreatsClose.closest_to(r)
                    retreatPoint = closestEnemy.position.furthest(retreatPoints)
                    self.combinedActions.append(r.move(retreatPoint))
                    continue # continue for loop, dont execute any of the following

            # reaper is ready to attack, shoot nearest ground unit
            enemyGroundUnits = self.known_enemy_units.not_flying.closer_than(5, r) # hardcoded attackrange of 5
            if r.weapon_cooldown == 0 and enemyGroundUnits.exists:
                enemyGroundUnits = enemyGroundUnits.sorted(lambda x: x.distance_to(r))
                closestEnemy = enemyGroundUnits[0]
                self.combinedActions.append(r.attack(closestEnemy))
                continue # continue for loop, dont execute any of the following
            
            # attack is on cooldown, check if grenade is on cooldown, if not then throw it to furthest enemy in range 5
            reaperGrenadeRange = self._game_data.abilities[KD8CHARGE_KD8CHARGE.value]._proto.cast_range
            enemyGroundUnitsInGrenadeRange = self.known_enemy_units.not_structure.not_flying.exclude_type([LARVA, EGG]).closer_than(reaperGrenadeRange, r)
            if enemyGroundUnitsInGrenadeRange.exists and (r.is_attacking or r.is_moving):
                abilities = await self.get_available_abilities(r)
                # if KD8CHARGE_KD8CHARGE in abilities
                enemyGroundUnitsInGrenadeRange = enemyGroundUnitsInGrenadeRange.sorted(lambda x: x.distance_to(r), reverse=True)
                furthestEnemy = None
                for enemy in enemyGroundUnitsInGrenadeRange:
                    if await self.can_cast(r, KD8CHARGE_KD8CHARGE, enemy, cached_abilities_of_unit=abilities):
                        furthestEnemy = enemy
                        break
                if furthestEnemy:
                    self.combinedActions.append(r(KD8CHARGE_KD8CHARGE, furthestEnemy))
                    continue # continue for loop, dont execute any of the following

            # move towards to max unit range if enemy is closer than 4
            # enemyThreatsVeryClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground and not x.is_snapshot).closer_than(3.5, r) # threats that can attack the reaper
            enemyThreatsVeryClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground).closer_than(4.5, r) # hardcoded attackrange - 0.5
            # threats that can attack the reaper
            if r.weapon_cooldown != 0 and enemyThreatsVeryClose.exists:
                retreatPoints = self.neighbors8(r.position, distance=2) | self.neighbors8(r.position, distance=4)               
                # filter points that are pathable
                retreatPoints = {x for x in retreatPoints if self.inPathingGrid(x)}
                if retreatPoints:
                    closestEnemy = enemyThreatsVeryClose.closest_to(r)
                    retreatPoint = max(retreatPoints, key=lambda x: x.distance_to(closestEnemy) - x.distance_to(r))
                    # retreatPoint = closestEnemy.position.furthest(retreatPoints)
                    self.combinedActions.append(r.move(retreatPoint))
                    continue # continue for loop, dont execute any of the following

            # move to nearest enemy ground unit/building because no enemy unit is closer than 5
            allEnemyGroundUnits = self.known_enemy_units.not_flying
            if allEnemyGroundUnits.exists:
                closestEnemy = allEnemyGroundUnits.closest_to(r)
                self.combinedActions.append(r.move(closestEnemy))
                continue # continue for loop, dont execute any of the following

            # move to random enemy start location if no enemy buildings have been seen
            self.combinedActions.append(r.move(random.choice(self.enemy_start_locations)))
            
        # manage idle scvs, would be taken care by distribute workers aswell
        if self.townhalls.exists:
            for w in self.workers.idle:
                th = self.townhalls.closest_to(w)
                mfs = self.state.mineral_field.closer_than(10, th)
                if mfs:
                    mf = mfs.closest_to(w)
                    self.combinedActions.append(w.gather(mf))

        # manage orbital energy and drop mules
        for oc in self.units(ORBITALCOMMAND).filter(lambda x: x.energy >= 50):
            mfs = self.state.mineral_field.closer_than(10, oc)
            if mfs:
                mf = max(mfs, key=lambda x:x.mineral_contents)
                self.combinedActions.append(oc(CALLDOWNMULE_CALLDOWNMULE, mf))

        # when running out of mineral fields near command center, fly to next base with minerals

        # execuite actions
        await self.do_actions(self.combinedActions)

    # helper functions

    def inPathingGrid(self, pos):
        # returns True if it is possible for a ground unit to move to pos - doesnt seem to work on ramps or near edges
        assert isinstance(pos, (Point2, Point3, Unit))
        pos = pos.position.to2.rounded
        return self._game_info.pathing_grid[(pos)] != 0

    def neighbors4(self, position, distance=1):
        p = position
        d = distance
        return {
            Point2((p.x - d, p.y)),
            Point2((p.x + d, p.y)),
            Point2((p.x, p.y - d)),
            Point2((p.x, p.y + d)),
        }

    def neighbors8(self, position, distance=1):
        p = position
        d = distance
        return self.neighbors4(position, distance) | {
            Point2((p.x - d, p.y - d)),
            Point2((p.x - d, p.y + d)),
            Point2((p.x + d, p.y - d)),
            Point2((p.x + d, p.y + d)),
        }



    # already pending function rewritten
    def already_pending(self, unit_type):
        ability = self._game_data.units[unit_type.value].creation_ability
        unitAttributes = self._game_data.units[unit_type.value].attributes

        buildings_in_construction = self.units.structure(unit_type).not_ready  
        if 8 not in unitAttributes and any(o.ability == ability for w in (self.units.not_structure) for o in w.orders): 
            return sum([o.ability == ability for w in (self.units - self.workers) for o in w.orders])
        # following checks for unit production in a building queue, like queen, also checks if hatch is morphing to LAIR
        elif any(o.ability.id == ability.id for w in (self.units.structure) for o in w.orders):
            return sum([o.ability.id == ability.id for w in (self.units.structure) for o in w.orders])
        # the following checks if a worker is about to start a construction (and for scvs still constructing if not checked for structures with same position as target)
        elif any(o.ability == ability for w in self.workers for o in w.orders):
            return sum([o.ability == ability for w in self.workers for o in w.orders]) \
                - buildings_in_construction.amount
        elif any(egg.orders[0].ability == ability for egg in self.units(EGG)):
            return sum([egg.orders[0].ability == ability for egg in self.units(EGG)])
        return 0

    # distribute workers function rewritten    
    async def distribute_workers(self, performanceHeavy=True, onlySaturateGas=False):
        # expansion_locations = self.expansion_locations
        # owned_expansions = self.owned_expansions


        mineralTags = [x.tag for x in self.state.units.mineral_field]
        # gasTags = [x.tag for x in self.state.units.vespene_geyser]
        geyserTags = [x.tag for x in self.geysers]

        workerPool = self.units & []
        workerPoolTags = set()

        # find all geysers that have surplus or deficit
        deficitGeysers = {}
        surplusGeysers = {}
        for g in self.geysers.filter(lambda x:x.vespene_contents > 0):
            # only loop over geysers that have still gas in them
            deficit = g.ideal_harvesters - g.assigned_harvesters
            if deficit > 0:
                deficitGeysers[g.tag] = {"unit": g, "deficit": deficit}
            elif deficit < 0:
                surplusWorkers = self.workers.closer_than(10, g).filter(lambda w:w not in workerPoolTags and len(w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_GATHER] and w.orders[0].target in geyserTags)
                # workerPool.extend(surplusWorkers)
                for i in range(-deficit):
                    if surplusWorkers.amount > 0:
                        w = surplusWorkers.pop()
                        workerPool.append(w)
                        workerPoolTags.add(w.tag)
                surplusGeysers[g.tag] = {"unit": g, "deficit": deficit}

        # find all townhalls that have surplus or deficit
        deficitTownhalls = {}
        surplusTownhalls = {}
        if not onlySaturateGas:
            for th in self.townhalls:
                deficit = th.ideal_harvesters - th.assigned_harvesters
                if deficit > 0:
                    deficitTownhalls[th.tag] = {"unit": th, "deficit": deficit}
                elif deficit < 0:
                    surplusWorkers = self.workers.closer_than(10, th).filter(lambda w:w.tag not in workerPoolTags and len(w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_GATHER] and w.orders[0].target in mineralTags)
                    # workerPool.extend(surplusWorkers)
                    for i in range(-deficit):
                        if surplusWorkers.amount > 0:
                            w = surplusWorkers.pop()
                            workerPool.append(w)
                            workerPoolTags.add(w.tag)
                    surplusTownhalls[th.tag] = {"unit": th, "deficit": deficit}

            if all([len(deficitGeysers) == 0, len(surplusGeysers) == 0, len(surplusTownhalls) == 0 or deficitTownhalls == 0]):
                # cancel early if there is nothing to balance
                return

        # check if deficit in gas less or equal than what we have in surplus, else grab some more workers from surplus bases
        deficitGasCount = sum(gasInfo["deficit"] for gasTag, gasInfo in deficitGeysers.items() if gasInfo["deficit"] > 0)
        surplusCount = sum(-gasInfo["deficit"] for gasTag, gasInfo in surplusGeysers.items() if gasInfo["deficit"] < 0)
        surplusCount += sum(-thInfo["deficit"] for thTag, thInfo in surplusTownhalls.items() if thInfo["deficit"] < 0)

        if deficitGasCount - surplusCount > 0:
            # grab workers near the gas who are mining minerals
            for gTag, gInfo in deficitGeysers.items():
                if workerPool.amount >= deficitGasCount:
                    break
                workersNearGas = self.workers.closer_than(10, gInfo["unit"]).filter(lambda w:w.tag not in workerPoolTags and len(w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_GATHER] and w.orders[0].target in mineralTags)
                while workersNearGas.amount > 0 and workerPool.amount < deficitGasCount:
                    w = workersNearGas.pop()
                    workerPool.append(w)
                    workerPoolTags.add(w.tag)

        # now we should have enough workers in the pool to saturate all gases, and if there are workers left over, make them mine at townhalls that have mineral workers deficit
        for gTag, gInfo in deficitGeysers.items():
            if performanceHeavy:
                # sort furthest away to closest (as the pop() function will take the last element)
                workerPool.sort(key=lambda x:x.distance_to(gInfo["unit"]), reverse=True)
            for i in range(gInfo["deficit"]):
                if workerPool.amount > 0:
                    w = workerPool.pop()
                    if len(w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_RETURN]:
                        self.combinedActions.append(w.gather(gInfo["unit"], queue=True))
                    else:
                        self.combinedActions.append(w.gather(gInfo["unit"]))

        if not onlySaturateGas:
            # if we now have left over workers, make them mine at bases with deficit in mineral workers
            for thTag, thInfo in deficitTownhalls.items():
                if performanceHeavy:
                    # sort furthest away to closest (as the pop() function will take the last element)
                    workerPool.sort(key=lambda x:x.distance_to(thInfo["unit"]), reverse=True)
                for i in range(thInfo["deficit"]):
                    if workerPool.amount > 0:
                        w = workerPool.pop()
                        mf = self.state.mineral_field.closer_than(10, thInfo["unit"]).closest_to(w)
                        if len(w.orders) == 1 and w.orders[0].ability.id in [AbilityId.HARVEST_RETURN]:
                            self.combinedActions.append(w.gather(mf, queue=True))
                        else:
                            self.combinedActions.append(w.gather(mf))

def main():
    sc2.run_game(sc2.maps.get("(2)CatalystLE"), [
        Bot(Race.Terran, MassReaperBot()),
        Computer(Race.Zerg, Difficulty.VeryHard)
    ], realtime=False)

if __name__ == '__main__':
    main()
