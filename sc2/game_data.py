class GameData(object):
    def __init__(self, data):
        self.abilities = [a for a in data.abilities if a.available]
        self.units = {u.unit_id: u for u in data.units if u.available}
