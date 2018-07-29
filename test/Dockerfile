FROM burnysc2/python-sc2-docker

# Copy run_tests bash script
ADD test/run_tests.sh /root/run_tests.sh

# Copy files from the current commit to root
ADD . /root/python-sc2

# This will be executed during the container run instead
# docker run --name mytest test_image /root/run_tests.sh
# RUN /root/run_tests.sh

ENTRYPOINT [ "/bin/bash" ]