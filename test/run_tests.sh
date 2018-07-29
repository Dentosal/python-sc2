#!/usr/bin/env bash

echo Hello world test from run_tests script


# Install the python-sc2 library and its requirements (s2clientprotocol etc)
cd /root/python-sc2
#tree
#pwd
python -m pip install .


python /root/python-sc2/test/test_units.py
python /root/python-sc2/test/test_bot.py