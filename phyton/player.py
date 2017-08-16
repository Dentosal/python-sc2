from .data import PlayerType, Race, Difficulty
from .bot_ai import BotAI

class Player(object):
    def __init__(self, type, race=None, difficulty=None):
        assert isinstance(type, PlayerType)

        if type == PlayerType.Computer:
            assert isinstance(difficulty, Difficulty)

        elif type == PlayerType.Observer:
            assert race is None
            assert difficulty is None

        else:
            assert isinstance(race, Race)
            assert difficulty is None

        self.type = type
        if race is not None:
            self.race = race
        if type == PlayerType.Computer:
            self.difficulty = difficulty

class Human(Player):
    def __init__(self, race):
        super().__init__(PlayerType.Participant, race)

class Bot(Player):
    def __init__(self, race, ai):
        assert isinstance(ai, BotAI)
        super().__init__(PlayerType.Participant, race)
        self.ai = ai

class Computer(Player):
    def __init__(self, race, difficulty=Difficulty.Easy):
        super().__init__(PlayerType.Computer, race, difficulty)

class Observer(Player):
    def __init__(self):
        super().__init__(PlayerType.Observer)
