import json
import os
from action_chain import Clicker, Scroller, Locator, Holder, Dragger


def compile_script(script_path: str, detect_time: float) -> dict:
    """
    Compile and make action chain
    :param script_path: path to the script
    :param detect_time: the time to detect an image
    :return: action chain dictionary
    """
    with open(script_path, 'r', encoding='utf-8') as script_f:
        script = json.load(script_f)
    image_dir = "Script_Img_Component"
    block_name = os.path.basename(script_path).replace(".json", "")
    action_chain = {}

    for action in script:
        if action['component'] == 'click':
            action_id = f"{block_name}_{action['id']}"
            # print(action_id)
            img_path = os.path.join(image_dir, f"{action_id}.jpg")
            clicker_action = Clicker(img_path, action['speed'], action['double_click'],
                                     action['time_out'] / detect_time, action['conf'])
            action_chain[action_id] = clicker_action
        elif action['component'] == 'scroll':
            action_id = f"{block_name}_{action['id']}"
            img_path = os.path.join(image_dir, f"{action_id}.jpg")
            scroller_action = Scroller(img_path, action['speed'], action['scroll_length'],
                                       action['time_out'] / detect_time, action['conf'])
            action_chain[action_id] = scroller_action
        elif action['component'] == 'if':
            action_id = f"{block_name}_{action['id']}"
            img_path = os.path.join(image_dir, f"{action_id}.jpg")
            locator_action = Locator(img_path, 1, action['conf'])
            action_chain[action_id] = locator_action
        elif action['component'] == 'elif':
            action_id = f"{block_name}_{action['id']}"
            img_path = os.path.join(image_dir, f"{action_id}.jpg")
            locator_action = Locator(img_path, 1, action['conf'])
            action_chain[action_id] = locator_action
        elif action['component'] == 'long_click':
            action_id = f"{block_name}_{action['id']}"
            img_path = os.path.join(image_dir, f"{action_id}.jpg")
            long_click_action = Holder(img_path, action['speed'], action['duration'],
                                     action['time_out'] / detect_time, action['conf'])
            action_chain[action_id] = long_click_action
        elif action['component'] == 'drag':
            action_id = f"{block_name}_{action['id']}"
            target_img_path = os.path.join(image_dir, f"{action_id}_0.jpg")
            destination_img_path = os.path.join(image_dir, f"{action_id}_1.jpg")
            dragger_action = Dragger(target_img_path, destination_img_path, action['duration'],
                                     action['time_out'] / detect_time, action['conf'])
            action_chain[action_id] = dragger_action

    return action_chain


if __name__ == '__main__':
    script_dir = 'Scripts'
    my_script = compile_script(os.path.join(script_dir, 'test1.json'), 1)
    print(my_script)
