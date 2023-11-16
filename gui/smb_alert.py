from .utils import *
from .widgets import *
from cfg import cnf


__all__ = ("SmbAlert", )


class SmbAlert(CWindow):
    def __init__(self):
        super().__init__()
        self.minsize(420, 85)
        self.protocol("WM_DELETE_WINDOW", self.close_smb)
        self.bind("<Escape>", self.close_smb)
        place_center(cnf.root, self, 420, 85)

        txt = cnf.lng.no_connection
        title_lbl = CLabel(
            self, text=txt, font=("San Francisco Pro", 22, "bold")
            )
        title_lbl.pack()

        txt2 = cnf.lng.smb_descr
        descr_lbl = CLabel(self, text=txt2, justify="left")
        descr_lbl.pack(padx=15, pady=(0, 5))

        cnf.root.update_idletasks()
        self.grab_set_global()

    def close_smb(self, e=None):
        self.destroy()
        cnf.root.focus_force()