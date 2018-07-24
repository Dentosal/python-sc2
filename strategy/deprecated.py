

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