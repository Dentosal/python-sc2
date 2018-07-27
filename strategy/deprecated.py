from bot_ai_extended import *


class Strategy_111Expand(Bot_AI_Extended):
    """Implementation of the 111 Expand Strategy"""
   
    def __init__(self):
        build_order = [

            # slightly modified
           
            (supply_at_least(14), add_supply(prioritize=True)),
            (supply_at_least(15), add_gas()),
            (supply_at_least(16), construct(UnitTypeId.BARRACKS, prioritize=True)),
            (all_of(supply_at_least(19), unit_count(UnitTypeId.BARRACKS, 1, include_pending=False)), train_unit(UnitTypeId.ORBITALCOMMAND, on_building = UnitTypeId.COMMANDCENTER)),
            (supply_at_least(19), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)),
            (supply_at_least(20), construct(UnitTypeId.FACTORY)),
            (supply_at_least(20), add_supply(prioritize=True)),
            (supply_at_least(20), add_gas()),
           # (supply_at_least(20), expand(prioritize=True)), # test
            (all_of(supply_at_least(20), unit_count(UnitTypeId.MARINE, 1, include_pending=False)), train_unit(UnitTypeId.REAPER, on_building = UnitTypeId.BARRACKS)),
            (all_of(supply_at_least(24), unit_count(UnitTypeId.FACTORY, 1, include_pending=False)), train_unit(UnitTypeId.HELLION, on_building = UnitTypeId.FACTORY)),
            (supply_at_least(24), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS)), # 1 Supply Missing
            (all_of(supply_at_least(26), unit_count(UnitTypeId.FACTORY, 1, include_pending=False)), construct(UnitTypeId.STARPORT, prioritize=True)),
            (supply_at_least(26), train_unit(UnitTypeId.HELLION, on_building=UnitTypeId.FACTORY)), # 2 Supply Missing
            (supply_at_least(27), add_supply(prioritize=True)),
            (supply_at_least(27), train_unit(UnitTypeId.HELLION, on_building=UnitTypeId.FACTORY)),
            (supply_at_least(31), add_supply(prioritize=True)),
            (all_of(supply_at_least(31), unit_count(UnitTypeId.STARPORT, 1, include_pending=False)), train_unit(UnitTypeId.STARPORTTECHLAB, on_building = UnitTypeId.STARPORT)),
            (all_of(supply_at_least(32), unit_count(UnitTypeId.STARPORTTECHLAB, 1, include_pending=False)), train_unit(UnitTypeId.BANSHEE, on_building = UnitTypeId.STARPORT)), # eigentlich TECHLAB bei unitcount
            # TODO  (all_of(supply_at_least(32), unit_count(UnitTypeId.TECHLAB, 1, include_pending=False)), train_unit(UnitTypeId.BANSHEECLOAK, on_building = UnitTypeId.STARPORT),
            
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1, include_pending=False), expand(prioritize=True, repeatable=False)), # eigentlich 36
           # (unit_count(UnitTypeId.STARPORTTECHLAB, 1, include_pending=False), research(UnitTypeId.STARPORTTECHLAB, AbilityId.RESEARCH_BANSHEECLOAKINGFIELD)),
            
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1), train_unit(UnitTypeId.MARINE, on_building=UnitTypeId.BARRACKS, repeatable=True)),
            #((supply_at_least(36), unit_count(UnitTypeId.BARRACKS, 5, include_pending=True)), add_supply(prioritize=True)),
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1), train_unit(UnitTypeId.BANSHEE, on_building=UnitTypeId.STARPORT, repeatable=True)),
            (unit_count(UnitTypeId.STARPORTTECHLAB, 1), train_unit(UnitTypeId.HELLION, on_building=UnitTypeId.FACTORY, repeatable=True))
         
        ]
        self.attack = False
        self.build_order = BuildOrder(self, build_order, worker_count=init_worker_count)
       
        
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_order.execute_build()
        await self.build_order.increase_supply()
        await self.build_order.increase_workers()
            
        if not self.cloak_started and self.units(STARPORTTECHLAB).ready.exists and self.can_afford(RESEARCH_BANSHEECLOAKINGFIELD):
            upgrader = self.units(STARPORTTECHLAB).ready.first
            await self.do(upgrader(RESEARCH_BANSHEECLOAKINGFIELD))
            self.cloak_started = True

        if iteration % gameloops_check_frequency == 0:
            await auto_attack(self)
            


def main():
    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Terran, Strategy_111Expand()),
        # Bot(Race.Terran, TerranBuildOrderBot()),
        Computer(Race.Random, Difficulty.Hard)
    ], realtime=False, save_replay_as="111ExpandVsEasy.SC2Replay")

if __name__ == '__main__':
    main()


def bot_ai():
    try:
        cost = self._game_data.calculate_ability_cost(item_id)
    except : # TODO fix e.g. 185cefb4cda1246ea8c3bdc6c033680f7279162a
        # ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1
        #if item_id == AbilityId.ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1 or item_id == "ENGINEERINGBAYRESEARCH_TERRANINFANTRYWEAPONSLEVEL1":
        #    return CanAffordWrapper(200 <= self.minerals, 200 <= self.vespene) # 100, 100
        #else:
            min_resource_unknown = 400
            print("Unknown item: " + item_id)
            return CanAffordWrapper(min_resource_unknown <= self.minerals, min_resource_unknown <= self.vespene)
            
    if cost is None:
        # TODO check if it works  
        # can_afford occasionally crashed when using for research # 
        # e.g. for ARMORYRESEARCH_TERRANVEHICLEWEAPONSLEVEL1
        min_resource_upgrades = 300
        return CanAffordWrapper(min_resource_upgrades <= self.minerals, min_resource_upgrades <= self.vespene)



async def auto_build(bot):
            
     # if much --> build new terran_military_buildings
    if bot.minerals > sufficently_much_minerals and bot.vespene > sufficently_much_vespene and bot.units.structure.idle.amount < auto_build_idle_limit:  
        for building in sample(terran_military_buildings, terran_military_buildings_sample):
            building_required = construct_requirements[building]
            if bot.units(building_required).owned.completed.amount > 0:      
                print("Build {0} due to a large surplus of resources".format(building))
                bot.cum_supply = bot.cum_supply + 2 # in case of stopped build order
                await bot.build(building, near = get_random_building_location(bot))
    elif bot.minerals > sufficently_much_minerals and bot.units(bot.basic_townhall_type).pending.amount == 0:
        print("Auto expand due to a large surplus of resources")
        await expand().execute(bot)
        
    # sample order for different units
    # build units if enough resources
    if bot.minerals > sufficently_enough_minerals and bot.vespene > sufficently_enough_vespene:  # and bot.can_afford(unit) 
        for unit in sample(terran_military_units_vepene, terran_military_units_vepene_sample): 
            building_required = unit_requirements[unit]

            if building_required in building_addons:
                building_required = construct_requirements[building_required]

            # find at least one idle building that can built the unit
            for building in bot.units(building_required).owned.completed.idle:
                if can_build(building, unit) and bot.can_afford(unit) : # and count_units(bot, building_required, True) > 0:
                        print("Train unit {0} due to surplus of resources".format(unit))
                        bot.cum_supply = bot.cum_supply + 1
                        await bot.do(building.train(unit))

                        #await train_unit(unit, building_required, 1).execute(bot) # increase only by one in order not to miss up the build order


    # build units if enough resources
    if bot.minerals > sufficently_enough_minerals and bot.vespene < sufficently_enough_vespene:  
        for unit in sample(terran_military_units_mineral, terran_military_units_mineral_sample): # shuffle(terran_military_units_mineral):
            building_required = unit_requirements[unit]

            if building_required in building_addons:
                building_required = construct_requirements[building_required]

            # find at least one idle building that can built the unit
            for building in bot.units(building_required).owned.completed.idle:
                if can_build(building, unit)  and bot.can_afford(unit) :
                #if building.noqueue and building.is_idle and count_units(bot, building_required, True) > 0:
                        print("Train unit {0} due to surplus of minerals".format(unit))
                        bot.cum_supply = bot.cum_supply + 1
                        await bot.do(building.train(unit))
                        # await train_unit(unit, building_required, 1).execute(bot) # increase only by one in order not to miss up the build order


# TODO list with upgrades pending or finished
'''
    def can_research(self, upgrade_id, on_building):
        if isinstance(upgrade_id, UpgradeId) and self.can_afford(upgrade_id) and self.units(on_building).ready.exists and not upgrade_id in get_researched_upgrades():
            upgrader = self.units(on_building).ready.first
            await self.do(upgrader(upgrade_id))
            #self.cloak_started = True
'''   

    
       
async def auto_build_factory_units(bot):
    """Auto build units in case of surplus of resources"""
    for building in bot.units(UnitTypeId.FACTORY).owned.completed.idle: # TODO or noqueue ???
        unit = sample(auto_build_factory_units, auto_build_factory_units_length) 
        if can_build(building, unit) and bot.can_afford(unit):
            print("Train unit {0} due to surplus of resources".format(unit))
            bot.cum_supply = bot.cum_supply + 1
            await bot.do(building.train(unit))






# TODO attack as group, or solution as in proxy_ray.py???
# TODO for other races
# TODO couldnt it be improved by adding new units automatically
# TODO can be improved significantly --> e.g. superclass units without SCV
def get_units_military(bot):
    units_military = []

    for unit in terran_military_units:
        units_military = units_military + bot.units(unit)
            
    return  units_military



def write_log(self):
    if self.log_file is None:
        return

    with open(self.log_file, "a") as f:
        for log in self.log:
            f.write("%s\n" % log)
