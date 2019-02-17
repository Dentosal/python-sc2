from sc2 import run_game, maps, Race, Difficulty, BotAI
from sc2.player import Bot, Computer

class WorkerRushBot(BotAI):
    def __init__(self):
        super().__init__()
        self.actions = []

    async def on_step(self, iteration):
        self.actions = []

        if iteration == 0:
            target = self.enemy_start_locations[0]

            for worker in self.workers:
                self.actions.append(worker.attack(target))

        await self.do_actions(self.actions)

def main():
    run_game(maps.get("Abyssal Reef LE"), [
        Bot(Race.Zerg, WorkerRushBot()),
        Computer(Race.Protoss, Difficulty.Medium)
    ], realtime=True)

if __name__ == '__main__':
    main()
