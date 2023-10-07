import os
import sys
import tkinter
from datetime import datetime

from PIL import Image

from cfg import conf

from .globals import Globals
from .utils import *

__all__ = (
    "CSep",
    "CButton",
    "CFrame",
    "CLabel",
    "CWindow",
    "SmbAlert",
    "ImageInfo",
    "MacMenu",
    "Context",
    )


class CSep(tkinter.Frame):
    def __init__(self, master: tkinter, **kw):
        super().__init__(master, **kw)

        if not kw:
            self.configure(bg=conf.btn_color, height=1)


class CButton(tkinter.Label):
    def __init__(self, master: tkinter, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg=conf.btn_color, fg=conf.fg_color, width=11, height=1,
            font=("San Francisco Pro", 13, "normal"))

    def cmd(self, cmd):
        self.bind('<ButtonRelease-1>', cmd)

    def press(self):
        self.configure(bg=conf.sel_color)
        conf.root.after(100, lambda: self.configure(bg=conf.btn_color))


class CFrame(tkinter.Frame):
    def __init__(self, master: tkinter, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=conf.bg_color)


class CLabel(tkinter.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg=conf.bg_color,
            fg=conf.fg_color,
            font=("San Francisco Pro", 13, "normal"),
            )


class CWindow(tkinter.Toplevel):
    def __init__(self):
        super().__init__()
        conf.root.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.close_win)
        self.bind('<Escape>', self.close_win)

        self.bind('<Command-q>', on_exit)

        self.resizable(0,0)
        self.configure(bg=conf.bg_color, padx=15, pady=15)

    def close_win(self, e=None):
        self.destroy()
        focus_last_win()


class SmbAlert(CWindow):
    def __init__(self):
        super().__init__()

        txt = conf.lang.smb_title
        title_lbl = CLabel(self, text=txt)
        title_lbl.configure(font=('San Francisco Pro', 22, 'bold'))
        title_lbl.pack()

        txt2 = conf.lang.smb_descr
        descr_lbl = CLabel(self, text=txt2, justify=tkinter.LEFT)
        descr_lbl.pack(padx=15, pady=(0, 5))

        btn = CButton(self, text=conf.lang.close)
        btn.cmd(self.btn_cmd)
        btn.pack()

        conf.root.update_idletasks()
        place_center()
        self.deiconify()
        self.wait_visibility()
        self.grab_set_global()

    def btn_cmd(self, e=None):
        self.destroy()
        focus_last_win()


class ImageInfo(CWindow):
    def __init__(self, src: str):
        under_win = None

        for k, v in conf.root.children.items():
            if isinstance(v, CWindow):
                under_win = v

        if not under_win:
            under_win = conf.root

        super().__init__()

        self.title(conf.lang.info)
        self.geometry("400x110")
        self.minsize(400, 110)
        self.maxsize(800, 150)
        self.configure(padx=5, pady=5)
        self.resizable(1, 1)

        name = src.split(os.sep)[-1]
        filemod = datetime.fromtimestamp(os.path.getmtime(src))
        filemod = filemod.strftime("%d-%m-%Y, %H:%M:%S")
        w, h = Image.open(src).size
        filesize = round(os.path.getsize(src)/(1024*1024), 2)

        frame = CFrame(self)
        frame.pack(expand=True, fill="both")

        labels = {
            conf.lang.info_collection: get_coll_name(src),
            conf.lang.info_filename: name,
            conf.lang.info_chanded: filemod,
            conf.lang.info_resolution: f"{w}x{h}",
            conf.lang.info_size: f"{filesize}мб",
            conf.lang.info_path: src,
            }

        left_lbl = CLabel(
            frame,
            text = "\n".join(i for i in labels.keys()),
            justify = tkinter.RIGHT,
            anchor = tkinter.E,
            )
        left_lbl.pack(anchor=tkinter.CENTER, side=tkinter.LEFT)

        right_lbl = CLabel(
            frame,
            text = "\n".join(i for i in labels.values()),
            justify = tkinter.LEFT,
            anchor = tkinter.W,
            )
        right_lbl.pack(anchor=tkinter.CENTER, side=tkinter.LEFT)

        self.protocol("WM_DELETE_WINDOW", self.close_win)
        self.bind('<Escape>', self.close_win)

        conf.root.update_idletasks()

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


class MacMenu(tkinter.Menu):
    def __init__(self):
        menubar = tkinter.Menu(conf.root)
        tkinter.Menu.__init__(self, menubar)

        if sys.version_info.minor < 10:
            conf.root.createcommand('tkAboutDialog', self.about_dialog)

        conf.root.configure(menu=menubar)

    def about_dialog(self):
        try:
            conf.root.tk.call('tk::mac::standardAboutPanel')
        except Exception:
            print("no dialog panel")


class Context(tkinter.Menu, Reveal):
    def __init__(self):
        super().__init__()

    def context_view(self, e: tkinter.Event):
        from .img_viewer import ImgViewer
        self.add_command(
            label=conf.lang.preview,
            command=lambda: ImgViewer(e.widget.src, e.widget.all_src)
            )

    def context_sep(self):
        self.add_separator()

    def context_img_info(self, e: tkinter.Event):
        self.add_command(
            label=conf.lang.info,
            command=lambda: ImageInfo(e.widget.src)
            )

    def context_show_jpg(self, e: tkinter.Event):
        self.add_command(
            label=conf.lang.show_jpeg,
            command = lambda: self.reveal_jpg(e.widget.src)
            )

    def context_show_tiffs(self, e: tkinter.Event):
        tiffs = self.find_tiffs(e.widget.src)
        self.add_command(
            label=conf.lang.show_tiff,
            command = lambda: self.reveal_tiffs(tiffs)
            )

    def context_paste(self):
        pasted = conf.root.clipboard_get().strip()
        self.add_command(
            label=conf.lang.search_paste,
            command=lambda: Globals.search_var.set(pasted)
            )

    def context_clear(self):
        self.add_command(
            label=conf.lang.search_clear,
            command=lambda: Globals.search_var.set("")
            )
    
    def context_download_group(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{conf.lang.context_copy} "
                f"\"{e.widget.title}\" "
                f"{conf.lang.context_downloads}"
                ),
            command=lambda: download_files(e.widget.title, e.widget.paths_list)
        )

    def context_download_onefile(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{conf.lang.context_copy} "
                "jpeg "
                f"{conf.lang.context_downloads}"
                ),
            command=lambda: download_onefile(e.widget.src)
        )

    def context_download_tiffs(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{conf.lang.context_copy} "
                "tiff "
                f"{conf.lang.context_downloads}"
                ),
            command=lambda: download_tiffs(e.widget.src)
        )

    def do_popup(self, e: tkinter.Event):
        try:
            self.tk_popup(e.x_root, e.y_root)
        finally:
            self.grab_release()