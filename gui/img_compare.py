import tkinter

import cfg
from utils import get_windows, place_center

from .widgets import CLabel, CWindow, ImgBtns, InfoWidget


class ImgCompare(CWindow):
    def __init__(self):
        CWindow.__init__(self)

        self.title('Сравнение')
        self.win_width, self.win_height = cfg.config['WIN_GEOMETRY']
        self.geometry(f'{self.win_width}x{self.win_height}')
        self.configure(pady=0, padx=0)

        wins = get_windows()

        self.img1 = wins[0].img_frame['image']
        self.src1 = wins[0].img_src
        info1_l, _, info1_r = wins[0].info_frame.winfo_children()
        self.info1_l, self.info1_r = info1_l['text'], info1_r['text']

        self.img2 = wins[1].img_frame['image']
        self.src2 = wins[1].img_src
        info2_l, _, info2_r = wins[1].info_frame.winfo_children()
        self.info2_l, self.info2_r = info2_l['text'], info2_r['text']

        self.curr_src = self.src1

        self.ln = 43

        self.img_frame = self.img_widget()
        self.img_frame.pack(pady=(0, 15), expand=1, fill=tkinter.BOTH)

        self.btns_frame = self.btns_widget()
        self.btns_frame.pack(pady=(0, 15))

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
        return ImgBtns(self, self.src1)

    def info_widget(self):
        info_widget = InfoWidget(self, self.ln, self.info1_l, self.info1_r)
        return info_widget

    def set_vars(self, img, src, l_info, r_info):
        self.img_frame['image'] = img
        self.curr_src = src

        self.btns_frame.img_src = src

        info_l, _, info_r = self.info_frame.winfo_children()
        info_l['text'] = l_info
        info_r['text'] = r_info

    def switch_img(self):
        if self.src1 == self.curr_src:
            self.set_vars(self.img2, self.src2, self.info2_l, self.info2_r)
        else:
            self.set_vars(self.img1, self.src1, self.info1_l, self.info1_r)
