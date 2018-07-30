#!/usr/bin/env bash

# Debugging
echo Hello from run_tests.sh script

# Install the python-sc2 library and its requirements (s2clientprotocol etc)
cd /root/python-sc2
echo Files in these folders
tree
echo Current path
pwd
python -m pip install .

# Run all example bots
python /root/python-sc2/examples/protoss/cannon_rush.py
python /root/python-sc2/examples/protoss/threebase_voidray.py
python /root/python-sc2/examples/protoss/warpgate_push.py

python /root/python-sc2/examples/terran/cyclone_push.py
python /root/python-sc2/examples/terran/mass_reaper.py
python /root/python-sc2/examples/terran/onebase_battlecruiser.py
python /root/python-sc2/examples/terran/proxy_rax.py
python /root/python-sc2/examples/terran/ramp_wall.py

python /root/python-sc2/examples/zerg/hydralisk_push.py
python /root/python-sc2/examples/zerg/onebase_broodlord.py
python /root/python-sc2/examples/zerg/zerg_rush.py


# Run tests
python /root/python-sc2/test/test_units.py
python /root/python-sc2/test/test_bot.py
