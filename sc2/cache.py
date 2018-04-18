from functools import wraps

def cache_forever(f):
    f.cache = {}
    @wraps(f)
    def inner(*args):
        if args not in f.cache:
            f.cache[args] = f(*args)
        return f.cache[args]
    return inner

def method_cache_forever(f):
    f.cache = {}
    @wraps(f)
    def inner(self, *args):
        if args not in f.cache:
            f.cache[args] = f(self, *args)
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
