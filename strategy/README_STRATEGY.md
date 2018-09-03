# Contribution HS

- Completely written all files in strategy folder:
	- bot_ai_extended.py
	- strategy_constants.py
	- strategy_selector.py
	- strategy_util.py
    - bot_config.py
    - strategy_test.py
    - util.py
- Partially modified or added, especially:
	- build_orders/build_order.py
	- build_orders/commands.py
    - state_conditions/conditions.py
    - unit.py and units.py
- Everywhere else, indicated with: # HS



# Strategy / Build-order support

## Current status

- Can re-execute predefined build-orders (Buildings, Units, Addons and Research) based upon reypaders fork
- Fair chance to win against difficulty level hard
  - Win-rate about 40 % without build-order
  - Better win-rates with build-orders
- Without external data, a good way to start is to have a look into Strategy Test
  - Write your own bot by inheriting from Bot AI Extending and override methods
- Limitations
  - Bot will not use Unit Abilities
  - Works fine with Terran but for Zerg and Protoss some features needs to be adapted (e.g. required buildings, morph, ...)
  - Auto build/train uses only units which requires no add-on
  - Add-ons are not automatically build to preserve the possibility for the build-order


## Code structure

- Strategy Constants: Contains constants for external data and Terran units
- Bot Config: Changes the behaviour of the bot

- Strategy Selector: Deals with external build-order data
- Strategy Util: Bot related access to files
- Bot AI Extended: Extends Bot AI by several features e.g. automatic building/training of units, attacking, defending, ...
- Strategy Test: Contains basic build-orders
- Util: Miscellaneous utitility functions




## External data (e.g. parsed from replay files)


- Note that SCV and Supply Depots are ignored, since they will be automatically constructed by the bot
- Used folder structure (adapt to yours in Strategy Constants)
  - Root
    - python-sc2
      - all files and folders of this repository
    - SC2-replays
      - DataSetName
        - buildorders-csv
          - Race1vsRace2
            - MapName
              - csv file containing the buildorder
            - csv file containing the strategy


- Build-order Format: csv
  - Note: SCV and Supply Depots will be omitted

| Type     | UnitName    | OnBuilding     | TotalSupply | Supply |
|----------|-------------|----------------|-------------|--------|
| Unit     | SCV         | Command Center | 12          | 1      |
| Unit     | SCV         | Command Center | 13          | 1      |
| Building | SupplyDepot | NA             | 13          | 0      |
| Unit     | SCV         | Command Center | 13          | 1      |
| Unit     | SCV         | Command Center | 14          | 1      |
| Unit     | SCV         | Command Center | 15          | 1      |
| Unit     | SCV         | Command Center | 17          | 1      |
| Building | Barracks    | NA             | 16          | 0      |
| Building | Barracks    | NA             | 16          | 0      |
| Unit     | SCV         | Command Center | 17          | 1      |
| Building | Barracks    | NA             | 17          | 0      |
| Unit     | Marine      | Barracks       | 18          | 1      |
| …        | …           | …              | …           | …      |

- Strategy Format: csv 
  - Note: Hash correspond to the file name, i.e. hash.csv

| Hash                                     | BestEqualWeighted | RandomEqualWeighted |
|------------------------------------------|-------------------|---------------------|
| 029b52b865a6fe4952353340945423333bdbed7c | 0.02              | 0.00480769230769231 |
| 034bf1e5842dc45b3218bbeca8e4d930d6df3e5c | 0.04              | 0.00961538461538462 |
| 19dae0df693753ccd9a8fcc95696c8a500d14dea | 0.06              | 0.0144230769230769  |
| 1af91988970684886affc3b51bca7c87986a6f15 | 0.08              | 0.0192307692307692  |
| 1e22bac62d47f2f30261c833889d9321da774767 | 0.1               | 0.0240384615384615  |
| 1f3f2d86b156407a3e940c65a591d23139e71b9f | 0.12              | 0.0288461538461538  |
| 269f656542eb4b473235ad74f19718222eae02ee | 0.14              | 0.0336538461538462  |
| 328e0c0a06d783cbe9cac251c5c8ce1a9046a872 | 0.16              | 0.0384615384615385  |
| 3648977816e444ca738b02bf8ec70a2a6551e305 | 0.18              | 0.0432692307692308  |
| 4424a7bd5535638d5b7e6a0672c5be2bc1f62917 | 0.2               | 0.0480769230769231  |
| 45c4f6cf6172fa1770dbcfc02e5d96469902fb6e | 0.22              | 0.0528846153846154  |
| 467af7a4ebefc92b396d748840e0ed674de77a10 | 0.24              | 0.0576923076923077  |
| ... | ...              | ...             |



