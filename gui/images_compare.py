import tkinter

import cfg
from utils import MyLabel, place_center

from .base_widgets import BaseImgButtons, BaseWindow, CloseButton


class Globals:
    img1, src1, info1 = None, str, str
    img2, src2, info2 = None, str, str
    img_widget, info_widget = tkinter.Label, tkinter.Label


globs = Globals()


def get_windows():
    widgets = tuple(i for i in cfg.ROOT.winfo_children())
    return tuple(i for i in widgets if isinstance(i, tkinter.Toplevel))[:-1]


def get_widgets(window: tkinter.Toplevel):
    """
    img: image from label,
    str: image src from label,
    str: image info from label
    """
    img_frame = window.children['!imgframe']['image']
    img_src = window.children['!imgframe']['text']
    img_info = window.children['!imginfo']['text']

    return (img_frame, img_src, img_info)


def switch_image():
    if globs.src1 == cfg.IMG_SRC:
        globs.img_widget['image'] = globs.img2
        globs.info_widget['text'] = globs.info2
        cfg.IMG_SRC = globs.src2
    else:
        globs.img_widget['image'] = globs.img1
        globs.info_widget['text'] = globs.info1
        cfg.IMG_SRC = globs.src1


class CompareWindow(BaseWindow):
    def __init__(self):
        BaseWindow.__init__(self)
        self.title('Сравнение')
        cfg.ROOT.update_idletasks()

        win1, win2 = get_windows()

        try:
            globs.img1, globs.src1, globs.info1 = get_widgets(win1)
            globs.img2, globs.src2, globs.info2 = get_widgets(win2)
        except KeyError:
            [i.destroy() for i in get_windows()]

        cfg.IMG_SRC = globs.src1

        image_frame = ImageFrame(self)
        image_frame.pack(pady=(0, 15), expand=True, fill=tkinter.BOTH)

        ImgButtons(self).pack(pady=(0, 15))
        ImgInfo(self).pack(pady=(0, 15))
        CloseButton(self).pack()

        place_center(self)
        self.deiconify()
        self.grab_set()


class ImageFrame(MyLabel):
    def __init__(self, master):
        MyLabel.__init__(self, master, borderwidth=0)
        self['bg']='black'
        self['image'] = globs.img1
        globs.img_widget = self
        self.bind('<ButtonRelease-1>', lambda e: switch_image())


class ImgButtons(BaseImgButtons):
    def __init__(self, master):
        BaseImgButtons.__init__(self, master)


class ImgInfo(MyLabel):
    def __init__(self, master):
        MyLabel.__init__(
            self, master, anchor=tkinter.W, justify=tkinter.LEFT,
            text=globs.info1, width=43)
        globs.info_widget = self
