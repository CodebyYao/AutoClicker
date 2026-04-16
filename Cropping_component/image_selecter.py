from tkinter import Tk
from tkinter.filedialog import askopenfilename
import shutil
import os


def select_img(save_dir: str, image_save_name: str) -> None:
    """
    Save the image user selected
    :param save_dir: the directory to save the image
    :param image_save_name: the name of the saved image
    :return: None
    """
    try:
        root = Tk()
        # prevents an empty tkinter window from appearing
        root.withdraw()
        root.call('wm', 'attributes', '.', '-topmost', True)
        filename = askopenfilename()
        root.update()
        dst = f"{os.path.join(save_dir, image_save_name)}.jpg"
        shutil.copyfile(filename, dst)
    except Exception as e:
        print("Image insertion failed, please remember to alter again.")
        print(e)


if __name__ == "__main__":
    select_img('Script_Img_Component', 'test1')
