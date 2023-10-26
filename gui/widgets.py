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
    def __init__(self, master: tkinter, bg=cnf.btn_color, height=1, **kw):
        super().__init__(master, bg=bg, height=height, **kw)


class CButton(tkinter.Label):
    def __init__(
            self, master: tkinter, bg=cnf.btn_color, fg=cnf.fg_color,
            width=11, height=1, font=("San Francisco Pro", 13, "normal"),
            **kwargs
            ):
        super().__init__(
            master, bg=bg, fg=fg, width=width, height=height,
            font=font, **kwargs
            )

    def cmd(self, cmd):
        self.bind('<ButtonRelease-1>', cmd)


class CFrame(tkinter.Frame):
    def __init__(self, master: tkinter, bg=cnf.bg_color, **kwargs):
        super().__init__(master, bg=bg, **kwargs)


class CLabel(tkinter.Label):
    def __init__(
            self, master, bg=cnf.bg_color, fg=cnf.fg_color,
            font=("San Francisco Pro", 13, "normal"),**kwargs
            ):
        super().__init__(master, bg=bg, fg=fg, font=font, **kwargs)


class CWindow(tkinter.Toplevel):
    def __init__(self, bg=cnf.bg_color, padx=15, pady=15):
        super().__init__(bg=bg, padx=padx, pady=pady)
        cnf.root.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.close_win)
        self.bind('<Escape>', self.close_win)
        self.bind('<Command-w>', self.close_win)
        self.bind('<Command-q>', on_exit)

        self.resizable(0,0)

    def close_win(self, e=None):
        self.destroy()
        focus_last_win()


class SmbAlert(CWindow):
    def __init__(self):
        super().__init__()

        txt = cnf.lng.no_connection
        title_lbl = CLabel(
            self, text=txt, font=('San Francisco Pro', 22, 'bold')
            )
        title_lbl.pack()

        txt2 = cnf.lng.smb_descr
        descr_lbl = CLabel(self, text=txt2, justify="left")
        descr_lbl.pack(padx=15, pady=(0, 5))

        btn = CButton(self, text=cnf.lng.close)
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
            label=cnf.lng.view,
            command=lambda: ImgViewer(e.widget.src, e.widget.all_src)
            )

    def imginfo(self, e: tkinter.Event):
        from .img_info import ImageInfo
        self.add_command(
            label=cnf.lng.info,
            command=lambda: ImageInfo(e.widget.src)
            )

    def reveal_jpg(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.find_jpg,
            command=lambda: finder_actions(e.widget.src, reveal=True),
            
            )

    def reveal_tiffs(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.find_tiff,
            command=lambda: finder_actions(e.widget.src, tiff=True, reveal=True),
            
            )

    def pastesearch(self):
        self.add_command(
            label=cnf.lng.paste,
            command=paste_search
            )

    def clear(self):
        self.add_command(
            label=cnf.lng.clear,
            command=lambda: Globals.search_var.set("")
            )

    def download_onefile(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lng.copy} jpg {cnf.lng.to_downloads}"
                ),
            command=lambda: finder_actions(e.widget.src, download=True),
            
        )

    def download_tiffs(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lng.copy} tiff {cnf.lng.to_downloads}"
                ),
            command=lambda: finder_actions(e.widget.src, tiff=True, download=True),
            
        )

    def reveal_coll(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.reveal_coll,
            command=lambda: reveal_coll(e.widget.coll_name)
            )

    def show_coll(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.view,
            command=lambda: Globals.show_coll(e)
            )
        
    def copy_tiffs_paths(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.copy_path_tiff,
            command=lambda: finder_actions(e.widget.src, tiff=True, copy_path=True),
            
            )
        
    def copy_jpg_path(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.copy_path_jpg,
            command=lambda: finder_actions(e.widget.src, copy_path=True),
            
            )

    def db_remove_img(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.remove_fromapp,
            command=lambda: db_remove_img(e.widget.src)
            )

    def download_group(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lng.copy} jpg\n"
                f"{cnf.lng.from_pretext} \"{e.widget.title}\" "
                f"{cnf.lng.to_downloads}"
                ),
            command=lambda: finder_actions(e.widget.paths_list, download=True),
            
        )

    def download_group_tiffs(self, e: tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lng.copy} tiff\n"
                f"{cnf.lng.from_pretext} \"{e.widget.title}\" "
                f"{cnf.lng.to_downloads}"
                ),
            command=lambda: finder_actions(e.widget.paths_list, tiff=True, download=True),
            
            )
        
    def copy_text(self, e: tkinter.Event):
        self.add_command(
            label=cnf.lng.copy,
            command=lambda: copy_text(e.widget.copy)
            )

    def copy_all(self, e:tkinter.Event):
        self.add_command(
            label=cnf.lng.copy_all,
            command=lambda: copy_text(e.widget.get("1.0",tkinter.END))
            )

    def download_fullsize(self, e:tkinter.Event):
        self.add_command(
            label=cnf.lng.fullsize,
            command=lambda: finder_actions(e.widget.src, tiff=True, fullsize=True),
            
            )

    def download_group_fullsize(self, e:tkinter.Event):
        self.add_command(
            label=(
                f"{cnf.lng.group_fullsize}\n"
                f"{cnf.lng.from_pretext} \"{e.widget.title}\" "
                f"{cnf.lng.to_downloads}"
                ),
            command=lambda: finder_actions(e.widget.paths_list, tiff=True, fullsize=True),
            )
        
    def apply_filter(self, label, e=None):
        self.add_command(
            label=label,
            command=lambda: apply_filter(label, e)
            )
        
    def please_wait(self):
        self.add_command(
            label=(
                f"{cnf.lng.please_wait}"
                f"\n{cnf.lng.updating} {cnf.lng.all_colls.lower()}"
                )
                )