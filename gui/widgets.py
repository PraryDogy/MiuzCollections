import os
import sys
import tkinter

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
        self.bind('<Command-w>', self.close_win)
        self.bind('<Command-q>', on_exit)

        self.resizable(0,0)
        self.configure(bg=cnf.bg_color, padx=15, pady=15)

    def close_win(self, e=None):
        self.destroy()
        focus_last_win()


class SmbAlert(CWindow):
    def __init__(self):
        super().__init__()

        txt = cnf.lang.no_connection
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

    def sep(self):
        self.add_separator()

    def do_popup(self, e: tkinter.Event):
        try:
            self.tk_popup(e.x_root, e.y_root)
        finally:
            self.grab_release()

    def imgview(self, e: tkinter.Event):
        from .img_viewer import ImgViewer
        self.add_command(
            label=cnf.lang.view,
            command=lambda: ImgViewer(e.widget.src, e.widget.all_src)
            )

    def imginfo(self, e: tkinter.Event):
        from .img_info import ImageInfo
        self.add_command(
            label=cnf.lang.info,
            command=lambda: ImageInfo(e.widget.src)
            )

    def reveal_jpg(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.find_jpg,
            command=lambda: reveal_jpg(e.widget.src)
            )

    def reveal_tiffs(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.find_tiff,
            command=lambda: reveal_tiffs(find_tiffs(e.widget.src))
            )

    def pastesearch(self):
        self.add_command(
            label=cnf.lang.paste,
            command=paste_search
            )

    def clear(self):
        self.add_command(
            label=cnf.lang.clear,
            command=lambda: Globals.search_var.set("")
            )

    def download_onefile(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lang.copy} jpg {cnf.lang.to_downloads}"
                ),
            command=lambda: download_one_jpg(e.widget.src)
        )

    def download_tiffs(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lang.copy} tiff {cnf.lang.to_downloads}"
                ),
            command=lambda: download_tiffs(e.widget.src)
        )

    def reveal_coll(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.reveal_coll,
            command=lambda: reveal_coll(e.widget.coll_name)
            )

    def show_coll(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.view,
            command=lambda: Globals.show_coll(e)
            )
        
    def copy_tiffs_paths(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.copy_path_tiff,
            command=lambda: copy_tiffs_paths(e.widget.src)
            )
        
    def copy_jpg_path(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.copy_path_jpg,
            command=lambda: copy_jpg_path(e.widget.src),
            )

    def db_remove_img(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.remove_fromapp,
            command=lambda: db_remove_img(e.widget.src)
            )

    def download_group(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lang.copy} jpg\n"
                f"{cnf.lang.from_pretext} \"{e.widget.title}\" "
                f"{cnf.lang.to_downloads}"
                ),
            command=lambda: download_group_jpg(e.widget.title, e.widget.paths_list)
        )

    def download_group_tiffs(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lang.copy} tiff\n"
                f"{cnf.lang.from_pretext} \"{e.widget.title}\" "
                f"{cnf.lang.to_downloads}"
                ),
            command=lambda: download_group_tiff(e.widget.title, e.widget.paths_list)
            )
        
    def copy_text(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lang.copy,
            command=lambda: copy_text(e.widget.copy)
            )

    def copy_all(self, e:tkinter.Event):
        self.add_command(
            label=cnf.lang.copy_all,
            command=lambda: copy_text(e.widget.get("1.0",tkinter.END))
            )

    def download_fullsize(self, e:tkinter.Event):
        self.add_command(
            label=cnf.lang.fullsize,
            command=lambda: download_fullsize(e.widget.src)
            )

    def download_group_fullsize(self, e:tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lang.group_fullsize}\n"
                f"{cnf.lang.from_pretext} \"{e.widget.title}\" "
                f"{cnf.lang.to_downloads}"
                ),
            command=lambda: download_group_fullsize(
                e.widget.title, e.widget.paths_list
                )
            )