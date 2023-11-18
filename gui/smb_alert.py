import tkinter

from cfg import cnf

from .utils import *
from .widgets import *

__all__ = ("SmbAlert", )


class SmbAlert(CWindow):
    def __init__(self):
        CWindow.__init__(self)
        self.minsize(420, 85)
        self.protocol("WM_DELETE_WINDOW", self.__close_smb)
        self.bind("<Escape>", self.__close_smb)
        place_center(self, 420, 85)

        title_lbl = CLabel(self, text=cnf.lng.no_connection,
                           font=("San Francisco Pro", 22, "bold"))
        title_lbl.pack()

        descr_lbl = CLabel(self, text=cnf.lng.smb_descr, justify="left")
        descr_lbl.pack(padx=15, pady=(0, 5))

        cnf.root.update_idletasks()
        self.grab_set_global()

    def __close_smb(self, e: tkinter.Event = None):
        self.destroy()
        cnf.root.focus_force()