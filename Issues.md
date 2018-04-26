# TODO

- poor building location placement --> trying to build addons failed due to missing space --> more distance to other buildings
- include_pending --> doesnt work for buildings, e.g. cant build Starport, since requirement factory + factory not completed
- Add condition: supply_left

- increase workers after expand()

- auto expand in mid/lategame

- Research in build order
	- check
	def research(building, upgrade, prioritize=True, repeatable=False):
		async def research_spec(bot):
			sp = bot.units(building).ready.noqueue
			if sp.exists and bot.can_afford(upgrade) and not bot.already_pending(upgrade):
				await bot.do(sp.first(upgrade))

		return research_spec
	- only execute respearch if not currently researching or research done 

- auto rename+export replays p1vsp2-time.SC2Replay