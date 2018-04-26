def all_of(*args):
    def condition(bot):
        return all(map(lambda a: a(bot), args))

    return condition


def any_of(*args):
    def condition(bot):
        return all(any(lambda a: a(bot), args))

    return condition


def always_true(bot):
    return True


def supply_at_least(s):
    def condition(bot):
        return bot.supply_used >= s

    return condition


def gas_at_least(s):
    def condition(bot):
        return bot.vespene >= s

    return condition


def gas_less_than(s):
    def condition(bot):
        return bot.vespene < s

    return condition


def minerals_at_least(s):
    def condition(bot):
        return bot.minerals >= s

    return condition


def minerals_less_than(s):
    def condition(bot):
        return bot.minerals < s

    return condition


def unit_count(unit, n, include_pending=False):
    def condition(bot):
        actual_amount = bot.units(unit).amount
        if include_pending:
            actual_amount += bot.already_pending(unit)
        return actual_amount == n

    return condition


def unit_count_at_least(unit, n, include_pending=False):
    def condition(bot):
        actual_amount = bot.units(unit).amount
        if include_pending:
            actual_amount += bot.already_pending(unit)
        return actual_amount >= n

    return condition


def unit_count_less_than(unit, n, include_pending=False):
    def condition(bot):
        actual_amount = bot.units(unit).amount
        if include_pending:
            actual_amount += bot.already_pending(unit)
        return actual_amount < n

    return condition
