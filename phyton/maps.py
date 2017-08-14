from .paths import Paths

def get():
    maps = []
    for mapdir in (p for p in Paths.MAPS.iterdir() if p.is_dir()):
        for mapfile in (p for p in mapdir.iterdir() if p.is_file()):
            if mapfile.suffix == ".SC2Map":
                maps.append(Map(mapfile))
    return maps

class Map(object):
    def __init__(self, path):
        self.path = path

    @property
    def name(self):
        return self.path.stem

    @property
    def data(self):
        with open(self.path, "rb") as f:
            return f.read()

    def __repr__(self):
        return f"Map({self.path})"
