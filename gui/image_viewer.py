"""
Gui for view image.
"""

import os
import subprocess
import tkinter

import cfg
from PIL import Image, ImageTk
from utils.utils import (MyButton, MyFrame, MyLabel, SmbChecker,
                         get_coll_name, my_copy)
from .images_compare import ImagesCompare


class Globals:
    """
    Stores variables
    """
    src = str
    path_lbl = tkinter.Label


def on_closing(obj):
    """
    Destroys current tkinter toplevel.
    Clears `cfg.IMAGES_COMPARE` list.
    * param `obj`: tkinter toplevel
    """
    if len(cfg.IMAGES_COMPARE)==2:
        cfg.IMAGES_COMPARE.remove(Globals.src)
    else:
        cfg.IMAGES_COMPARE.clear()
    obj.destroy()


class ImagePreview(tkinter.Toplevel):
    """
    Creates new window (tkinter Top Level) with image & buttons.
    * param `src`: source path of image.
    """
    def __init__(self, src):
        Globals.src = src

        tkinter.Toplevel.__init__(self)
        self.withdraw()

        if not SmbChecker().check():
            return

        if src is None:
            return

        self.protocol("WM_DELETE_WINDOW", lambda: on_closing(self))
        self.bind('<Command-w>', lambda e: on_closing(self))

        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)
        self.resizable(0,0)
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')

        ImageFrame(self).pack(fill=tkinter.BOTH, expand=True)
        CopyCompare(self).pack(pady=(15, 15))
        NamePath(self).pack(pady=(0, 15), padx=15)
        OpenCloseFrame(self).pack()

        cfg.ROOT.update_idletasks()

        self.geometry(f'+{cfg.ROOT.winfo_x() + 100}+{cfg.ROOT.winfo_y()}')
        self.deiconify()


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image 0.8 wight, height of screen.
    * param `master`: tkinter toplevel.
    """
    def __init__(self, master):
        self.master = master
        img_src = Image.open(Globals.src)
        img_copy= img_src.copy()

        MyLabel.__init__(self, master, borderwidth=0)
        self['bg']='black'
        self.bind("<Configure>", lambda e: self.resize(e, img_copy))

    def resize(self, e, img):
        """
        Fits image to label size.
        * param `img`: current image.
        """
        size = (e.width, e.height)
        img.thumbnail(size)
        Globals.img = ImageTk.PhotoImage(img)

        self.configure(image=Globals.img)
        self.image_names = Globals.img

        if len(cfg.IMAGES_COMPARE) < 2:
            cfg.IMAGES_COMPARE.add(Globals.src)


class NamePath(MyFrame):
    """
    Creates tkinter frame.
    * param `master`: tkinter top level.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)

        txt = (f'Коллекция: {get_coll_name(Globals.src)}'
                f'\nИмя: {Globals.src.split(os.sep)[-1]}')

        Globals.path_lbl = MyLabel(
            self, text=txt, justify=tkinter.CENTER)
        Globals.path_lbl.pack(side=tkinter.LEFT)


class CopyCompare(MyFrame):
    """
    Tkinter frame with button that calls images compare method.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        b_wight = 13

        copy_btn = MyButton(self, text='Копировать имя')
        copy_btn.configure(height=1, width=b_wight)
        copy_btn.cmd(lambda e: self.copy_name(copy_btn))
        copy_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        comp_btn = MyButton(self, text='Сравнить')
        comp_btn.configure(height=1, width=b_wight)
        comp_btn.cmd(lambda e: self.compare(comp_btn))
        comp_btn.pack(side=tkinter.RIGHT)

        if os.path.exists(Globals.src):
            open_btn = MyButton(self, text='Папка с фото')
            open_btn.configure(height=1, width=b_wight)
            open_btn.cmd(lambda e: self.open_folder(open_btn))
            open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

    def compare(self, btn):
        """
        Compares two images and open gui with result.
        * param `btn`: current tkinter button.
        """
        btn.press()
        if len(cfg.IMAGES_COMPARE) < 2:
            old_txt = Globals.path_lbl['text']
            txt = '\nОткройте второе изображение'
            Globals.path_lbl['text'] = txt
            cfg.ROOT.after(
                1500, lambda: Globals.path_lbl.configure(text=old_txt))
            return
        ImagesCompare()

    def copy_name(self, btn):
        """
        Copies path to folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        my_copy(Globals.src.split('/')[-1].split('.')[0])

    def open_folder(self, btn):
        """
        Opens folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        path = '/'.join(Globals.src.split('/')[:-1])
        subprocess.check_output(["/usr/bin/open", path])


class OpenCloseFrame(MyFrame):
    """
    Creates tkinter frame for open and close buttons.
    * param `master`: tkinter frame.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)

        close = MyButton(self, text='Закрыть')
        close.configure(height=2)
        close.cmd(lambda e: on_closing(self.winfo_toplevel()))
        close.pack(side=tkinter.RIGHT)
