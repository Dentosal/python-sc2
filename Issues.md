# TODO

- poor building location placement --> trying to build addons failed due to missing space --> more distance to other buildings
- include_pending --> doesnt work for buildings, e.g. cant build Starport, since requirement factory + factory not completed
- Add condition: supply_left

- auto expand in mid/lategame



- auto rename+export replays p1vsp2-time.SC2Replay


- export x,y coordinate to hash.csv and use info for placement?
  - problem: what if different start position

- do multiple commands in parallel if enough minerals/gas

- add total supply, in case of dying units

- rebuild dying unit/building

- build random units after finishing build order
- attack after reaching end of build order


# Think its done

- increase workers after expand()

- Research in build order --> using train_unit
	- check
	def research(building, upgrade, prioritize=True, repeatable=False):
		async def research_spec(bot):
			sp = bot.units(building).ready.noqueue
			if sp.exists and bot.can_afford(upgrade) and not bot.already_pending(upgrade):
				await bot.do(sp.first(upgrade))

		return research_spec
	- only execute respearch if not currently researching or research done 