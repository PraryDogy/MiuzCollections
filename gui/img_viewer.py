import os
import tkinter

import cv2
import sqlalchemy
from PIL import ImageTk

from cfg import cnf
from database import Dbase, ThumbsMd

from .context import *
from .utils import *
from .utils import place_center
from .widgets import *

__all__ = (
    "ImgViewer",
    )


class ContextViewer(Context):
    def __init__(self, e: tkinter.Event, img_src):
        super().__init__()

        self.imginfo(e.widget.winfo_toplevel(), img_src)
        self.sep()

        self.sep()
        self.copy_jpg_path(img_src)
        self.reveal_jpg(img_src)
        self.download_jpg(img_src)

        self.sep()
        self.copy_tiff_path(img_src)
        self.reveal_tiff(img_src)
        self.download_tiff(img_src)

        self.sep()
        self.download_fullsize(img_src)

        self.do_popup(e)


class ImgViewer(CWindow):
    def __init__(self, img_src: str):
        super().__init__(bg="black", pady=0, padx=0)

        self.img_src = img_src

        self.set_title()
        self.minsize(500, 300)
        self.resizable(1, 1)
        self.geometry(f"{cnf.imgview_g['w']}x{cnf.imgview_g['h']}")
        place_center(cnf.root, self, cnf.imgview_g["w"], cnf.imgview_g["h"])
        self.protocol("WM_DELETE_WINDOW", self.close_view)
        self.bind("<Escape>", self.close_view)

        self.img = CLabel(
            self, bg="black", width=cnf.imgview_g["w"],
            height=cnf.imgview_g["h"]
            )
        self.img.bind("<ButtonRelease-1>", lambda e: self.l_click(e))
        self.img.bind(
            "<ButtonRelease-2>",
            lambda e, img_src=self.img_src: ContextViewer(e, img_src)
            )
        self.img.pack()

        cnf.root.update_idletasks()

        self.resize_task = None

        self.load_thumb()
        self.img_task = cnf.root.after(300, self.load_img)
        cnf.root.after(
            400, lambda: self.bind("<Configure>", self.decect_resize)
            )

        self.wait_visibility()
        self.grab_set_global()

        self.bind(
            "<Left>",
            lambda e: self.switch_img(cnf.all_src.index(self.img_src)-1)
            )
        self.bind(
            "<Right>",
            lambda e: self.switch_img(cnf.all_src.index(self.img_src)+1)
            )

    def decect_resize(self, e: tkinter.Event):
        try:
            if self.resize_task:
                cnf.root.after_cancel(self.resize_task)
            self.resize_task = cnf.root.after(300, lambda: self.resize_win(e))
        except tkinter.TclError:
            print("img viewer > detect resize > no window")

    def resize_win(self, e: tkinter.Event):
        try:
            if e.width != cnf.imgview_g["w"] or e.height != cnf.imgview_g["h"]:
                cnf.imgview_g["h"] = e.height
                cnf.imgview_g["w"] = e.width

                self.img.configure(
                    width=cnf.imgview_g["w"], height=cnf.imgview_g["h"]
                    )

                self.load_thumb()
                cnf.root.after(300, self.load_img)
        except Exception as ex:
            print("img viewer > resize win > no win")
            print(ex)

    def load_thumb(self):
        img = Dbase.conn.execute(sqlalchemy.select(ThumbsMd.img150).where(
            ThumbsMd.src==self.img_src)).first()[0]
        img = decode_image(img)
        img = resize_image(
            img, cnf.imgview_g["w"], cnf.imgview_g["h"], thumbnail=False
            )
        img = convert_to_rgb(img)
        self.tk_img(img)

    def load_img(self):
        try:
            img = cv2.imread(self.img_src, cv2.IMREAD_UNCHANGED)
            
            if self.img_src.endswith(("png", "PNG")):
                img = replace_bg(img, cnf.bg_color)

            img = resize_image(
                img, cnf.imgview_g["w"], cnf.imgview_g["h"], thumbnail=False
                )
            img = convert_to_rgb(img)
            self.tk_img(img)

        except Exception as ex:
            print("img viewer > img place > no win")
            print(ex)

    def tk_img(self, img):
        img_tk = ImageTk.PhotoImage(img)
        self.img.configure(image=img_tk)
        self.img.image_names = img_tk

    def switch_img(self, ind: int):
        cnf.root.after_cancel(self.img_task)
        try:
            self.img_src = cnf.all_src[ind]
        except IndexError:
            self.img_src = cnf.all_src[0]

        self.set_title()
        self.bind(
            "<ButtonRelease-2>",
            lambda e, img_src=self.img_src: ContextViewer(e, img_src)
            )

        self.load_thumb()
        self.img_task = cnf.root.after(500, self.load_img)

    def l_click(self, e: tkinter.Event):
        if e.x <= cnf.imgview_g["w"]//2:
            index = cnf.all_src.index(self.img_src) - 1
        else:
            index = cnf.all_src.index(self.img_src) + 1
        self.switch_img(index)

    def set_title(self):
        name = self.img_src.split(os.sep)[-1]
        collection_name = get_coll_name(self.img_src)
        self.title(f"{collection_name} - {name}")

    def close_view(self, e=None):
        self.grab_release()
        self.destroy()