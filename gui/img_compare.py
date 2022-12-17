import tkinter

import cfg
from utils import place_center

from .macosx_menu import CLabel
from .widgets import CWindow, ImgBtns, InfoWidget


class ImgCompare(CWindow):
    def __init__(self):
        CWindow.__init__(self)

        self.title('Сравнение')
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{int(side*1.3)}x{side}')
        self.configure(pady=0, padx=0)

        self.img1 = cfg.WINS[0].img_frame['image']
        self.src1 = cfg.WINS[0].img_src
        info1_l, _, info1_r = cfg.WINS[0].info_frame.winfo_children()
        self.info1_l, self.info1_r = info1_l['text'], info1_r['text']

        self.img2 = cfg.WINS[1].img_frame['image']
        self.src2 = cfg.WINS[1].img_src
        info2_l, _, info2_r = cfg.WINS[1].info_frame.winfo_children()
        self.info2_l, self.info2_r = info2_l['text'], info2_r['text']

        self.curr_src = self.src1
        cfg.IMG_SRC = self.src1

        self.ln = 43

        self.img_frame = self.img_widget()
        self.img_frame.pack(pady=(0, 15), expand=1, fill=tkinter.BOTH)

        self.btns = self.btns_widget()
        self.btns.pack(pady=(0, 15))

        self.info_frame = self.info_widget()
        self.info_frame.pack(pady=(0, 15))

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
        info_widget = InfoWidget(self, self.ln, self.info1_l, self.info1_r)
        return info_widget

    def set_vars(self, img, src, l_info, r_info):
        self.img_frame['image'] = img
        self.curr_src = src
        cfg.IMG_SRC = src

        info_l, _, info_r = self.info_frame.winfo_children()
        info_l['text'] = l_info
        info_r['text'] = r_info

    def switch_img(self):
        if self.src1 == self.curr_src:
            self.set_vars(self.img2, self.src2, self.info2_l, self.info2_r)
        else:
            self.set_vars(self.img1, self.src1, self.info1_l, self.info1_r)
