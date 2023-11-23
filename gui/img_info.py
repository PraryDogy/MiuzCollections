import os
import re
import tkinter
from datetime import datetime
from typing import Literal

from PIL import Image

from cfg import cnf

from .context import *
from .utils import *
from .widgets import *
from utils_p import SysUtils

__all__ = ("ImageInfo",)


class ContextInfo(Context):
    def __init__(self, e: tkinter.Event):
        Context.__init__(self)
        self.copy_text(e=e)
        self.add_separator()
        self.copy_all(e=e)
        self.do_popup(e=e)


class ImageInfo(CWindow, SysUtils):
    def __init__(self, parrent: tkinter.Toplevel, img_src: Literal["file path"]):
        CWindow.__init__(self)
        self.title(string=cnf.lng.info)
        self.minsize(width=416, height=155)
        place_center(win=self, width=416, height=155, parrent_win=parrent)
        self.protocol(name="WM_DELETE_WINDOW",
                      func=lambda: self.__close_info(parrent=parrent))
        self.bind(sequence="<Escape>",
                  func=lambda e: self.__close_info(parrent=parrent))

        name = img_src.split(os.sep)[-1]
        try:
            filemod = datetime.fromtimestamp(os.path.getmtime(filename=img_src))
            filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")
            w, h = Image.open(img_src).size
            filesize = round(os.path.getsize(filename=img_src) / (1024*1024), 2)
        except FileNotFoundError:
            self.print_err()
            filemod = cnf.lng.no_connection
            filemod = cnf.lng.no_connection
            w, h = cnf.lng.no_connection, cnf.lng.no_connection
            filesize = cnf.lng.no_connection

        frame = CFrame(master=self)
        frame.pack(expand=1, fill="both")

        max_ln = 40

        r_name = "\n".join(
            re.findall(r".{1,%i}" % max_ln, name)
            )
        l_name = cnf.lng.file_name + "\n"*r_name.count("\n")

        r_path = "\n".join(
            re.findall(r".{1,%i}" % max_ln, os.path.split(img_src)[0])
            )
        l_path = cnf.lng.file_path + "\n"*r_path.count("\n")

        labels = {cnf.lng.collection: get_coll_name(src=img_src),
                  l_name: r_name,
                  cnf.lng.date_changed: filemod,
                  cnf.lng.resolution: f"{w}x{h}",
                  cnf.lng.file_size: f"{filesize}{cnf.lng.mb}",
                  l_path: r_path}

        left_lbl = CLabel(master=frame, justify="right", anchor="ne",
                          text="\n".join(i for i in labels.keys()))
        left_lbl.pack(anchor="n", side="left")

        fake = CLabel(master=frame, justify="left", anchor="nw",
                      text="\n".join(i for i in labels.values()))

        text_frame = CFrame(master=frame, height=fake.winfo_reqheight(),
                            width=fake.winfo_reqwidth())
        text_frame.pack(anchor="n", side="left", pady=3)
        text_frame.pack_propagate(flag=False)

        fake.destroy()

        right_lbl = tkinter.Text(master=text_frame, highlightthickness=0,
                                 bg=cnf.bg_color, fg=cnf.fg_color,
                                 font=("San Francisco Pro", 13, "normal"))

        right_lbl.insert(index=1.0, chars="\n".join(i for i in labels.values()))
        right_lbl.bind(sequence="<ButtonRelease-2>", func=self.__r_click)

        right_lbl.configure(state=tkinter.DISABLED)
        right_lbl.pack(anchor="n", side="left")

        cnf.root.update_idletasks()
        self.grab_set_global()

    def __r_click(self, e: tkinter.Event):
        try:
            e.widget.copy = e.widget.selection_get()
        except tkinter.TclError:
            self.print_err()
            e.widget.copy = e.widget.get("1.0",tkinter.END)

        ContextInfo(e=e)

    def __close_info(self, parrent: tkinter.Toplevel):
        self.grab_release()
        self.destroy()
        if isinstance(parrent, tkinter.Toplevel):
            parrent.grab_set_global()