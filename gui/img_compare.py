import tkinter

import cfg
from utils import get_windows, place_center

from .macosx_menu import CLabel
from .widgets import CWindow, ImgBtns


class Globals:
    img1, src1, info1 = None, str, str
    img2, src2, info2 = None, str, str
    img_widget, info_widget = tkinter.Label, tkinter.Label
    curr_txt = str
    count = 0

globs = Globals()


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
    if globs.curr_txt == globs.info1:
        globs.img_widget['image'] = globs.img2
        globs.info_widget['text'] = globs.info2
        globs.curr_txt = globs.info2
    else:
        globs.img_widget['image'] = globs.img1
        globs.info_widget['text'] = globs.info1
        globs.curr_txt = globs.info1


class CompareWindow(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.title('Сравнение')
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{int(side*1.3)}x{side}')
        self.configure(pady=0, padx=0)

        win1, win2 = get_windows()[:2]

        try:
            globs.img1, globs.src1, globs.info1 = get_widgets(win1)
            globs.img2, globs.src2, globs.info2 = get_widgets(win2)
        except KeyError:
            if globs.count >= 3:
                self.error_exit()
                return

            globs.count += 1
            self.destroy()
            print('compare window key error')
            return

        globs.curr_txt = globs.info1

        image_frame = ImageFrame(self)
        image_frame.pack(pady=(0, 15), expand=1, fill=tkinter.BOTH)

        ImgButtons(self).pack(pady=(0, 15))
        ImgInfo(self).pack(pady=(0, 15))

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
