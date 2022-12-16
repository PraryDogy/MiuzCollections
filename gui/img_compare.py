import tkinter

import cfg
from utils import get_windows, place_center

from .macosx_menu import CLabel
from .widgets import CWindow, ImgBtns


class ImgCompare(CWindow):
    def __init__(self):
        CWindow.__init__(self)

        self.title('Сравнение')
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{int(side*1.3)}x{side}')
        self.configure(pady=0, padx=0)

        self.img1 = cfg.WINS[0].img_frame['image']
        self.src1 = cfg.WINS[0].img_src
        self.info1 = cfg.WINS[0].info_frame['text']

        self.img2 = cfg.WINS[1].img_frame['image']
        self.src2 = cfg.WINS[1].img_src
        self.info2 = cfg.WINS[1].info_frame['text']

        self.curr_src = self.src1
        cfg.IMG_SRC = self.src1

        self.img_frame = self.img_widget()
        self.img_frame.pack(pady=(0, 15), expand=1, fill=tkinter.BOTH)

        self.btns = self.btns_widget()
        self.btns.pack(pady=(0, 15))

        self.i_frame = self.info_widget()
        self.i_frame.pack(pady=(0, 15))

        cfg.ROOT.update_idletasks()
        place_center(self)
        self.deiconify()
        self.grab_set()


    def img_widget(self):
        label = CLabel(self)
        label['bg']='black'
        label['image'] = self.img1
        label['height'] = 1
        label.bind('<ButtonRelease-1>', lambda e: self.switch_img())
        return label

    def btns_widget(self):
        return ImgBtns(self)

    def info_widget(self):
        label = CLabel(
            self, anchor=tkinter.W, justify=tkinter.LEFT,
            text=self.info1, width=43)
        return label

    def set_vars(self, img, info, src):
        self.img_frame['image'] = img
        self.i_frame['text'] = info
        self.curr_src = src
        cfg.IMG_SRC = src

    def switch_img(self):
        print(self.img1, self.img2)
        if self.src1 == self.curr_src:
            self.set_vars(self.img2, self.info2, self.src2)
        else:
            self.set_vars(self.img1, self.info1, self.src1)


        cfg.ROOT.update_idletasks()
        print(self.img_frame.winfo_height())