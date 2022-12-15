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


class ImgViewer(CWindow):
    def __init__(self, src: str, all_src: list):
        CWindow.__init__(self)

        self.all_src = all_src
        self.height = 0
        cfg.IMG_SRC = src

        if not smb_check():
            close_windows()
            SmbAlert()
            return

        self.title('Просмотр')
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{int(side*1.3)}x{side}')
        self.configure(pady=0, padx=0)

        self.pack_widgets()

        if cfg.COMPARE:
            t1 = threading.Thread(target=cfg.STBAR_WAIT)
            t1.start()
            while t1.is_alive():
                cfg.ROOT.update()
            self.img_place()
            CompareWindow()
            cfg.STBAR_NORM()
            return

        cfg.ROOT.update_idletasks()
        place_center(self)
        self.deiconify()
        self.grab_set()
        
        self.img_place()

    def pack_widgets(self):
        self.img_frame = self.img_widget()
        self.img_frame.pack(pady=(0, 15), expand=1, fill=tkinter.BOTH)

        self.btns = self.btns_widget()
        self.btns.pack(pady=(0, 15))
        
        self.info_frame = self.info_widget()
        self.info_frame.pack(pady=(0, 15))

        if self.height == 0:
            cfg.ROOT.update_idletasks()
            self.height = self.img_frame.winfo_height()
            self.width = self.winfo_width()

        self.img_thumbnail()

    def switch_img(self, ind: int):
        try:
            cfg.IMG_SRC = self.all_src[ind]
        except IndexError:
            cfg.IMG_SRC = self.all_src[0]

        for i in self.winfo_children():
            i.destroy()
        self.pack_widgets()
        self.img_place()

    def img_widget(self):
        label = CLabel(self)
        label['bg']='black'
        label.bind('<ButtonRelease-1>', lambda e: self.img_click(e))
        self.bind('<Left>', lambda e: self.switch_img(self.img_ind()-1))
        self.bind('<Right>', lambda e: self.switch_img(self.img_ind()+1))
        return label

    def img_ind(self) -> int: 
        return self.all_src.index(cfg.IMG_SRC)

    def img_set(self, img):
        img_tk = ImageTk.PhotoImage(img)
        self.img_frame.configure(image=img_tk)
        self.img_frame.image_names = img_tk

    def img_click(self, e: tkinter.Event):
        if e.x <= self.width//2:
            index = self.img_ind() - 1
        else:
            index = self.img_ind() + 1
        self.switch_img(index)

    def img_thumbnail(self):
        thumb = Dbase.conn.execute(sqlalchemy.select(Thumbs.img150).where(
            Thumbs.src == cfg.IMG_SRC)).first()[0]
        decoded = decode_image(thumb)
        resized = resize_image(decoded, self.width, self.height, False)
        self.img_h, self.img_w = resized.shape[:2]
        rgb_image = convert_to_rgb(resized)
        self.img_set(rgb_image)

    def __img_place(self):
        img_read = cv2.imread(cfg.IMG_SRC)
        resized = cv2.resize(
            img_read, (self.img_w, self.img_h), interpolation=cv2.INTER_AREA)
        img_rgb = convert_to_rgb(resized)
        self.img_set(img_rgb)

        t = self.info_frame['text']
        h, w = img_read.shape[:2]
        self.info_frame['text'] = t.replace('Загрузка', f'{w} x {h}')

    def img_place(self):
        task = threading.Thread(target=self.__img_place)
        task.start()
        while task.is_alive():
            cfg.ROOT.update()

    def btns_widget (self):
        btns_frame = ImgBtns(self)
        comp_btn = CButton(btns_frame, text='Сравнить')
        comp_btn.cmd(lambda e: self.btn_compare(comp_btn))
        comp_btn.pack(side=tkinter.RIGHT)
        return btns_frame

    def btn_compare(self, btn: CButton):
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

    def info_widget(self):
        label = CLabel(self)
        ln = 43

        name = cfg.IMG_SRC.split(os.sep)[-1]
        name = self.name_cut(name, ln)

        path = cfg.IMG_SRC.replace(cfg.config["COLL_FOLDER"], "Коллекции")
        path = path.replace(cfg.config["PHOTO_DIR"], "Фото")
        path = self.name_cut(path, ln)

        filesize = round(os.path.getsize(cfg.IMG_SRC)/(1024*1024), 2)

        filemod = datetime.fromtimestamp(os.path.getmtime(cfg.IMG_SRC))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")

        txt = (f'Коллекция: {get_coll_name(cfg.IMG_SRC)}'
                f'\nИмя: {name}'
                f'\nПуть: {path}'
                f'\nРазрешение: Загрузка'
                f'\nРазмер: {filesize} мб'
                f'\nДата изменения: {filemod}')

        label.configure(
            text=txt, justify=tkinter.LEFT, anchor=tkinter.W, width=ln)
        
        return label

    def name_cut(self, name: str, ln: int):
        return [name[:ln]+'...' if len(name) > ln else name][0]