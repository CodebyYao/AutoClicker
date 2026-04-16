import json
import os
from image_selecter import select_img


def block_appender(com_id, script: list, option: str, com_param) -> list | None:
    """
    Insert the desire component
    :param com_id: id to indentify component
    :param script: the main script block
    :param option: the specify option
    :param com_param: the parameter of input component
    :return: script if success, None if failed
    """
    # option make
    try:
        com_id = str(com_id)
        if option == 'click':
            if len(com_param) != 5:
                # print('Yes')
                return None
            insert_index = int(com_param[4])
            # 2024-09-02 revised
            click_com = add_click(com_id, float(com_param[0]), float(com_param[1]), bool(com_param[2]),
                                  insert_index, len(script), float(com_param[3]))
            if click_com is None:
                return None
            script = update_loop_if_else(insert_index, script, 1)
            script.insert(insert_index, click_com)
        elif option == 'scroll':
            if len(com_param) != 5:
                return None
            insert_index = int(com_param[4])
            # 2024-09-02 revised
            scroll_com = add_scroll(com_id, float(com_param[0]), float(com_param[1]), float(com_param[2]),
                                    insert_index, len(script), float(com_param[3]))
            if scroll_com is None:
                return None
            script = update_loop_if_else(insert_index, script, 1)
            script.insert(insert_index, scroll_com)
        elif option == 'loop':
            if len(com_param) != 2:
                print("Loop length error")
                return None
            loop_com = add_loop(com_id, int(com_param[0]), int(com_param[1]), len(script))
            if loop_com is None:
                print("Failed in loop")
                return None
            # print(loop_com)
            # print(loop_dict)
            script = update_loop_if_else(int(com_param[1]), script, 1)
            script = update_loop_if_else(int(com_param[1]) + 1, script, 1)
            script.insert(int(com_param[1]), loop_com[1])
            script.insert(int(com_param[1]), loop_com[0])

            # print("update complete!")
        elif option == 'if_else':
            if len(com_param) != 4:
                return None
            insert_index = int(com_param[3])
            if_else_com = add_if_else(com_id, float(com_param[0]), int(com_param[1]), insert_index,
                                      len(script), com_param[2])
            if if_else_com is None:
                return None
            # update script after if
            script = update_loop_if_else(insert_index, script, 1)
            # update script after elif
            for i in range(int(com_param[1])):
                script = update_loop_if_else(insert_index + i + 1, script, 1)
            # update script after else
            script = update_loop_if_else(insert_index + int(com_param[1]) + 1, script, 1)
            # update script after end
            script = update_loop_if_else(insert_index + int(com_param[1]) + 2, script, 1)
            # insert end
            script.insert(insert_index, if_else_com[3])
            # insert else
            script.insert(insert_index, if_else_com[2])
            # insert elif
            if_else_com[1].reverse()
            for elif_comp in if_else_com[1]:
                script.insert(insert_index, elif_comp)
            # insert if
            script.insert(insert_index, if_else_com[0])

        elif option == 'pause':
            if len(com_param) != 2:
                print("Parameter don't match")
                return None
            insert_index = int(com_param[1])
            pause_com = add_pause(com_id, float(com_param[0]), insert_index, len(script))
            if pause_com is None:
                print("Value error")
                return None
            script = update_loop_if_else(insert_index, script, 1)
            script.insert(insert_index, pause_com)

        elif option == 'del':
            if len(com_param) != 1:
                return None
            tmp_script = del_component(script, int(com_param[0]))
            if tmp_script is None:
                print("Deletion Failed")
                return None
            script = tmp_script

        elif option == 'drag':
            if len(com_param) != 2:
                return None
            script = drag_component(int(com_param[0]), int(com_param[1]), script)

        elif option == 'edit':
            script = edit_component_param(com_param, script)

        elif option == 'break':
            if len(com_param) != 1:
                return None
            insert_index = int(com_param[0])
            break_comp = add_break(com_id, insert_index, script)
            if break_comp is None:
                print("Value error")
                return None
            script = update_loop_if_else(insert_index, script, 1)
            script.insert(insert_index, break_comp)

        elif option == 'script':
            if len(com_param) != 2:
                return None
            insert_index = int(com_param[1])
            script_comp = add_script(com_id, com_param[0], insert_index, script)
            if script_comp is None:
                return None
            script = update_loop_if_else(insert_index, script, 1)
            script.insert(insert_index, script_comp)

        elif option == 'long_click':
            if len(com_param) != 5:
                # print('Yes')
                return None
            insert_index = int(com_param[4])
            long_click_com = add_long_click(com_id, float(com_param[0]), float(com_param[1]), float(com_param[2]),
                                  insert_index, len(script), float(com_param[3]))
            if long_click_com is None:
                return None
            script = update_loop_if_else(insert_index, script, 1)
            script.insert(insert_index, long_click_com)

        elif option == 'dragger':
            if len(com_param) != 4:
                return None
            insert_index = int(com_param[3])
            drag_com = add_drag(com_id, float(com_param[0]), float(com_param[1]), insert_index, len(script),
                                float(com_param[2]))
            if drag_com is None:
                return None
            script = update_loop_if_else(insert_index, script, 1)
            script.insert(insert_index, drag_com)

        else:
            print('No such command!')
            return None

    except Exception as e:
        print(f"Unknown error {e}")
        return None
    # print(script)
    return script


def add_click(com_id, speed: float, timeout_value: float, doubleclick: bool, insert_index: int,
              limit: int, conf: float) -> dict | None:
    """
    Add clicker element
    :param com_id: id to indentify component
    :param speed: the speed of which to move toward click target
    :param timeout_value: the time until the program give up searching
    :param doubleclick: whether to double-click the target image
    :param insert_index: the index to insert
    :param limit: the upper limit of the current block
    :param conf: the confidence of the image
    :return: a dictionary that specify the click instruction
    """
    if insert_index < 0 or insert_index > limit:
        print(f"Inserted index out of range: {insert_index}: {limit}")
        return None
    click_dict = {
        'component': 'click',
        'id': com_id,
        'speed': speed,
        'time_out': timeout_value,
        'double_click': doubleclick,
        'conf': conf
    }
    return click_dict


def add_scroll(com_id, speed: float, timeout_value: float, scroll_length: float, insert_index: int,
               limit: int, conf: float) -> dict | None:
    """
    Add scroll element
    :param com_id: id to indentify component
    :param speed: the speed of which to move toward scroll target
    :param timeout_value: the time until the program give up searching
    :param scroll_length: the length of which to scroll
    :param insert_index: the index to insert
    :param limit: the upper limit of the current block
    :param conf: the confidence of the image
    :return: a dictionary that specify the scroll instruction
    """
    if insert_index < 0 or insert_index > limit:
        print(f"Inserted index out of range: {insert_index}: {limit}")
        return None
    scroll_dict = {
        'component': 'scroll',
        'id': com_id,
        'speed': speed,
        'time_out': timeout_value,
        'scroll_length': scroll_length,
        'conf': conf
    }
    return scroll_dict


def add_loop(com_id, times: int, start_in: int, limit: int) -> tuple | None:
    """
    Add loop element
    :param com_id: id to indentify component
    :param times: the times of which to execute
    :param start_in: the starting index of the loop
    :param limit: the upper limit of the current block
    :return: none if illegal, otherwise the loop instruction
    """
    # check start index
    if start_in < 0 or start_in > limit:
        print(f"Inserted index out of range: {start_in}: {limit}")
        return None
    loop_start_comp = {
        'component': 'loop_s',
        'id': com_id,
        'end': start_in + 1
    }
    loop_end_comp = {
        'component': 'loop_e',
        'id': com_id,
        'goto': start_in,
        'times': times
    }
    return loop_start_comp, loop_end_comp


def add_if_else(com_id, timeout_value: float,  elif_cnt: int, if_index: int, limit: int, conf: float) -> tuple | None:
    """
    Add if-else element
    :param timeout_value: the time until the program give up searching
    :param com_id: id to indentify component
    :param if_index: the index to insert
    :param limit: the upper limit of the current block
    :param elif_cnt: the number of elif to insert
    :param conf: the confidence of the image
    :return: none if illegal, otherwise the if_else instruction
    """
    # check if the inserted index exceed the limit
    if if_index < 0 or if_index > limit:
        print(f"Inserted index out of range: {if_index}: {limit}")
        return None
    if elif_cnt < 0:
        elif_cnt = 0
    elif_next_index = if_index + 1
    if_dict = {
        'component': 'if',
        'id': com_id,
        'if': if_index,
        'next': elif_next_index,
        'else': if_index + elif_cnt + 1,
        'end': if_index + elif_cnt + 2,
        'comp_count': elif_cnt,
        'time_out': timeout_value,
        # 2024-09-02 revised
        'conf': conf
    }
    elif_next_index += 1
    elif_list = []
    for i in range(elif_cnt):
        elif_dict = {
            'component': 'elif',
            'id': f"{com_id}_{i}",
            'if': if_index,
            'next': elif_next_index,
            'else': if_index + elif_cnt + 1,
            'end': if_index + elif_cnt + 2,
            # 2024-09-02 revised
            'conf': conf
        }
        elif_list.append(elif_dict)
        elif_next_index += 1

    else_dict = {
        'component': 'else',
        'id': com_id,
        'if': if_index,
        'else': if_index + elif_cnt + 1,
        'end': if_index + elif_cnt + 2,
    }
    end_dict = {
        'component': 'end',
        'id': com_id,
        'if': if_index,
        'else': if_index + elif_cnt + 1,
        'end': if_index + elif_cnt + 2,
    }
    return if_dict, elif_list, else_dict, end_dict


def add_pause(com_id, pause_time: float, insert_index: int, limit: int) -> dict | None:
    """
    Add pause element
    :param com_id: com_id: id to indentify component
    :param pause_time: the time to pause
    :param insert_index: the index to insert
    :param limit: the upper limit of the current block
    :return: dict if success, None if fail
    """
    if insert_index < 0 or insert_index > limit:
        print(f"Inserted index out of range: {insert_index}: {limit}")
        return None
    pause_com = {
        'component': 'pause',
        'id': com_id,
        'pause_time': pause_time
    }
    return pause_com


def add_break(com_id, insert_index: int, script: list) -> dict | None:
    """
    Break from the current loop
    :param com_id: id to indentify component
    :param insert_index: the index to insert component
    :param script: the main script block
    :return: dict if success, None if fail
    """
    limit = len(script)
    if insert_index < 0 or insert_index > limit:
        print(f"Inserted index out of range: {insert_index}: {limit}")
        return None

    def _cal_nearest_loop() -> int:
        nearest_loop = len(script) - 1
        nearest_loop_start = -1
        # loop for nearest loop end
        for comp_index in range(insert_index, len(script)):
            if script[comp_index]['component'] == 'loop_e':
                if nearest_loop_start == -1 or script[comp_index]['id'] != script[nearest_loop_start]['id']:
                    nearest_loop = comp_index
                    break
            elif script[comp_index]['component'] == 'loop_s':
                nearest_loop_start = comp_index
        return nearest_loop

    nearest_loop = _cal_nearest_loop()
    if nearest_loop < 0:
        print("Not inside loop block")
        return None
    break_com = {
        'component': 'break',
        'id': com_id,
        'goto': nearest_loop + 1
    }
    return break_com


def add_script(com_id, script_name: str, insert_index: int, script: list) -> dict | None:
    """
    Insert script as component
    :param com_id: id to indentify component
    :param script_name: the name of the inserted script
    :param insert_index: the index to insert component
    :param script: the main script
    :return: dict if success, None if fail
    """
    limit = len(script)
    if insert_index < 0 or insert_index > limit:
        print(f"Inserted index out of range: {insert_index}: {limit}")
        return None
    if script_name not in os.listdir('Scripts'):
        script_name = 'tmp.json'
    script_comp = {
        'component': 'script',
        'id': com_id,
        'script_name': script_name
    }
    return script_comp


def add_long_click(com_id, speed: float, timeout_value: float, duration: float, insert_index: int,
              limit: int, conf: float) -> dict | None:
    """
    Add long click component
    :param com_id: id to indentify component
    :param speed: the speed of which to move toward click target
    :param timeout_value: the time until the program give up searching
    :param duration: the time to hold down the mouse
    :param insert_index: the index to insert the component
    :param limit: the length of the script
    :param conf: the confidence of the image
    :return: dict if success, None if fail
    """
    if insert_index < 0 or insert_index > limit:
        print(f"Inserted index out of range: {insert_index}: {limit}")
        return None
    long_click_dict = {
        'component': 'long_click',
        'id': com_id,
        'speed': speed,
        'time_out': timeout_value,
        'duration': duration,
        'conf': conf
    }
    return long_click_dict


def add_drag(com_id, timeout_value: float, duration: float, insert_index: int,
              limit: int, conf: float) -> dict | None:
    """
    Add drag component
    :param com_id: id to indentify component
    :param timeout_value: the time until the program give up searching
    :param duration: the time it takes to drag target image to destination image
    :param insert_index: the index to insert the component
    :param limit: the length of the script
    :param conf: the confidence of the image
    :return: dict if success, None if fail
    """
    if insert_index < 0 or insert_index > limit:
        print(f"Inserted index out of range: {insert_index}: {limit}")
        return None
    drag_dict = {
        'component': 'drag',
        'id': com_id,
        'time_out': timeout_value,
        'duration': duration,
        'conf': conf
    }
    return drag_dict


def update_loop_if_else(insert_index: int, script: list, offset: int) -> list:
    """
    Update the script
    :param insert_index: the index to insert component into
    :param script: the main script block
    :return: the main script block
    """
    # alter the main script before insertion
    for action in script:
        if action['component'] == 'else' or action['component'] == 'end':
            if action['if'] >= insert_index:
                action['if'] += offset
            if action['else'] >= insert_index:
                action['else'] += offset
            if action['end'] >= insert_index:
                action['end'] += offset
        elif action['component'] == 'if' or action['component'] == 'elif':
            if action['if'] >= insert_index:
                action['if'] += offset
            if action['else'] >= insert_index:
                action['else'] += offset
            if action['end'] >= insert_index:
                action['end'] += offset
            if action['next'] >= insert_index:
                action['next'] += offset
        elif action['component'] == 'loop_s':
            if action['end'] >= insert_index:
                action['end'] += offset
        elif action['component'] == 'loop_e':
            if action['goto'] >= insert_index:
                action['goto'] += offset
        elif action['component'] == 'break':
            if action['goto'] >= insert_index:
                action['goto'] += offset
    # print(f"alter main script complete")
    # alter the loop dict
    # print("Update Complete!")
    return script


def del_individual_component(script: list, del_index: int) -> list | None:
    """
    Update script after deletion of uni-component
    :param script: the main script block
    :param del_index: the index of the component to delete
    :return:
    """
    if del_index < 0 or del_index >= len(script):
        print('Deleted index out of range')
        return None
    script = update_loop_if_else(del_index, script, -1)
    script.pop(del_index)
    return script


def del_component(script: list, del_index: int) -> list | None:
    """
    Update script after deletion
    :param script: the main script block
    :param del_index: the index of the component to delete
    :return: Script if legal, None if illegal
    """
    if del_index < 0 or del_index >= len(script):
        print('Deleted index out of range')
        return None
    comp = script[del_index]['component']
    # print(comp)
    if comp == 'loop_s':
        loop_end_index = script[del_index]['end']
        script = del_individual_component(script, loop_end_index)
        script = del_individual_component(script, del_index)
    elif comp == 'loop_e':
        loop_start_index = script[del_index]['goto']
        script = del_individual_component(script, del_index)
        script = del_individual_component(script, loop_start_index)
    elif comp == 'if' or comp == 'elif' or comp == 'else' or comp == 'end':
        if_index = script[del_index]['if']
        else_index = script[del_index]['else']
        end_index = script[del_index]['end']
        if_else_id = script[del_index]['id'].split('_')[0]
        elif_indexes = []
        for i in range(end_index, if_index, -1):
            if script[i]['component'] == 'elif' and script[i]['id'].split('_')[0] == if_else_id:
                elif_indexes.append(i)
        # delete backward
        script = del_individual_component(script, end_index)
        script = del_individual_component(script, else_index)
        for elif_index in elif_indexes:
            script = del_individual_component(script, elif_index)
        script = del_individual_component(script, if_index)
    elif (comp == 'click' or comp == 'scroll' or comp == 'pause' or comp == 'break' or comp == 'script'
          or comp == 'long_click' or comp == 'drag'):
        script = del_individual_component(script, del_index)
    return script


def edit_component_img(block_name: str, img_edit_index: int, script: list) -> bool:
    """
    Edit the image in component
    :param block_name: the name of the main script block
    :param img_edit_index: the index of the component
    :param script: the main script block
    :return: True if success, False if Fail
    """
    block_name = block_name.replace('.json', '')
    if img_edit_index < 0 or img_edit_index > len(script):
        return False
    comp = script[img_edit_index]['component']
    comp_id = script[img_edit_index]['id']
    if comp == 'click' or comp == 'scroll' or comp == 'if' or comp == 'elif' or comp == 'long_click':
        print(f"try saving: {block_name}_{str(comp_id)}")
        select_img('Script_Img_Component',  f"{block_name}_{str(comp_id)}")
        return True
    elif comp == 'drag':
        select_img('Script_Img_Component', f"{block_name}_{str(comp_id)}_0")
        select_img('Script_Img_Component', f"{block_name}_{str(comp_id)}_1")
        return True
    return False


def drag_component(edit_index: int, insert_index: int, script: list) -> list | None:
    """
    Edit the main script
    :param edit_index: the index to edit
    :param insert_index: the index to insert
    :param script: the main script block
    :return: the main script block if success, None if fail
    """
    if edit_index < 0 or edit_index >= len(script) or insert_index < 0 or insert_index >= len(script):
        return None
    comp = script[edit_index]['component']
    if comp == 'click':
        # print(f"{edit_index} to {insert_index}")
        if insert_index > edit_index:
            insert_index -= 1
        elif insert_index == edit_index:
            return script
        # extract the parameter
        com_id = script[edit_index]['id']
        speed = script[edit_index]['speed']
        time_out = script[edit_index]['time_out']
        double_click = script[edit_index]['double_click']
        # 2024-09-02 revised
        conf = script[edit_index]['conf']
        # just delete and re-add
        script = del_individual_component(script, edit_index)
        # print(script)
        script = update_loop_if_else(insert_index, script, 1)
        # print(script)
        click_com = add_click(com_id, speed, time_out, double_click, insert_index, len(script), conf)
        script.insert(insert_index, click_com)
        # print(script)
    elif comp == 'scroll':
        if insert_index > edit_index:
            insert_index -= 1
        elif insert_index == edit_index:
            return script
        # extract the parameter
        com_id = script[edit_index]['id']
        speed = script[edit_index]['speed']
        time_out = script[edit_index]['time_out']
        scroll_length = script[edit_index]['scroll_length']
        # 2024-09-02 revised
        conf = script[edit_index]['conf']
        # just delete and re-add
        script = del_individual_component(script, edit_index)
        script = update_loop_if_else(insert_index, script, 1)
        scroll_com = add_scroll(com_id, speed, time_out, scroll_length, insert_index, len(script), conf)
        script.insert(insert_index, scroll_com)
    elif comp == 'pause':
        if insert_index > edit_index:
            insert_index -= 1
        elif insert_index == edit_index:
            return script
        # extract the parameter
        com_id = script[edit_index]['id']
        pause_time = script[edit_index]['pause_time']
        # just delete and re-add
        script = del_individual_component(script, edit_index)
        script = update_loop_if_else(insert_index, script, 1)
        pause_com = add_pause(com_id, pause_time, insert_index, len(script))
        script.insert(insert_index, pause_com)
    # if the component is if-else
    elif comp == 'if' or comp == 'else' or comp == 'end' or comp == 'elif':
        if_start_index = script[edit_index]['if']
        if_end_index = script[edit_index]['end']
        # check if the insert index is still in if-else block
        if insert_index >= if_start_index and insert_index <= if_end_index:
            print("Can't move inside own block")
            return None
        if_else_block = script[if_start_index: if_end_index + 1]
        # update the main script first
        script = update_loop_if_else(if_end_index + 1, script, -len(if_else_block))

        # recalculate the insert index
        if insert_index > edit_index:
            insert_index -= len(if_else_block)
        # update the if-else block
        if_else_block = update_loop_if_else(0, if_else_block, insert_index - if_start_index)
        # delete elements in the main script
        for i in range(len(if_else_block)):
            script.pop(if_start_index)
        # update the script again
        script = update_loop_if_else(insert_index, script, len(if_else_block))
        # adding the if-else block back
        if_else_block.reverse()
        for component in if_else_block:
            script.insert(insert_index, component)

    # if the component is a loop
    elif comp == 'loop_s' or comp == 'loop_e':
        if comp == 'loop_s':
            loop_start_index = edit_index
            loop_end_index = script[edit_index]['end']
        else:
            loop_start_index = script[edit_index]['goto']
            loop_end_index = edit_index
        # check if the insert index is still in loop block
        if insert_index >= loop_start_index and insert_index <= loop_end_index:
            print("Can't move inside own block")
            return None
        loop_block = script[loop_start_index: loop_end_index + 1]
        # update the main script first
        script = update_loop_if_else(loop_end_index + 1, script, -len(loop_block))
        # recalculate the insert index
        if insert_index > edit_index:
            insert_index -= len(loop_block)
        # update the loop block
        loop_block = update_loop_if_else(0, loop_block, insert_index - loop_start_index)
        # delete elements in the main script
        for i in range(len(loop_block)):
            script.pop(loop_start_index)
        # update the script again
        script = update_loop_if_else(insert_index, script, len(loop_block))
        # adding the loop block back
        loop_block.reverse()
        for component in loop_block:
            script.insert(insert_index, component)
    elif comp == 'break':
        if insert_index > edit_index:
            insert_index -= 1
        elif insert_index == edit_index:
            return script
        # extract the parameter
        com_id = script[edit_index]['id']
        # just delete and re-add
        script = del_individual_component(script, edit_index)
        script = update_loop_if_else(insert_index, script, 1)
        break_com = add_break(com_id, insert_index, script)
        script.insert(insert_index, break_com)
    elif comp == 'script':
        if insert_index > edit_index:
            insert_index -= 1
        elif insert_index == edit_index:
            return script
        # extract the parameter
        com_id = script[edit_index]['id']
        script_name = script[edit_index]['script_name']
        # just delete and re-add
        script = del_individual_component(script, edit_index)
        script = update_loop_if_else(insert_index, script, 1)
        script_com = add_script(com_id, script_name, insert_index, script)
        script.insert(insert_index, script_com)
    elif comp == 'long_click':
        if insert_index > edit_index:
            insert_index -= 1
        elif insert_index == edit_index:
            return script
        # extract the parameter
        com_id = script[edit_index]['id']
        speed = script[edit_index]['speed']
        time_out = script[edit_index]['time_out']
        duration = script[edit_index]['duration']
        # 2024-09-02 revised
        conf = script[edit_index]['conf']
        # just delete and re-add
        script = del_individual_component(script, edit_index)
        # print(script)
        script = update_loop_if_else(insert_index, script, 1)
        # print(script)
        long_click_com = add_long_click(com_id, speed, time_out, duration, insert_index, len(script), conf)
        script.insert(insert_index, long_click_com)
    elif comp == 'drag':
        # print(f"{edit_index} to {insert_index}")
        if insert_index > edit_index:
            insert_index -= 1
        elif insert_index == edit_index:
            return script
        # extract the parameter
        com_id = script[edit_index]['id']
        time_out = script[edit_index]['time_out']
        duration = script[edit_index]['duration']
        # 2024-09-02 revised
        conf = script[edit_index]['conf']
        # just delete and re-add
        script = del_individual_component(script, edit_index)
        # print(script)
        script = update_loop_if_else(insert_index, script, 1)
        # print(script)
        click_com = add_drag(com_id, time_out, duration, insert_index, len(script), conf)
        script.insert(insert_index, click_com)
    return script


def edit_component_param(com_param: list, script: list) -> list | None:
    """
    Edit the parameters of the components
    :param com_param: the component parameters
    :param script: the main script block
    :return: the main script if success, None if fail
    """
    try:
        edit_index = int(com_param[-1])
    except Exception as e:
        print(e)
        return None
    if edit_index < 0 or edit_index >= len(script):
        print("Edit index out of range")
        return None
    comp = script[edit_index]['component']
    if comp == 'click':
        # 2024-09-02 revised
        if len(com_param) != 5:
            return None
        try:
            script[edit_index]['speed'] = float(com_param[0])
            script[edit_index]['time_out'] = float(com_param[1])
            script[edit_index]['double_click'] = bool(com_param[2])
            # 2024-09-02 revised
            script[edit_index]['conf'] = float(com_param[3])
        except Exception as e:
            print(e)
            return None
    elif comp == 'scroll':
        # 2024-09-02 revised
        if len(com_param) != 5:
            return None
        try:
            script[edit_index]['speed'] = float(com_param[0])
            script[edit_index]['time_out'] = float(com_param[1])
            script[edit_index]['scroll_length'] = float(com_param[2])
            # 2024-09-02 revised
            script[edit_index]['conf'] = float(com_param[3])
        except Exception as e:
            print(e)
            return None
    elif comp == 'pause':
        if len(com_param) != 2:
            return None
        try:
            script[edit_index]['pause_time'] = float(com_param[0])
        except Exception as e:
            print(e)
            return None
    elif comp == 'if' or comp == 'else' or comp == 'end' or comp == 'elif':
        # 2024-09-02 revised
        if len(com_param) != 4:
            return None
        try:
            if_index = int(script[edit_index]['if'])
            else_ori_index = int(script[edit_index]['else'])
            elif_count = max(script[if_index]['comp_count'], int(com_param[0]))
            # if elif_count > script[edit_index]['comp_count']:
            #     elif_count = elif_count - script[if_index]['comp_count']
            # else:
            #     print(f"Please change the elif count, input {elif_count}, previous: {script[if_index]['comp_count']}")
            #     return None
            if elif_count > script[if_index]['comp_count']:
                elif_count = elif_count - script[if_index]['comp_count']
                # get the id
                if_else_id = script[edit_index]['id']
                # get the max elif count
                max_elif_id = -1
                ori_elif_index = -1
                for cur_index in range(if_index, else_ori_index):
                    if script[cur_index]['component'] == 'elif':
                        max_elif_id = max(max_elif_id, int(script[cur_index]['id'].split('_')[1]))
                        ori_elif_index = cur_index
                # print(com_param)
                # print(f"{max_elif_id}, {ori_elif_index}, {elif_count}")
                # append at the index right before else
                # append elif component
                # first update the script after else index

                script = update_loop_if_else(else_ori_index, script, elif_count)
                # recalculate the if, else, end index
                if_index = int(script[edit_index]['if'])
                else_index = int(script[edit_index]['else'])
                end_index = int(script[edit_index]['end'])
                conf = float(com_param[2])
                # append elif component to the script

                # then insert elif component backward (next index)
                elif_next_index = else_index
                for i in range(max_elif_id + elif_count, max_elif_id, -1):
                    elif_dict = {
                        'component': 'elif',
                        'id': f"{if_else_id}_{i}",
                        'if': if_index,
                        'next': elif_next_index,
                        'else': else_index,
                        'end': end_index,
                        'conf': conf
                    }
                    script.insert(else_ori_index, elif_dict)
                    elif_next_index -= 1

                # and update next index if there were an elif component
                if ori_elif_index != -1:
                    script[ori_elif_index]['next'] = elif_next_index
                else:
                    script[if_index]['next'] = elif_next_index
                script[if_index]['comp_count'] = elif_count + script[if_index]['comp_count']

            script[if_index]['time_out'] = float(com_param[1])
            # 2024-09-02 revised
            script[if_index]['conf'] = float(com_param[2])
        except Exception as e:
            print(e)
            return None
    elif comp == 'loop_e':
        if len(com_param) != 2:
            return None
        try:
            script[edit_index]['times'] = int(com_param[0])
        except Exception as e:
            print(e)
            return None
    elif comp == 'loop_s':
        if len(com_param) != 2:
            return None
        try:
            end_index = int(script[edit_index]['end'])
            script[end_index]['times'] = int(com_param[0])
        except Exception as e:
            print(e)
            return None
    elif comp == 'script':
        if len(com_param) != 2:
            return None
        if com_param[0] not in os.listdir('Scripts'):
            print(f"Script {com_param} does not exist")
            return None
        script[edit_index]['script_name'] = com_param[0]
    elif comp == 'long_click':
        if len(com_param) != 5:
            return None
        try:
            script[edit_index]['speed'] = float(com_param[0])
            script[edit_index]['time_out'] = float(com_param[1])
            script[edit_index]['duration'] = float(com_param[2])
            # 2024-09-02 revised
            script[edit_index]['conf'] = float(com_param[3])
        except Exception as e:
            print(e)
            return None
    elif comp == 'drag':
        if len(com_param) != 4:
            return None
        try:
            script[edit_index]['time_out'] = float(com_param[0])
            script[edit_index]['duration'] = float(com_param[1])
            # 2024-09-02 revised
            script[edit_index]['conf'] = float(com_param[2])
        except Exception as e:
            print(e)
            return None

    return script


def current_id(script: list) -> int:
    """
    find the current max id
    :param script: the main script
    :return: the current max id
    """
    cur_id = 0
    for comp in script:
        if int(comp['id'].split('_')[0]) > cur_id:
            cur_id = int(comp['id'])
    return cur_id + 1


if __name__ == '__main__':
    script_save_dir = 'Scripts'
    script = []
    block_name = input("Please enter block name: ")
    com_id = 0
    if f"{block_name}.json" in os.listdir(script_save_dir):
        with open(os.path.join(script_save_dir, f"{block_name}.json"), 'r', encoding='utf-8') as in_f:
            script = json.load(in_f)
        com_id = current_id(script)
        while True:
            user_choice = input("Script already exists, r to replace, or enter another name: ")
            if user_choice != 'r':
                if f"{user_choice}.json" in os.listdir(script_save_dir):
                    print("Name Exists! change another name!")
                else:
                    block_name = user_choice
                    break
            else:
                break

    while True:
        try:
            user_input = input(f'Please enter your command: ').split()
        except:
            continue
        if len(user_input) == 1 and user_input[0] == 'q':
            break
        elif user_input[0] == 'edit_img':
            if len(user_input) != 2:
                print("Argument error")
                continue
            try:
                edit_img_index = int(user_input[1])
            except:
                print("Index error!")
                continue
            try:
                edit_result = edit_component_img(block_name, edit_img_index, script)
                if edit_result:
                    break
                else:
                    print("Edit image Failed!")
            except:
                print("Edit image Failed!")
        else:
            com_param = user_input[1:]
            tmp_script = block_appender(str(com_id), script, user_input[0], com_param)
            if tmp_script is not None:
                script = tmp_script
                if user_input[0] == 'click' or user_input[0] == 'scroll':
                    # select_img('Script_Img_Component', f"{block_name}_{str(com_id)}")
                    pass
                elif user_input[0] == 'if_else':
                    # select_img('Script_Img_Component', f"{block_name}_{str(com_id)}")
                    try:
                        times = int(user_input[2])
                    except Exception as e:
                        print(e)
                        continue
                    for i in range(times):
                        input(f'press any key to continue taking {i} elif: ')
                        # select_img('Script_Img_Component', f"{block_name}_{str(com_id)}_{i}")
                com_id += 1
            else:
                print("Failed to append script")
    print(f"Final Script: {script}")
    with open(os.path.join(script_save_dir, f"{block_name}.json"), 'w', encoding='utf-8') as out_f:
        json.dump(script, out_f, indent=2, ensure_ascii=False)
