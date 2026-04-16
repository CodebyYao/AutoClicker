import json
import os
from time import sleep
from loader import compile_script
from action_chain import Initializer


def run_script(script_dir: str, script_name: str, detect_time: float) -> bool:
    """
    Execute the script
    :param script_dir: path to the script directory
    :param script_name: name of the script
    :param detect_time: the time to detect an image
    :return: execute success or not
    """
    script_path = os.path.join(script_dir, script_name)
    # load in the script
    with open(script_path, 'r', encoding='utf-8') as script_f:
        script = json.load(script_f)
    if len(script) == 0:
        return True
    # initialize the action chain
    action_chain = compile_script(script_path, detect_time)

    block_name = os.path.basename(script_path).replace(".json", "")
    # initializing current index
    current_index = 0
    # initializing if-else count
    if_else_count = 0
    # flag to indicate if an if-else component has satisfied
    if_else_flag = False
    # current loop count
    loop_count = 0
    loop_stack = []
    while True:
        if current_index >= len(script):
            break
        component = script[current_index]['component']
        com_id = f"{block_name}_{script[current_index]['id']}"
        if component == 'click':
            click_result = action_chain[com_id].nav_to_image()
            if not click_result:
                # print(f"{current_index}: failed")
                return False
        elif component == 'scroll':
            scroll_result = action_chain[com_id].nav_to_scroll()
            if not scroll_result:
                return False
        elif component == 'if':
            if not if_else_flag and if_else_count <= 0:
                # reset if-else count
                # check how many if and elif component there is
                if_else_comp_count = script[current_index]['comp_count'] + 1
                if_else_count = int(script[current_index]['time_out'] / (if_else_comp_count * detect_time))
                # print(f"if_else_times: {if_else_count}")
                if if_else_count < 1:
                    if_else_count = 1
            if_result = action_chain[com_id].check_if_locate()
            if if_result:
                # print(f"If satisfied: {current_index}")
                if_else_flag = True
                pass
            else:
                current_index = script[current_index]['next']
                continue
        elif component == 'elif':
            # if an if-else component has satisfied
            if if_else_flag:
                current_index = script[current_index]['end']
                continue
            elif_result = action_chain[com_id].check_if_locate()
            if elif_result:
                if_else_flag = True
                pass
            else:
                current_index = script[current_index]['next']
                continue

        elif component == 'else':
            # if an if-else component has satisfied
            if if_else_flag:
                current_index = script[current_index]['end']
                continue
            # decrease the check times
            if_else_count -= 1
            # print(if_else_count)
            # check whether how many check times are left
            if if_else_count <= 0:
                if_else_count = 0
                pass
            else:
                current_index = script[current_index]['if']
                continue

        elif component == 'end':
            # reset the flag
            if_else_flag = False
            # reset the count
            if_else_count = 0

        elif component == 'loop_s':
            end_index = script[current_index]['end']
            new_loop_time = script[end_index]['times']
            # stack previous loop count
            loop_stack.append(loop_count)
            loop_count = new_loop_time

        elif component == 'loop_e':
            loop_count -= 1
            if loop_count > 0:
                current_index = script[current_index]['goto'] + 1
                continue
            if len(loop_stack) > 0:
                loop_count = loop_stack.pop(-1)

        elif component == 'pause':
            sleep(max(0, script[current_index]['pause_time'] - detect_time))

        elif component == 'break':
            try:
                loop_count = loop_stack.pop(-1)
            except:
                pass
            current_index = script[current_index]['goto'] + 1
            # print(f"Break goto {current_index}")
            if_else_flag = False
            # reset the count
            if_else_count = 0
            continue

        elif component == 'script':
            external_script_name = script[current_index]['script_name']
            print(f"Calling script: {external_script_name}")
            if not run_script(script_dir, external_script_name, detect_time):
                return False

        elif component == 'long_click':
            long_click_result = action_chain[com_id].nav_to_hold()
            if not long_click_result:
                return False

        elif component == 'drag':
            dragger_result = action_chain[com_id].drag_to_dest()
            if not dragger_result:
                return False

        current_index += 1
    return True


def init_time() -> float:
    """
    Measure the time to detect an image
    :return: the time to detect an image
    """
    img_init = Initializer()
    detect_time = img_init.detect_time()
    return detect_time


if __name__ == '__main__':
    script_dir = 'Scripts'
    script_name = 'popcat.json'
    detect_time = init_time()
    sleep(10)
    print(run_script(script_dir, script_name, detect_time))
