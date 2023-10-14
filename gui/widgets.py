import os
import sys
import tkinter
from datetime import datetime

from PIL import Image

from cfg import cnf

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
            self.configure(bg=cnf.btn_color, height=1)


class CButton(tkinter.Label):
    def __init__(self, master: tkinter, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg=cnf.btn_color, fg=cnf.fg_color, width=11, height=1,
            font=("San Francisco Pro", 13, "normal"))

    def cmd(self, cmd):
        self.bind('<ButtonRelease-1>', cmd)


class CFrame(tkinter.Frame):
    def __init__(self, master: tkinter, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg=cnf.bg_color)


class CLabel(tkinter.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg=cnf.bg_color,
            fg=cnf.fg_color,
            font=("San Francisco Pro", 13, "normal"),
            )


class CWindow(tkinter.Toplevel):
    def __init__(self):
        super().__init__()
        cnf.root.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.close_win)
        self.bind('<Escape>', self.close_win)

        self.bind('<Command-q>', on_exit)

        self.resizable(0,0)
        self.configure(bg=cnf.bg_color, padx=15, pady=15)

    def close_win(self, e=None):
        self.destroy()
        focus_last_win()


class SmbAlert(CWindow):
    def __init__(self):
        super().__init__()

        txt = cnf.lang.smb_title
        title_lbl = CLabel(self, text=txt)
        title_lbl.configure(font=('San Francisco Pro', 22, 'bold'))
        title_lbl.pack()

        txt2 = cnf.lang.smb_descr
        descr_lbl = CLabel(self, text=txt2, justify=tkinter.LEFT)
        descr_lbl.pack(padx=15, pady=(0, 5))

        btn = CButton(self, text=cnf.lang.close)
        btn.cmd(self.btn_cmd)
        btn.pack()

        cnf.root.update_idletasks()
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

        for k, v in cnf.root.children.items():
            if isinstance(v, CWindow):
                under_win = v

        if not under_win:
            under_win = cnf.root

        super().__init__()

        self.title(cnf.lang.info)
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
            cnf.lang.info_collection: get_coll_name(src),
            cnf.lang.info_filename: name,
            cnf.lang.info_chanded: filemod,
            cnf.lang.info_resolution: f"{w}x{h}",
            cnf.lang.info_size: f"{filesize}мб",
            cnf.lang.info_path: src,
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


class MacMenu(tkinter.Menu):
    def __init__(self):
        menubar = tkinter.Menu(cnf.root)
        tkinter.Menu.__init__(self, menubar)

        if sys.version_info.minor < 10:
            cnf.root.createcommand('tkAboutDialog', self.about_dialog)

        cnf.root.configure(menu=menubar)

    def about_dialog(self):
        try:
            cnf.root.tk.call('tk::mac::standardAboutPanel')
        except Exception:
            print("no dialog panel")


class Context(tkinter.Menu):
    def __init__(self):
        super().__init__()

    def cont_sep(self):
        self.add_separator()

    def do_popup(self, e: tkinter.Event):
        try:
            self.tk_popup(e.x_root, e.y_root)
        finally:
            self.grab_release()

    def cont_imgview(self, e: tkinter.Event):
        from .img_viewer import ImgViewer
        self.add_command(
            label=cnf.lang.view,
            command=lambda: ImgViewer(e.widget.src, e.widget.all_src)
            )

    def cont_imginfo(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.info,
            command=lambda: ImageInfo(e.widget.src)
            )

    def cont_reveal_jpg(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.show_jpeg,
            command=lambda: reveal_jpg(e.widget.src)
            )

    def cont_reveal_tiffs(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.show_tiff,
            command=lambda: reveal_tiffs(find_tiffs(e.widget.src))
            )

    def cont_pastesearch(self):
        self.add_command(
            label=cnf.lang.search_paste,
            command=paste_search
            )

    def cont_clear(self):
        self.add_command(
            label=cnf.lang.search_clear,
            command=lambda: Globals.search_var.set("")
            )

    def cont_download_onefile(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lang.context_copy} "
                "jpeg "
                f"{cnf.lang.context_downloads}"
                ),
            command=lambda: download_one_jpeg(e.widget.src)
        )

    def cont_download_tiffs(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lang.context_copy} "
                "tiff "
                f"{cnf.lang.context_downloads}"
                ),
            command=lambda: download_tiffs(e.widget.src)
        )

    def cont_reveal_coll(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.show_coll,
            command=lambda: reveal_coll(e.widget.coll_name)
            )

    def cont_show_coll(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.view,
            command=lambda: Globals.show_coll(e)
            )
        
    def cont_copy_tiffs_paths(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.copy_tiff_path,
            command=lambda: copy_tiffs_paths(e.widget.src)
            )
        
    def cont_copy_jpeg_path(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.copy_jpeg_path,
            command=lambda: copy_jpeg_path(e.widget.src),
            )

    def cont_db_remove_img(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.remove_fromapp,
            command=lambda: db_remove_img(e.widget.src)
            )

    def cont_download_group(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lang.context_copy} jpeg\n"
                f"{cnf.lang.live_from} \"{e.widget.title}\" "
                f"{cnf.lang.context_downloads}"
                ),
            command=lambda: download_group_jpeg(e.widget.title, e.widget.paths_list)
        )

    def cont_download_group_tiffs(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lang.context_copy} tiff\n"
                f"{cnf.lang.live_from} \"{e.widget.title}\" "
                f"{cnf.lang.context_downloads}"
                ),
            command=lambda: download_group_tiff(e.widget.title, e.widget.paths_list)
            )