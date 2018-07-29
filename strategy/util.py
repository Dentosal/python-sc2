from random import uniform, randrange
import logging
logger = logging.getLogger("sc2.performance")
logger.setLevel(logging.INFO)
import functools
import timeit
import time
import os


def create_folder(folder):
    """Creates folder if not exists"""
    if not os.path.exists(folder):
        os.makedirs(folder)

def get_random_building_location(bot):
    """Generates random placement suggestion for building location"""
    random1 = randrange(5, 15, 2)
    random2 = randrange(5, 12, 2)

    if bot.townhalls.exists: 
        return bot.townhalls.random.position.towards(bot.game_info.map_center, random1).random_on_distance(random2)
    else:
        return bot.first_base.position.towards(bot.game_info.map_center, random1).random_on_distance(random2)
 
def print_log(logger, level, message):
    """Logs or print messages"""
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




# Based on: https://stackoverflow.com/a/20924212
def measure_runtime(func):
    """Measures runtime, logs in case of slow performance"""
    @functools.wraps(func)
    async def newfunc(*args, **kwargs):
        start = time.time()
        await func(*args, **kwargs)
        elaped_ms = int((time.time() - start) * 1000)

        level = None
        if elaped_ms <= 50:
            return
        elif elaped_ms > 1000:            
            level = logging.ERROR
        elif elaped_ms > 500:            
            level = logging. WARNING           
        elif elaped_ms > 100:            
            level = logging.INFO
        elif elaped_ms > 50:            
            level = logging.DEBUG
        else:            
            level = logging.CRITICAL

        print_log(logger, level, "Function {} required {} ms".format(func.__name__, elaped_ms))

    return newfunc



