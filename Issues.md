# TODO

- do multiple commands in parallel if enough minerals/gas

- Research in build order --> using train_unit
	- check
	def research(building, upgrade, prioritize=True, repeatable=False):
		async def research_spec(bot):
			sp = bot.units(building).ready.noqueue
			if sp.exists and bot.can_afford(upgrade) and not bot.already_pending(upgrade):
				await bot.do(sp.first(upgrade))

		return research_spec
	- only execute respearch if not currently researching or research done 



- attack in groups instead of sending single units
- when defending, dont move to opponent area

- minimum distance between buildings --> addons must have space --> round + placement steps?

- mark my contribution with HS

- duplicate building requiredbuilding due to already pending not counting 

# CHECK

- poor building location placement --> trying to build addons failed due to missing space --> more distance to other buildings

- fix cum supply by 1 too low despite init at 12
- executing multiple build order items in parallel


# Still persists?

- include_pending --> doesnt work for buildings, e.g. cant build Starport, since requirement factory + factory not completed
- Add condition: supply_left

- improve export of csv
  - not all upgrades have buildings
  - maybe export requires

# Things that should/could work

- rebuild dying unit/building
- build random units after finishing build order <-- via sufficently enough resources
- attack after reaching end of build order
- auto expand in mid/lategame
- auto rename+export replays p1vsp2-time.SC2Replay


- cant reproduce buildings switching places (addon swapping)
  - e.g. solve via: if enough units simple build an addon? what if a different one is build later
  - better: why upgrade/addon/unit cant be build 
    - check if building not pending / exists --> if not build building
    - check if addon can be build --> if not create new building
    - check if unit cant be build due to missing add on --> build add on