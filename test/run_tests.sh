#!/usr/bin/env bash

echo Hello world test from run_tests script
echo Files:
ls
echo Files in root:
ls /root/
echo Files in root/python-sc2:
ls /root/python-sc2
echo Files in root/python-sc2/test:
ls /root/python-sc2/test
python -m pip install /python-sc2
python /python-sc2/test/test_units.py