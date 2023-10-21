import os
import tkinter

import cv2
import sqlalchemy
from PIL import ImageTk

from cfg import cnf
from database import Dbase, Thumbs
from .utils import *
from .utils import place_center

from .widgets import *

__all__ = (
    "ImgViewer",
    )


src = str
all_src = []
win = tkinter.Toplevel


class ContextViewer(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()

        if cnf.first_load:
            self.please_wait()

        else:
            self.imginfo(e)
            self.sep()

            self.sep()
            self.copy_jpg_path(e)
            self.reveal_jpg(e)
            self.download_onefile(e)

            self.sep()
            self.copy_tiffs_paths(e)
            self.reveal_tiffs(e)
            self.download_tiffs(e)

            self.sep()
            self.download_fullsize(e)

        self.do_popup(e)


class ImgViewer(CWindow):
    def __init__(self, img_src: str, src_list: list):
        global src, all_src, win
        super().__init__()

        win = self
        src = img_src
        all_src = src_list

        self.set_title()
        self["bg"] = "black"

        self.geometry(f'{cnf.imgview_w}x{cnf.imgview_h}')
        self.minsize(500, 300)

        self.configure(pady=0, padx=0)
        self.resizable(1, 1)

        self.img_frame = self.img_widget()
        self.img_frame.pack()

        cnf.root.update_idletasks()

        self.img_frame['width'] = cnf.imgview_w
        self.img_frame['height'] = cnf.imgview_h

        self.thumb_place(cnf.imgview_w, cnf.imgview_h)
        self.task = cnf.root.after(
            250, lambda: self.img_place(cnf.imgview_w, cnf.imgview_h))

        place_center()
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

        self.bind('<Configure>', self.decect_resize)
        self.bind("<ButtonRelease-2>", self.r_click)
        self.resize_task = None

    def r_click(self, e):
        e.widget.src = src
        e.widget.all_src = all_src
        ContextViewer(e)

    def decect_resize(self, e):
        if self.resize_task:
            cnf.root.after_cancel(self.resize_task)
        self.resize_task = cnf.root.after(250, lambda: self.resize_win())

    def resize_win(self):
        try:
            new_w, new_h = self.winfo_width(), self.winfo_height()
        except Exception:
            print("no win")
            return

        if new_w != cnf.imgview_w or new_h != cnf.imgview_h:
            cnf.imgview_h = new_h
            cnf.imgview_w = new_w

            self.img_frame['width'] = cnf.imgview_w
            self.img_frame['height'] = cnf.imgview_h

            self.thumb_place(cnf.imgview_w, cnf.imgview_h)
            cnf.root.after(
                500,
                lambda: self.img_place(cnf.imgview_w, cnf.imgview_h)
                )

    def img_widget(self):
        label = CLabel(self)
        label['bg']='black'
        label.bind('<ButtonRelease-1>', lambda e: self.img_click(e))
        self.bind('<Left>', lambda e: self.switch_img(self.img_ind()-1))
        self.bind('<Right>', lambda e: self.switch_img(self.img_ind()+1))
        return label

    def switch_img(self, ind: int):
        global src

        cnf.root.after_cancel(self.task)
        try:
            src = all_src[ind]
            self.set_title()
        except IndexError:
            src = all_src[0]
            self.set_title()

        self.thumb_place(cnf.imgview_w, cnf.imgview_h)
        self.task = cnf.root.after(
            500,
            lambda: self.img_place(cnf.imgview_w, cnf.imgview_h)
            )

    def img_ind(self):
        return all_src.index(src)

    def img_set(self, img):
        img_tk = ImageTk.PhotoImage(img)
        self.img_frame.configure(image=img_tk)
        self.img_frame.image_names = img_tk

    def img_click(self, e: tkinter.Event):
        if cnf.imgview_w == self.winfo_width():

            if e.x <= cnf.imgview_w//2:
                index = self.img_ind() - 1
            else:
                index = self.img_ind() + 1

            self.switch_img(index)

    def thumb_load(self):
        thumb = Dbase.conn.execute(sqlalchemy.select(Thumbs.img150).where(
            Thumbs.src==src)).first()[0]
        return decode_image(thumb)

    def thumb_place(self, width, height):
        thumb = self.thumb_load()
        resized = resize_image(thumb, width, height, False)
        rgb_thumb = convert_to_rgb(resized)
        self.img_set(rgb_thumb)

    def img_place(self, width, height):
        try:
            img_read = cv2.imread(src, cv2.IMREAD_UNCHANGED)
            
            if src.endswith(("png", "PNG")):
                img_read = replace_bg(img_read, cnf.bg_color)

            resized = resize_image(img_read, width, height, False)
            img_rgb = convert_to_rgb(resized)
            self.img_set(img_rgb)
        except AttributeError:
            print("img viewer no img\n\n")

    def set_title(self):
        name = src.split(os.sep)[-1]
        collection_name = get_coll_name(src)
        self.title(f"{collection_name} - {name}")

