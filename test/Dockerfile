## For local testing
#FROM test_image2

# For live version
FROM burnysc2/python-sc2-docker

# # Copy run_tests bash script
# ADD test/run_tests.sh /root/run_tests.sh

# Copy files from the current commit to root
ADD . /root/python-sc2

# Install the python-sc2 library and its requirements (s2clientprotocol etc.)
WORKDIR /root/python-sc2
RUN python -m pip install .

# This will be executed during the container run instead
# docker run test_image -c "python examples/protoss/cannon_rush.py"
# RUN python "examples/protoss/cannon_rush.py"

ENTRYPOINT [ "/bin/bash" ]
