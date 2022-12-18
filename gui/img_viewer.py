import os
import threading
import tkinter
from datetime import datetime

import cv2
import sqlalchemy
from PIL import ImageTk, Image

import cfg
from database import Dbase, Thumbs
from utils import (close_windows, convert_to_rgb, decode_image, get_coll_name,
                   place_center, resize_image, smb_check)

from .img_compare import ImgCompare
from .widgets import CButton, CLabel, CWindow, ImgBtns, SmbAlert, InfoWidget


class ImgViewer(CWindow):
    def __init__(self, img_src: str, all_src: list):
        CWindow.__init__(self)

        if not smb_check():
            close_windows()
            SmbAlert()
            return

        cfg.IMG_SRC = img_src
        self.img_src = img_src
        self.all_src = all_src
        self.ln = 43

        self.title('Просмотр')
        side = int(cfg.ROOT.winfo_screenheight()*0.9)
        self.geometry(f'{int(side*1.3)}x{side}')
        self.configure(pady=0, padx=0)

        self.img_frame = self.img_widget()
        self.img_frame.pack(pady=(0, 15), expand=1, fill=tkinter.BOTH)

        self.btns = self.btns_widget()
        self.btns.pack(pady=(0, 15))
        
        self.info_frame = self.info_widget()
        self.info_frame.pack(pady=(0, 15))

        cfg.ROOT.update_idletasks()

        self.height = self.img_frame.winfo_height()
        self.width = self.winfo_width()

        self.thumb_place()
        self.task = cfg.ROOT.after(500, self.img_place)

        if cfg.COMPARE:
            cfg.ROOT.after(0, cfg.ST_BAR.wait)
            cfg.ROOT.after(501, self.run_compare)
            return

        place_center(self)
        self.deiconify()
        self.grab_set()

    def img_widget(self):
        label = CLabel(self)
        label['bg']='black'
        label.bind('<ButtonRelease-1>', lambda e: self.img_click(e))
        self.bind('<Left>', lambda e: self.switch_img(self.img_ind()-1))
        self.bind('<Right>', lambda e: self.switch_img(self.img_ind()+1))
        return label

    def btns_widget (self):
        btns_frame = ImgBtns(self)
        comp_btn = CButton(btns_frame, text='Сравнить')
        comp_btn.cmd(lambda e: self.btn_compare(comp_btn))
        comp_btn.pack(side=tkinter.RIGHT)
        return btns_frame

    def info_widget(self):
        info1, info2 = self.create_info()
        info_widget = InfoWidget(self, self.ln, info1, info2)
        return info_widget

    def run_compare(self):
        t1 = threading.Thread(target=cfg.ST_BAR.wait)
        t1.start()
        while t1.is_alive():
            cfg.ROOT.update()
        ImgCompare()
        cfg.ST_BAR.normal()

    def switch_img(self, ind: int):
        cfg.ROOT.after_cancel(self.task)
        try:
            cfg.IMG_SRC = self.all_src[ind]
        except IndexError:
            cfg.IMG_SRC = self.all_src[0]
        self.thumb_place()
        self.task = cfg.ROOT.after(500, self.img_place)

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

    def thumb_place(self):
        thumb = Dbase.conn.execute(sqlalchemy.select(Thumbs.img150).where(
            Thumbs.src == cfg.IMG_SRC)).first()[0]
        decoded = decode_image(thumb)
        resized = resize_image(decoded, self.width, self.height, False)
        rgb_image = convert_to_rgb(resized)
        self.img_set(rgb_image)

    def img_place(self):
        img_read = cv2.imread(cfg.IMG_SRC)
        resized = resize_image(img_read, self.width, self.height, False)
        img_rgb = convert_to_rgb(resized)
        self.img_set(img_rgb)

        info1, _, info2 = self.info_frame.winfo_children()
        info1['text'], info2['text'] = self.create_info()

    def btn_compare(self, btn: CButton):
        btn.press()
        if not cfg.COMPARE:
            cfg.ST_BAR.compare()
            for i in cfg.GALLERY.thumbs_list:
                if i['text'] == cfg.IMG_SRC:
                    i['bg'] = cfg.BGPRESSED
                    break
            win = self.winfo_toplevel()
            win.withdraw()
            win.grab_release()
            cfg.COMPARE = True
            return

    def create_info(self):
        name = cfg.IMG_SRC.split(os.sep)[-1]
        name = self.name_cut(name, self.ln)

        path = cfg.IMG_SRC.replace(cfg.config["COLL_FOLDER"], "Коллекции")
        path = path.replace(cfg.config["PHOTO_DIR"], "Фото")
        path = self.name_cut(path, self.ln)

        filesize = round(os.path.getsize(cfg.IMG_SRC)/(1024*1024), 2)

        filemod = datetime.fromtimestamp(os.path.getmtime(cfg.IMG_SRC))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")

        w, h = Image.open(cfg.IMG_SRC).size

        t1 = (f'Разрешение: {w}x{h}'
                f'\nРазмер: {filesize} мб'
                f'\nДата изменения: {filemod}')

        t2 = (f'Коллекция: {get_coll_name(cfg.IMG_SRC)}'
                f'\nИмя: {name}'
                f'\nПуть: {path}')

        return (t1, t2)

    def name_cut(self, name: str, ln: int):
        return [name[:ln]+'...' if len(name) > ln else name][0]