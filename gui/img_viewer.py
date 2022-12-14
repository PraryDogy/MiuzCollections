import os
import threading
import tkinter
from datetime import datetime

import cv2
import sqlalchemy
from PIL import ImageTk

import cfg
from database import Dbase, Thumbs
from utils import (close_windows, convert_to_rgb, decode_image, get_coll_name,
                   place_center, resize_image, smb_check)

from .img_compare import CompareWindow
from .widgets import CButton, CLabel, CWindow, ImgBtns, SmbAlert


all_src = []
width, height = 0, 0
img_info = tkinter.Label
img_frame = tkinter.Label
info_w = 43


def pack_widgets(win: tkinter.Toplevel):
    image_frame = ImgFrame(win)
    image_frame.pack(pady=(0, 15), expand=1, fill=tkinter.BOTH)

    ImgButtons(win).pack(pady=(0, 15))
    ImgInfo(win).pack(pady=(0, 15))

    global height, width
    if height == 0:
        cfg.ROOT.update_idletasks()
        height = image_frame.winfo_height()
        width = win.winfo_width()

    image_frame.place_thumbnail()


def switch_image(master: tkinter.Widget, index: int, all_src: list):
    try:
        cfg.IMG_SRC = all_src[index]
    except IndexError:
        cfg.IMG_SRC = all_src[0]
    master = master.winfo_toplevel()
    for i in master.winfo_children():
        i.destroy()
    pack_widgets(master)
    img_frame.place_image()


class PreviewWindow(CWindow):
    def __init__(self, src: str, src_list: list):
        CWindow.__init__(self)

        global all_src
        all_src = src_list
        cfg.IMG_SRC = src

        if not smb_check():
            close_windows()
            SmbAlert()
            return

        self.title('Просмотр')
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{int(side*1.3)}x{side}')
        self.configure(pady=0, padx=0)

        pack_widgets(self)

        if cfg.COMPARE:
            t1 = threading.Thread(target=cfg.STBAR_WAIT)
            t1.start()
            while t1.is_alive():
                cfg.ROOT.update()
            img_frame.place_image()
            CompareWindow()
            cfg.STBAR_NORM()
            return

        cfg.ROOT.update_idletasks()
        place_center(self)
        self.deiconify()
        self.grab_set()
        img_frame.place_image()


class ImgFrame(CLabel):
    def __init__(self, master: tkinter.Toplevel):
        CLabel.__init__(self, master, borderwidth=0)

        global img_frame
        img_frame = self

        self['bg']='black'
        self.bind('<ButtonRelease-1>', lambda e: self.click_image(e))
        master.bind('<Left>', lambda e: switch_image(self, self.img_ind()-1), all_src)
        master.bind('<Right>', lambda e: switch_image(self, self.img_ind()+1), all_src)

    def img_ind(self) -> int: 
        return all_src.index(cfg.IMG_SRC)

    def set_img(self, img):
        img_tk = ImageTk.PhotoImage(img)
        self.configure(image=img_tk)
        self.image = img_tk

    def click_image(self, e: tkinter.Event):
        if e.x <= width//2:
            index = self.img_ind() - 1
        else:
            index = self.img_ind() + 1
        switch_image(self, index, all_src)

    def place_thumbnail(self):
        thumb = Dbase.conn.execute(sqlalchemy.select(Thumbs.img150).where(
            Thumbs.src == cfg.IMG_SRC)).first()[0]
        decoded = decode_image(thumb)
        resized = resize_image(decoded, width, height, False)
        self.img_h, self.img_w = resized.shape[:2]
        rgb_image = convert_to_rgb(resized)
        self.set_img(rgb_image)

    def __place_image(self):
        global img_info

        img_read = cv2.imread(cfg.IMG_SRC)
        resized = cv2.resize(
            img_read, (self.img_w, self.img_h), interpolation=cv2.INTER_AREA)
        img_rgb = convert_to_rgb(resized)
        self.set_img(img_rgb)

        t = img_info['text']
        h, w = img_read.shape[:2]

        img_info['text'] = t.replace('Загрузка', f'{w} x {h}')
        self['text'] = cfg.IMG_SRC

    def place_image(self):
        task = threading.Thread(target=self.__place_image)
        task.start()
        while task.is_alive():
            cfg.ROOT.update()


class ImgButtons(ImgBtns):
    def __init__(self, master):
        ImgBtns.__init__(self, master)

        comp_btn = CButton(self, text='Сравнить')
        comp_btn.cmd(lambda e: self.compare(comp_btn))
        comp_btn.pack(side=tkinter.RIGHT)

    def compare(self, btn: CButton):
        btn.press()
        if not cfg.COMPARE:
            cfg.STBAR_COMPARE()
            for i in cfg.THUMBS:
                if i['text'] == cfg.IMG_SRC:
                    i['bg'] = cfg.BGPRESSED
                    break
            win = self.winfo_toplevel()
            win.withdraw()
            win.grab_release()
            cfg.COMPARE = True
            return


class ImgInfo(CLabel):
    def __init__(self, master: tkinter.Widget):
        CLabel.__init__(self, master)
        global img_info, info_w
        img_info = self

        name = cfg.IMG_SRC.split(os.sep)[-1]
        name = self.name_cut(name)

        path = cfg.IMG_SRC.replace(cfg.config["COLL_FOLDER"], "Коллекции")
        path = path.replace(cfg.config["PHOTO_DIR"], "Фото")
        path = self.name_cut(path)

        filesize = round(os.path.getsize(cfg.IMG_SRC)/(1024*1024), 2)

        filemod = datetime.fromtimestamp(os.path.getmtime(cfg.IMG_SRC))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")

        txt = (f'Коллекция: {get_coll_name(cfg.IMG_SRC)}'
                f'\nИмя: {name}'
                f'\nПуть: {path}'
                f'\nРазрешение: Загрузка'
                f'\nРазмер: {filesize} мб'
                f'\nДата изменения: {filemod}')

        self.configure(
            text=txt, justify=tkinter.LEFT, anchor=tkinter.W, width=info_w)

    def name_cut(self, name: str):
        return [name[:info_w]+'...' if len(name) > info_w else name][0]