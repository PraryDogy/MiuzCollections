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


class Globals:
    all_src = []
    width, height = 0, 0
    img_info = tkinter.Label
    img_frame = tkinter.Label
    curr_img = ImageTk
    info_w = 43

globs = Globals()


def pack_widgets(win: tkinter.Toplevel):
    image_frame = ImgFrame(win)
    image_frame.pack(pady=(0, 15), expand=1, fill=tkinter.BOTH)

    ImgButtons(win).pack(pady=(0, 15))
    ImgInfo(win).pack(pady=(0, 15))

    if globs.height == 0:
        cfg.ROOT.update_idletasks()
        globs.height = image_frame.winfo_height()
        globs.width = win.winfo_width()

    image_frame.place_thumbnail()


def switch_image(master: tkinter.Widget, index: int):
    try:
        cfg.IMG_SRC = globs.all_src[index]
    except IndexError:
        cfg.IMG_SRC = globs.all_src[0]
    master = master.winfo_toplevel()
    for i in master.winfo_children():
        i.destroy()
    pack_widgets(master)
    globs.img_frame.place_image()


class PreviewWindow(CWindow):
    def __init__(self, src: str, all_src: list):
        CWindow.__init__(self)

        if not smb_check():
            close_windows()
            SmbAlert()
            return

        self.title('Просмотр')
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{int(side*1.3)}x{side}')
        self.configure(pady=0, padx=0)

        cfg.IMG_SRC, globs.all_src = src, all_src

        pack_widgets(self)

        if cfg.COMPARE:
            t1 = threading.Thread(target=cfg.STBAR_WAIT)
            t1.start()
            while t1.is_alive():
                cfg.ROOT.update()
            cfg.STBAR_WAIT
            globs.img_frame.place_image()
            CompareWindow()
            cfg.STBAR_NORM()
            return

        cfg.ROOT.update_idletasks()
        place_center(self)
        self.deiconify()
        self.grab_set()
        globs.img_frame.place_image()


class ImgFrame(CLabel):
    def __init__(self, master: tkinter.Toplevel):
        CLabel.__init__(self, master, borderwidth=0)
        globs.img_frame = self
        self['bg']='black'
        self.bind('<ButtonRelease-1>', lambda e: self.click_image(e))
        master.bind('<Left>', lambda e: switch_image(self, self.img_ind()-1))
        master.bind('<Right>', lambda e: switch_image(self, self.img_ind()+1))

    def img_ind(self) -> int: 
        return globs.all_src.index(cfg.IMG_SRC)

    def set_img(self, img):
        img_tk = ImageTk.PhotoImage(img)
        self.configure(image=img_tk)
        self.image = img_tk

    def click_image(self, e: tkinter.Event):
        if e.x <= globs.width//2:
            index = self.img_ind() - 1
        else:
            index = self.img_ind() + 1
        switch_image(self, index)

    def place_thumbnail(self):
        thumb = Dbase.conn.execute(sqlalchemy.select(Thumbs.img150).where(
            Thumbs.src == cfg.IMG_SRC)).first()[0]
        decoded = decode_image(thumb)
        resized = resize_image(decoded, globs.width, globs.height, False)
        self.img_h, self.img_w = resized.shape[:2]
        rgb_image = convert_to_rgb(resized)
        self.set_img(rgb_image)

    def __place_image(self):
        img_read = cv2.imread(cfg.IMG_SRC)
        resized = cv2.resize(
            img_read, (self.img_w, self.img_h), interpolation=cv2.INTER_AREA)
        globs.curr_img = convert_to_rgb(resized)
        self.set_img(globs.curr_img)
        t = globs.img_info['text']
        h, w = img_read.shape[:2]
        globs.img_info['text'] = t.replace('Загрузка', f'{w} x {h}')
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
        globs.img_info = self

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
            text=txt, justify=tkinter.LEFT, anchor=tkinter.W, width=globs.info_w)

    def name_cut(self, name: str):
        return [name[:globs.info_w]+'...' if len(name) > globs.info_w else name][0]