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


def supply_at_least(s):
    def condition(bot, state):
        return bot.supply_used >= s

    return condition


def gas_at_least(s):
    def condition(bot, state):
        return bot.vespene >= s

    return condition


def minerals_at_least(s):
    def condition(bot, state):
        return bot.minerals >= s

    return condition


def unit_count(unit, n, include_pending=False):
    def condition(bot,state):
        actual_amount = bot.units(unit).amount
        if include_pending:
            actual_amount += bot.already_pending(unit)
        return actual_amount == n
    return condition
