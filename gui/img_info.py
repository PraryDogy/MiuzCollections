import os
import re
import tkinter
from datetime import datetime
from typing import Literal

from PIL import Image

from cfg import cnf

from .utils import *
from .widgets import *
from .context import *


class ContextInfo(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()
        self.copy_text(e)
        self.add_separator()
        self.copy_all(e)
        self.do_popup(e)


class ImageInfo(CWindow):
    def __init__(self, parrent: tkinter.Toplevel, img_src: Literal["file path"]):
        super().__init__()
        self.title(cnf.lng.info)
        self.minsize(416, 155)
        place_center(parrent, self, 416, 155)
        self.protocol("WM_DELETE_WINDOW", lambda: self.close_info(parrent))
        self.bind("<Escape>", lambda e: self.close_info(parrent))

        name = img_src.split(os.sep)[-1]
        try:
            filemod = datetime.fromtimestamp(os.path.getmtime(img_src))
            filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")
            w, h = Image.open(img_src).size
            filesize = round(os.path.getsize(img_src)/(1024*1024), 2)
        except FileNotFoundError:
            filemod = ""
            filemod = ""
            w, h = "", ""
            filesize = ""

        frame = CFrame(self)
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

        labels = {
            cnf.lng.collection: get_coll_name(img_src),
            l_name: r_name,
            cnf.lng.date_changed: filemod,
            cnf.lng.resolution: f"{w}x{h}",
            cnf.lng.file_size: f"{filesize}мб",
            l_path: r_path,
            }

        left_lbl = CLabel(
            frame,
            text="\n".join(i for i in labels.keys()),
            justify="right",
            anchor="ne",
            )
        left_lbl.pack(anchor="n", side="left")

        fake = CLabel(
            frame,
            text="\n".join(i for i in labels.values()),
            justify="left",
            anchor="nw",
            )

        text_frame = CFrame(
            frame,
            height=fake.winfo_reqheight(),
            width=fake.winfo_reqwidth()
            )
        text_frame.pack(anchor="n", side="left", pady=3)
        text_frame.pack_propagate(False)

        fake.destroy()

        right_lbl = tkinter.Text(
            text_frame,
            highlightthickness=0,
            bg=cnf.bg_color,
            fg=cnf.fg_color,
            font=("San Francisco Pro", 13, "normal"),
            )

        right_lbl.insert(1.0, "\n".join(i for i in labels.values()))
        right_lbl.bind("<ButtonRelease-2>", self.r_click)

        right_lbl.configure(state=tkinter.DISABLED)
        right_lbl.pack(anchor="n", side="left")

        cnf.root.update_idletasks()
        self.grab_set_global()

    def r_click(self, e: tkinter.Event):
        try:
            e.widget.copy = e.widget.selection_get()
        except tkinter.TclError:
            e.widget.copy = e.widget.get("1.0",tkinter.END)
            print("img_info > ImageInfo > r_click > text not selected")

        ContextInfo(e)

    def close_info(self, parrent: tkinter.Toplevel):
        self.grab_release()
        self.destroy()
        if isinstance(parrent, tkinter.Toplevel):
            parrent.grab_set_global()