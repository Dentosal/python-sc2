FROM burnysc2/python-sc2-docker


# Copy run_tests bash script
#ADD $TRAVIS_BUILD_DIR/test/run_tests.sh /root/run_tests.sh
#ADD $CI_PROJECT_DIR/test/run_tests.sh /root/run_tests.sh
ADD test/run_tests.sh /root/run_tests.sh

# Copy files from the current commit to root
#ADD $TRAVIS_BUILD_DIR /root/python-sc2
#ADD $CI_PROJECT_DIR /root/python-sc2
ADD . /root/python-sc2


# This will be executed during the container run instead
# RUN /root/run_tests.sh


ENTRYPOINT [ "/bin/bash" ]