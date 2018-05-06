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

- Research in build order --> using train_unit
	- check
	def research(building, upgrade, prioritize=True, repeatable=False):
		async def research_spec(bot):
			sp = bot.units(building).ready.noqueue
			if sp.exists and bot.can_afford(upgrade) and not bot.already_pending(upgrade):
				await bot.do(sp.first(upgrade))

		return research_spec
	- only execute respearch if not currently researching or research done 

- cant reproduce buildings switching places
  - e.g. solve via: if enough units simple build an addon? what if a different one is build later
  - better: why upgrade/addon/unit cant be build 
    - check if building not pending / exists --> if not build building
    - check if addon can be build --> if not create new building
    - check if unit cant be build due to missing add on --> build add on

- improve export of csv
  - not all upgrades have buildings
  - maybe export requires

- if under attack --> defend with all units except workers (inc. MULE)

# Think its done

- increase workers after expand()

