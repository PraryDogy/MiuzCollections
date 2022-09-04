"""
Gui for view image.
"""

import os
import subprocess
import tkinter

import cfg
from PIL import Image, ImageTk
from Utils.Styled import MyButton, MyFrame, MyLabel
from Utils.Utils import SmbChecker, my_copy


class Globals:
    """
    Stores variables
    """
    src = str


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

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind('<Command-w>', lambda e: self.destroy())
        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)
        self.resizable(0,0)

        ImageFrame(self).pack(fill=tkinter.BOTH)
        NamePath(self).pack(pady=(15, 15), padx=15)
        OpenCloseFrame(self).pack()

        cfg.ROOT.update_idletasks()
        self.geometry(f'+{self.winfo_x()}+0')
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image 0.8 wight, height of screen.
    * param `master`: tkinter toplevel.
    """
    def __init__(self, master):
        self.master = master
        img_src = Image.open(Globals.src)
        img_copy= img_src.copy()

        MyLabel.__init__(
            self, master, height=int(cfg.ROOT.winfo_screenheight()*0.7),
            borderwidth=0)
        self.configure(bg='black')
        self.bind("<Configure>", lambda e: self.resize(e, img_copy))

    def resize(self, e, img):
        """
        Fits image to label size.
        * param `img`: current image.
        """
        size = (e.width, e.height)
        img.thumbnail(size)
        img_tk = ImageTk.PhotoImage(img)

        self.configure(image=img_tk)
        self.image_names = img_tk

class NamePath(MyFrame):
    """
    Creates tkinter frame.
    * param `master`: tkinter top level.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)

        path_lbl = MyLabel(
            self, text=Globals.src.replace(cfg.PHOTO_DIR, ''),
            wraplength=500, justify=tkinter.LEFT)
        path_lbl.pack(side=tkinter.LEFT)

        copy_btn = MyButton(self, text='Копировать имя')
        copy_btn.configure(height=1)
        copy_btn.Cmd(lambda e: self.copy_name(copy_btn))
        copy_btn.pack(side=tkinter.LEFT, padx=(15, 0))

    def copy_name(self, btn=MyButton):
        """
        Copies path to folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.Press()
        my_copy(Globals.src.split('/')[-1].split('.')[0])


class OpenCloseFrame(MyFrame):
    """
    Creates tkinter frame for open and close buttons.
    * param `master`: tkinter frame.
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)

        close = MyButton(self, text='Закрыть')
        close.configure(height=2)
        close.Cmd(lambda e: self.winfo_toplevel().destroy())
        close.pack(side=tkinter.RIGHT)

        if os.path.exists(Globals.src):
            open_btn = MyButton(self, text='Открыть папку')
            open_btn.configure(height=2)
            open_btn.Cmd(lambda e: self.open_folder(open_btn))
            open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

    def open_folder(self, btn=MyButton):
        """
        Opens folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.Press()
        path = '/'.join(Globals.src.split('/')[:-1])
        subprocess.check_output(["/usr/bin/open", path])
