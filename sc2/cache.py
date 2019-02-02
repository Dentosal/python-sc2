from functools import wraps
from collections import Counter

def cache_forever(f):
    f.cache = {}

    @wraps(f)
    def inner(*args):
        if args not in f.cache:
            f.cache[args] = f(*args)
        return f.cache[args]

    return inner


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
        cache_name = "_cache_" + f.__name__
        frame_name = "_frame_" + f.__name__
        if not hasattr(self, cache_name) or not hasattr(self, frame_name) or getattr(self, frame_name) != self.state.game_loop:
            setattr(self, cache_name, f(self))
            setattr(self, frame_name, self.state.game_loop)

        cached_data = getattr(self, cache_name)
        if type(cached_data).__name__ == "Units":
            return cached_data.copy()
        if isinstance(cached_data, (list, set, dict, Counter)):
            return cached_data.copy()
        return cached_data

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
