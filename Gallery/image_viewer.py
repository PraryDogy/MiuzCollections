"""
Gui for view image.
"""

import os
import subprocess
import tkinter

import cfg
from PIL import Image, ImageTk
from Utils.Styled import MyFrame, MyButton, MyLabel
from Utils.Utils import my_copy


class Globals:
    """
    Stores variables
    """
    src = str()


class ImagePreview(tkinter.Toplevel):
    """
    Creates new window (tkinter Top Level) with image & buttons.
    * param src: source path of image.
    """
    def __init__(self, src):
        if src is None:
            return

        Globals.src = src

        tkinter.Toplevel.__init__(self)
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind('<Command-w>', lambda e: self.destroy())
        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)

        if os.path.exists(Globals.src):
            cfg.ROOT.update_idletasks()
            ImageFrame(self).pack(expand=True, fill=tkinter.BOTH)
        else:
            ImageError(self)

        NamePathFrame(self)
        OpenCloseFrame(self)

        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.geometry(f'+{self.winfo_x()}+0')
        self.deiconify()


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image 0.8 wight, height of screen.
    * param master: tkinter toplevel.
    """
    def __init__(self, master):
        img_src = Image.open(Globals.src)
        img_copy= img_src.copy()

        screen_h = int(cfg.ROOT.winfo_screenheight()*0.8)
        screen_w = int(cfg.ROOT.winfo_screenwidth()*0.8)
        img_copy.thumbnail((screen_w, screen_h))

        img_tk = ImageTk.PhotoImage(img_copy)

        MyLabel.__init__(self, master, image=img_tk)
        self.image_names = img_tk


class ImageError(MyLabel):
    """
    Creates tkinter label with error message.
    * param master: tkinter toplevel
    """
    def __init__(self, master):
        txt = (
            'Не могу открыть изображение. Возможные причины:'
            '\n\nНет подключения к сетевому диску MIUZ,'
            '\nпопробуйте открыть любую папку на сетевом диске.'
            '\n\nПопробуйте запустить полное сканирование из настроек.'
            )
        MyLabel.__init__(self, master, text=txt)
        self.pack()


class NamePathFrame(MyFrame):
    """
    Creates tkinter frame.
    * param master: tkinter top level.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        self.pack(pady=(15, 15))
        NamePathTitle(self)
        NamePathButton(self)


class NamePathTitle(MyLabel):
    """
    Creates tkinter label with src path to img.
    * param master: tkinter frame.
    """
    def __init__(self, master):
        MyLabel.__init__(
            self, master, text=Globals.src.replace(cfg.PHOTO_DIR, ''))
        self.pack(side=tkinter.LEFT)


class NamePathButton(MyButton):
    """
    Creates tkinter button with copy img path fuction.
    * param master: tkinter frame.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='Копировать имя')
        self.configure(height=1)
        self.Cmd(lambda e: self.copy_name())
        self.pack(side=tkinter.LEFT, padx=(15, 0))

    def copy_name(self):
        """
        Copies path to folder with image.
        Simulates button press with color.
        """
        self.Press()
        my_copy(Globals.src.split('/')[-1].split('.')[0])


class OpenCloseFrame(MyFrame):
    """
    Creates tkinter frame for open and close buttons.
    * param master: tkinter frame.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        self.pack()
        if os.path.exists(Globals.src):
            OpenButton(self)
        CloseButton(self)


class OpenButton(MyButton):
    """
    Creates tkinter button with open image folder function.
    * param master: tkinter frame.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='Открыть папку')
        self.configure(height=2)
        self.Cmd(lambda e: self.open_folder())
        self.pack(side=tkinter.LEFT, padx=(0, 15))

    def open_folder(self):
        """
        Opens folder with image.
        Simulates button press with color.
        """
        self.Press()
        path = '/'.join(Globals.src.split('/')[:-1])
        subprocess.check_output(["/usr/bin/open", path])


class CloseButton(MyButton):
    """
    Creates tkinter button with close current toplevel function.
    * param master: tkinter frame.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='Закрыть')
        self.configure(height=2)
        self.Cmd(lambda e: self.winfo_toplevel().destroy())
        self.pack(side=tkinter.RIGHT)
