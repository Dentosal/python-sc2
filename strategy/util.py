from random import uniform, randrange
import logging

def get_random_building_location(bot):
    random1 = randrange(5, 15, 2)
    random2 = randrange(5, 12, 2)

    if bot.townhalls.exists: 
        return bot.townhalls.random.position.towards(bot.game_info.map_center, random1).random_on_distance(random2)
    else:
        return bot.first_base.position.towards(bot.game_info.map_center, random1).random_on_distance(random2)
 
def print_log(logger, level, message):
    if logger is not None:
        if level == logging.DEBUG:
            logger.debug(message)
        elif level == logging.INFO:
            logger.info(message)
        elif level == logging.WARNING:
            logger.warning(message)
        elif level == logging.ERROR:
            logger.error(message)
        elif level == logging.CRITICAL:
            logger.critical(message)
        else:
            logger.error("UNKNOWN LEVEL: "+ message)
    
    else:
        print(message)