import tkinter

from cfg import cnf

from utils import SysUtils
from .widgets import *

__all__ = ("SmbAlert", )


class Win:
    win = False


class SmbAlert(CWindow, SysUtils):
    def __init__(self):
        w, h = 420, 85
        if Win.win:
            Win.win.destroy()
            Win.win = False

        CWindow.__init__(self)
        Win.win = self
        self.minsize(width=w, height=h)
        self.protocol("WM_DELETE_WINDOW", self.__close_smb)
        self.bind("<Escape>", self.__close_smb)
        self.place_center(w=w, h=h)

        title_lbl = CLabel(master=self, text=cnf.lng.no_connection,
                           font=("San Francisco Pro", 22, "bold"))
        title_lbl.pack()

        descr_lbl = CLabel(master=self, text=cnf.lng.smb_descr, justify="left")
        descr_lbl.pack(padx=15, pady=(0, 5))

        close = CButton(master=self, text=cnf.lng.close)
        close.pack(pady=(10, 0))
        close.cmd(self.__close_smb)

    def __close_smb(self, e: tkinter.Event = None):
        self.destroy()
        cnf.root.focus_force()
        Win.win = False