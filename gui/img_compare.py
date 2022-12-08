import tkinter

import cfg
from utils import place_center, close_windows

from .macosx_menu import CLabel
from .widgets import ImgBtns, CWindow, CloseBtn, AskExit


class Globals:
    img1, src1, info1 = None, str, str
    img2, src2, info2 = None, str, str
    img_widget, info_widget = tkinter.Label, tkinter.Label


globs = Globals()


def get_windows():
    widgets = tuple(i for i in cfg.ROOT.winfo_children())
    return tuple(i for i in widgets if isinstance(i, tkinter.Toplevel))


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


class CompareWindow(CWindow):
    def __init__(self):
        CWindow.__init__(self)

        self.bind('<Command-q>', lambda e: AskExit())
        self.protocol("WM_DELETE_WINDOW", lambda: close_windows())
        self.bind('<Command-w>', lambda e: close_windows())
        self.bind('<Escape>', lambda e: close_windows())

        self.title('Сравнение')
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')

        win1, win2 = get_windows()[:2]

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
        CloseBtn(self, text='Закрыть').pack()

        cfg.ROOT.update_idletasks()
        place_center(self)
        self.deiconify()
        self.grab_set()


class ImageFrame(CLabel):
    def __init__(self, master):
        CLabel.__init__(self, master, borderwidth=0)
        self['bg']='black'
        self['image'] = globs.img1
        globs.img_widget = self
        self.bind('<ButtonRelease-1>', lambda e: switch_image())


class ImgButtons(ImgBtns):
    def __init__(self, master):
        ImgBtns.__init__(self, master)


class ImgInfo(CLabel):
    def __init__(self, master):
        CLabel.__init__(
            self, master, anchor=tkinter.W, justify=tkinter.LEFT,
            text=globs.info1, width=43)
        globs.info_widget = self
