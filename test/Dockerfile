FROM burnysc2/python-sc2-docker

# Copy python-sc2 directory to docker image
ADD $TRAVIS_BUILD_DIR /root/python-sc2
# ADD python-sc2 /root/python-sc2

# Copy run_tests bash script
ADD $TRAVIS_BUILD_DIR/test/run_tests.sh /root/run_tests.sh

# RUN /root/run_tests.sh

# docker rm mytest
# docker run --name mytest ubuntu echo one
# docker start -i mytest
# docker cp run_tests.sh mytest:/root/
# docker cp python-sc2/. mytest:/root/python-sc2
# docker exec mytest bash /root/run_tests.sh