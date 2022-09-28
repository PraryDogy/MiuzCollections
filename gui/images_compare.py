import subprocess
import tkinter

import cfg
from utils.utils import MyButton, MyFrame, MyLabel, my_copy


def images_list():
    return [i.__dict__['image_names'] for i in list(cfg.IMAGES_COMPARE)]

def on_closing(obj):
    """
    Destroys current tkinter toplevel.
    Clears `cfg.IMAGES_COMPARE` list.
    * param `obj`: tkinter toplevel
    """
    
    prevs = [v for k, v in cfg.ROOT.children.items() if "preview" in k]
    [i.destroy() for i in prevs]
    cfg.IMAGES_COMPARE.clear()
    cfg.IMAGES_INFO.clear()
    cfg.IMAGES_SRC.clear()
    obj.destroy()


class Globals:
    curr_img = tkinter.Image
    img_frame = tkinter.Label
    info_frame = tkinter.Label
    ind = int


class ImagesCompare(tkinter.Toplevel):
    def __init__(self):
        prevs = [v for k, v in cfg.ROOT.children.items() if "preview" in k]
        [i.withdraw() for i in prevs]

        tkinter.Toplevel.__init__(self)
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", lambda: on_closing(self))
        self.bind('<Command-w>', lambda e: on_closing(self))
        self.bind('<Command-q>', lambda e: quit())

        self.configure(bg=cfg.BGCOLOR, padx=15, pady=15)
        self.resizable(0,0)
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')

        ImageFrame(self).pack(fill=tkinter.BOTH, expand=True, pady=(0, 15))
        CopyCompare(self).pack(pady=(0, 15))
        NamePath(self).pack(pady=(0, 15))
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
        MyLabel.__init__(self, master, borderwidth=0)
        self['bg']='black'

        Globals.curr_img = images_list()[0]
    
        self.configure(
            image=Globals.curr_img,
            width=Globals.curr_img.height(),
            height=Globals.curr_img.height()
            )

        Globals.img_frame = self
        Globals.ind = 0

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

        open_btn = MyButton(self, text='Папка с фото')
        open_btn.configure(height=1, width=b_wight)
        open_btn.cmd(lambda e: self.open_folder(open_btn))
        open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        toogle = MyButton(self, text='Переключить')
        toogle.configure(height=1, width=b_wight)
        toogle.cmd(lambda e: self.param(toogle))
        toogle.pack(side=tkinter.LEFT, padx=(0, 0))

        self.flick(toogle)

    def copy_name(self, btn):
        """
        Copies path to folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        my_copy(cfg.IMAGES_SRC[Globals.ind].split('/')[-1].split('.')[0])

    def open_folder(self, btn):
        """
        Opens folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        path = '/'.join(cfg.IMAGES_SRC[Globals.ind].split('/')[:-1])
        subprocess.check_output(["/usr/bin/open", path])

    def param(self, btn):
            btn.press()
            images = images_list()

            Globals.ind = 0 if images.index(Globals.curr_img) == 1 else 1

            Globals.img_frame.configure(image=images[Globals.ind])
            Globals.info_frame.configure(text=cfg.IMAGES_INFO[Globals.ind])
            Globals.curr_img = images[Globals.ind]

    def flick(self, btn):
        for i in range(100, 1000, 200):
            cfg.ROOT.after(i, lambda: btn.press())


class NamePath(MyLabel):
    """
    Creates tkinter frame.
    * param `master`: tkinter top level.
    """
    def __init__(self, master):
        MyLabel.__init__(
            self, master, text=cfg.IMAGES_INFO[0], justify=tkinter.LEFT)
        Globals.info_frame = self


class OpenCloseFrame(MyButton):
    """
    Creates tkinter frame for open and close buttons.
    * param `master`: tkinter frame.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='Закрыть')
        self.configure(height=2)
        self.cmd(lambda e: on_closing(self.winfo_toplevel()))
