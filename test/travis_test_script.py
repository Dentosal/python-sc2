import sys, subprocess, time, threading

retries = 10
timeout_time = 2*60

# A class that can run a command and kill it if it is longer than timeout
class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.result = None

    def run(self, timeout):
        def target():
            print('Thread started')
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
            self.result = self.process.communicate()
            print('Thread finished')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print('Terminating process')
            self.process.terminate()
            thread.join()
        # print(self.process.returncode)
        return self.process, self.result





# Run the game from here via arguments e.g.:
# python test/travis_test_script.py examples/protoss/cannon_rush_bot.py
if len(sys.argv) > 1:
# if 1:

    # Attempt to run process up to 5 times with 180 seconds timeout time
    t0 = time.time()
    process, output = None, None
    for i in range(retries):
        t0 = time.time()
        # print("Launching bot {}, attempt {}/{}".format("examples/protoss/cannon_rush.py", i+1, retries))
        print("Launching bot {}, attempt {}/{}".format(sys.argv[1], i+1, retries))
        command = Command(["python", sys.argv[1]])
        # command = Command(["python", "../examples/protoss/cannon_rush.py"])
        process, output = command.run(timeout_time)
        if output is None:
            continue
        out, err = output
        result = out.decode("utf-8")
        # Break as the bot run was successful
        break

    # Bot was not successfully run in time
    if process.returncode != 0:
        print("Exiting with exit code 5, error: Attempted to launch script {} timed out after {} seconds. Retries completed: {}".format(sys.argv[1], timeout_time, retries))
        exit(5)

    # Reformat the output into a list
    print_output: str = result
    print(print_output)
    linebreaks = [
        ["\r\n", print_output.count("\r\n")],
        ["\r", print_output.count("\r")],
        ["\n", print_output.count("\n")],
    ]
    most_linebreaks_type = max(linebreaks, key=lambda x: x[1])
    linebreak_type, linebreak_count = most_linebreaks_type
    output_as_list = print_output.split(linebreak_type)

    # result.returncode will always return 0 if the game was run successfully or if there was a python error
    print("Returncode: {}".format(process.returncode))
    print("Game took {} real time seconds".format(round(time.time() - t0, 1)))
    if process is not None and process.returncode == 0:
        for line in output_as_list:
            # This will throw an error if a bot is called Traceback
            if "Traceback " in line:
                print("Exiting with exit code 3, error log:\r\n{}".format(output_as_list))
                exit(3)
        print("Exiting with exit code 0")
        exit(0)

    # Exit code 1: game crashed I think
    print("Exiting with exit code 1")
    exit(1)

# Exit code 2: bot was not launched
print("Exiting with exit code 2")
exit(2)