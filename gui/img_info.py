import os
import tkinter
from datetime import datetime

from PIL import Image

from cfg import cnf

from .utils import *
from .widgets import *


class ContextInfo(Context):
    def __init__(self, e: tkinter.Event):
        super().__init__()
        self.cont_copy_text(e)
        self.add_separator()
        self.cont_copy_all(e)
        self.do_popup(e)


class ImageInfo(CWindow):
    def __init__(self, src: str):
        under_win = None

        for k, v in cnf.root.children.items():
            if isinstance(v, CWindow):
                under_win = v

        if not under_win:
            under_win = cnf.root

        super().__init__()

        self.title(cnf.lang.info)
        self.configure(padx=10, pady=10)

        name = src.split(os.sep)[-1]
        filemod = datetime.fromtimestamp(os.path.getmtime(src))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")
        w, h = Image.open(src).size
        filesize = round(os.path.getsize(src)/(1024*1024), 2)

        frame = CFrame(self)
        frame.pack(expand=True, fill="both")

        max_ln = 40

        r_name = "".join(
            [name[i:i+max_ln]+"\n" for i in range(0, len(name), max_ln)]
            ).strip()
        l_name = cnf.lang.info_filename + "\n"*r_name.count("\n")

        r_path = os.path.split(src)[0]
        r_path = "".join(
            [r_path[i:i+max_ln]+"\n" for i in range(0, len(r_path), max_ln)]
            ).strip()
        l_path = cnf.lang.info_path + "\n"*r_path.count("\n")

        labels = {
            cnf.lang.info_collection: get_coll_name(src),
            l_name: r_name,
            cnf.lang.info_chanded: filemod,
            cnf.lang.info_resolution: f"{w}x{h}",
            cnf.lang.info_size: f"{filesize}мб",
            l_path: r_path,
            }

        left_lbl = CLabel(
            frame,
            text = "\n".join(i for i in labels.keys()),
            justify = tkinter.RIGHT,
            anchor = tkinter.NE,
            )
        left_lbl.pack(anchor=tkinter.N, side=tkinter.LEFT)

        fake = CLabel(
            frame,
            text = "\n".join(i for i in labels.values()),
            justify = tkinter.LEFT,
            anchor = tkinter.NW,
            )

        text_frame = CFrame(
            frame,
            height=fake.winfo_reqheight(),
            width=fake.winfo_reqwidth()
            )
        text_frame.pack(anchor=tkinter.N, side=tkinter.LEFT, pady=3)
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
        right_lbl.pack(anchor=tkinter.N, side=tkinter.LEFT)

        self.protocol("WM_DELETE_WINDOW", self.close_win)
        self.bind('<Escape>', self.close_win)

        cnf.root.update_idletasks()

        x, y = under_win.winfo_x(), under_win.winfo_y()
        xx = x + under_win.winfo_width()//2 - self.winfo_width()//2
        yy = y + under_win.winfo_height()//2 - self.winfo_height()//2

        self.geometry(f'+{xx}+{yy}')

        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def close_win(self, e=None):
        self.destroy()
        focus_last_win()

    def r_click(self, e: tkinter.Event):
        try:
            e.widget.copy = e.widget.selection_get()
        except tkinter.TclError:
            e.widget.copy = e.widget.get("1.0",tkinter.END)
            print("img_info > ImageInfo > r_click > text not selected")

        ContextInfo(e)
