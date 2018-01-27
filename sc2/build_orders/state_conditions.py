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


def unit_count(building, n, include_pending=False):
    def condition(bot,state):
        actual_amount = bot.units(building).amount
        if include_pending:
            actual_amount += bot.already_pending(building)
        return actual_amount == n
    return condition