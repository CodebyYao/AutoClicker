import random
import subprocess
import sys
import time


def make_click(current_index):
    speed = random.uniform(0, 1)
    wait_time = random.randint(0, 1)
    double_click = random.choice([True, False])
    insert_index = random.randint(0, current_index)
    return f"click {speed} {wait_time} {double_click} {insert_index}"


def make_scroll(current_index):
    speed = random.uniform(0, 1)
    wait_time = random.randint(0, 1)
    scroll_length = random.uniform(100, 600)
    insert_index = random.randint(0, b=current_index)
    return f"scroll {speed} {wait_time} {scroll_length} {insert_index}"


def make_break(current_index):
    insert_index = random.randint(0, b=current_index)
    return f"break {insert_index}"


def make_pause(current_index):
    insert_index = random.randint(0, b=current_index)
    wait_time = random.randint(0, 1)
    return f"pause {wait_time} {insert_index}"


def make_if_else(current_index):
    insert_index = random.randint(0, b=current_index)
    wait_time = random.randint(0, 1)
    if_else_count = random.randint(0, 2)
    return f"if_else {wait_time} {if_else_count} { insert_index}"


def make_loop(current_index):
    insert_index = random.randint(0, b=current_index)
    loop_time = random.randint(0, 2)
    return f"loop {loop_time} {insert_index}"


def make_del(current_index):
    insert_index = random.randint(0,b=current_index)
    return f"del {insert_index}"


def make_drag(current_index):
    drag_to = random.randint(0, b=current_index)
    drag_from = random.randint(0, b=current_index)
    return f"drag {drag_from} {drag_to}"


def san_test_main():
    choose_list = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7]
    current_index = 0
    inputs = []
    inputs.append('sanity_check_9')
    inputs.append('r')
    command = ''
    for i in range(200):
        action = random.choice(choose_list)
        if action == 0:
            command = make_click(current_index)
            current_index += 1
        elif action == 1:
            command = make_scroll(current_index)
            current_index += 1
        if action == 2:
            command = make_break(current_index)
            current_index += 1
        elif action == 3:
            command = make_pause(current_index)
            current_index += 1
        elif action == 4:
            command = make_if_else(current_index)
            current_index += 1
        elif action == 5:
            command = make_loop(current_index)
            current_index += 1
        elif action == 6:
            command = make_del(current_index)
        elif action == 7:
            command = make_drag(current_index)

        inputs.append(command)
    inputs.append('q')
    input_data = "\n".join(inputs) + "\n"
    print(input_data)
    python_executable = sys.executable
    process = subprocess.Popen(
        [python_executable, "script_maker_v2.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True  # Ensure text mode for easier handling of input/output
    )
    start_time = time.time()
    for input_str in inputs:
        process.stdin.write(input_str + '\n')
        process.stdin.flush()  # Ensure the input is sent immediately
        # time.sleep(0.4)  # Delay for 1 second

    # Close the stdin to indicate no more input
    process.stdin.close()

    # Wait for the process to complete and get the output
    stdout, stderr = process.communicate()

    # Print the output from the main program
    print("Output from main program:")
    print(stdout)
    print(f"Compile time: {time.time() - start_time}")
    # Check for any errors
    if stderr:
        print("Errors from main program:")
        print(stderr)


if __name__ == "__main__":
    san_test_main()