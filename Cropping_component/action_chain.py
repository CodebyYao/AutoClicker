import time
import pyautogui as pt
from time import sleep


class Initializer:
    def __init__(self):
        pt.FAILSAFE = True
        pass

    def detect_time(self):
        start_time = time.time()
        try:
            position = pt.locateCenterOnScreen('Resources/Set_up.png', confidence=.7)
            pt.moveTo(position[0], position[1])
        except Exception as e:
            pass
        return time.time() - start_time


class Clicker:
    def __init__(self, target_img, speed=.001, doubleclick=False, retry_times=1, conf=0.7):
        """
        :param target_img: the image to click on
        :param speed: the speed of which to move toward click target
        :param retry_times: the number of time the program attempts to search
        :param doubleclick: whether to double-click the target image
        :param conf: the confidence of the image
        """
        self.target_img = target_img
        self.speed = speed
        self.doubleclick = doubleclick
        pt.FAILSAFE = True
        self.retry_times = int(retry_times)
        self.conf = conf
        # print(self.retry_times)

    def nav_to_image(self, offset_x=0, offset_y=0, doubleclick=False):
        """
        Move to target image and click
        :param offset_x: x offset to click the target image
        :param offset_y: y offset to click the target image
        :param doubleclick: whether to double-click the target image
        :return: execute success or not
        """
        for i in range(self.retry_times):
            try:
                position = pt.locateCenterOnScreen(self.target_img, confidence=self.conf)
                pt.moveTo(position[0]+offset_x, position[1]+offset_y, duration=self.speed)
                if self.doubleclick or doubleclick:
                    # print("Double clicked")
                    pt.doubleClick()
                    pt.doubleClick()
                else:
                    pt.leftClick()
                return True  # execute success
            except Exception as e:
                if i >= self.retry_times / 2:
                    self.time_out()
                # print(f"Can't locate {e}")
                pass
        return False  # error occur

    def time_out(self):
        try:
            position = pt.locateCenterOnScreen('Resources/timeout_support.png', confidence=.7)
            pt.moveTo(position[0] - 600, position[1] - 600, duration=self.speed)
            pt.doubleClick()
        except:
            pass


class Scroller:
    def __init__(self, loc_png, speed=.001, scroll_length=-700, retry_times=1, conf=0.7):
        """
        :param loc_png: the image to scroll on
        :param speed: the speed of which to move toward scroll target
        :param retry_times: the number of time the program attempts to search
        :param scroll_length: the length of which to scroll
        :param conf: the confidence of the image
        """
        self.loc_png = loc_png
        self.speed = speed
        self.scroll_length = scroll_length
        pt.FAILSAFE = True
        self.retry_times = int(retry_times)
        self.conf = conf

    def nav_to_scroll(self, x_offset=0, y_offset=0):
        """
        Move to target image and scroll
        :param x_offset: x offset to scroll the target image
        :param y_offset: y offset to scroll the target image
        :return: execute success or not
        """
        for i in range(self.retry_times):
            try:
                # print(f"image: {self.loc_png}")
                position = pt.locateCenterOnScreen(image=self.loc_png, confidence=self.conf)
                # print(f"Position: {position}")
                pt.moveTo(x=position[0] + x_offset, y=position[1]+y_offset, duration=self.speed)
                # print("Move success")
                # print(f"Parameter: {self.scroll_length}, {position[0]}, {position[1]}")
                pt.scroll(int(self.scroll_length), x=position[0] + x_offset, y=position[1]+y_offset)
                # print("Scroll success")
                return True  # execute success
            except Exception as e:
                print(f"cant find scroll image {e}")
                pass
        return False  # error occur


class Locator:
    def __init__(self, target_png, retry_times=1, conf=0.7):
        """
        :param target_png: image to detect
        :param retry_times: the number of time the program attempts to search
        :param conf: the confidence of the image
        """
        self.target_png = target_png
        pt.FAILSAFE = True
        self.retry_times = int(retry_times)
        self.conf = conf

    def check_if_locate(self) -> bool:
        """
        Check whether an element is on screen
        :return:
        """
        try:
            position = pt.locateCenterOnScreen(self.target_png, confidence=self.conf)
            if position is not None:
                return True  # execute success
        except:
            pass
        return False  # error occur


class Holder:
    def __init__(self, target_img, speed=.001, hold_time=0, retry_times=1, conf=0.7):
        self.hold_time = hold_time
        self.target_img = target_img
        self.speed = speed
        pt.FAILSAFE = True
        self.retry_times = int(retry_times)
        self.conf = conf

    def nav_to_hold(self, offset_x=0, offset_y=0):
        for i in range(self.retry_times):
            try:
                position = pt.locateCenterOnScreen(self.target_img, confidence=self.conf)
                pt.moveTo(position[0]+offset_x, position[1]+offset_y, duration=self.speed)
                pt.mouseDown()
                sleep(self.hold_time)
                pt.mouseUp()
                return True  # execute success
            except Exception as e:
                pass
        return False  # error occur


class Dragger:
    def __init__(self, target_img, destination_img, duration=0.1, retry_times=1, conf=0.7):
        self.target_img = target_img
        self.destination_img = destination_img
        self.duration = duration
        pt.FAILSAFE = True
        self.retry_times = int(retry_times)
        self.conf = conf

    def drag_to_dest(self):
        for i in range(self.retry_times):
            try:
                target_position = pt.locateCenterOnScreen(self.target_img, confidence=self.conf)
                destination_position = pt.locateCenterOnScreen(self.destination_img, confidence=self.conf)
                pt.moveTo(target_position[0], target_position[1])
                pt.dragTo(destination_position[0], destination_position[1], self.duration, button='left')
                return True  # execute success
            except Exception as e:
                pass
        return False  # error occur