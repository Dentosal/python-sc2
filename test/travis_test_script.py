import sys, subprocess, time

retries = 10
timeout_time = 2*60

# Run the game from here via arguments e.g.:
# python test/travis_test_script.py examples/protoss/cannon_rush_bot.py
if len(sys.argv) > 1:
    # Attempt to run process up to 5 times with 180 seconds timeout time
    t0 = time.time()
    result = None
    for i in range(retries):
        try:
            t0 = time.time()
            print("Launching bot {}, attempt {}/{}".format(sys.argv[1], i+1, retries))
            result = subprocess.run(["python", sys.argv[1]], stdout=subprocess.PIPE, timeout=timeout_time)
        except subprocess.TimeoutExpired:
            print("Bot expired.")
            continue
        finally:
            break

    # Bot was not successfully run in time
    if result is None:
        print("Exiting with exit code 5, error: Attempted to launch script {} timed out after {} seconds. Retry attempt number {}".format(sys.argv[1], timeout_time, i+1))
        exit(5)

    print_output: str = result.stdout.decode('utf-8')
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
    print("Returncode: {}".format(result.returncode))
    print("Game took {} real time seconds".format(round(time.time() - t0, 1)))
    if result.returncode == 0:
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