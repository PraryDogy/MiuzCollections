"""
Tkinter toplevel window with compared images with open cv method.
"""

from datetime import datetime
import os
import threading
import tkinter

import cfg
import cv2
from PIL import Image, ImageTk
from utils.utils import Compare, MyButton, MyFrame, MyLabel


def on_closing():
    """
    Destroys all tkinter toplevels with "compare" name.
    Clears `cfg.IMAGES_COMPARE`, `cfg.IMAGES_COMPARED` lists.
    """
    cfg.IMAGES_COMPARE.clear()
    cfg.IMAGES_COMPARED.clear()

    comp_win = [v for k, v in cfg.ROOT.children.items() if 'compare' in k]
    [i.destroy() for i in comp_win]


class ImagesCompare(tkinter.Toplevel):
    """
    Tkinter toplevel window with compared images with open cv method.
    """
    def __init__(self):
        tkinter.Toplevel.__init__(self)

        prevs = [v for k, v in cfg.ROOT.children.items() if 'prev' in k]
        [i.destroy() for i in prevs]

        analyse_lbl = AnalyseLbl(self)
        analyse_lbl.pack()
        close_btn = CloseBtn(self)
        close_btn.pack(pady=(0, 10))

        self.protocol("WM_DELETE_WINDOW", on_closing)
        self.bind('<Command-w>', lambda e: on_closing())
        self.configure(bg=cfg.BGCOLOR, padx=10, pady=5)
        self.resizable(0,0)
        self.grab_set()

        xx = cfg.ROOT.winfo_x()+cfg.ROOT.winfo_width()//2 - self.winfo_width()//2
        yy = cfg.ROOT.winfo_y()+cfg.ROOT.winfo_height()//2 - self.winfo_height()//2
        self.geometry(f'+{xx}+{yy}')

        tsk = threading.Thread(target=Compare)
        tsk.start()

        while tsk.is_alive():
            cfg.ROOT.update()

        if cfg.IMAGES_COMPARED[0] is None:
            analyse_lbl.destroy()
            ErrorLbl(self).pack(side=tkinter.TOP)
            close_btn.pack(side=tkinter.BOTTOM, pady=(0, 10))
            return

        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{int(side*1.8)}x{side}')
        cfg.ROOT.update_idletasks()
        center = cfg.ROOT.winfo_screenwidth()//2-self.winfo_width()//2
        self.geometry(f'+{center}+{0}')
        self.grab_release()

        analyse_lbl.destroy()
        ImagesSplit(self).pack(
            side=tkinter.TOP, fill=tkinter.BOTH, expand=True, pady=(0, 15))
        ImagesInfo(self).pack(side=tkinter.BOTTOM, pady=(0, 15))
        close_btn.pack(side=tkinter.BOTTOM, pady=(0, 10))


class AnalyseLbl(MyLabel):
    """
    Tkinter label with text and styles from cfg.
    """
    def __init__(self, master):
        MyLabel.__init__(self, master, text='Анализирую', width=25, height=4)


class ErrorLbl(MyLabel):
    """
    Tkinter label with text and styles from cfg.
    """
    def __init__(self, master):
        txt = (
            'Ошибка'
            '\n- Изображения разного размера'
            '\n- Это разные изображения'
            )
        MyLabel.__init__(self, master, text=txt, width=25, height=4)


class CloseBtn(MyButton):
    """
    Tkinter close window button.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='Закрыть')
        self.cmd(lambda e: on_closing())


class ImagesInfo(MyFrame):
    """
    Tkinter label with text and styles from cfg.
    Text: images names, images sizes, image modification dates
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        images_src = list(cfg.IMAGES_COMPARE)
        file1, file2 = images_src[0], images_src[1]

        file1_size = f'{(os.path.getsize(file1)/(1024*1024)).__round__(2)}мб'
        file2_size = f'{(os.path.getsize(file2)/(1024*1024)).__round__(2)}мб'

        file1_mod = datetime.fromtimestamp(
            os.path.getmtime(file1)).strftime("%d-%m-%Y %H:%M:%S")
        file2_mod = datetime.fromtimestamp(
            os.path.getmtime(file2)).strftime("%d-%m-%Y %H:%M:%S")

        txt = (
            f'Совпадение: {int(cfg.IMAGES_SIMILAR)}%'
            f'\nИмена: {file1.split("/")[-1]} / {file2.split("/")[-1]}'
            f'\nРазмеры: {file1_size} / {file2_size}'
            f'\nДата изменения: {file1_mod} / {file2_mod}'
            )

        info = MyLabel(master, text=txt)
        info.pack()


class ImagesSplit(MyFrame):
    """
    Tkinter frame for images
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)

        ImageFrame(self, cfg.IMAGES_COMPARED[0]).pack(
            fill=tkinter.BOTH, expand=True, side=tkinter.LEFT, padx=(0, 5))

        ImageFrame(self, cfg.IMAGES_COMPARED[1]).pack(
            fill=tkinter.BOTH, expand=True, side=tkinter.RIGHT)


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image 0.8 wight, height of screen.
    * param `master`: tkinter toplevel.
    """
    def __init__(self, master, image):
        self.master = master

        conv = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb = Image.fromarray(conv)

        MyLabel.__init__(self, master, borderwidth=0)
        self['bg']='black'
        self.bind("<Configure>", lambda e: self.resize(e, image_rgb))

    def resize(self, e, img):
        """
        Fits image to label size.
        * param `img`: current image.
        """
        size = (e.width, e.height)
        img.thumbnail(size)
        img = ImageTk.PhotoImage(img)

        self.configure(image=img)
        self.image_names = img
