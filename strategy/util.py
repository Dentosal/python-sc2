from random import uniform, randrange

def get_random_building_location(bot):
    if bot.townhalls.exists: 
        return bot.townhalls.random.position.towards(bot.game_info.map_center, randrange(5, 15)).random_on_distance(randrange(5, 12))
    else:
        return bot.first_base.position.towards(bot.game_info.map_center, randrange(5, 15)).random_on_distance(randrange(5, 12))
 
