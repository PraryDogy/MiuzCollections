import os
import tkinter

import sqlalchemy
from PIL import Image, ImageOps, ImageTk

from cfg import cnf
from database import Dbase, ThumbsMd

from .context import Context
from .widgets import *

try:
    from typing_extensions import Literal
except ImportError:
    from typing import Literal

from utils import FitImg, SysUtils

__all__ = ("ImgViewer",)


class Win:
    win: CWindow = False


class ContextViewer(Context, SysUtils):
    def __init__(self, e: tkinter.Event, img_src: Literal["file path"]):
        Context.__init__(self)

        self.imginfo(parrent=e.widget.winfo_toplevel(), img_src=img_src)

        self.sep()
        self.reveal_jpg(img_src=img_src)
        self.reveal_tiff(img_src=img_src)

        self.sep()
        self.copy_jpg_path(img_src=img_src)
        self.copy_tiff_path(img_src=img_src)

        self.sep()
        self.download_jpg(img_src=img_src)
        self.download_tiff(img_src=img_src)

        self.sep()
        self.download_fullsize(img_src=img_src)

        self.do_popup(e=e)


class ImgViewer(CWindow, SysUtils, FitImg):
    def __init__(self, img_src: Literal["file path"]):
        w, h = cnf.imgview_g["w"], cnf.imgview_g["h"]

        if Win.win:
            Win.win.destroy()
            Win.win = False

        CWindow.__init__(self, bg="black", pady=0, padx=0)
        Win.win = self
        self.__img_src = img_src

        self.__set_title()
        self.minsize(width=500, height=300)
        self.resizable(width=1, height=1)
        self.geometry(newGeometry=f"{w}x{h}")
        self.place_center(w=w, h=h)
        self.protocol(name="WM_DELETE_WINDOW", func=self.__close_view)
        self.bind(sequence="<Escape>", func=self.__close_view)

        self.img = CLabel(master=self, bg="black", width=w,height=h)
        self.img.bind(sequence="<ButtonRelease-1>",
                      func=lambda e: self.__l_click(e=e))
        self.img.bind(sequence="<ButtonRelease-2>",
                    func=lambda e: ContextViewer(e=e, img_src=self.__img_src))
        self.img.pack()

        cnf.root.update_idletasks()
        self.__resize_task = None

        self.__load_thumb()
        self.__img_task = cnf.root.after(300, self.__load_img)

        cnf.root.after(ms=400, func=lambda:
                    self.bind(sequence="<Configure>", func=self.__decect_resize))

        self.bind(sequence="<Left>", func=lambda e:
                  self.__switch_img(ind=cnf.all_img_src.index(self.__img_src)-1))
        self.bind(sequence="<Right>", func=lambda e:
                  self.__switch_img(ind=cnf.all_img_src.index(self.__img_src)+1))

    def __decect_resize(self, e: tkinter.Event):
        if self.__resize_task:
            cnf.root.after_cancel(id=self.__resize_task)

        self.__resize_task = cnf.root.after(
            ms=300, func=lambda: self.__resize_win(e=e))

    def __resize_win(self, e: tkinter.Event):
        try:
            if e.width != cnf.imgview_g["w"] or e.height != cnf.imgview_g["h"]:

                cnf.imgview_g.update({"w": e.width, "h": e.height})
                self.img.configure(width=cnf.imgview_g["w"], height=cnf.imgview_g["h"])

                self.__load_thumb()
                cnf.root.after(ms=300, func=self.__load_img)

        except Exception:
            self.print_err()

    def __load_thumb(self):
        img = Dbase.conn.execute(sqlalchemy.select(ThumbsMd.img150).where(
            ThumbsMd.src==self.__img_src)).first()[0]
        img = self.decode_image(img=img)
        img = self.fit(img=img, w=cnf.imgview_g["w"], h=cnf.imgview_g["h"])

        if self.winfo_exists():
            self.__set_tk_img(img=img)

    def __load_img(self):
        try:
            img = Image.open(self.__img_src)
        except FileNotFoundError:
            self.print_err()

        img = ImageOps.exif_transpose(image=img)
        img = self.fit(img=img, w=cnf.imgview_g["w"], h=cnf.imgview_g["h"])
        if self.winfo_exists():
            self.__set_tk_img(img=img)

    def __set_tk_img(self, img: Literal["PIL Image"]):
        img_tk = ImageTk.PhotoImage(image=img)
        self.img.configure(image=img_tk)
        self.img.image_names = img_tk

    def __switch_img(self, ind: int):
        cnf.root.after_cancel(id=self.__img_task)
        try:
            self.__img_src = cnf.all_img_src[ind]
        except IndexError:
            # self.print_err()
            print("repeat images list img view")
            self.__img_src = cnf.all_img_src[0]

        self.__set_title()
        self.img.unbind(sequence="<ButtonRelease-2>")
        self.img.bind(sequence="<ButtonRelease-2>",
                  func=lambda e: ContextViewer(e=e, img_src=self.__img_src))

        self.__load_thumb()
        self.__img_task = cnf.root.after(ms=500, func=self.__load_img)

    def __l_click(self, e: tkinter.Event):
        if e.x <= cnf.imgview_g["w"] // 2:
            index = cnf.all_img_src.index(self.__img_src) - 1
        else:
            index = cnf.all_img_src.index(self.__img_src) + 1
        self.__switch_img(ind=index)

    def __set_title(self):
        name = self.__img_src.split(os.sep)[-1]
        collection_name = self.get_coll_name(src=self.__img_src)
        self.title(string=f"{collection_name} - {name}")

    def __close_view(self, e: tkinter.Event = None):
        self.destroy()
        Win.win = False