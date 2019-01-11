from functools import wraps


def cache_forever(f):
    f.cache = {}

    @wraps(f)
    def inner(*args):
        if args not in f.cache:
            f.cache[args] = f(*args)
        return f.cache[args]

    return inner


def method_cache_once_per_frame(f):
    """ Untested but should work for functions with arguments
    Only works on properties of the bot object because it requires access to self.state.game_loop """
    f.frame = -1
    f.cache = {}

    @wraps(f)
    def inner(self, *args):
        if f.frame != self.state.game_loop:
            f.frame = self.state.game_loop
            f.cache = {}
        if args not in f.cache:
            f.cache[args] = f(self, *args)
        return f.cache[args]

    return inner


def property_cache_once_per_frame(f):
    """ This decorator caches the return value for one game loop, then clears it if it is accessed in a different game loop
    Only works on properties of the bot object because it requires access to self.state.game_loop """
    f.frame = -1
    f.cache = None

    @wraps(f)
    def inner(self):
        if f.frame != self.state.game_loop:
            f.frame = self.state.game_loop
            f.cache = None
        if f.cache is None:
            f.cache = f(self)
        return f.cache

    return property(inner)


def property_immutable_cache(f):
    @wraps(f)
    def inner(self):
        if f.__name__ not in self.cache:
            self.cache[f.__name__] = f(self)
        return self.cache[f.__name__]

    return property(inner)


def property_mutable_cache(f):
    @wraps(f)
    def inner(self):
        if f.__name__ not in self.cache:
            self.cache[f.__name__] = f(self)
        return self.cache[f.__name__].copy()

    return property(inner)
    
