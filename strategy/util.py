from random import uniform, randrange

def get_random_building_location(bot):
    random1 = randrange(5, 15, 2)
    random2 = randrange(5, 12, 2)

    if bot.townhalls.exists: 
        return bot.townhalls.random.position.towards(bot.game_info.map_center, random1).random_on_distance(random2)
    else:
        return bot.first_base.position.towards(bot.game_info.map_center, random1).random_on_distance(random2)
 
