REM Remove previous test container
docker rm my_test

REM Move to same location where travis builds from, if this batch file is in pythons-sc2/test/
cd ..
REM For local testing:
REM docker build -t test_image2 -f test/temp/Dockerfile .
REM For live usage:
docker build -t test_image -f test/Dockerfile .

REM Run image
docker run --name my_test test_image /root/run_tests.sh