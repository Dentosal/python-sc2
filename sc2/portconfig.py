import portpicker

class Portconfig(object):
    def __init__(self):
        self.shared = portpicker.pick_unused_port()
        self.server = [portpicker.pick_unused_port() for _ in range(2)]
        self.players = [[portpicker.pick_unused_port() for _ in range(2)] for _ in range(2)]
