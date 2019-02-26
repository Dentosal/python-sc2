from collections import Counter
from functools import wraps


def property_cache_forever(f):
    f.cached = None

    @wraps(f)
    def inner(self):
        if f.cached is None:
            f.cached = f(self)
        return f.cached

    return property(inner)


def property_cache_once_per_frame(f):
    """ This decorator caches the return value for one game loop, then clears it if it is accessed in a different game loop
    Only works on properties of the bot object because it requires access to self.state.game_loop """
    f.frame = -1
    f.cache = None

    @wraps(f)
    def inner(self):
        if f.cache is None or f.frame != self.state.game_loop:
            f.cache = f(self)
            f.frame = self.state.game_loop
        if type(f.cache).__name__ == "Units":
            return f.cache.copy()
        if isinstance(f.cache, (list, set, dict, Counter)):
            return f.cache.copy()
        return f.cache

    return property(inner)


def property_immutable_cache(f):
    """ This cache should only be used on properties that return an immutable object """

    @wraps(f)
    def inner(self):
        if f.__name__ not in self.cache:
            self.cache[f.__name__] = f(self)
        return self.cache[f.__name__]

    return property(inner)


def property_mutable_cache(f):
    """ This cache should only be used on properties that return a mutable object (Units, list, set, dict, Counter) """

    @wraps(f)
    def inner(self):
        if f.__name__ not in self.cache:
            self.cache[f.__name__] = f(self)
        return self.cache[f.__name__].copy()

    return property(inner)
