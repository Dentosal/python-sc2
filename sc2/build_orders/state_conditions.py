def all_of(*args):
    def condition(bot, state):
        return all(map(lambda a: a(bot, state), args))

    return condition


def any_of(*args):
    def condition(bot, state):
        return all(any(lambda a: a(bot, state), args))

    return condition


def always_true(bot, state):
    return True


def supply_is(s):
    def condition(bot, state):
        return bot.supply_used == s

    condition.__str__()
    return condition


def gas_at_least(s):
    def condition(bot, state):
        return bot.vespene >= s

    return condition


def minerals_at_least(s):
    def condition(bot, state):
        return bot.minerals >= s

    return condition
