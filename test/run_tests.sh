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

# Run tests
python /root/python-sc2/test/test_units.py
python /root/python-sc2/test/test_bot.py
