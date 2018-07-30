REM Remove previous test containers
docker rm python-sc2-test101
docker rm python-sc2-test102
docker rm python-sc2-test103

docker rm python-sc2-test201
docker rm python-sc2-test202
docker rm python-sc2-test203
docker rm python-sc2-test204
docker rm python-sc2-test205

docker rm python-sc2-test301
docker rm python-sc2-test302
docker rm python-sc2-test303


REM Move to same location where travis builds from, if this batch file is in pythons-sc2/test/
cd ..
docker build -t test_image -f test/Dockerfile .


REM Run image
docker run --name python-sc2-test101 test_image -c "python examples/protoss/cannon_rush.py"
docker run --name python-sc2-test102 test_image -c "python examples/protoss/threebase_voidray.py"
docker run --name python-sc2-test103 test_image -c "python examples/protoss/warpgate_push.py"

docker run --name python-sc2-test201 test_image -c "python examples/terran/cyclone_push.py"
docker run --name python-sc2-test202 test_image -c "python examples/terran/mass_reaper.py"
docker run --name python-sc2-test203 test_image -c "python examples/terran/onebase_battlecruiser.py"
docker run --name python-sc2-test204 test_image -c "python examples/terran/proxy_rax.py"
docker run --name python-sc2-test205 test_image -c "python examples/terran/ramp_wall.py"

docker run --name python-sc2-test301 test_image -c "python examples/zerg/hydralisk_push.py"
docker run --name python-sc2-test302 test_image -c "python examples/zerg/onebase_broodlord.py"
docker run --name python-sc2-test303 test_image -c "python examples/zerg/zerg_rush.py"