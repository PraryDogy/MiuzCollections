import tkinter

from customtkinter import CTkProgressBar

from cfg import cnf
from utils import SysUtils

from .widgets import *

__all__ = ("ScanerGui", )


class Win:
    win: CWindow = False


class ScanerGui(CWindow, SysUtils):
    def __init__(self):
        w, h = 300, 150
        if Win.win:
            Win.win.destroy()
            Win.win = False

        CWindow.__init__(self)
        Win.win = self
        self.title(string=cnf.lng.updating)
        self.geometry(newGeometry=f"{w}x{h}")
        self.place_center(w=w, h=h)
        self.protocol(name="WM_DELETE_WINDOW", func=self.close_scangui)
        self.bind(sequence="<Escape>", func=self.close_scangui)

        descr = CLabel(master=self, text=cnf.lng.scan_gui_text,
                                 anchor="w", justify="left")
        descr.pack(expand=1, fill="both")

        pr_fr = CFrame(master=self)
        pr_fr.pack(pady=10, expand=1)

        self.progressbar = CTkProgressBar(master=pr_fr, width=170,
                                corner_radius=cnf.corner,
                                progress_color=cnf.blue_color,
                                variable=cnf.progressbar_var)
        self.progressbar.pack(side="left")

        self.can_btn = CButton(master=pr_fr, text=cnf.lng.stop)
        self.can_btn.pack(side="left", padx=(15, 0))
        self.can_btn.cmd(self.cancel_scan)

        self.close_btn = CButton(master=self, text=cnf.lng.close)
        self.close_btn.pack()
        self.close_btn.cmd(self.close_scangui)

    def cancel_scan(self, e: tkinter.Event = None):
        cnf.scan_status = False

    def close_scangui(self, e: tkinter.Event = None):
        self.destroy()
        cnf.root.focus_force()
        Win.win = False
