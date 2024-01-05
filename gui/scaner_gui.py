import tkinter

from customtkinter import CTkProgressBar

from cfg import cnf
from utils import SysUtils

from .widgets import *

__all__ = ("ScanerGui", )


class Win:
    win: CWindow = False


class Colors:
    prog_color = "#262626"


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
            corner_radius=cnf.corner, variable=cnf.progressbar_var)
        self.progressbar.pack(side="left")

        self.can_btn = CButton(master=pr_fr, text=cnf.lng.stop)
        self.can_btn.pack(side="left", padx=(15, 0))
        self.can_btn.cmd(self.cancel_scan)

        close_btn = CButton(master=self, text=cnf.lng.close)
        close_btn.pack()
        close_btn.cmd(self.close_scangui)

        self.prog_callback()

        self.tra = cnf.progressbar_var.trace_add(
            mode="read", callback=self.prog_callback)

    def cancel_scan(self, e: tkinter.Event = None):
        cnf.scan_status = False
        cnf.progressbar_var.set(value=1)
        self.prog_callback()

    def close_scangui(self, e: tkinter.Event = None):
        cnf.progressbar_var.trace_remove(mode="read", cbname=self.tra)
        self.destroy()
        cnf.root.focus_force()
        Win.win = False

    def prog_callback(self, *args):
        if cnf.progressbar_var.get() >= 0.6:
            self.can_btn.configure(state="disabled")
            self.progressbar.configure(progress_color=Colors.prog_color)

        if cnf.progressbar_var.get() < 0.6:
            self.can_btn.configure(state="normal")
            self.progressbar.configure(progress_color=cnf.blue_color)
