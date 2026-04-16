import os
import tkinter as tk
import json
from script_maker_v2 import block_appender, edit_component_img, edit_component_param, current_id, del_component
from runner import run_script, init_time
from time import sleep
from PIL import Image, ImageTk


class Block(tk.Frame):
    grid = [[1] * 10 for _ in range(10)]
    id = 0
    selected_block = None

    def __init__(self, master, component_type, canvas, delete_area, image_area, info_area, param_area, block_param_list
                 , script_name, multiply, **kwargs):
        super().__init__(master, bd=2, relief='raised', **kwargs)
        self.component_type = component_type
        self.canvas = canvas  # 畫布(工作區)，控制block的地方
        self.delete_area = delete_area  # 刪除區域
        self.image_area = image_area  # 放照片的區域
        self.info_area = info_area  # 顯示block的資訊
        self.param_area = param_area  # 讓使用者輸入參數
        self.block_param_list = block_param_list  # 儲存component的參數
        self.is_drag = False  #是否拖曳
        self.script_name = script_name  #script名稱

        self.label = tk.Label(self, text=component_type, width=4, height=2, bg=self['bg'])
        self.label.pack(padx=10, pady=10)
        self.params = self.get_default_params()  # 設置component初始參數

        self.bind("<Button-1>", self.on_click)  # 綁定點擊
        self.bind("<ButtonRelease-1>", self.on_release)  # 施放點擊

        # 2024/8/31 revised
        self.label.bind("<Button-1>", self.on_label_click)
        self.label.bind("<ButtonRelease-1>", self.on_label_release)

        self._drag_data = {"x": 0, "y": 0}  # 設置拖曳初始位置
        self.grid_size = 60 * multiply  # 設置每個格子大小
        self.previous_pos = 0  # 查看每個component位於哪個格子
        self.param_entries = {}  # 用於儲存參數輸入框
        self.image_path = None  # 圖片路徑
        if master == canvas:
            self.bind("<B1-Motion>", self.on_drag)  # 假如在block在工作區，則多綁定一個拖曳功能
            # 2024/8/31 revised
            self.label.bind("<B1-Motion>", self.on_label_drag)

    def get_default_params(self):  # 初始參數
        if self.component_type == "click":
            return {"component": "click", "id": self.id, "speed": 0.001, "time_out": 5, "double_click": False,
                    "conf": 0.7}
        elif self.component_type == "scroll":
            return {"component": "scroll", "id": self.id, "speed": 0.001, "time_out": 10, "scroll_length": 400,
                    "conf": 0.7}
        elif self.component_type == "if_else":
            return {"component": "if_else", "id": self.id, "time_out": 5, "elif_cnt": 0, "conf": 0.7}
        elif self.component_type == "if":
            return {'component': 'if', 'id': self.id, 'if': 0, 'next': 1, 'else': 1, 'end': 2, 'comp_count': 0, 'time_out': 5.0, "conf": 0.7}
        elif self.component_type == "else":
            return {'component': 'else', 'id': self.id, 'if': 0, 'else': 1, 'end': 2}
        elif self.component_type == "end":
            return {'component': 'end', 'id': self.id, 'if': 0, 'else': 1, 'end': 2}
        elif self.component_type == "W_s":
            return {"component": "loop", "id": self.id, "times": 5}
        elif self.component_type == "loop_s":
            return {'component': 'loop_s', 'id': self.id, 'end': 1}
        elif self.component_type == "loop_e":
            return {'component': 'loop_e', 'id': self.id, 'goto': 0, 'times': 5}
        elif self.component_type == "pause":
            return {"component": "pause", "id": self.id, "pause_time": 1}
        elif self.component_type == "break":
            return {"component": "break", "id": self.id}
        elif self.component_type == "script":
            return {"component": "script", "id": self.id, "script_name": ''}
        elif self.component_type == "long_click":
            return {"component": "long_click", "id": self.id, "speed": 0.001, "time_out": 5, "duration": 1.0
                , "conf": 0.7}
        elif self.component_type == "drag":
            return {"component": "dragger", "id": self.id, "time_out": 5, "duration": 1.0, "conf": 0.7}
        else:
            return {}

    def on_click(self, event):  # 點擊block
        self.is_drag = False  # 查看是否拖曳
        # self.selected_block = event.widget
        # if self.selected_block in self.canvas.winfo_children():
        #     self.selected_block.config(highlightbackground="yellow", highlightthickness=3)
        # self.config(highlightbackground="yellow", highlightthickness=3)
        # print(f"{event.x} {event.y}")
        self._drag_data = {"x": event.x, "y": event.y}  # 紀錄拖曳初始位置
        self.update_script()  # 根據演算法更新block顯示位置
        if self.master == self.canvas:
            # print('in canvas')
            self.previous_pos = self.grid_pos()  # 查看當前格子編號
            self.update_params()  # 更新block 參數
        self.display_block_info()  # 顯示block attribute

    def on_drag(self, event):  # 拖曳block
        self.is_drag = True
        x = self.winfo_x() + (event.x if event else 0) - self._drag_data["x"]
        y = self.winfo_y() + (event.y if event else 0) - self._drag_data["y"]
        snapped_x, snapped_y = self.snap_to_grid(x, y)  # 將block append在離最近的格子上
        self.place(x=snapped_x, y=snapped_y)  # 放置block

    def on_release(self, event):  # 施放block
        if self.is_drag:
            current_pos = self.grid_pos()  # 查看當前施放格子編號
            self.block_param_list = self.check_delete_area()  # 利用check_delete_area來查看是否將block拖曳至delete_area
            self.remove_block()
            self.drag_component(self.previous_pos, current_pos)
        self.display_block_info()

    # 2024/8/31 revised
    def on_label_release(self, event):  # 施放block
        if self.is_drag:
            current_pos = self.grid_pos()  # 查看當前施放格子編號
            self.block_param_list = self.check_delete_area()  # 利用check_delete_area來查看是否將block拖曳至delete_area
            self.remove_block()
            self.drag_component(self.previous_pos, current_pos)
        self.display_block_info()

    # 2024/8/31 revised
    def on_label_drag(self, event):  # 拖曳block
        self.is_drag = True
        x = self.winfo_x() + (event.x + self.label.winfo_x() if event else 0) - self._drag_data["x"]
        y = self.winfo_y() + (event.y + self.label.winfo_y() if event else 0) - self._drag_data["y"]
        snapped_x, snapped_y = self.snap_to_grid(x, y)  # 將block append在離最近的格子上
        self.place(x=snapped_x, y=snapped_y)  # 放置block

    # 2024/8/31 revised
    def on_label_click(self, event):  # 點擊block
        self.is_drag = False  # 查看是否拖曳
        self._drag_data = {"x": event.x + self.label.winfo_x(), "y": event.y + self.label.winfo_y()}  # 紀錄拖曳初始位置
        self.update_script()  # 根據演算法更新block顯示位置
        if self.master == self.canvas:
            # print('in canvas')
            self.previous_pos = self.grid_pos()  # 查看當前格子編號
            self.update_params()  # 更新block 參數
        self.display_block_info()  # 顯示block attribute

    def grid_pos(self):
        return self.winfo_y() // self.grid_size * 10 + self.winfo_x() // self.grid_size

    def remove_block(self):
        for widget in self.canvas.winfo_children():
            if isinstance(widget, Block) and widget.master == self.canvas and self.is_drag is True:
                widget.destroy()

    def drag_component(self, previous_pos: int, insert_pos: int):
        if self.master == self.canvas:
            tmp_script = block_appender('', self.block_param_list, 'drag', [previous_pos, insert_pos])
            if tmp_script is not None:
                self.block_param_list = tmp_script
            else:
                pass
        app.load_blocks_from_list()  # 根據list內容來更新block位置

    def update_script(self):
        if self.master == self.canvas:
            self.previous_pos = self.grid_pos()
            self.params = self.block_param_list[self.previous_pos]
        input_param = [par for par in self.params.values()]
        input_param.append(len(self.block_param_list))
        insert_id = current_id(self.block_param_list)
        if self.master != self.canvas:
            tmp_script = block_appender(insert_id, self.block_param_list, input_param[0], input_param[2:])
            if tmp_script is not None:
                self.block_param_list = tmp_script
        app.load_blocks_from_list()  # 根據list內容來更新block位置

    def snap_to_grid(self, x, y):  # 將block append在離最近的格子上
        x_snap = round(x / self.grid_size) * self.grid_size
        y_snap = round(y / self.grid_size) * self.grid_size
        return x_snap, y_snap

    def is_within_bounds(self, x, y):  # 是否有在範圍之內
        max_width = self.canvas.winfo_width()
        max_height = self.canvas.winfo_height()
        return 0 <= x < max_width and 0 <= y < max_height

    def check_delete_area(self):  # 删除区域

        try:
            block_x, block_y = self.winfo_rootx(), self.winfo_rooty()
        except tk.TclError:
            # If the widget has been destroyed, skip the rest of this method
            return self.block_param_list

        delete_area_x1, delete_area_y1 = self.delete_area.winfo_rootx(), self.delete_area.winfo_rooty()
        delete_area_x2 = delete_area_x1 + self.delete_area.winfo_width()
        delete_area_y2 = delete_area_y1 + self.delete_area.winfo_height()

        if delete_area_x1 <= block_x <= delete_area_x2 and delete_area_y1 <= block_y <= delete_area_y2:
            tmp_script = del_component(self.block_param_list, self.previous_pos)
            print("Block deleted successfully")
            return tmp_script
        return self.block_param_list

    def display_block_info(self):
        self.info_area.config(state=tk.NORMAL)
        self.info_area.delete(1.0, tk.END)
        display_msg = ''
        for param_key, param_value in self.params.items():
            display_msg += f"{param_key}: {param_value}\n"
        self.info_area.insert(tk.END, display_msg)
        self.info_area.config(state=tk.DISABLED)
        self.image_path = f"{self.script_name.replace('.json', '')}_{self.block_param_list[self.previous_pos]['id']}.jpg"
        if self.image_path not in os.listdir('Script_Img_Component'):
            self.image_path = None
        else:
            self.image_path = os.path.join('Script_Img_Component', self.image_path)
        self.display_image(self.image_path)

    def update_params(self):  # 更新block参数
        def display_param(script_param_dict: dict, start_index: int):
            for param, value in list(script_param_dict.items())[start_index:]:
                frame = tk.Frame(self.param_area)
                frame.pack()
                label = tk.Label(frame, text=param)
                label.pack(side=tk.LEFT)
                entry = tk.Entry(frame, width=8)
                entry.insert(0, value)
                entry.pack(side=tk.RIGHT)
                self.param_entries[param] = entry

        for widget in self.param_area.winfo_children():
            widget.destroy()

        if self.component_type == "if":
            display_param(self.block_param_list[self.previous_pos], 6)

        elif self.component_type == "loop_e":
            # loop_end_index = self.block_param_list[self.params['goto']]['end']
            display_param(self.block_param_list[self.previous_pos], 3)

        elif self.component_type == 'loop_s':
            loop_end_index = self.params['end']
            display_param(self.block_param_list[loop_end_index], 3)

        elif self.component_type == "else" or self.component_type =="end" \
                or self.component_type == "elif":
            if_start_index = self.params['if']
            display_param(self.block_param_list[if_start_index], 6)
        elif self.component_type == "break":
            pass

        else:
            display_param(self.block_param_list[self.previous_pos], 2)

        update_button = tk.Button(self.param_area, text="Update", command=self.update_block_params)
        update_button.pack(pady=5)
        image_button = tk.Button(self.param_area, text="Select image", command=self.image_select)
        image_button.pack(pady=5)
        run_button = tk.Button(self.param_area, text="Run Script", command=self.run_script)
        run_button.pack(pady=5)

    def image_select(self):
        # self.image_path = "popcat3.jpg"
        return edit_component_img(self.script_name, self.previous_pos, self.block_param_list)

    def display_image(self, image_path):
        if image_path is not None:
            image = Image.open(image_path)
            image = image.resize((200, 200), Image.LANCZOS)
            self.image_tk = ImageTk.PhotoImage(image)
            self.image_area.create_image(0, 0, anchor=tk.NW, image=self.image_tk, tags='display_img')
        else:
            self.image_area.delete('display_img')

    def run_script(self):
        with open(os.path.join('Scripts', self.script_name), 'w', encoding='utf-8') as script_f:
            json.dump(self.block_param_list, script_f, indent=2, ensure_ascii=False)
        detect_time = init_time()
        print("Begin in 10s...")
        sleep(10)
        print("Executing script...")
        result = run_script('Scripts', self.script_name, detect_time)
        print(f"Executed complete: {result}")
        return

    def convert_params(self, com_param, component_type):
        try:
            if component_type == 'click':
                return [float(com_param[0]), float(com_param[1]), bool(int(com_param[2])), float(com_param[3])]
            elif component_type == 'scroll':
                return [float(com_param[0]), float(com_param[1]), float(com_param[2]), float(com_param[3])]
            elif component_type == 'pause':
                return [float(com_param[0])]
            elif component_type == 'if':
                return [int(com_param[0]), float(com_param[1]), float(com_param[2])]
            elif component_type == 'loop_e':
                return [int(com_param[0])]
            elif component_type == 'loop_s':
                return [int(com_param[0])]
            elif component_type == 'long_click':
                return [float(com_param[0]), float(com_param[1]), float(com_param[2]), float(com_param[3])]
            elif component_type == 'drag':
                return [float(com_param[0]), float(com_param[1]), float(com_param[2])]
            else:
                return com_param
        except ValueError as e:
            print(f"Error converting parameters: {e}")
            return None

    def update_block_params(self):
        if self:
            com_param = [entry.get() for entry in self.param_entries.values()]
            try:
                converted_params = self.convert_params(com_param, self.block_param_list[self.previous_pos]['component'])\
                                   + [self.previous_pos]
                print(converted_params)
                if converted_params is not None:
                    updated_script = edit_component_param(converted_params, self.block_param_list)
                    if updated_script is not None:
                        self.block_param_list = updated_script
                        self.display_block_info()
                        app.load_blocks_from_list()
                        print(f"Updated block parameters: {self.block_param_list[self.previous_pos]}")
                    else:
                        print("Failed to update block parameters")
                else:
                    print("Error in parameter conversion")
            except Exception as e:
                print(f"Failed to update block parameters: {e}")


class Script_name:
    def __init__(self, root, multiply):
        self.root = root
        self.root.title("Enter Script Name")
        init_width = 300 * multiply
        init_height = 100 * multiply
        self.root.geometry(f"{init_width}x{init_height}")
        self.entry = tk.Entry(root)  # 放入單行輸入框
        self.entry.pack()
        self.submit_button = tk.Button(root, text="Submit", command=self.on_submit)
        self.submit_button.pack()

    def on_submit(self):
        self.script_name = self.entry.get()
        self.root.destroy()


class App:
    def __init__(self, root, script_name, multiply):
        script_name += '.json'

        self.multiply = multiply
        self.root = root
        self.root.title("Block Editor")
        init_width = 1500 * multiply
        init_height = 950 * multiply
        self.root.geometry(f"{init_width}x{init_height}")

        self.selected_blocks = []
        self.block_list = []

        self.palette = tk.Frame(self.root, bg='lightgrey', width=300 * self.multiply, height=300 * self.multiply)
        self.palette.pack(side=tk.LEFT, padx=10, pady=10)

        self.canvas = tk.Canvas(self.root, bg='white', width=600 * self.multiply, height=600 * self.multiply)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH)

        self.delete_area = tk.Frame(self.root, bg='red', width=200 * self.multiply, height=200 * self.multiply)
        self.delete_area.pack(side=tk.BOTTOM, anchor='sw')

        self.image_area = tk.Canvas(self.root, bg='white', width=200 * multiply, height=200 * self.multiply, state=tk.DISABLED)
        self.image_area.pack(side=tk.LEFT, padx=10, pady=10)

        self.info_area = tk.Text(self.root, width=20 * self.multiply, height=10 * self.multiply, state=tk.DISABLED)
        self.info_area.pack(side=tk.LEFT, padx=10, pady=10)

        self.param_area = tk.Frame(self.root, width=200 * self.multiply, height=200 * self.multiply)
        self.param_area.pack(side=tk.RIGHT, padx=10, pady=10)

        self.Save_button = tk.Button(self.root, text="Save", command=self.save_script)
        self.Save_button.pack(side=tk.BOTTOM, pady=10)

        self.create_grid()
        self.script_name = script_name
        self.block_param_list = []
        if script_name in os.listdir('Scripts'):
            with open(os.path.join('Scripts', script_name), 'r', encoding='utf-8') as in_f:
                self.block_param_list = json.load(in_f)
            self.load_blocks_from_list()
        self.create_palette_blocks()

    def create_palette_blocks(self):
        block_texts = ["click", "scroll", "if_else", "W_s", "pause", "break", "script", "long_click", 'drag']
        color_tags = ['lightsalmon', 'bisque2', 'palegreen', 'gold', 'hotpink', 'red2', 'lightblue', 'tomato', 'cornsilk3']
        for text, color_tags in zip(block_texts, color_tags):

            block = Block(self.palette, text, self.canvas, self.delete_area, self.image_area ,self.info_area, self.param_area,
                          self.block_param_list, self.script_name, self.multiply, bg=color_tags)
            block.pack(pady=10, padx=10)
            block.bind("<ButtonRelease-1>", self.on_palette_block_release)  # 一定要加這行

    def on_palette_block_release(self, event):
        pass

    def create_grid(self):
        for i in range(10):
            for j in range(10):
                x0, y0 = i * 60 * self.multiply, j * 60 * self.multiply
                x1, y1 = x0 + 60 * self.multiply, y0 + 60 * self.multiply
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black")
                self.canvas.create_text((x0 + x1) // 2, (y0 + y1 + 40 * self.multiply) // 2, text=j * 10 + i + 1)

    def save_script(self):
        with open(os.path.join('Scripts', self.script_name), 'w', encoding='utf-8') as script_f:
            json.dump(self.block_param_list, script_f, indent=2, ensure_ascii=False)

    def load_blocks_from_list(self):
        for block_id, comp in enumerate(self.block_param_list):
            component_type = comp['component']
            row = block_id // 10
            col = block_id % 10
            x = col * 60 * self.multiply
            y = row * 60 * self.multiply
            color = 'lightblue'
            if component_type == 'click':
                color = 'lightsalmon'
            elif component_type == 'scroll':
                color = 'bisque2'
            elif component_type == 'pause':
                color = 'hotpink'
            elif component_type == 'break':
                color = 'red2'
            elif component_type == 'loop_s' or component_type == 'loop_e':
                color = 'gold'
            elif (component_type == 'if' or component_type == 'else' or component_type == 'end'
                  or component_type == 'elif'):
                color = 'palegreen'
            elif component_type == 'script':
                color = 'lightblue'
            elif component_type == 'long_click':
                color = 'tomato'
            elif component_type == 'drag':
                color = 'cornsilk3'
            new_block = Block(self.canvas, component_type, self.canvas, self.delete_area, self.image_area, self.info_area,
                              self.param_area, self.block_param_list, self.script_name, self.multiply, bg=color)
            new_block.place(x=x, y=y)


if __name__ == "__main__":
    root1 = tk.Tk()
    s_n = Script_name(root1, 2)
    root1.wait_window(s_n.root)  # 等待 Script_name 窗口关闭

    root = tk.Tk()
    app = App(root, s_n.script_name, 2)
    root.mainloop()